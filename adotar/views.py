from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.db import transaction
from django.core.mail import send_mail
from django.utils.timezone import now
from django.http import JsonResponse
from divulgar.models import Pet
from adote.settings import constants
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import requests

@login_required
def listar_pets(request):
    pets_list = Pet.objects.filter(status__in=["P"], is_active=True).order_by('-created_at')  # Ordena por data_criacao decrescente 

    # Obter os valores de filtro do formulário
    estado_id = request.GET.get('estado')
    cidade_nome = request.GET.get('cidade')  # Usar o nome da cidade
    tamanho = request.GET.get('tamanho')
    especie = request.GET.get('especie')

    # Filtrando por estado (agora usando o ID)
    if estado_id:
        pets_list = pets_list.filter(usuario__userprofile__estado_id=estado_id)  # Filtra por estado_id do UserProfile

    # Filtrando por cidade (usando o nome da cidade)
    if cidade_nome:
        pets_list = pets_list.filter(usuario__userprofile__cidade_nome=cidade_nome)

    if tamanho:
        pets_list = pets_list.filter(tamanho=tamanho)
    if especie:
        pets_list = pets_list.filter(especie=especie)

    choices_especie = Pet.choices_especie
    choices_tamanho = Pet.choices_tamanho

    # Pagination (limitando o número de cards inicialmente)
    paginator = Paginator(pets_list, 12)  # Show 10 pets per page.
    page = request.GET.get('page') or 1  # Get the page number from the request, default to 1

    try:
        pets = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page.
        pets = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page.
        pets = paginator.page(paginator.num_pages)

    # Customize pagination display (same as before)
    page_numbers = []
    current_page = pets.number  # Página atual
    total_pages = paginator.num_pages  # Total de páginas

    # Construindo a lista de números de página para exibição personalizada
    if total_pages <= 7:
        page_numbers = list(range(1, total_pages + 1))
    else:
        if current_page <= 4:
            # Mostra os primeiros 5 números e o último
            page_numbers = list(range(1, 6)) + ["...", total_pages]
        elif current_page >= total_pages - 3:
            # Mostra os últimos 5 números e o primeiro
            page_numbers = [1, "..."] + list(range(total_pages - 4, total_pages + 1))
        else:
            # Mostra os números em torno da página atual
            page_numbers = [1, "..."] + list(range(current_page - 1, current_page + 2)) + ["...", total_pages]

    # Passa os números de página personalizados para o template
    return render(request, 'listar_pets.html', {
        'pets': pets,
        'cidade_nome': cidade_nome,  # Passa o nome da cidade para o template
        'estado_id': estado_id,  # Passa o estado_id para o template
        'tamanho': tamanho,
        'especie': especie,
        'choices_especie': choices_especie,
        'choices_tamanho': choices_tamanho,
        'page_numbers': page_numbers,
    })
    
    
    



