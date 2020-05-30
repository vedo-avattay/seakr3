from django.urls import include, path
from . import views

urlpatterns = [
	path('', views.index, name='index'),
    path('queries', views.index, name='queries'),
    path('queries/new', views.new_query, name='new_query'),
    path('queries/<id>/delete', views.delete_query, name='delete_query'),
    path('queries/<id>', views.query_jobs_list, name='query_jobs_list'),
    path('', views.index, name='groups'),
    path('', views.index, name='results'),
    path('accounts/', include('django.contrib.auth.urls'))
	
]