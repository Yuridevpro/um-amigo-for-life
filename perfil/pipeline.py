from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages
from django.contrib.messages import constants
from social_django.models import UserSocialAuth
from social_core.exceptions import AuthAlreadyAssociated
from .models import UserProfile

# Função para criar ou atualizar o perfil do usuário
def create_profile(strategy, details, user=None, *args, **kwargs):
    if user:
        try:
            profile = UserProfile.objects.get(user=user)
            # O perfil já existe, faz o login e redireciona para a página inicial
            login(strategy.request, user, backend='social_core.backends.google.GoogleOAuth2')
            return redirect(reverse('home'))
        except UserProfile.DoesNotExist:
            # Se o perfil não existir, cria um novo e redireciona para editar o perfil
            profile = UserProfile(user=user, email=details.get('email'))
            profile.save()
            login(strategy.request, user, backend='social_core.backends.google.GoogleOAuth2')
            return redirect(reverse('editar_perfil'))
    return {'user': user}

# Função para associar um e-mail a um usuário existente ou criar um novo usuário
def associate_by_email(backend, details, user=None, *args, **kwargs):
    email = details.get('email') or backend.strategy.session_get('email')

    if not email:
        # Se o e-mail não estiver disponível, redireciona para a edição de perfil
        return {'user': None, 'redirect': reverse('editar_perfil')}

    try:
        existing_user = User.objects.get(email=email)

        if user and user.pk != existing_user.pk:
            # Se o e-mail já está em uso por outro usuário e é um usuário diferente
            messages.add_message(backend.strategy.request, constants.ERROR, 'Este e-mail já está em uso por outro usuário.')
            return render(backend.strategy.request, 'cadastro.html')

        try:
            # Verifica se o usuário já está associado a este provedor
            social_auth = UserSocialAuth.objects.filter(user=existing_user, provider=backend.name).first()
            if social_auth:
                # Se já existe uma associação com este provedor, loga o usuário
                login(backend.strategy.request, existing_user, backend=f'social_core.backends.{backend.name}.{backend.name.capitalize()}OAuth2')
                return {'user': existing_user, 'redirect': reverse('home')}
            else:
                # Associa o novo provedor ao usuário existente
                backend.strategy.storage.user.create_social_auth(user=existing_user, provider=backend.name, uid=details.get('uid'))
                login(backend.strategy.request, existing_user, backend=f'social_core.backends.{backend.name}.{backend.name.capitalize()}OAuth2')
                return {'user': existing_user, 'redirect': reverse('editar_perfil')}

        except AuthAlreadyAssociated:
            # Captura a exceção caso o e-mail já esteja associado a outro provedor
            messages.add_message(backend.strategy.request, constants.ERROR, 'Este e-mail já está associado a outro provedor.')
            return render(backend.strategy.request, 'cadastro.html')

    except User.DoesNotExist:
        # Cria o usuário se não existir
        user = User.objects.create_user(
            username=email,  # Usa o email como username
            email=email,
            password=None
        )
        # Cria a associação do provedor com o novo usuário
        backend.strategy.storage.user.create_social_auth(user=user, provider=backend.name, uid=details.get('uid'))
        login(backend.strategy.request, user, backend=f'social_core.backends.{backend.name}.{backend.name.capitalize()}OAuth2')
        return {'user': user, 'redirect': reverse('editar_perfil')}
