# Generated by Django 2.2.7 on 2019-11-26 18:41

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('im', '0002_auto_20191102_1014'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='online',
            field=models.BooleanField(default=False),
        ),
    ]