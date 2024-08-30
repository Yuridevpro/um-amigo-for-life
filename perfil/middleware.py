from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from django.contrib.auth import logout
from django.urls import reverse
class ProfileCompleteMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and not request.user.is_superuser:
            profile = UserProfile.objects.get_or_create(user=request.user)[0]
            if not profile.nome or not profile.sobrenome or not profile.telefone or not profile.estado_nome or not profile.cidade_nome:
                if request.method == 'POST' and request.path == '/auth/logout/':  # Verifica se a requisição é um POST request e se o usuário está tentando fazer logout
                    logout(request)  # Realiza o logout
                    return redirect('login')  # Redireciona para a página de login
                elif request.path != '/perfil/editar_perfil/' and request.path != '/auth/logout/' and request.path != '/auth/login/':  # Verifica se a página atual não é a página de edição de perfil, logout ou login
                    return redirect(reverse('editar_perfil'))
        return self.get_response(request)


from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
from importlib import import_module

class SeparateAdminSessionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/admin/'):
            request.session_cookie_name = settings.ADMIN_SESSION_COOKIE_NAME
        else:
            request.session_cookie_name = settings.SESSION_COOKIE_NAME

        # Carrega a engine de sessão configurada
        session_engine = import_module(settings.SESSION_ENGINE)
        
        # Substitui a chave de sessão ativa pela nova chave do cookie, se existir
        session_key = request.COOKIES.get(request.session_cookie_name)
        request.session = session_engine.SessionStore(session_key)

    def process_response(self, request, response):
        # Define o cookie correto na resposta, conforme o tipo de sessão
        response.set_cookie(
            request.session_cookie_name,
            request.session.session_key,
            httponly=True,
            secure=request.is_secure(),
            samesite='Lax',
            path=settings.ADMIN_SESSION_COOKIE_PATH if request.path.startswith('/admin/') else settings.SESSION_COOKIE_PATH
        )
        return response


