from django.shortcuts import render, redirect, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from divulgar.models import Pet
from perfil.models import UserProfile
from .models import Depoimento
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.http import JsonResponse

def home(request):
    pets_list = Pet.objects.filter(status__in=["P"], is_active=True).order_by('-created_at')  # Ordena por data_criacao decrescente 
    estado_id = request.GET.get('estado')
    cidade_nome = request.GET.get('cidade')
    tamanho = request.GET.get('tamanho')
    especie = request.GET.get('especie')

    if estado_id:
        pets_list = pets_list.filter(usuario__userprofile__estado_id=estado_id)

    if cidade_nome:
        pets_list = pets_list.filter(usuario__userprofile__cidade_nome=cidade_nome)

    if tamanho:
        pets_list = pets_list.filter(tamanho=tamanho)
    if especie:
        pets_list = pets_list.filter(especie=especie)

    choices_especie = Pet.choices_especie
    choices_tamanho = Pet.choices_tamanho
    
    
    paginator = Paginator(pets_list, 6)
    page = request.GET.get('page') or 1

    try:
        pets = paginator.page(page)
    except PageNotAnInteger:
        pets = paginator.page(1)
    except EmptyPage:
        pets = paginator.page(paginator.num_pages)

    page_numbers = []
    current_page = pets.number
    total_pages = paginator.num_pages

    if total_pages <= 7:
        page_numbers = list(range(1, total_pages + 1))
    else:
        if current_page <= 4:
            page_numbers = list(range(1, 6)) + ["...", total_pages]
        elif current_page >= total_pages - 3:
            page_numbers = [1, "..."] + list(range(total_pages - 4, total_pages + 1))
        else:
            page_numbers = [1, "..."] + list(range(current_page - 1, current_page + 2)) + ["...", total_pages]

    depoimentos_list = Depoimento.objects.order_by('-data_criacao')
    depoimentos_paginator = Paginator(depoimentos_list, 3)
    depoimentos = depoimentos_paginator.page(1)  # Mostra a primeira página

    mais_depoimentos = depoimentos_paginator.num_pages > 1

    # Adiciona o perfil do usuário ao contexto
    user_profile = None
    if request.user.is_authenticated:
        try:
            user_profile = UserProfile.objects.get(user=request.user)
        except UserProfile.DoesNotExist:
            messages.error(request, 'Você precisa criar um perfil para acessar esta página.')
            return redirect('editar_perfil') 

    return render(request, 'home.html', {
        'pets': pets,
        'page_numbers': page_numbers,
        'choices_especie': choices_especie,
        'choices_tamanho': choices_tamanho,
        'estado_id': estado_id,
        'cidade_nome': cidade_nome,
        'tamanho': tamanho,
        'especie': especie,
        'depoimentos': depoimentos,
        'mais_depoimentos': mais_depoimentos,
        'user_profile': user_profile,
    })

@login_required
def criar_depoimento(request):
    mensagem_erro = ''

    if request.method == 'POST':
        mensagem = request.POST.get('mensagem')
        nome = request.user.userprofile.nome
        sobrenome = request.user.userprofile.sobrenome  # Captura o sobrenome
        email = request.user.userprofile.email

        try:
            # Tenta obter o depoimento existente do usuário
            depoimento = Depoimento.objects.get(email=email)
            # Se encontrado, atualiza o depoimento existente
            depoimento.mensagem = mensagem
            depoimento.save()
            messages.success(request, 'Depoimento atualizado com sucesso!')
        except Depoimento.DoesNotExist:
            # Se não encontrado, cria um novo depoimento
            depoimento = Depoimento.objects.create(nome=nome, sobrenome=sobrenome, email=email, mensagem=mensagem, usuario=request.user)
            messages.success(request, 'Depoimento enviado com sucesso!')

        return redirect('depoimento')  # Redireciona para a página de depoimentos

    # Tenta obter o depoimento existente do usuário
    try:
        depoimento = Depoimento.objects.get(email=request.user.userprofile.email)
    except Depoimento.DoesNotExist:
        depoimento = None

    context = {
        'mensagem_erro': mensagem_erro,
        'depoimento': depoimento,
        'nome': request.user.userprofile.nome,  # Adiciona o nome ao contexto
        'sobrenome': request.user.userprofile.sobrenome  # Adiciona o sobrenome ao contexto
    }
    return render(request, 'depoimento.html', context)

@login_required
def editar_depoimento(request, pk):
    depoimento = get_object_or_404(Depoimento, pk=pk)
    mensagem_erro = ''

    if request.method == 'POST':
        mensagem = request.POST.get('mensagem')
        depoimento.mensagem = mensagem
        depoimento.save()
        messages.success(request, 'Depoimento atualizado com sucesso!')
        return redirect('depoimento')  # Redireciona para a página de depoimentos após salvar

    context = {
        'depoimento': depoimento,
        'mensagem_erro': mensagem_erro,
        'nome': request.user.userprofile.nome,  # Adiciona o nome ao contexto
        'sobrenome': request.user.userprofile.sobrenome  # Adiciona o sobrenome ao contexto
    }
    return render(request, 'depoimento.html', context)

@login_required
def deletar_depoimento(request, pk):
    depoimento = get_object_or_404(Depoimento, pk=pk)
    if request.method == 'POST':
        depoimento.delete()
        messages.success(request, 'Depoimento deletado com sucesso!')
        return redirect('depoimento')  # Redireciona para a página de depoimentos após deletar
    context = {'depoimento': depoimento}
    return render(request, 'depoimento.html', context)

@login_required
def mais_depoimentos(request):
    """View para carregar mais depoimentos."""
    depoimentos_list = Depoimento.objects.order_by('-data_criacao')
    depoimentos_paginator = Paginator(depoimentos_list, 3)

    # Pega a página atual (a partir da query string)
    pagina_atual = int(request.GET.get('pagina_atual', 1))
    try:
        depoimentos = depoimentos_paginator.page(pagina_atual + 1)
    except EmptyPage:
        depoimentos = None

    if depoimentos:
        # Renderiza os depoimentos em um formato JSON
        depoimentos_json = [
            {
                'mensagem': depoimento.mensagem,
                'nome': depoimento.nome,
                'sobrenome': depoimento.sobrenome,
            }
            for depoimento in depoimentos
        ]
        return JsonResponse({'depoimentos': depoimentos_json})
    else:
        # Se não houver mais depoimentos, retorna um JSON vazio
        return JsonResponse({'depoimentos': []})
    
    