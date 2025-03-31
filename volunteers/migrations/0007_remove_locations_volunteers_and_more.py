# Generated by Django 5.1.6 on 2025-03-29 20:58

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('volunteers', '0006_alter_volunteerparticipation_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='locations',
            name='volunteers',
        ),
        migrations.AddField(
            model_name='volunteerparticipation',
            name='location',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='volunteers.locations'),
        ),
    ]
