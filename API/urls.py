from django.urls import path
from API import views
from .views import api_jobs_list, api_job_details

urlpatterns = [
	path('jobs', views.api_jobs_list, name='api_jobs_list'),
    path('jobs/<int:pk>', views.api_job_details, name='api_job_details'),
	
]