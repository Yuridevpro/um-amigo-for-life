# Generated by Django 5.0.6 on 2024-07-31 14:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('perfil', '0013_alter_userprofile_email'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='userprofile',
            name='foto_perfil',
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='sobrenome',
            field=models.CharField(max_length=100),
        ),
    ]
