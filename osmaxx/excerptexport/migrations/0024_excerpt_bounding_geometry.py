# -*- coding: utf-8 -*-
# Generated by Django 1.9.5 on 2016-05-03 14:36
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('excerptexport', '0023_auto_20160503_1605'),
    ]

    operations = [
        migrations.AddField(
            model_name='excerpt',
            name='bounding_geometry',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(null=True, srid=4326, verbose_name='bounding geometry'),
        ),
    ]
