# Generated by Django 2.0.9 on 2019-03-29 11:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('odonto', '0008_auto_20190329_0950'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='fp17incompletetreatment',
            options={'verbose_name': 'Incomplete treatment and treatment dates'},
        ),
        migrations.RemoveField(
            model_name='fp17incompletetreatment',
            name='incomplete_treatment_band_1',
        ),
        migrations.RemoveField(
            model_name='fp17incompletetreatment',
            name='incomplete_treatment_band_2',
        ),
        migrations.RemoveField(
            model_name='fp17incompletetreatment',
            name='incomplete_treatment_band_3',
        ),
        migrations.AddField(
            model_name='fp17incompletetreatment',
            name='treatment_band',
            field=models.CharField(blank=True, choices=[('Band 1', 'Band 1'), ('Band 2', 'Band 2'), ('Band 3', 'Band 3')], max_length=255, null=True),
        ),
        migrations.AlterField(
            model_name='fp17incompletetreatment',
            name='completion_or_last_visit',
            field=models.DateField(blank=True, null=True, verbose_name='Completion or last visit'),
        ),
        migrations.AlterField(
            model_name='fp17incompletetreatment',
            name='date_of_acceptance',
            field=models.DateField(blank=True, null=True, verbose_name='Date of acceptance'),
        ),
    ]
