# Generated by Django 2.0.7 on 2018-07-25 09:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QieGaoWorld', '0014_auto_20180724_2253'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='permissions',
            field=models.CharField(default='%police_cases_watch%police_cases_add%declaration_animals%declaration_buildings%declaration_watch%', max_length=2048),
        ),
    ]