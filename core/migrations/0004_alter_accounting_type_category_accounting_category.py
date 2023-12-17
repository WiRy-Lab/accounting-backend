# Generated by Django 4.2.7 on 2023-12-17 03:34

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_accounting'),
    ]

    operations = [
        migrations.AlterField(
            model_name='accounting',
            name='type',
            field=models.CharField(choices=[('income', 'income'), ('outcome', 'outcome')], max_length=255),
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AddField(
            model_name='accounting',
            name='category',
            field=models.ManyToManyField(to='core.category'),
        ),
    ]