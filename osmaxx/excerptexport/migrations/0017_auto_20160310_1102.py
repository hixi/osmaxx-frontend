# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-10 10:02
from __future__ import unicode_literals

from django.db import migrations
import django_enumfield.db.fields
import osmaxx.excerptexport.models.extraction_order


class Migration(migrations.Migration):

    dependencies = [
        ('excerptexport', '0016_extractionorder_process_start_time'),
    ]

    operations = [
        migrations.AlterField(
            model_name='extractionorder',
            name='state',
            field=django_enumfield.db.fields.EnumField(default=1, enum=osmaxx.excerptexport.models.extraction_order.ExtractionOrderState, verbose_name='state'),
        ),
    ]
