# Generated by Django 2.0.7 on 2018-07-24 14:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('QieGaoWorld', '0013_auto_20180724_2248'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='avatar',
            field=models.CharField(default='static\\media\\face\\default.jpg', max_length=1024),
        ),
    ]
