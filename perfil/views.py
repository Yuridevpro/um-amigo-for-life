from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import requests
from .models import UserProfile
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.messages import constants
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
import re
from django.contrib.auth import authenticate, logout
from django.shortcuts import get_object_or_404
from divulgar.models import Pet
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.contrib.auth import update_session_auth_hash


@login_required
def meu_perfil(request):
    user = request.user

    # Verifica se o usuário tem um perfil
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Você precisa criar um perfil para acessar esta página.')
        return redirect('editar_perfil')

    # Pets divulgados (cadastrados) pelo usuário
    pets_divulgados = Pet.objects.filter(usuario=user).count()  # Conta todos os pets do usuário

    # Pets cadastrados pelo usuário que foram adotados
    pets_adotados = Pet.objects.filter(usuario=user, status='A').count() 

    # Obter os pets do usuário
    meus_pets = Pet.objects.filter(usuario=user, is_active=True).order_by('-id')  # Adicione is_active=True para filtrar pets ativos

    # Pagination (limitando o número de cards inicialmente)
    paginator = Paginator(meus_pets, 6)  # Show 6 pets per page.
    page = request.GET.get('page') or 1  # Get the page number from the request, default to 1

    try:
        meus_pets = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page.
        meus_pets = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page.
        meus_pets = paginator.page(paginator.num_pages)

    # Customize pagination display 
    page_numbers = []
    current_page = meus_pets.number  # Página atual
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
    return render(request, 'meu_perfil.html', {
        'user': user,
        'pets_divulgados': pets_divulgados,
        'pets_adotados': pets_adotados,
        'meus_pets': meus_pets,  # Passa os pets do usuário para o template
        'page_numbers': page_numbers,
    })
    

def perfil_protetor(request, user_id):
    user = get_object_or_404(User, pk=user_id)
    
    # Verifica se o usuário tem um perfil
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        messages.error(request, 'Este usuário não possui um perfil.')
        return redirect('login')

    # Obter os pets do usuário
    pets = Pet.objects.filter(usuario=user, is_active=True) 
    
    # Contar todos os pets do usuário
    pets_divulgados = Pet.objects.filter(usuario=user, is_active=True).count() 
    
    # Verificar se o usuário atual é o dono do perfil
    is_owner = user == request.user
    
    # Contar os pets adotados
    pets_adotados = Pet.objects.filter(usuario=user, status='A').count()  

    # Se o usuário for o dono do perfil, redireciona para o meu_perfil
    if is_owner:
        return redirect('meu_perfil')  # corrigido o redirecionamento

    # Pagination (limitando o número de cards inicialmente)
    paginator = Paginator(pets, 6)  # Show 6 pets per page.
    page = request.GET.get('page') or 1  # Get the page number from the request, default to 1

    try:
        pets = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver the first page.
        pets = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page.
        pets = paginator.page(paginator.num_pages)

    # Customize pagination display 
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
    return render(request, 'perfil_protetor.html', {
        'user': user,
        'user_profile': user_profile,
        'pets': pets,
        'is_owner': is_owner, 
        'pets_adotados': pets_adotados,
        'profile_user': user,
        'pets_divulgados': pets_divulgados,  # Passa a contagem total para o template
        'page_numbers': page_numbers,
    })

    
@login_required
def ver_perfil(request, user_id):
    profile_user = get_object_or_404(User, id=user_id)
    return render(request, 'ver_perfil.html', {'profile_user': profile_user})





@login_required
def editar_perfil(request):
    user = request.user
    
    # Verifica se o usuário já tem um perfil
    try:
        user_profile = UserProfile.objects.get(user=user)
    except UserProfile.DoesNotExist:
        user_profile = UserProfile.objects.create(user=user)

    if request.method == "POST":
        nome = request.POST.get('nome')
        sobrenome = request.POST.get('sobrenome')
        email = request.POST.get('email')
        telefone = request.POST.get('telefone')
        estado_id = request.POST.get('estado')
        estado_nome = request.POST.get('estado_nome')
        cidade = request.POST.get('cidade')
        foto_perfil = request.FILES.get('foto_perfil')
        remove_foto_perfil = request.POST.get('remove_foto_perfil') == 'true'

        errors = []
        if not nome:
            errors.append('Nome é obrigatório.')
        if not sobrenome:
            errors.append('Sobrenome é obrigatório.')
        if not telefone:
            errors.append('Telefone é obrigatório.')
        if not estado_nome:
            errors.append('Estado é obrigatório.')
        if not cidade:
            errors.append('Cidade é obrigatória.')

        # Valida o formato do email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            errors.append('Email inválido')

        # Valida o telefone
        telefone_pattern = r'^\(?([0-9]{2})\)?[-. ]?([0-9]{4,5})[-. ]?([0-9]{4})$'
        if not re.match(telefone_pattern, telefone):
            errors.append('Telefone inválido')

        # Verifica se o email já está sendo usado por outro usuário
        if User.objects.filter(email=email).exclude(pk=user.pk).exists():
            errors.append('Este email já está sendo usado por outro usuário.')

        if errors:
            for error in errors:
                messages.error(request, error)
            return redirect('editar_perfil')

        # Atualiza o perfil do usuário
        user_profile.nome = nome
        user_profile.sobrenome = sobrenome
        user_profile.telefone = telefone
        user_profile.estado_id = estado_id
        user_profile.estado_nome = estado_nome
        user_profile.cidade_nome = cidade

        # Atualiza o email e a foto de perfil se fornecidos
        user_profile.email = email  # Aqui estamos definindo o email no UserProfile
        
        if foto_perfil:
            user_profile.foto_perfil = foto_perfil
        elif remove_foto_perfil:
            if user_profile.foto_perfil:
                user_profile.foto_perfil.delete(save=False)
                
        user_profile.save()

        # Mensagem de sucesso
        messages.add_message(request, constants.SUCCESS, 'Perfil atualizado com sucesso')

        # Se o perfil foi atualizado com sucesso, verificar se há um fluxo social pendente
        if 'partial_pipeline' in request.session:
            backend = request.session['partial_pipeline']['backend']
            return redirect('social:complete', backend=backend)

        return redirect('meu_perfil')
    else:
        # Verifica se todos os campos estão preenchidos
        if not user_profile.nome or not user_profile.sobrenome or not user_profile.telefone or not user_profile.estado_nome or not user_profile.cidade_nome:
            messages.error(request, 'Você precisa preencher todos os campos do perfil antes de continuar.')

    return render(request, 'editar_perfil.html', {'user_profile': user_profile})


