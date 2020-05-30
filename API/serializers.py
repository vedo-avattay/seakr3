from rest_framework import serializers
from .models import Query, QueryJob, IP

class QuerySerializer(serializers.ModelSerializer):

    class Meta:

        model = Query

        fields = ['query_type', 'any_ip_addr']

class QueryJobSerializer(serializers.ModelSerializer):

    queries = QuerySerializer(many=True, required=False)

    class Meta:

        model = QueryJob

        fields = ['id', 'name', 'ip_addr', 'ptr', 'description', 'seaker_status', 'external_status', 'start_date', 'end_date', 'associated_user', 'queries']


    def create(self, validated_data):

        return QueryJob.objects.create(**validated_data)

    def update(self, instance, validated_data):

        instance.name = validated_data('name', instance.name)

        instance.description = validated_data('description', instance.description)

        instance.first_run_date = validated_data('start_date', instance.first_run_date)

        instance.save()        

        return instance