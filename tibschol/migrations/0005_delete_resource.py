# Generated by Django 3.1.14 on 2022-02-04 10:20

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('apis_metainfo', '0002_auto_20220201_1241'),
        ('apis_labels', '0002_auto_20220201_1241'),
        ('apis_relations', '0002_property_property_class_uri'),
        ('apis_ontology', '0004_auto_20220204_1016'),
    ]

    operations = [
        migrations.DeleteModel(
            name='Resource',
        ),
    ]