# Generated by Django 2.1 on 2019-06-06 05:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authentication', '0004_auto_20190606_0511'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='bio',
            field=models.CharField(default='', max_length=255),
        ),
        migrations.AlterField(
            model_name='user',
            name='image',
            field=models.CharField(default='', max_length=255),
        ),
    ]
