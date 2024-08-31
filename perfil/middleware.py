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



from django.utils.deprecation import MiddlewareMixin
from django.conf import settings

from django.utils.deprecation import MiddlewareMixin

class SeparateAdminSessionMiddleware(MiddlewareMixin):
    def process_request(self, request):
        if request.path.startswith('/admin/'):
            request.session.cookie_name = settings.ADMIN_SESSION_COOKIE_NAME
            request.session.engine = settings.ADMIN_SESSION_ENGINE
            request.session.cache_alias = settings.ADMIN_SESSION_CACHE_ALIAS
        else:
            request.session.cookie_name = settings.SESSION_COOKIE_NAME
            request.session.engine = settings.SESSION_ENGINE
            request.session.cache_alias = settings.SESSION_CACHE_ALIAS

    def process_response(self, request, response):
        response.set_cookie(request.session.cookie_name, request.session.session_key)
        return response


