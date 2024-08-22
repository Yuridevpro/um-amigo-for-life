from django.urls import path
from . import views

urlpatterns = [
    path('home/', views.home, name='home'),
    path('depoimento/', views.criar_depoimento, name='depoimento'),
    path('depoimento/<int:pk>/editar/', views.editar_depoimento, name='editar_depoimento'),
    path('depoimento/<int:pk>/deletar/', views.deletar_depoimento, name='deletar_depoimento'),
    path('mais_depoimentos/', views.mais_depoimentos, name='mais_depoimentos'),  # Adicione esta rota
    path('', views.home, name='home'),  # adicione a URL desejada
    
]

