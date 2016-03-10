# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-03-10 10:24
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('countries', '0002_inital_country_data_import'),
    ]

    operations = [
        migrations.RenameField(
            model_name='country',
            old_name='polygon',
            new_name='border'
        ),
        migrations.RenameField(
            model_name='country',
            old_name='simplified_polygon',
            new_name='simplified_border'
        ),
        migrations.AlterField(
            model_name='country',
            name='border',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(help_text='original border multipolygon', srid=4326, verbose_name='border'),
        ),
        migrations.AlterField(
            model_name='country',
            name='simplified_border',
            field=django.contrib.gis.db.models.fields.MultiPolygonField(srid=4326, verbose_name='simplified border multipolygon'),
        ),
    ]