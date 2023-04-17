# Generated by Django 3.1.14 on 2023-04-11 10:45

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('apis_entities', '0001_initial'),
        ('apis_metainfo', '0004_auto_20230310_0804'),
    ]

    operations = [
        migrations.CreateModel(
            name='GenericItem',
            fields=[
                ('tempentityclass_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_entities.tempentityclass')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_entities.tempentityclass',),
        ),
        migrations.CreateModel(
            name='GenericStatement',
            fields=[
                ('tempentityclass_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_entities.tempentityclass')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_entities.tempentityclass',),
        ),
        migrations.CreateModel(
            name='GenericWork',
            fields=[
                ('tempentityclass_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_entities.tempentityclass')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_entities.tempentityclass',),
        ),
        migrations.CreateModel(
            name='IdentificationOfEntity',
            fields=[
                ('rootobject_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_metainfo.rootobject')),
                ('identified_by', models.CharField(choices=[('explicit_in_source', 'Explicit in Source'), ('implicit_in_source', 'Implicit in Source'), ('inferred_from_other_source', 'Inferred from Other Source'), ('guess', 'Guess')], max_length=100)),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_metainfo.rootobject',),
        ),
        migrations.CreateModel(
            name='Organisation',
            fields=[
                ('tempentityclass_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_entities.tempentityclass')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_entities.tempentityclass',),
        ),
        migrations.CreateModel(
            name='Person',
            fields=[
                ('tempentityclass_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_entities.tempentityclass')),
            ],
            options={
                'verbose_name': 'Person',
            },
            bases=('apis_entities.tempentityclass',),
        ),
        migrations.CreateModel(
            name='Place',
            fields=[
                ('tempentityclass_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_entities.tempentityclass')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_entities.tempentityclass',),
        ),
        migrations.CreateModel(
            name='Acquisition',
            fields=[
                ('genericstatement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.genericstatement')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.genericstatement',),
        ),
        migrations.CreateModel(
            name='ArtWork',
            fields=[
                ('genericwork_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.genericwork')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.genericwork',),
        ),
        migrations.CreateModel(
            name='ArtworkCommission',
            fields=[
                ('genericstatement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.genericstatement')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.genericstatement',),
        ),
        migrations.CreateModel(
            name='ArtworkCreation',
            fields=[
                ('genericstatement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.genericstatement')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.genericstatement',),
        ),
        migrations.CreateModel(
            name='Birth',
            fields=[
                ('genericstatement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.genericstatement')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.genericstatement',),
        ),
        migrations.CreateModel(
            name='Death',
            fields=[
                ('genericstatement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.genericstatement')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.genericstatement',),
        ),
        migrations.CreateModel(
            name='Election',
            fields=[
                ('genericstatement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.genericstatement')),
                ('position', models.CharField(blank=True, max_length=200, verbose_name='Position elected to')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.genericstatement',),
        ),
        migrations.CreateModel(
            name='Membership',
            fields=[
                ('genericstatement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.genericstatement')),
                ('role', models.CharField(blank=True, max_length=500)),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.genericstatement',),
        ),
        migrations.CreateModel(
            name='MusicCreation',
            fields=[
                ('genericstatement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.genericstatement')),
            ],
            options={
                'verbose_name': 'Music Creation',
            },
            bases=('apis_ontology.genericstatement',),
        ),
        migrations.CreateModel(
            name='MusicPerformance',
            fields=[
                ('genericstatement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.genericstatement')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.genericstatement',),
        ),
        migrations.CreateModel(
            name='MusicWork',
            fields=[
                ('genericwork_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.genericwork')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.genericwork',),
        ),
        migrations.CreateModel(
            name='Naming',
            fields=[
                ('genericstatement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.genericstatement')),
                ('forename', models.CharField(blank=True, help_text='contains a forename, given or baptismal name (for multiple, separate with a space)', max_length=200, verbose_name='Forename')),
                ('surname', models.CharField(blank=True, help_text='contains a family (inherited) name, as opposed to a given, baptismal, or nick name (for multiple, separate with a space)', max_length=200)),
                ('role_name', models.CharField(blank=True, help_text='contains a name component which indicates that the referent has a particular role or position in society, such as an official title or rank.', max_length=200)),
                ('add_name', models.CharField(blank=True, help_text='(additional name) contains an additional name component, such as a nickname, epithet, or alias, or any other descriptive phrase used within a personal name.', max_length=200)),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.genericstatement',),
        ),
        migrations.CreateModel(
            name='Order',
            fields=[
                ('genericstatement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.genericstatement')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.genericstatement',),
        ),
        migrations.CreateModel(
            name='ParentalRelation',
            fields=[
                ('genericstatement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.genericstatement')),
                ('parental_type', models.CharField(blank=True, choices=[('mother', 'Mother'), ('father', 'Father'), ('unknown', 'Unknown')], max_length=9, verbose_name='parental types')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.genericstatement',),
        ),
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('genericstatement_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.genericstatement')),
                ('amount', models.IntegerField(blank=True)),
                ('payment_for', models.CharField(blank=True, max_length=500)),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.genericstatement',),
        ),
        migrations.CreateModel(
            name='ArtworkExchange',
            fields=[
                ('acquisition_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='apis_ontology.acquisition')),
            ],
            options={
                'abstract': False,
            },
            bases=('apis_ontology.acquisition',),
        ),
    ]
