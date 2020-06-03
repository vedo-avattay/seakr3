from django.shortcuts import render, HttpResponse, get_object_or_404, HttpResponseRedirect, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from API.models import Query, QueryJob, Results
from rest_framework.parsers import JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import api_view
from .serializers import QueryJobSerializer, QuerySerializer, ResultsSerializer
import logging

# Create your views here.
@api_view(['GET', 'POST'])
def api_jobs_list(request):

    logger = logging.getLogger(__name__)

    if request.method == 'GET':

        jobs = QueryJob.objects.all()

        job_serializer = QueryJobSerializer(jobs, many=True)

        return JsonResponse(job_serializer.data, safe = False)

    elif request.method == 'POST':

        data = JSONParser().parse(request)

        job_serializer = QueryJobSerializer(data=data)

        print(job_serializer)

        if job_serializer.is_valid():
            
            job_serializer.save()

            print(job_serializer.data)

            query_job_id = job_serializer.data['id']

            query_job_ips = job_serializer.data['ip_addr']

            new_query = QueryJob.objects.get(pk=query_job_id)

            logger.info("serializer was valid. Saving all queries for this job")

            query_types = [
                'ddos_attacks',
                'ddos_commands',
                'bars_controllers',
                'bars_victoms',
                'chatter',
                'dns_derived_domains_via_domain',
                'dns_derived_domains_via_ip',
                'dns_derived_ips_via_domain',
                'dns_derived_ips_via_ip',
                'banners_ptr',
                'dns_query',
                'nmap_dnsrr',
                'pdns',
                'pdns_nxd',
                'pdns_other',
                'banners',
                'dns_fingerprint',
                'nmap_port',
                'nmap_fingerprint',
                'ntp_server',
                'open_ports',
                'os_fingerprint',
                'router',
                'sip',
                'snmp',
                'ssh',
                'tor',
                'x509',
                'antipaste',
                'compromised_hosts',
                'open_resolvers',
                'spam_domains',
                'spam_headers',
                'flows',
                'flows_tagged',
                'bgp_updates',
                'bgp_history',
                'bgp_info',
                'conpot_honeypot',
                'cowrie_honeypot',
                'darknet',
                'dionaea_honeypot',
                'portscan',
                'scanner',
                'beacons',
                'cookies',
                'files',
                'ftp_traffic',
                'imap',
                'pop',
                'rdp_traffic',
                'smtp',
                'ssh_connections',
                'urls',
                'useragents'
            ]

            for query in query_types:

                Query.objects.create(query_job=new_query, query_type=query, any_ip_addr=query_job_ips)
         

            return JsonResponse(job_serializer.data, status=201)

        else:

            return JsonResponse(job_serializer.errors, status=400)


def api_job_details(request, pk):

    try:
        query = QueryJob.objects.get(pk=pk)

    except Exception as e:

        print(e)

        return HttpResponse('Wrong id, please check your query ids and try again', status=404)

    if request.method == 'GET':

        serializer = QueryJobSerializer(query)

        return JsonResponse(serializer.data, status=200)

    elif request.method == 'PUT':
        data = JSONParser().parse(request)

        serializer = QueryJobSerializer(query, data=data)

        if serializer.is_valid():
            serializer.save()

            return JsonResponse(serializer.data, status=201)

        else:

            return JsonResponse(serializer.errors, status=400)

    elif request.method == 'DELETE':

        query.delete()

        return HttpResponse(status=200)


def api_job_results(request, pk):

    try:
        query = Results.objects.get(pk=pk)

    except Exception as e:

        print(e)

        return HttpResponse('Wrong id, please check your query ids and try again', status=404)

    if request.method == 'GET':

        serializer = ResultsSerializer(query)

        return JsonResponse(serializer.data, status=200)

    
