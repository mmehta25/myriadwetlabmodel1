# Generated by Django 3.2.4 on 2021-06-28 21:53

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('labmodel', '0003_auto_20210628_1449'),
    ]

    operations = [
        migrations.AlterField(
            model_name='instrumentinstance',
            name='instrument',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='labmodel.instrument'),
        ),
    ]
