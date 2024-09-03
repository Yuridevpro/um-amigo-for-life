from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from social_django.models import UserSocialAuth
from .models import UserProfile

def create_profile(strategy, details, user=None, *args, **kwargs):
    if user:
        email = details.get('email')
        
        if email:
            # Verifica se o email já está em uso por outro usuário
            try:
                existing_user = User.objects.get(email=email)
                if existing_user != user:
                    # Se o email já está em uso por outro usuário, mostra uma mensagem de erro
                    messages.add_message(strategy.request, messages.ERROR, 'Este e-mail já está em uso.')
                    return redirect(reverse('login'))
            except User.DoesNotExist:
                pass
        
        try:
            profile = UserProfile.objects.get(user=user)
            login(strategy.request, user, backend='social_core.backends.google.GoogleOAuth2')
            return redirect(reverse('home'))
        except UserProfile.DoesNotExist:
            profile = UserProfile(user=user, email=email)
            profile.save()
            login(strategy.request, user, backend='social_core.backends.google.GoogleOAuth2')
            return redirect(reverse('editar_perfil'))

    return {'user': user}

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse
from social_django.models import UserSocialAuth
from .models import UserProfile

def associate_by_email(backend, details, user=None, *args, **kwargs):
    # Obtém o e-mail dos detalhes fornecidos pelo backend ou da sessão
    email = details.get('email') or backend.strategy.session_get('email')

    if not email:
        # Se o e-mail não estiver disponível, tente obtê-lo a partir do perfil do usuário
        if user:
            try:
                user_profile = UserProfile.objects.get(user=user)
                email = user_profile.email
            except UserProfile.DoesNotExist:
                pass

    if not email:
        # Se o e-mail ainda não estiver disponível, redireciona para o perfil para que o usuário possa fornecer o e-mail
        return {'user': None, 'redirect': reverse('editar_perfil')}

    try:
        # Tenta obter um usuário existente com o e-mail fornecido
        existing_user = User.objects.get(email=email)

        # Verifica se o usuário já está associado ao Facebook
        social_auth = UserSocialAuth.objects.filter(user=existing_user, provider='facebook').first()
        if social_auth:
            # Se o usuário já estiver associado ao Facebook, faça login normalmente
            login(backend.strategy.request, existing_user, backend='social_core.backends.facebook.FacebookOAuth2')
            return {'user': existing_user, 'redirect': reverse('home')}
        else:
            # Se o usuário não estiver associado ao Facebook, crie a associação
            backend.strategy.storage.user.create_social_auth(user=existing_user, provider='facebook', uid=details.get('uid'))
            login(backend.strategy.request, existing_user, backend='social_core.backends.facebook.FacebookOAuth2')
            return {'user': existing_user, 'redirect': reverse('editar_perfil')}
    
    except User.DoesNotExist:
        # Se o usuário não existir, crie um novo usuário
        if email:
            user = User.objects.create_user(
                username=email,
                email=email,
                password=None
            )
            backend.strategy.storage.user.create_social_auth(user=user, provider='facebook', uid=details.get('uid'))
            login(backend.strategy.request, user, backend='social_core.backends.facebook.FacebookOAuth2')
            return {'user': user, 'redirect': reverse('editar_perfil')}
        else:
            # Se o e-mail não estiver disponível, redirecione para o perfil
            return {'user': None, 'redirect': reverse('editar_perfil')}



