# ativacao/models.py
from django.db import models
from django.contrib.auth.models import User



class Ativacao(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    confirmation_token = models.CharField(max_length=32, blank=True)
    confirmation_token_expiration = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return self.user.username



class ResetSenha(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    reset_token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'ResetSenha para {self.user.username}'
