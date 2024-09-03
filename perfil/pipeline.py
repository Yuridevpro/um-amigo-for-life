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

from django.contrib.auth import login
from django.contrib.auth.models import User
from django.shortcuts import redirect
from django.urls import reverse
from social_django.models import UserSocialAuth
from .models import UserProfile
from social_core.exceptions import AuthAlreadyAssociated

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
        existing_user = User.objects.get(email=email)

        if user and user.pk != existing_user.pk:
            # Se o e-mail já está em uso por outro usuário e é um usuário diferente
            messages.add_message(backend.strategy.request, constants.ERROR, 'Este e-mail já está em uso por outro usuário.')
            return render(backend.strategy.request, 'cadastro.html')

        try:
            # Verifica se o usuário já está associado a este provedor
            social_auth = backend.strategy.storage.user.get_social_auth_for_user(existing_user)
            if social_auth and social_auth.filter(provider=backend.name).exists():
                # Se já existe uma associação com este provedor, loga o usuário com o backend correto
                login(backend.strategy.request, existing_user, backend=backend.name)
                return {'user': existing_user, 'redirect': reverse('home')}
            else:
                # Associa o novo provedor ao usuário existente
                backend.strategy.storage.user.create_social_auth(user=existing_user, provider=backend.name, uid=details.get('uid'))
                login(backend.strategy.request, existing_user, backend=backend.name)
                return {'user': existing_user, 'redirect': reverse('home')}
        
        except AuthAlreadyAssociated:
            # Captura a exceção caso o email já esteja associado a outro provedor
            messages.add_message(backend.strategy.request, constants.ERROR, 'Este e-mail já está associado a outro provedor.')
            return render(backend.strategy.request, 'cadastro.html')
    
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