@login_required
@receiver(post_save, sender=UserProfile)
def update_user(sender, instance, created, **kwargs):
    user = instance.user
    
    # Se o email do UserProfile for preenchido e o email do usuário estiver vazio, atualize-o
    if instance.email and not user.email:
        user.email = instance.email
    
    # Mantenha o username como o email do usuário, se necessário
    if not user.username or user.username != instance.email:
        user.username = instance.email
    
    user.save()



@login_required
def remover_foto_perfil(request):
    if request.method == 'POST' and request.user.is_authenticated:
        user_profile = get_object_or_404(UserProfile, user=request.user)
        
        # Remova a foto de perfil
        user_profile.foto_perfil.delete(save=True)
        
        return JsonResponse({'message': 'Foto de perfil removida com sucesso.'})

    # Caso o método da requisição não seja POST ou o usuário não esteja autenticado,
    # pode retornar um JsonResponse com erro ou redirecionar para outra página.
    return JsonResponse({'error': 'Acesso não autorizado ou método inválido.'}, status=403)


@login_required
def alterar_senha(request):
    if request.method == 'POST':
        senha_atual = request.POST.get('senha_atual')
        senha_nova = request.POST.get('senha_nova')
        confirmar_senha = request.POST.get('confirmar_senha')

        # Verificar se todos os campos foram preenchidos
        if not senha_atual or not senha_nova or not confirmar_senha:
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos.')
            return render(request, 'alterar_senha.html')

        # Verificar se a senha atual está correta
        user = authenticate(request, username=request.user.username, password=senha_atual)
        if user is None:
            messages.add_message(request, constants.ERROR, 'Senha atual incorreta.')
            return render(request, 'alterar_senha.html')

        # Verificar se as senhas coincidem
        if senha_nova != confirmar_senha:
            messages.add_message(request, constants.ERROR, 'As senhas não coincidem.')
            return render(request, 'alterar_senha.html')

        # Verificar se a nova senha atende aos requisitos
        senha_pattern = r'^(?=.*[a-zA-Z])(?=.*[0-9]).{8,}$'
        if not re.match(senha_pattern, senha_nova):
            messages.add_message(request, constants.ERROR, 'A nova senha deve ter pelo menos 8 caracteres, com letras e números.')
            return render(request, 'alterar_senha.html')

        # Se tudo estiver correto, alterar a senha
        try:
            user.set_password(senha_nova)
            user.save()
            update_session_auth_hash(request, user)  # Importante para manter o usuário logado após a mudança de senha
            messages.add_message(request, constants.SUCCESS, 'Sua senha foi alterada com sucesso!')
            return redirect('meu_perfil')  # corrigido o redirecionamento
        except Exception as e:
            messages.add_message(request, constants.ERROR, 'Erro ao alterar senha: ' + str(e))
            return render(request, 'alterar_senha.html')
    else:
        return render(request, 'alterar_senha.html')

@login_required
def remover_pet(request, id):
    pet = Pet.objects.get(id=id)
    if not pet.usuario == request.user:
        messages.add_message(request, messages.ERROR, 'Esse pet não é seu!')
        return redirect('/divulgar/seus_pets')

    pet.is_active = False
    pet.save()
    messages.success(request, 'Pet removido com sucesso.')
    return redirect('meu_perfil') 

@login_required
@csrf_exempt
def remover_conta(request):
    if request.method == 'POST':
        user = request.user
        try:
            user.delete()
            logout(request)
            messages.add_message(request, constants.SUCCESS, 'Conta removida com sucesso!')
            return redirect('login') 
        except Exception as e:
            messages.add_message(request, constants.ERROR, f'Erro ao remover conta: {str(e)}')
            return JsonResponse({'error': str(e)}, status=400) 
    else:
        return JsonResponse({'error': 'Método inválido.'}, status=405)

@login_required
def sair(request):
    logout(request)
    return redirect('/auth/login')


