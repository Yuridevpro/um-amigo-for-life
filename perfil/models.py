from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from storages.backends import s3boto3
s3_storage = s3boto3.S3Boto3Storage()

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    nome = models.CharField(max_length=100)
    sobrenome = models.CharField(max_length=100)
    telefone = models.CharField(max_length=15)
    estado_nome = models.CharField(max_length=100)
    estado_id = models.IntegerField(blank=True, null=True)
    cidade_nome = models.CharField(max_length=100)
    email = models.EmailField(max_length=100)
    foto_perfil = models.ImageField(upload_to='profile_pics/', storage=s3_storage, blank=True, null=True)

    def __str__(self):
        return f"{self.nome} {self.sobrenome}"


