# -*- coding: utf-8 -*-
# Generated by Django 1.9.6 on 2016-05-04 18:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('countries', '0003_auto_20160310_1124'),
        ('excerptexport', '0026_auto_20160504_2010'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='bboxboundinggeometry',
            name='boundinggeometry_ptr',
        ),
        migrations.RemoveField(
            model_name='osmosispolygonfilterboundinggeometry',
            name='boundinggeometry_ptr',
        ),
        migrations.RemoveField(
            model_name='excerpt',
            name='bounding_geometry_old',
        ),
        migrations.AddField(
            model_name='excerpt',
            name='country',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='countries.Country', verbose_name='Country'),
        ),
        migrations.DeleteModel(
            name='BBoxBoundingGeometry',
        ),
        migrations.DeleteModel(
            name='BoundingGeometry',
        ),
        migrations.DeleteModel(
            name='OsmosisPolygonFilterBoundingGeometry',
        ),
    ]
