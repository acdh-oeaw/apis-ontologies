# Generated by Django 4.1.10 on 2023-07-06 01:37

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("apis_ontology", "0010_delete_contribution"),
    ]

    operations = [
        migrations.DeleteModel(
            name="Identifier",
        ),
    ]
