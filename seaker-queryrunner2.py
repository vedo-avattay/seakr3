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

import requests
import pymysql
import json

# global variables
augury_get_jobs_url = "https://augury5.heliumrain.com/api/jobs"
augury_api_headers = {
    'Content-Type': "application/x-www-form-urlencoded",
    'Authorization': "a89e6b0d7c358b99a7411174a4106e0ab5429ed0"
}

# Open database connection
connection = pymysql.connect("localhost", "root", "DEXTER!dexter1", "seaker")


# connection = pymysql.connect("localhost","root","DEXTER!dexter1","seaker",cursorclass=pymysql.cursors.DictCursor)

# Check the seaker database for jobs with status of "Submitted" or "In Progress"
# Returns:
#	tuple containing augury_job_id's (fetchall results)
def get_seaker_submitted_jobs():
    try:
        with connection.cursor() as cursor:
            cursor.execute(
                "select augury_job_id from API_queryjob where external_status = 'Submitted' OR status = 'In Progress'")
            submitted_jobs = cursor.fetchall()
    except pymysql.Error as e:
        print("failed to read submitted jobs from db")
        print("Error %d: %s" % (e.args[0], e.args[1]))
    return submitted_jobs


# Get the details and status of each job in augury
# Parameters:
# 	submitted_jobs: tuple containing augury_job_id's
# Returns:
#	dictionary with augury_job_id:status key/value pairs
def get_augury_job_status(submitted_jobs):
    payload = ""
    job_status = {}
    for job in submitted_jobs:
        augury_job_id = job[0]
        augury_get_job_details_url = "https://augury5.heliumrain.com/api/jobs/" + augury_job_id + "/details"
        print(augury_get_job_details_url)
        response = requests.request("GET", augury_get_job_details_url, data=payload, headers=augury_api_headers)
        job = json.loads(response.text)
        job_completed = "true"
        job_in_progress = "false"
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
        print(job_status[augury_job_id])
    return job_status

# Set the status of a job locally
# Parameters:
#	augury_job_id:
#	status:
def set_seaker_job_status(augury_job_id, status):
    try:
        with connection.cursor() as cursor:
            cursor.execute('update API_queryjob set `status`=%s where `augury_job_id`=%s', (status, augury_job_id))
            connection.commit()
    except pymysql.Error as e:
        print("set_seaker_job_status: failed to set job status")
        print("Error %d: %s" % (e.args[0], e.args[1]))
    return


def set_seaker_augury_job_id(queryjob_id, augury_job_id):
    try:
        with connection.cursor() as cursor:
            cursor.execute('update API_queryjob set `augury_job_id`=%s where `id`=%s', (augury_job_id, queryjob_id))
            connection.commit()
    except pymysql.Error as e:
        print("set_seaker_job_augury_job_id: failed to set job augury_job_id")
        print("Error %d: %s" % (e.args[0], e.args[1]))
    return


# Download all job results for "Completed" jobs and save in Seaker database,
# then set the seaker job status to "Completed"
# Parameters:
#	job_status: dictionary with augury_job_id:augury_job_status key/value pairs
def get_augury_job_results(job_status):
    for augury_job_id, augury_job_status in job_status.items():
        if augury_job_status == "Completed":
            get_augury_job_results_url = "https://augury5.heliumrain.com/api/jobs/" + augury_job_id + "?format=json"
            payload = ""
            response = requests.request("GET", get_augury_job_results_url, data=payload, headers=augury_api_headers)
            results = response.text
            # each line in the response is a json string.. ugh.
            results_list = results.splitlines()
            for r in results_list:
                result_dict = json.loads(r)
                print(result_dict)

                # DATA CLEANUP BEFORE SAVING
                # class field called "class" to "class_name"
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
                        # TODO: put the real job_id in here!
                        result_dict['job_id'] = "1"
                        result_dict['augury_job_id'] = augury_job_id
                        placeholder = ", ".join(["%s"] * len(result_dict))
                        stmt = "INSERT INTO `{table}` ({columns}) VALUES ({values});".format(
                            table="seakerUI_auguryresults", \
                            columns=",".join(result_dict.keys()), values=placeholder)
                        cursor.execute(stmt, list(result_dict.values()))
                    connection.commit()
                except pymysql.Error as e:
                    print("failed to save to db")
                    print("Error %d: %s" % (e.args[0], e.args[1]))
            set_seaker_job_status(augury_job_id, "Completed")


# Returns tuple of new jobs (status of "Pending")
def get_seaker_new_jobs():
    try:
        with connection.cursor() as cursor:
            cursor.execute("select * from seakerUI_job where status = 'Pending'")
            new_jobs = cursor.fetchall()
    except pymysql.Error as e:
        print("get_seaker_new_jobs: failed to read new jobs from db")
        print("Error %d: %s" % (e.args[0], e.args[1]))
    return new_jobs
    return


# Create a new Augury job
# TODO: Grab the JSON to submit from the seaker API
def create_augury_job(new_job):
    new_job[0] = queryjob_id
    create_augury_job_url = "https://augury5.heliumrain.com/api/jobs"
    payload = {
        'job_name': 'Testjob',
        'job_description': 'Testjob description',
        'start_date': '11/01/2019 00:00:00',
        'end_date': '11/10/2019 00:00:00',
        'queries': [
            {
                'query_typ': 'flows',
                'any_ip_addr': '8.8.8.8',
            }
        ]
    }

    # Submit the job to augury 
    # TODO 
    # augury_job_id = ...

    # Set the job status locally to Submitted
    set_seaker_job_status(augury_job_id, "Submitted")

    # Save the augury_job_id locally
    set_seaker_augury_job_id(queryjob_id, augury_job_id)
    return


def main():
    # Get jobs that have been submitted to Augury, but haven't completed yet
    submitted_jobs = get_seaker_submitted_jobs()

    # Check on their current status
    job_status = get_augury_job_status(submitted_jobs)

    # Get and save the results of any that are Complete
    get_augury_job_results(job_status)

    # Get jobs that have NOT been submitted to Augury
    new_jobs = get_seaker_new_jobs()
    # Submit those jobs to Augury
    # for new_job in new_jobs:
    #	create_augury_job(new_job)

    # Disconnect from database
    connection.close()
    return


def seaker_set_augury_job_id(augury_job_id):
    return


if __name__ == "__main__":
    main()
