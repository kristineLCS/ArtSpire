# Generated by Django 4.2.16 on 2025-04-05 17:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('homepage', '0010_postreport'),
    ]

    operations = [
        migrations.AddField(
            model_name='postreport',
            name='status',
            field=models.CharField(choices=[('pending', 'Pending'), ('reviewed', 'Reviewed'), ('action_taken', 'Action Taken'), ('dismissed', 'Dismissed')], default='pending', max_length=20),
        ),
    ]
