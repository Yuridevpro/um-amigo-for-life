# Generated by Django 5.0.6 on 2024-06-16 15:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perfil', '0003_remove_userprofile_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='email',
            field=models.CharField(default=None, max_length=100),
        ),
    ]