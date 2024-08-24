from django.shortcuts import render

def quem_somos(request):
    return render(request, 'quem_somos.html')
def politica_privacidade(request):
    return render(request, 'politica_privacidade.html')
def termos_servico(request):
    return render(request, 'termos_servico.html')
