# Then script depends on a "seakerUI_job" table in DB that contains:
#	All columns in the seakerUI_querytypes table PLUS
#	"status" field that will have values of "Not Submitted", "Submitted", "In Progress", "Completed"
#	"augury_job_id" field that will contain the "id" returned by Augury when submitting a job
#
# General flow:
#
# 1. Clicking "Run Query" in the Seaker UI will create a "job" in the database with status "Not Submitted"
#
# 2. This script will be run once per minute (via supervisord or cron) to:
#	a. Check database for jobs with "Submitted" or "In Progress" status.  For each one:
#		Get job details via GET request to /jobs/{id}/details
#		Iterate through the "results" array in the response
#			IF any query has a status of "In Progress", set the job status to "In Progress"
#			IF all queries have a status of "Completed",
#				download/save the results via GET to /jobs/{id}
#				change job status to "Completed"
#	b. Check database for jobs with "Pending" status (i.e. new jobs). For each one:
#		Submit job to Augury /jobs endpoint,
#		Save the "id" returned by Augury to the database ("augury_job_id" field)
#		Change the status of the job to "Submitted"

# Augury API testing:
#
# Get list of jobs
# curl --url 'https://augury5.heliumrain.com/api/jobs' --request GET --header 'Content-Type: application/x-www-form-urlencoded' --header 'Authorization: a89e6b0d7c358b99a7411174a4106e0ab5429ed0'
#
# Get details of a specific job
# curl --url 'https://augury5.heliumrain.com/api/jobs/642725/details' --request GET --header 'Content-Type: application/json' --header 'Authorization: a89e6b0d7c358b99a7411174a4106e0ab5429ed0'
# {
#   "job_id":642725,
#   "job_name":"Test Query1",
#   "group_name":null,
#   "origin":"api",
#   "results":[
#      {
#         "id":7749322,
#         "query_type":"flows",
#         "name":"Flows",
#         "created_at":"2020-06-02 17:35:56",
#         "started_at":"2020-06-02 17:35:58",
#         "updated_at":"2020-06-02 17:35:56",
#         "completed_at":"2020-06-02 17:36:16",
#         "errors":null,
#         "query":"{\"cc\":[],\"cidr\":[],\"port\":[],\"limit\":5000000,\"proto\":[],\"any_cc\":[],\"format\":\"json\",\"ip_addr\":[],\"timeout\":14400,\"any_cidr\":[\"47.206.130.223\\\/32\"],\"any_port\":[80],\"end_date\":\"2020-04-29T13:52:51.999999+00:00\",\"tcp_flags\":[],\"exclude_cc\":[],\"num_octets\":[],\"port_range\":[],\"query_type\":\"flows\",\"start_date\":\"2020-04-26T13:52:51+00:00\",\"any_ip_addr\":[],\"exclude_port\":[],\"exclude_proto\":[],\"any_port_range\":[],\"exclude_any_cc\":[],\"exclude_dst_cc\":[],\"exclude_src_cc\":[],\"exclude_ip_addr\":[],\"tcp_flags_range\":[],\"exclude_any_port\":[],\"num_octets_range\":[],\"exclude_tcp_flags\":[],\"exclude_num_octets\":[],\"exclude_port_range\":[],\"exclude_any_ip_addr\":[],\"exclude_any_port_range\":[],\"exclude_tcp_flags_range\":[],\"exclude_num_octets_range\":[]}",
#         "row_count":0,
#         "total_bytes":8192,
#         "status":"Completed"
#      }
#   ]
#}

import requests
import pymysql
import json
import datetime
import logging, platform

# global variables
augury_get_jobs_url = "https://augury5.heliumrain.com/api/jobs"
augury_api_headers = {
    'Content-Type': "application/x-www-form-urlencoded",
    'Authorization': "a89e6b0d7c358b99a7411174a4106e0ab5429ed0"
}

# Open database connection
connection = pymysql.connect("localhost", "root", "DEXTER!dexter1", "seaker")
# connection = pymysql.connect("localhost","root","DEXTER!dexter1","seaker",cursorclass=pymysql.cursors.DictCursor)

