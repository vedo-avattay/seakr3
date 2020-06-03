from django.db import models
from django.contrib.auth.models import User
import datetime
from django.utils.timezone import now
from .validators import validate_ips
from django.core.exceptions import ValidationError


class QueryJob(models.Model):

    name = models.CharField(max_length=720)
    
    associated_user = models.ForeignKey(User, on_delete=models.CASCADE, blank=False)

    start_date = models.DateTimeField(default=now)

    end_date = models.DateTimeField(default=now)

    description = models.TextField(blank=True)

    seaker_status = models.CharField(default="Pending", max_length=24)

    external_status = models.CharField(default="Not Submitted", max_length=24, blank=True)

    results_id = models.IntegerField(blank=True, null=True) 

    augury_job_id = models.IntegerField(blank=True, null=True)

    ip_addr = models.CharField(max_length=1040, blank=True, validators=[validate_ips])

    ptr = models.CharField(max_length=1040, blank=True)

    def __str__(self):
        return self.name

    def clean(self):

        if self.ip_addr and self.ptr is None:

            raise ValidationError("One of either hostname or IP field is required")


class Query(models.Model):
    
    query_job = models.ForeignKey(QueryJob, related_name='queries', on_delete=models.CASCADE)

    query_type = models.CharField(max_length=120)

    any_ip_addr = models.CharField(max_length=1040)

    def __str__(self):
        return self.query_job.name + ' - ' + self.query_type

class Results(models.Model):

    query_job = models.ForeignKey(QueryJob, related_name='results', on_delete=models.CASCADE)

    aug_job_id = models.IntegerField(blank=True, null=True)

    aug_results = models.TextField(blank=True)

    def __str__(self):
        return self.augury_response    

class IP(models.Model):

    query_type = models.ForeignKey(QueryJob, on_delete=models.CASCADE)

    ip = models.GenericIPAddressField()

    def __str__(self):
        return self.ip

class Hostnames(models.Model):

    query_type = models.ForeignKey(Query, on_delete=models.CASCADE)

    hostname = models.CharField(max_length=248)

    def __str__(self):
        return self.hostname

class ExcludeIP(models.Model):

    query_type = models.ForeignKey(Query, on_delete=models.CASCADE)

    exclude_ip = models.GenericIPAddressField()


class CC(models.Model):

    query_type = models.ForeignKey(Query, on_delete=models.CASCADE)

    cc = models.CharField(max_length=8)

class ExcludeCC(models.Model):

    query_type = models.ForeignKey(Query, on_delete=models.CASCADE)

    exclude_cc = models.CharField(max_length=8)

class ExcludePort(models.Model):
    query_type = models.ForeignKey(Query, on_delete=models.CASCADE)

    port = models.IntegerField()

class Proto(models.Model):
    query_type = models.ForeignKey(Query, on_delete=models.CASCADE)

    proto = models.IntegerField()

class ExcludeProto(models.Model):
    query_type = models.ForeignKey(Query, on_delete=models.CASCADE)

    exclude_proto = models.IntegerField()

class TCPFlag(models.Model):
    query_type = models.ForeignKey(Query, on_delete=models.CASCADE)

    tcp_flag = models.IntegerField()
