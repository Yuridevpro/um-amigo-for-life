# Generated by Django 5.0.6 on 2024-06-24 13:30

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('perfil', '0009_userprofile_confirmation_token_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='confirmation_token',
        ),
        migrations.RemoveField(
            model_name='userprofile',
            name='confirmation_token_expiration',
        ),
    ]
