# Generated by Django 4.2.7 on 2023-12-28 12:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0008_alter_savemoneytarget_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='savemoneytarget',
            name='end_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='savemoneytarget',
            name='from_date',
            field=models.DateField(null=True),
        ),
    ]