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

class AdminSessionMiddleware(MiddlewareMixin):
    """
    Middleware para definir um cookie de sessão separado para o Django Admin.
    """
    def process_request(self, request):
        # Verifica se o usuário está acessando o Django Admin
        if request.path.startswith('/admin/'):
            # Usar um cookie de sessão separado para o admin
            admin_session_key = request.COOKIES.get(settings.ADMIN_SESSION_COOKIE_NAME)
            if admin_session_key:
                request.session._session_key = admin_session_key  # Atribui o cookie de sessão do admin ao request

            # Define o cookie CSRF para o admin
            request.META['CSRF_COOKIE'] = settings.ADMIN_CSRF_COOKIE_NAME
        else:
            # Usar o cookie de sessão padrão para o resto do site
            session_key = request.COOKIES.get(settings.SESSION_COOKIE_NAME)
            if session_key:
                request.session._session_key = session_key  # Atribui o cookie de sessão padrão ao request

            # Define o cookie CSRF padrão
            request.META['CSRF_COOKIE'] = settings.CSRF_COOKIE_NAME

    def process_response(self, request, response):
        # Verifica se o usuário está acessando o Django Admin
        if request.path.startswith('/admin/'):
            # Configura o cookie de sessão para o admin
            response.set_cookie(
                settings.ADMIN_SESSION_COOKIE_NAME,
                request.session._session_key,
                path=settings.ADMIN_SESSION_COOKIE_PATH
            )
        else:
            # Configura o cookie de sessão padrão para o resto do site
            response.set_cookie(
                settings.SESSION_COOKIE_NAME,
                request.session._session_key,
                path='/'
            )
        return response


