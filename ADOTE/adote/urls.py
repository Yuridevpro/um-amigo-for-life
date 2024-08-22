from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('auth/', include('usuarios.urls')),
    path('divulgar/', include('divulgar.urls')),
    path('adotar/', include('adotar.urls')),
    path('perfil/', include('perfil.urls')),
    path('sobre_nos/', include('sobre_nos.urls')),
    path('pagina_inicio/', include('pagina_inicio.urls')),
  
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

