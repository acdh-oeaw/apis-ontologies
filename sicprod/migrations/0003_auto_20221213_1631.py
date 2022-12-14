# Generated by Django 3.1.14 on 2022-12-13 16:31

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('apis_ontology', '0002_remove_person_class_affiliation'),
    ]

    operations = [
        migrations.RenameField(
            model_name='salary',
            old_name='type',
            new_name='repetitionType',
        ),
        migrations.RemoveField(
            model_name='salary',
            name='amount',
        ),
        migrations.RemoveField(
            model_name='salary',
            name='currency',
        ),
        migrations.RemoveField(
            model_name='salary',
            name='repetition_note',
        ),
        migrations.RemoveField(
            model_name='salary',
            name='repetitions',
        ),
        migrations.AddField(
            model_name='salary',
            name='typ',
            field=models.CharField(blank=True, choices=[('Sold', 'Sold'), ('Zehrung', 'Zehrung'), ('Provision', 'Provision'), ('Kredit', 'Kredit'), ('Sonstiges', 'Sonstiges')], max_length=9),
        ),
        migrations.AlterField(
            model_name='place',
            name='type',
            field=models.CharField(blank=True, choices=[('Stadt', 'Stadt'), ('Dorf/Nachbarschaft/Gemein/Siedlung/Weiler', 'Dorf/Nachbarschaft/Gemein/Siedlung/Weiler'), ('Burg/Schloss', 'Burg/Schloss'), ('Land/Herrschaftskomplex', 'Land/Herrschaftskomplex'), ('Landschaft/Region', 'Landschaft/Region'), ('Lehen', 'Lehen'), ('Haus/Hof', 'Haus/Hof'), ('Gericht', 'Gericht'), ('Kloster', 'Kloster'), ('Gewässer', 'Gewässer'), ('Grundherrschaft', 'Grundherrschaft'), ('Hofmark', 'Hofmark'), ('Tal', 'Tal'), ('Berg', 'Berg'), ('Bergrevier', 'Bergrevier'), ('Pflege', 'Pflege'), ('(Land-)Vogtei', '(Land-)Vogtei'), ('Propstei', 'Propstei')], max_length=41),
        ),
    ]
