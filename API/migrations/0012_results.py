# Generated by Django 3.0.6 on 2020-06-02 19:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('API', '0011_queryjob_augury_job_id'),
    ]

    operations = [
        migrations.CreateModel(
            name='Results',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('augury_response', models.TextField(blank=True)),
                ('query_job', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='results', to='API.QueryJob')),
            ],
        ),
    ]
