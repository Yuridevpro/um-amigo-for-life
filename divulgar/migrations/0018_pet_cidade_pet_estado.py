# Generated by Django 5.0.6 on 2024-06-20 15:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('divulgar', '0017_delete_userprofile'),
    ]

    operations = [
        migrations.AddField(
            model_name='pet',
            name='cidade',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
        migrations.AddField(
            model_name='pet',
            name='estado',
            field=models.CharField(blank=True, max_length=100, null=True),
        ),
    ]
