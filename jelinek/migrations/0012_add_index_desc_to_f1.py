# Generated by Django 3.1.14 on 2022-03-17 22:26

from dataclasses import Field
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        
        ('apis_ontology', '0011_f26_crm_base'),
    ]

    operations = [
        migrations.AddField(
            model_name="F1_Work",
            name="index_desc",
            field=models.CharField(blank=True, max_length=1024, null=True)
        )
    ]
