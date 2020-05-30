# Generated by Django 3.0.5 on 2020-04-25 13:31

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('query_type', models.CharField(max_length=120)),
            ],
        ),
        migrations.CreateModel(
            name='TCPFlag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('tcp_flag', models.IntegerField()),
                ('query_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.Query')),
            ],
        ),
        migrations.CreateModel(
            name='QueryJob',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=720)),
                ('start_date', models.DateTimeField()),
                ('end_date', models.DateTimeField()),
                ('description', models.TextField(blank=True)),
                ('seaker_status', models.CharField(default='Pending', max_length=24)),
                ('external_status', models.CharField(blank=True, max_length=24)),
                ('associated_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='query',
            name='query_job',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='queries', to='API.QueryJob'),
        ),
        migrations.CreateModel(
            name='Proto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('proto', models.IntegerField()),
                ('query_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.Query')),
            ],
        ),
        migrations.CreateModel(
            name='IP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('ip', models.GenericIPAddressField()),
                ('query_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='ips', to='API.Query')),
            ],
        ),
        migrations.CreateModel(
            name='Hostnames',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('hostname', models.CharField(max_length=248)),
                ('query_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.Query')),
            ],
        ),
        migrations.CreateModel(
            name='ExcludeProto',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exclude_proto', models.IntegerField()),
                ('query_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.Query')),
            ],
        ),
        migrations.CreateModel(
            name='ExcludePort',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('port', models.IntegerField()),
                ('query_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.Query')),
            ],
        ),
        migrations.CreateModel(
            name='ExcludeIP',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exclude_ip', models.GenericIPAddressField()),
                ('query_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.Query')),
            ],
        ),
        migrations.CreateModel(
            name='ExcludeCC',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exclude_cc', models.CharField(max_length=8)),
                ('query_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.Query')),
            ],
        ),
        migrations.CreateModel(
            name='CC',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('cc', models.CharField(max_length=8)),
                ('query_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='API.Query')),
            ],
        ),
    ]