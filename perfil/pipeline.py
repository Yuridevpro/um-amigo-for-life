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
            # Como o middleware já lida com a verificação do perfil, você pode omitir essa verificação aqui.
            login(strategy.request, user, backend='social_core.backends.google.GoogleOAuth2')
            return redirect(reverse('home'))
        except UserProfile.DoesNotExist:
            profile = UserProfile(user=user, email=details.get('email'))
            profile.save()
            login(strategy.request, user, backend='social_core.backends.google.GoogleOAuth2')
            return redirect(reverse('editar_perfil'))

    return {'user': user}

def associate_by_email(backend, details, user=None, *args, **kwargs):
    email = details.get('email') or backend.strategy.session_get('email')

    if not email:
        return {'user': None, 'redirect': reverse('editar_perfil')}

    try:
        existing_user = User.objects.get(email=email)

        # Verifica se a conta já está associada ao Facebook
        if UserSocialAuth.objects.filter(user=existing_user, provider='facebook').exists():
            login(backend.strategy.request, existing_user, backend='social_core.backends.facebook.FacebookOAuth2')
            return {'user': existing_user, 'redirect': reverse('home')}
        else:
            # Associa o novo provedor à conta existente
            backend.strategy.storage.user.create_social_auth(user=existing_user, provider=backend.name, uid=details.get('uid'))
            login(backend.strategy.request, existing_user, backend='social_core.backends.' + backend.name)
            return {'user': existing_user, 'redirect': reverse('home')}

    except User.DoesNotExist:
        # Cria um novo usuário e associa o provedor
        user = User.objects.create_user(
            username=email,
            email=email,
            password=None
        )
        backend.strategy.storage.user.create_social_auth(user=user, provider=backend.name, uid=details.get('uid'))
        login(backend.strategy.request, user, backend='social_core.backends.' + backend.name)
        return {'user': user, 'redirect': reverse('editar_perfil')}
