# Generated by Django 3.1.14 on 2022-03-17 22:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('apis_ontology', '0007_ids_and_short_texts'),
    ]

    operations = [
        migrations.AddField(
            model_name='F26_Recording',
            name='note',
            field=models.CharField(blank=True, max_length=1024, null=True)
        ),
    ]
