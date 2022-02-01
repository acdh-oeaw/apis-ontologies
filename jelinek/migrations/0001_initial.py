# Generated by Django 3.1.14 on 2022-02-01 13:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('apis_entities', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Chapter',
            fields=[
                ('tempentityclass_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_entities.tempentityclass')),
                ('chapter_number', models.CharField(blank=True, max_length=1024, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_entities.tempentityclass',),
        ),
        migrations.CreateModel(
            name='E1_Crm_Entity',
            fields=[
                ('tempentityclass_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_entities.tempentityclass')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_entities.tempentityclass',),
        ),
        migrations.CreateModel(
            name='XmlFile',
            fields=[
                ('tempentityclass_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_entities.tempentityclass')),
                ('file_path', models.CharField(blank=True, max_length=1024, null=True, verbose_name='Untertitel')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_entities.tempentityclass',),
        ),
        migrations.CreateModel(
            name='E40_Legal_Body',
            fields=[
                ('e1_crm_entity_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.e1_crm_entity')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.e1_crm_entity',),
        ),
        migrations.CreateModel(
            name='E55_Type',
            fields=[
                ('e1_crm_entity_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.e1_crm_entity')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.e1_crm_entity',),
        ),
        migrations.CreateModel(
            name='F10_Person',
            fields=[
                ('e1_crm_entity_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.e1_crm_entity')),
                ('role', models.CharField(blank=True, max_length=1024, null=True)),
                ('pers_id', models.CharField(blank=True, max_length=1024, null=True)),
                ('forename', models.CharField(blank=True, help_text='The persons´s forename. In case of more then one name...', max_length=255, null=True, verbose_name='Vorname')),
                ('surname', models.CharField(blank=True, max_length=255, null=True, verbose_name='Nachname')),
                ('name_generisch', models.CharField(blank=True, max_length=255, null=True, verbose_name='Name generisch')),
                ('vorname_zweitansetzung', models.CharField(blank=True, max_length=255, null=True, verbose_name='Vorname (Zweitansetzung)')),
                ('nachname_zweitansetzung', models.CharField(blank=True, max_length=255, null=True, verbose_name='Nachname (Zweitansetzung)')),
                ('name_generisch_zweitansetzung', models.CharField(blank=True, max_length=255, null=True, verbose_name='Name generisch (Zweitansetzung)')),
                ('gender', models.CharField(blank=True, choices=[('female', 'female'), ('male', 'male'), ('third gender', 'third gender')], max_length=15)),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.e1_crm_entity',),
        ),
        migrations.CreateModel(
            name='F1_Work',
            fields=[
                ('e1_crm_entity_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.e1_crm_entity')),
                ('untertitel', models.CharField(blank=True, max_length=1024, null=True, verbose_name='Untertitel')),
                ('idno', models.CharField(blank=True, max_length=1024, null=True)),
                ('anmerkung', models.CharField(blank=True, max_length=1024, null=True, verbose_name='Anmerkung')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.e1_crm_entity',),
        ),
        migrations.CreateModel(
            name='F3_Manifestation_Product_Type',
            fields=[
                ('e1_crm_entity_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.e1_crm_entity')),
                ('idno', models.CharField(blank=True, max_length=1024, null=True)),
                ('bibl_id', models.CharField(blank=True, max_length=1024, null=True)),
                ('note', models.CharField(blank=True, max_length=1024, null=True)),
                ('series', models.CharField(blank=True, max_length=1024, null=True)),
                ('edition', models.CharField(blank=True, max_length=1024, null=True)),
                ('ref_target', models.URLField(blank=True, null=True)),
                ('ref_accessed', models.CharField(blank=True, max_length=1024, null=True)),
                ('text_language', models.CharField(blank=True, max_length=1024, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.e1_crm_entity',),
        ),
        migrations.CreateModel(
            name='F9_Place',
            fields=[
                ('e1_crm_entity_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.e1_crm_entity')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.e1_crm_entity',),
        ),
        migrations.CreateModel(
            name='F17_Aggregation_Work',
            fields=[
                ('f1_work_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.f1_work')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.f1_work',),
        ),
        migrations.CreateModel(
            name='F20_Performance_Work',
            fields=[
                ('f1_work_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.f1_work')),
                ('note', models.CharField(blank=True, max_length=1024, null=True)),
                ('category', models.CharField(blank=True, max_length=1024, null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.f1_work',),
        ),
    ]