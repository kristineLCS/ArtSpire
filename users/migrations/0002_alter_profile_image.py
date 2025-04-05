# Generated by Django 4.2.16 on 2025-04-05 12:27

import cloudinary.models
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='image',
            field=cloudinary.models.CloudinaryField(default='v1234567890/default_profile', max_length=255, verbose_name='image'),
        ),
    ]
