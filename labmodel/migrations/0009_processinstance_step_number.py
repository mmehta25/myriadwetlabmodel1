# Generated by Django 3.2.4 on 2021-08-08 16:48

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('labmodel', '0008_processinstance_only_walkup'),
    ]

    operations = [
        migrations.AddField(
            model_name='processinstance',
            name='step_number',
            field=models.IntegerField(default=0, help_text='Enter the Step Number of this process.'),
        ),
    ]