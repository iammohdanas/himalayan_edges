# Generated by Django 4.2.16 on 2024-11-22 11:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('authenticator', '0002_profile_is_mobile_number_verified'),
    ]

    operations = [
        migrations.AddField(
            model_name='profile',
            name='otp_token',
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
