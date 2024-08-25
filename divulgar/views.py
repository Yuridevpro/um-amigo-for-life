from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Pet, PetImage
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.urls import reverse
from django.shortcuts import render, redirect, get_object_or_404

@login_required
def novo_pet(request):
    if request.method == 'POST':
        especie = request.POST.get('especie')
        sexo = request.POST.get('sexo')
        tamanho = request.POST.get('tamanho')
        nome_pet = request.POST.get('nome_pet')
        historia_pet = request.POST.get('historia_pet')
        cuidados = request.POST.getlist('cuidados')
        vive_bem_em = request.POST.getlist('vive_bem_em')
        temperamento = request.POST.getlist('temperamento')
        sociavel_com = request.POST.getlist('sociavel_com')
       

        # Validation
        errors = []
        if not request.FILES.get('foto_principal'):
            errors.append('Foto principal é obrigatória.')
        if not especie:
            errors.append('Espécie é obrigatória.')
        if not sexo:
            errors.append('Sexo é obrigatório.')
        if not tamanho:
            errors.append('Tamanho é obrigatório.')
        if not nome_pet:
            errors.append('Nome do Pet é obrigatório.')
        if not cuidados:
            errors.append('Cuidados são obrigatórios.')
        if not vive_bem_em:
            errors.append('Vive bem em é obrigatório.')
        if not temperamento:
            errors.append('Temperamento é obrigatório.')
        if not sociavel_com:
            errors.append('Sociável com é obrigatório.')
        
        secondary_images = request.FILES.getlist('fotos_secundarias')
        if len(secondary_images) > 5:
            errors.append('Você pode enviar no máximo 5 imagens secundárias.')
        
        if errors:
            return render(request, 'novo_pet.html', {
                'especie': especie,
                'sexo': sexo,
                'tamanho': tamanho,
                'cuidados': cuidados,
                'vive_bem_em': vive_bem_em,
                'temperamento': temperamento,
                'sociavel_com': sociavel_com,
                'nome_pet': nome_pet,
                'historia_pet': historia_pet,
                'errors': errors,
            })

        # Save Pet instance
        pet = Pet(
            especie=especie,
            sexo=sexo,
            tamanho=tamanho,
            nome_pet=nome_pet,
            historia_pet=historia_pet,
            usuario=request.user,
            cuidados=cuidados,
            vive_bem_em=vive_bem_em,
            temperamento=temperamento,
            sociavel_com=sociavel_com,
           
        )
        pet.save()

        # Save Pet Images
        main_image = request.FILES.get('foto_principal')
        if main_image:
            pet.foto_principal = main_image
            pet.save()

        secondary_images = request.FILES.getlist('fotos_secundarias')
        for image in secondary_images[:5]:
            secondary_image = PetImage.objects.create(pet=pet, image=image)
            pet.fotos_secundarias.add(secondary_image)

        messages.success(request, 'Pet cadastrado com sucesso!')
        return redirect(reverse('listar_pets'))

    return render(request, 'novo_pet.html')





def ver_pet(request, id):
    pet = get_object_or_404(Pet, id=id)
    
    if request.method == "GET":
        return render(request, 'ver_pet.html', {'pet': pet})

    if request.method == "POST":
        # Verifica se o usuário é o dono do pet
        if pet.usuario != request.user:
            messages.add_message(request, messages.ERROR, 'Esse pet não é seu!')
            return redirect('ver_pet', id=id)

        # Atualiza o status do pet para "Adotado"
        pet.status = 'A'
        pet.save()

        messages.success(request, 'Pet marcado como adotado com sucesso.')
        return redirect('ver_pet', id=id)



