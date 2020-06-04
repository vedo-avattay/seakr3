from rest_framework import serializers
from .models import Query, QueryJob, IP, Results

class QuerySerializer(serializers.ModelSerializer):

    class Meta:

        model = Query

        fields = ['query_type', 'any_ip_addr']

class QueryJobSerializer(serializers.ModelSerializer):

    # SHC: for now, lets not show them the queries
    # queries = QuerySerializer(many=True, required=False)

    class Meta:

	# SHC: for now, lets not show them the queries
        #fields = ['id', 'name', 'ip_addr', 'ptr', 'description', 'seaker_status', 'external_status', 'results_id', 'start_date', 'end_date', 'associated_user', 'queries']
        model = QueryJob
        fields = ['id', 'name', 'ip_addr', 'ptr', 'description', 'seaker_status', 'external_status', 'results_id', 'start_date', 'end_date', 'associated_user']


    def create(self, validated_data):

        return QueryJob.objects.create(**validated_data)

    def update(self, instance, validated_data):

        instance.name = validated_data('name', instance.name)

        instance.description = validated_data('description', instance.description)

        instance.first_run_date = validated_data('start_date', instance.first_run_date)

        instance.save()        

        return instance

class ResultsSerializer(serializers.ModelSerializer):

    class Meta:

        model = Results

        fields = ['id', 'aug_results']
