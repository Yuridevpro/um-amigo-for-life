from django.urls import path
from . import views

urlpatterns = [
    path('quem_somos/', views.quem_somos, name='quem_somos'),
    path('politica_privacidade/', views.politica_privacidade, name='politica_privacidade'),
    path('termos_servico/', views.termos_servico, name='termos_servico'),
]
