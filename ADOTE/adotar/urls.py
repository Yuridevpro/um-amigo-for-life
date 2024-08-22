from django.urls import path
from .views import listar_pets
from . import views

urlpatterns = [

    path('listar_pets/', listar_pets, name='listar_pets'),
    
]