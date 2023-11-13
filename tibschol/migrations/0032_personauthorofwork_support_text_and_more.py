# Generated by Django 4.1.13 on 2023-11-13 06:55

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis_ontology', '0031_personauthorofwork'),
    ]

    operations = [
        migrations.AddField(
            model_name='personauthorofwork',
            name='support_text',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='personauthorofwork',
            name='tei_refs',
            field=models.TextField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name='personauthorofwork',
            name='zotero_refs',
            field=models.TextField(blank=True, null=True),
        ),
    ]
