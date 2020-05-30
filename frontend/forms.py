from django.forms import ModelForm, Form
from django import forms
from django.forms import DateInput, TextInput, Textarea
from API.models import Query, QueryJob, IP, ExcludeIP, Hostnames, CC, ExcludeCC, ExcludePort, Proto, ExcludeProto, TCPFlag

class QueryForm(forms.ModelForm):

    class Meta:

        model = Query

        fields = ['query_type']

class QueryJobForm(forms.ModelForm):

    class Meta: 

        model = QueryJob

        widgets = {'start_date': DateInput(attrs={'class': 'datepicker'}), 'end_date': DateInput(attrs={'class': 'datepicker'})}

        fields = ['name', 'description', 'start_date', 'end_date']

class IpForm(forms.ModelForm):

    class Meta:

        model = IP

        fields = ['ip']

class ExcludeIPForm(forms.ModelForm):

    class Meta:

        model = ExcludeIP

        fields = ['exclude_ip']

class HostnamesForm(forms.ModelForm):

    class Meta:

        model = Hostnames

        fields = ['hostname']

class CCForm(forms.ModelForm):

    class Meta:

        model = CC

        fields = ['cc']

class ExcludeCCForm(forms.ModelForm):

    class Meta:

        model = ExcludeCC

        fields = ['exclude_cc']

class ExcludePortForm(forms.ModelForm):

    class Meta:

        model = ExcludePort

        fields = ['port']

class ExcludeProtoForm(forms.ModelForm):

    class Meta:

        model = ExcludeProto

        fields = ['exclude_proto']

class TCPFlagForm(forms.ModelForm):

    class Meta:

        model = TCPFlag

        fields = ['tcp_flag']