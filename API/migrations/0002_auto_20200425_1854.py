# Generated by Django 3.0.5 on 2020-04-25 18:54

import datetime
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ip',
            name='query_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='any_ip_addr', to='API.Query'),
        ),
        migrations.AlterField(
            model_name='queryjob',
            name='end_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 4, 25, 18, 54, 57, 332418)),
        ),
        migrations.AlterField(
            model_name='queryjob',
            name='external_status',
            field=models.CharField(blank=True, default='Not Submitted', max_length=24),
        ),
        migrations.AlterField(
            model_name='queryjob',
            name='start_date',
            field=models.DateTimeField(default=datetime.datetime(2020, 4, 25, 18, 54, 57, 332392)),
        ),
    ]
