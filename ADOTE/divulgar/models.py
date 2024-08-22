# models.py
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Pet(models.Model):
    choices_status = (('P', 'Para adoção'), ('A', 'Adotado'))
    choices_especie = (('Cachorro', 'Cachorro'), ('Gato', 'Gato'))
    choices_sexo = (('Macho', 'Macho'), ('Fêmea', 'Fêmea'))
    choices_tamanho = (('Grande', 'Grande'), ('Médio', 'Médio'), ('Pequeno', 'Pequeno'))
    choices_cuidados_veterinarios = (
        ('Castrado', 'Castrado'),
        ('Precisa de cuidados especiais', 'Precisa de cuidados especiais'),
        ('Vacinado', 'Vacinado'),
        ('Vermifugado', 'Vermifugado')
    )
    choices_vive_bem_em = (
        ('Apartamento', 'Apartamento'),
        ('Casa com quintal', 'Casa com quintal'),
        ('Dentro de casa', 'Dentro de casa')
    )
    choices_temperamento = (
        ('Agressivo', 'Agressivo'),
        ('Arisco', 'Arisco'),
        ('Brincalhão', 'Brincalhão'),
        ('Calmo', 'Calmo'),
        ('Carente', 'Carente'),
        ('Docil', 'Docil')
    )
    choices_sociavel_com = (
        ('Cachorros', 'Cachorros'),
        ('Crianças', 'Crianças'),
        ('Desconhecidos', 'Desconhecidos'),
        ('Gatos', 'Gatos')
    )

    nome_pet = models.CharField(max_length=10, help_text='Nome do Pet (máximo de 10 caracteres)')
    usuario = models.ForeignKey(User, on_delete=models.CASCADE, default=None) 
    historia_pet = models.TextField(default='História do Pet não fornecida')
    status = models.CharField(max_length=1, choices=choices_status, default='P')
    especie = models.CharField(max_length=10, choices=choices_especie)
    sexo = models.CharField(max_length=10, choices=choices_sexo)
    tamanho = models.CharField(max_length=10, choices=choices_tamanho)
    cuidados = models.JSONField(default=list, blank=True)
    vive_bem_em = models.JSONField(default=list, blank=True)
    temperamento = models.JSONField(default=list, blank=True)
    sociavel_com = models.JSONField(default=list, blank=True)
    foto_principal = models.ImageField(upload_to='pet_images/', null=True, blank=True)
    fotos_secundarias = models.ManyToManyField('PetImage', blank=True, related_name='secondary_images')
    telefone = models.CharField(max_length=20, null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.nome_pet


@receiver(post_save, sender=Pet)
def update_pet_location(sender, instance, created, **kwargs):
    if created:
        instance.estado = instance.usuario.userprofile.estado_nome  # Obter do UserProfile
        instance.cidade = instance.usuario.userprofile.cidade_nome  # Obter do UserProfile
        instance.telefone = instance.usuario.userprofile.telefone
        instance.save()


class PetImage(models.Model):
    pet = models.ForeignKey(Pet, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='pet_images/')

    def __str__(self):
        return f"Image for {self.pet.nome_pet}"
