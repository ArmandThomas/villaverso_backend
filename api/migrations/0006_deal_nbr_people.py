# Generated by Django 4.2.2 on 2023-06-29 14:13

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_alter_house_description_disponibility_deal'),
    ]

    operations = [
        migrations.AddField(
            model_name='deal',
            name='nbr_people',
            field=models.IntegerField(default=0),
        ),
    ]