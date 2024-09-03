from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.urls import reverse
from django.contrib import messages
from django.contrib.messages import constants
from social_django.models import UserSocialAuth
from .models import UserProfile

def create_profile(strategy, details, user=None, *args, **kwargs):
    if user:
        try:
            profile = UserProfile.objects.get(user=user)
            # O perfil já existe, apenas faz login e redireciona
            login(strategy.request, user, backend='social_core.backends.google.GoogleOAuth2')
            return redirect(reverse('home'))
        except UserProfile.DoesNotExist:
            # O perfil não existe, cria um novo
            profile = UserProfile(user=user, email=details.get('email'))
            profile.save()
            login(strategy.request, user, backend='social_core.backends.google.GoogleOAuth2')
            return redirect(reverse('editar_perfil'))

    return {'user': user}


    return {'user': user}

from django.contrib.auth.models import User
from social_django.models import UserSocialAuth

def associate_by_email(backend, details, user=None, *args, **kwargs):
    email = details.get('email') or backend.strategy.session_get('email')

    if not email:
        return {'user': None, 'redirect': reverse('editar_perfil')}

    try:
        existing_user = User.objects.get(email=email)

        # Verifica se o usuário já está associado ao Facebook
        social_auth = UserSocialAuth.objects.filter(user=existing_user, provider='facebook').first()
        if social_auth:
            # Se o usuário já estiver associado, faça login normalmente
            login(backend.strategy.request, existing_user, backend='social_core.backends.facebook.FacebookOAuth2')
            return {'user': existing_user, 'redirect': reverse('home')}
        else:
            # Se o usuário existir, mas não estiver associado ao Facebook, associe-o
            backend.strategy.storage.user.create_social_auth(user=existing_user, provider='facebook', uid=details.get('uid'))
            login(backend.strategy.request, existing_user, backend='social_core.backends.facebook.FacebookOAuth2')
            return {'user': existing_user, 'redirect': reverse('home')}

    except User.DoesNotExist:
        # Se o usuário não existir, crie-o e associe-o ao Facebook
        user = User.objects.create_user(
            username=email,
            email=email,
            password=None
        )
        backend.strategy.storage.user.create_social_auth(user=user, provider='facebook', uid=details.get('uid'))
        login(backend.strategy.request, user, backend='social_core.backends.facebook.FacebookOAuth2')
        return {'user': user, 'redirect': reverse('editar_perfil')}

