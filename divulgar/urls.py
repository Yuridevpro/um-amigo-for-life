from django.urls import path
from . import views

urlpatterns = [
    path('novo_pet/', views.novo_pet, name="novo_pet"),
    path('ver_pet/<int:id>', views.ver_pet, name="ver_pet"),

]