# Get hostname class for injecting into the logs
class HostnameFilter(logging.Filter):
    hostname = platform.node()
    def filter(self, record):
        record.hostname = HostnameFilter.hostname
        return True

def get_queryjob_id(augury_job_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute("select id from API_queryjob where augury_job_id = " + str(augury_job_id))
            queryjob_id = cursor.fetchone()
    except pymysql.Error as e:
        logger.error("failed to fetch queryjob_id")
        logger.error("Error %d: %s" % (e.args[0], e.args[1]))
    return queryjob_id 



# Check the seaker database for jobs with status of "Submitted" or "In Progress"
# Returns:
#	tuple containing augury_job_id's (fetchall results)
def get_active_jobs():
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "select augury_job_id from API_queryjob where external_status = 'Submitted' OR external_status = 'In Progress'")
            active_jobs = cursor.fetchall()
    except pymysql.Error as e:
        logger.error("failed to read submitted jobs from db")
        logger.error("Error %d: %s" % (e.args[0], e.args[1]))
    return active_jobs


# Get the details and status of each job in augury
# Parameters:
# 	active_jobs: tuple containing augury_job_id's
# Returns:
#	dictionary with augury_job_id:status key/value pairs
def get_augury_job_status(active_jobs):
    logger.info("In get_augury_job_status to check these jobs: "+str(active_jobs))
    payload = ""
    job_status = {}
    for job in active_jobs:
        augury_job_id = job[0]
        augury_get_job_details_url = "https://augury5.heliumrain.com/api/jobs/" + str(augury_job_id) + "/details"
        response = requests.request("GET", augury_get_job_details_url, data=payload, headers=augury_api_headers)
        job = json.loads(response.text)
        job_completed = "true"
        job_in_progress = "false"

        # Each job can have multiple results (from multiple queries)
        # Check them all to get the overall job status
        for result in job['results']:
            if result['status'] != "Completed":
                job_completed = "false"
            if result['status'] == "In Progress":
                job_in_progress = "true"

        if job_in_progress == "true":
            job_status[augury_job_id] = "In Progress"
        elif job_completed == "true":
            job_status[augury_job_id] = "Completed"
        else:
            job_status[augury_job_id] = "Unknown"
    return job_status

# Set the status of a job locally
# Parameters:
#	augury_job_id:
#	status:
def set_seaker_status(queryjob_id, status):
    try:
        with connection.cursor() as cursor:
            cursor.execute('update API_queryjob set `seaker_status`=%s where `id`=%s', (status, queryjob_id))
            connection.commit()
    except pymysql.Error as e:
        logger.error("set_job_status: failed to set seaker_status")
        logger.error("Error %d: %s" % (e.args[0], e.args[1]))
    return

def set_external_status(queryjob_id, status):
    try:
        with connection.cursor() as cursor:
            cursor.execute('update API_queryjob set `external_status`=%s where `id`=%s', (status, queryjob_id))
            connection.commit()
    except pymysql.Error as e:
        logger.error("set_job_status: failed to set external_status")
        logger.error("Error %d: %s" % (e.args[0], e.args[1]))
    return

