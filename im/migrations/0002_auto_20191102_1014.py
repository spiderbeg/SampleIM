# Generated by Django 2.2.6 on 2019-11-02 10:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('im', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='groupuser',
            name='gmid',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userrelation',
            name='umid',
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name='userrelation',
            name='umid2',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
