from django.contrib import admin
from .models import Query, QueryJob, IP, ExcludeIP, Hostnames, CC, ExcludeCC, ExcludePort, Proto, ExcludeProto, TCPFlag

# Register your models here.
admin.site.register(Query)
admin.site.register(QueryJob)
admin.site.register(IP)
admin.site.register(ExcludeIP)
admin.site.register(Hostnames)
admin.site.register(CC)
admin.site.register(ExcludeCC)
admin.site.register(ExcludePort)
admin.site.register(Proto)
admin.site.register(ExcludeProto)
admin.site.register(TCPFlag)