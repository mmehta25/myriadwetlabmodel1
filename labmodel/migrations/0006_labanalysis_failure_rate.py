# Generated by Django 3.2.4 on 2021-07-14 20:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labmodel', '0005_alter_processinstance_process'),
    ]

    operations = [
        migrations.AddField(
            model_name='labanalysis',
            name='failure_rate',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=4, verbose_name='Integrated Hours'),
        ),
    ]
