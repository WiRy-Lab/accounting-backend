# Generated by Django 4.2.7 on 2023-12-28 13:00

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0009_savemoneytarget_end_date_savemoneytarget_from_date'),
    ]

    operations = [
        migrations.AlterField(
            model_name='savemoneytarget',
            name='end_date',
            field=models.DateField(),
        ),
        migrations.AlterField(
            model_name='savemoneytarget',
            name='from_date',
            field=models.DateField(),
        ),
    ]
