# Generated by Django 5.0.6 on 2024-07-17 05:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('prototypeApp', '0002_adoptionrequest'),
    ]

    operations = [
        migrations.AddField(
            model_name='cat',
            name='in_review',
            field=models.BooleanField(default=False),
        ),
    ]