def set_augury_job_id(queryjob_id, augury_job_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute('update API_queryjob set `augury_job_id`=%s where `id`=%s', (augury_job_id, queryjob_id))
            connection.commit()
    except pymysql.Error as e:
        logger.error("set_augury_job_id: failed to set job augury_job_id")
        logger.error("Error %d: %s" % (e.args[0], e.args[1]))
    return


# Download all job results for "Completed" jobs and save in Seaker database, one row per job,
# 	then set the seaker job status to "Completed"
# Parameters:
#	active_job_status: dictionary with augury_job_id:augury_job_status key/value pairs
def get_augury_job_results(active_job_status):

    logger.info("In get_augury_job_results")

    for augury_job_id, augury_job_status in active_job_status.items():

        if augury_job_status == "Completed":
            logger.info("Completed job found.  Getting results now")

            queryjob_id = get_queryjob_id(augury_job_id)
            get_augury_job_results_url = "https://augury5.heliumrain.com/api/jobs/" + str(augury_job_id) + "?format=json"
            payload = ""
            response = requests.request("GET", get_augury_job_results_url, data=payload, headers=augury_api_headers)
            results = response.text
            logger.info(results)

            # Insert the raw response/results into 1 row of the API_results table
            try:
                with connection.cursor() as cursor:
                    insert_statement = "insert into `API_results` (`aug_results`,`query_job_id`,`aug_job_id`) VALUES (%s, %s, %s)"
                    cursor.execute(insert_statement, (results, queryjob_id, augury_job_id))
                    connection.commit()
            except pymysql.Error as e:
                logger.error("set_job_status: failed to save augury results")
                logger.error("Error %d: %s" % (e.args[0], e.args[1]))

            # Now update the job with the results_id
            results_id = cursor.lastrowid
            try:
                with connection.cursor() as cursor:
                    insert_statement = "update `API_queryjob` set `results_id`=%s where id=%s"
                    cursor.execute(insert_statement, (results_id, queryjob_id))
                    connection.commit()
            except pymysql.Error as e:
                logger.error("set_job_status: failed to save augury results")
                logger.error("Error %d: %s" % (e.args[0], e.args[1]))



            # Each line in the response is a json string.. ugh.
#### If we want to store each line in the results in a different row (still json), we can do this
#            results_list = results.splitlines()
#            for r in results_list:
#                try:
#                    with connection.cursor() as cursor:
#                        insert_statement = "insert into `API_results` (`aug_results`,`query_job_id`) VALUES (%s, %s)"
#                        cursor.execute(insert_statement, (r, queryjob_id))
#                        connection.commit()
#                except pymysql.Error as e:
#                    print("set_job_status: failed to save augury results")
#                    print("Error %d: %s" % (e.args[0], e.args[1]))
                
            # Store each line in the results in a different row, so we can do queries and stuff :)
            results_list = results.splitlines()
            for r in results_list:

               result_dict = json.loads(r)
               print(result_dict)

                # DATA CLEANUP BEFORE SAVING
                # change "class" to "class_name"
               if 'class' in result_dict.keys():
                   result_dict['class_name'] = result_dict['class']
                   result_dict.pop("class")

                # For banners, the data key is a json object
               if result_dict['query_type'] == "banners" and result_dict['results'] != None:
                   print('Cleaning up banners data to not use mysql reserved words as column names')
                   result_dict['banners_ssl'] = result_dict['ssl']
                   result_dict.pop("ssl")

                # SAVE TO DATABASE
               try:
                   with connection.cursor() as cursor:
                       result_dict['query_job_id'] = queryjob_id
                       result_dict['aug_job_id'] = augury_job_id
                       placeholder = ", ".join(["%s"] * len(result_dict))
                       stmt = "INSERT INTO `{table}` ({columns}) VALUES ({values});".format(
                           table="API_resultsparsed", \
                           columns=",".join(result_dict.keys()), values=placeholder)
                       cursor.execute(stmt, list(result_dict.values()))
                   connection.commit()
               except pymysql.Error as e:
                   logger.error("Failed to save parsed results to database")
                   logger.error("Error %d: %s" % (e.args[0], e.args[1]))

            set_seaker_status(augury_job_id, "Completed")
    return


# Returns tuple of new jobs (status of "Pending")
def get_new_jobs():
    try:
        with connection.cursor() as cursor:
            cursor.execute("select id,name,DATE_FORMAT(start_date,'%m/%d/%Y %T'), DATE_FORMAT(end_date,'%m/%d/%Y %T'),ip_addr from API_queryjob where seaker_status = 'Pending'")
            new_jobs = cursor.fetchall()
    except pymysql.Error as e:
        logger.error("get_new_jobs: failed to read new jobs from db")
        logger.error("Error %d: %s" % (e.args[0], e.args[1]))
    return new_jobs


# Create a new Augury job
# Sample request to Augury:
# curl --url 'https://augury5.heliumrain.com/api/jobs' --request POST\
#     --header 'Content-Type: application/json' \
#     --header 'Authorization: Token valid_api_key' \
#     --data '{"job_name": "Example Job","job_description": "This job is just an example.","start_date": "04/26/2017 00:00:00","end_date": "05/03/2017 23:59:59","queries": [{"query_type": "flows","any_ip_addr": "1.1.1.1","any_port": "10,20-60"},{"query_type": "pdns","any_ip_addr": "2.2.2.2,8.8.8.0/24"}]}' 
# Sample response from Augury
# {"job":{"user_id":10208,"name":"Test Query1","description":"Test Query1","updated_at":"2020-06-02 17:26:54","created_at":"2020-06-02 17:26:54","id":642720},"queries":[{"query_type":"flows","any_cc":[],"any_cidr":["47.206.130.223\/32"],"any_ip_addr":[],"any_port":[80],"any_port_range":[],"cc":[],"cidr":[],"ip_addr":[],"num_octets":[],"num_octets_range":[],"port":[],"port_range":[],"proto":[],"tcp_flags":[],"tcp_flags_range":[],"exclude_any_cc":[],"exclude_any_ip_addr":[],"exclude_any_port":[],"exclude_any_port_range":[],"exclude_cc":[],"exclude_dst_cc":[],"exclude_src_cc":[],"exclude_ip_addr":[],"exclude_num_octets":[],"exclude_num_octets_range":[],"exclude_port":[],"exclude_port_range":[],"exclude_proto":[],"exclude_tcp_flags":[],"exclude_tcp_flags_range":[],"timeout":14400,"limit":5000000,"start_date":"2020-04-26T13:52:51+00:00","end_date":"2020-04-29T13:52:51.999999+00:00","format":"json","id":7749273}]}

def create_augury_job(new_job):
    queryjob_id = new_job[0]
    create_augury_job_url = "https://augury5.heliumrain.com/api/jobs"
    payload = {
        'job_name': new_job[1],
        'job_description': new_job[1],
        'start_date': new_job[2],
        'end_date': new_job[3],
        'queries': [
            {
                'query_type': 'flows',
                'any_ip_addr': new_job[4],
                'any_port': '1-65535'
            }
        ]
    }
    logger.info("Submitting new job to Augury with request payload: "+str(payload))

    # Submit the job to augury 
    augury_api_headers = {
        'Content-Type': "application/json",
        'Authorization': "a89e6b0d7c358b99a7411174a4106e0ab5429ed0"
    }
    response = requests.post(create_augury_job_url, data=json.dumps(payload), headers=augury_api_headers)
    response_json = response.json()
    logger.debug(response_json)
    augury_job_id = response_json["job"]["id"]

    # Save the augury_job_id locally
    set_augury_job_id(queryjob_id, augury_job_id)

    # Set the job status locally to Submitted
    set_seaker_status(queryjob_id, "Submitted")

    # Set the external status (augury_status)
    set_external_status(queryjob_id, "Submitted")

    return

if __name__ == "__main__":
    # Set up logging
    handler = logging.FileHandler('./seaker-queryrunner.log')
    handler.addFilter(HostnameFilter())
    handler.setFormatter(logging.Formatter('%(asctime)s %(hostname)s - %(levelname)s: %(message)s'))

    logger = logging.getLogger()
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)

    # Get jobs that have been submitted to Augury (Status of "Submitted" or "In Progress" only)
    active_jobs = get_active_jobs()

    if len(active_jobs) > 0:

        logger.info("Found some active jobs.")
        # Get current status of all active jobs from Augury
        active_jobs_status = get_augury_job_status(active_jobs)
        # Save the status locally
        for augury_job_id,status in active_jobs_status.items():
            queryjob_id = get_queryjob_id(augury_job_id)
            set_seaker_status(queryjob_id, status)
            set_external_status(queryjob_id, status)

        # Get and save the results of any that are Complete
        get_augury_job_results(active_jobs_status)

    # Get local jobs that have NOT been submitted to Augury yet
    new_jobs = get_new_jobs()

    if len(new_jobs) > 0:
        # Submit new jobs to Augury
        for new_job in new_jobs:
            create_augury_job(new_job)
    else:
        logger.info("There were no new jobs to submit")

    # Disconnect from database
    connection.close()


def seaker_set_augury_job_id(augury_job_id):
    return

