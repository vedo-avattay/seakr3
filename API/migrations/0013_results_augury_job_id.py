# Generated by Django 3.0.6 on 2020-06-02 20:45

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0012_results'),
    ]

    operations = [
        migrations.AddField(
            model_name='results',
            name='augury_job_id',
            field=models.IntegerField(blank=True, null=True),
        ),
    ]