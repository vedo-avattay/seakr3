import logging

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import (HttpResponse, HttpResponseRedirect,
                              get_object_or_404, redirect, render, reverse)

from API.models import Query

from .filters import QueryFilter
from .forms import *


# Create your views here.
@login_required
def index(request):

    query_list = QueryJob.objects.all()

    f = QueryFilter(request.GET, queryset=query_list)

    context = {'query_list': query_list, 'filter': f}


    return render(request, 'frontend/query_list.html', context)


@login_required
def query_jobs_list(request, id):

    # Start a list of dictionaries
    query_jobs = []

    # Get the master query we are looking at
    query = get_object_or_404(Query, pk=id)

    # Let's start building our dictionary to pass to the frontend
    query_jobs_list = query.queryjob_set.all()

    print(query_jobs)

    #print(query_host_list)

    context = {'query_jobs': query_jobs_list}

    return render(request, 'frontend/query_jobs_list.html', context)

@login_required
def new_query(request):

    if request.method == 'POST':

        query_form = QueryForm(request.POST)

        query_job_form = QueryJobForm(request.POST)

        # TODO: Need to rework this to make sure that all forms are valid before saving anything
        if query_form.is_valid() & query_job_form.is_valid():

            query = query_form.save()

            query_job = query_job_form.save(commit=False)

            query_job.query = query

            query_job.save()

            return HttpResponseRedirect(reverse('index'))


        else:

            print("Unable to create query")

    else:

        query_form = QueryForm()

        query_job_form = QueryJobForm()

        return render(request, 'frontend/new_query.html', {'query_form': query_form, 'query_job_form': query_job_form})

@login_required
def delete_query(request, id):

    return HttpResponse("Delete a query!)")
