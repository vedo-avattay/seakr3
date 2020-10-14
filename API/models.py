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

class ResultsParsed(models.Model):

    query_job = models.ForeignKey(QueryJob, related_name='resultsparsed', on_delete=models.CASCADE)
    aug_job_id = models.IntegerField(blank=True, null=True)

    query_type = models.CharField(max_length=40, null=True, blank=True)
    src_ip_addr = models.GenericIPAddressField(null=True, blank=True)
    dst_ip_addr = models.GenericIPAddressField(null=True, blank=True)
    src_port = models.CharField(max_length=8, null=True, blank=True)
    dst_port = models.CharField(max_length=8, null=True, blank=True)
    src_cc = models.CharField(max_length=4, null=True, blank=True)
    dst_cc = models.CharField(max_length=4, null=True, blank=True)
    proto = models.CharField(max_length=8, null=True, blank=True)
    tcp_flags = models.CharField(max_length=8, null=True, blank=True)
    num_pkts = models.CharField(max_length=16, null=True, blank=True)
    num_octets = models.CharField(max_length=16, null=True, blank=True)
    sample_algo = models.CharField(max_length=64, null=True, blank=True)
    sample_interval = models.CharField(max_length=64, null=True, blank=True)
    timestamp = models.DateTimeField()
    os = models.CharField(max_length=32, null=True, blank=True)
    description = models.CharField(max_length=32, null=True, blank=True)
    comment = models.CharField(max_length=32, null=True, blank=True)
    client_ip_addr = models.GenericIPAddressField(null=True, blank=True)
    server_ip_addr = models.GenericIPAddressField(null=True, blank=True)
    client_cc = models.CharField(max_length=4, null=True, blank=True)
    server_cc = models.CharField(max_length=4, null=True, blank=True)
    server_comment = models.CharField(max_length=128, null=True, blank=True)
    server_port = models.CharField(max_length=8, null=True, blank=True)
    results = models.CharField(max_length=255, null=True, blank=True)
    ip_addr = models.GenericIPAddressField(null=True, blank=True)
    cc = models.CharField(max_length=4, null=True, blank=True)
    port = models.CharField(max_length=8, null=True, blank=True)
    service = models.CharField(max_length=64, null=True, blank=True)
    data = models.TextField()
    asn = models.CharField(max_length=64, null=True, blank=True)
    asname = models.CharField(max_length=128, null=True, blank=True)
    cn = models.CharField(max_length=128, null=True, blank=True)
    altnames = models.CharField(max_length=512, null=True, blank=True)
    c = models.CharField(max_length=64, null=True, blank=True)
    o = models.CharField(max_length=64, null=True, blank=True)
    email = models.CharField(max_length=64, null=True, blank=True)
    subject = models.CharField(max_length=256, null=True, blank=True)
    not_after = models.DateTimeField()
    not_before = models.DateTimeField()
    version = models.CharField(max_length=8, null=True, blank=True)
    md5md5 = models.CharField(max_length=64, null=True, blank=True)
    sha1 = models.CharField(max_length=96, null=True, blank=True)
    issuer = models.CharField(max_length=256, null=True, blank=True)
    issuer_cn = models.CharField(max_length=64, null=True, blank=True)
    issuer_c = models.CharField(max_length=8, null=True, blank=True)
    issuer_o = models.CharField(max_length=64, null=True, blank=True)
    sig_algo = models.CharField(max_length=64, null=True, blank=True)
    serial = models.CharField(max_length=64, null=True, blank=True)
    pem = models.TextField()
    section = models.CharField(max_length=32, null=True, blank=True)
    aa = models.CharField(max_length=32, null=True, blank=True)
    qname = models.CharField(max_length=64, null=True, blank=True)
    class_name = models.CharField(max_length=16, null=True, blank=True)
    type = models.CharField(max_length=64, null=True, blank=True)
    ttl = models.CharField(max_length=32, null=True, blank=True)
    rdata = models.CharField(max_length=32, null=True, blank=True)
    rdata_cc = models.CharField(max_length=8, null=True, blank=True)
    sub_type = models.CharField(max_length=32, null=True, blank=True)
    banners_ssl = models.CharField(max_length=8, null=True, blank=True)
    start_time = models.DateTimeField(auto_now_add=True, blank=True)

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
