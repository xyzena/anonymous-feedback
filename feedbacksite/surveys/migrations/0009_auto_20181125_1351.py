# Generated by Django 2.1.2 on 2018-11-25 19:51

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('surveys', '0008_auto_20181125_0955'),
    ]

    operations = [
        migrations.AlterField(
            model_name='survey',
            name='pub_date',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='date published'),
        ),
        migrations.AlterField(
            model_name='survey',
            name='results_published',
            field=models.BooleanField(default=False, verbose_name='Publish results'),
        ),
    ]
