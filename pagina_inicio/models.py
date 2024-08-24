from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from perfil.models import UserProfile  # Importar UserProfile

class Depoimento(models.Model):
    nome = models.CharField(max_length=100)
    sobrenome = models.CharField(max_length=100, blank=True) # Adiciona o campo sobrenome
    email = models.EmailField(unique=True)  # Adicione 'unique=True' aqui
    mensagem = models.TextField()
    data_criacao = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, related_name='depoimentos')

    def __str__(self):
        return f"{self.nome} - {self.data_criacao.strftime('%d/%m/%Y')}"
    
    def save(self, *args, **kwargs):
        if self.usuario:
            user_profile = UserProfile.objects.get(user=self.usuario)
            self.nome = user_profile.nome
            self.sobrenome = user_profile.sobrenome
        super().save(*args, **kwargs)