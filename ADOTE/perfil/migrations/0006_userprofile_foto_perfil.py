# Generated by Django 5.0.6 on 2024-06-16 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perfil', '0005_alter_userprofile_email'),
    ]

    operations = [
        migrations.AddField(
            model_name='userprofile',
            name='foto_perfil',
            field=models.ImageField(blank=True, null=True, upload_to='profile_pics/'),
        ),
    ]
