from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from perfil.models import UserProfile  # Importa o modelo UserProfile
from django.contrib import messages
from django.contrib.messages import constants
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
import re
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.conf import settings
from django.contrib.sites.shortcuts import get_current_site
from django.utils.crypto import get_random_string
from django.utils import timezone
from datetime import timedelta
from .models import Ativacao, ResetSenha
from django.utils.encoding import force_bytes
from django.contrib.auth.tokens import default_token_generator
from social_django.models import UserSocialAuth  # Importe o modelo UserSocialAuth
from django.db import IntegrityError


def cadastro(request):
    # Redireciona o usuário para a página de divulgação se ele já estiver autenticado
     # Redireciona o usuário para a página de divulgação se ele já estiver autenticado
    if request.user.is_authenticated:
        if request.user.is_superuser:
            messages.add_message(request, messages.ERROR, "Superusuários não têm permissão para acessar esta página, faça o cadastro com outra conta e acesse.")
            return redirect('/auth/login/')  
        return redirect('/divulgar/novo_pet')

    # Processa a requisição GET (exibe o formulário de cadastro)
    if request.method == "GET":
        return render(request, 'cadastro.html')
    # Processa a requisição POST (trata o envio do formulário)
    elif request.method == "POST":
        # Recupera os dados do formulário
        nome = request.POST.get('nome')
        sobrenome = request.POST.get('sobrenome')
        email = request.POST.get('email')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')
        telefone = request.POST.get('telefone')
        estado_id = request.POST.get('estado_id')
        estado_nome = request.POST.get('estado_nome')
        cidade_nome = request.POST.get('cidade_nome')

        # Valida se todos os campos foram preenchidos
        if not nome or not sobrenome or not email or not senha or not confirmar_senha or not telefone or not estado_id or not cidade_nome:
            messages.add_message(request, constants.ERROR, 'Preencha todos os campos')
            return render(request, 'cadastro.html', {'nome': nome, 'sobrenome': sobrenome, 'email': email, 'telefone': telefone, 'estado_id': estado_id, 'cidade_nome': cidade_nome})

        # Valida se as senhas coincidem
        if senha != confirmar_senha:
            messages.add_message(request, constants.ERROR, 'As senhas não coincidem')
            return render(request, 'cadastro.html', {'nome': nome, 'sobrenome': sobrenome, 'email': email, 'telefone': telefone, 'estado_id': estado_id, 'cidade_nome': cidade_nome})

        # Valida o formato do email
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            messages.add_message(request, constants.ERROR, 'Email inválido')
            return render(request, 'cadastro.html', {'nome': nome, 'sobrenome': sobrenome, 'email': email, 'telefone': telefone, 'estado_id': estado_id, 'cidade_nome': cidade_nome})

        # Valida a complexidade da senha
        senha_pattern = r'^(?=.*[a-zA-Z])(?=.*[0-9]).{8,}$'
        if not re.match(senha_pattern, senha):
            messages.add_message(request, constants.ERROR, 'Senha deve ter pelo menos 8 caracteres, com letras e números')
            return render(request, 'cadastro.html', {'nome': nome, 'sobrenome': sobrenome, 'email': email, 'telefone': telefone, 'estado_id': estado_id, 'cidade_nome': cidade_nome})

        try:
            # Verifica se o email já existe no banco de dados
            if User.objects.filter(email=email).exists():
                # Se o usuário já existe e está inativo, envia um novo email de ativação
                user_inativo = User.objects.get(email=email, is_active=False)
                token = get_random_string(length=32)
                ativacao, created = Ativacao.objects.get_or_create(user=user_inativo)
                ativacao.confirmation_token = token
                ativacao.confirmation_token_expiration = timezone.now() + timedelta(days=1)
                ativacao.save()

                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
                uidb64 = urlsafe_base64_encode(force_bytes(user_inativo.pk))
                link = f'http://{domain}/auth/confirmar_email/{uidb64}/{token}'

                subject = f'Confirmação de Cadastro - {site_name}'
                message_html = render_to_string(
                    'email_confirmacao.html',
                    {
                        'user': user_inativo,
                        'domain': domain,
                        'uidb64': uidb64,
                        'token': token,
                        'link': link,
                    }
                )
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [email]

                email = EmailMultiAlternatives(subject, '', from_email, recipient_list)
                email.attach_alternative(message_html, "text/html")
                email.send(fail_silently=False)

                messages.add_message(request, constants.SUCCESS, 'Enviamos um novo email de confirmação para seu endereço. Por favor, verifique sua caixa de entrada ou spam.')
                return render(request, 'cadastro.html', {'nome': nome, 'sobrenome': sobrenome, 'email': email, 'telefone': telefone, 'estado_id': estado_id, 'cidade_nome': cidade_nome})
            else:
                # Cria um novo usuário com o email como username
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password=senha,
                    is_active=False,
                )
                # Cria o perfil do usuário com campos adicionais
                UserProfile.objects.create(
                    user=user,
                    telefone=telefone,
                    estado_nome=estado_nome,
                    estado_id=estado_id,
                    cidade_nome=cidade_nome,
                    nome=nome,
                    sobrenome=sobrenome,
                    email=email
                )

                # Gera um token de ativação e salva na tabela Ativacao
                token = get_random_string(length=32)
                ativacao = Ativacao.objects.create(
                    user=user,
                    confirmation_token=token,
                    confirmation_token_expiration=timezone.now() + timedelta(days=1)
                )

                # Gera o link de ativação e envia o email de confirmação
                current_site = get_current_site(request)
                site_name = current_site.name
                domain = current_site.domain
                uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
                link = f'http://{domain}/auth/confirmar_email/{uidb64}/{token}'

                subject = f'Confirmação de Cadastro - {site_name}'
                message_html = render_to_string(
                    'email_confirmacao.html',
                    {
                        'user': user,
                        'domain': domain,
                        'uidb64': uidb64,
                        'token': token,
                        'link': link,
                    }
                )
                from_email = settings.EMAIL_HOST_USER
                recipient_list = [email]

                email = EmailMultiAlternatives(subject, '', from_email, recipient_list)
                email.attach_alternative(message_html, "text/html")
                email.send(fail_silently=False)

                messages.add_message(request, constants.SUCCESS, 'Enviamos um email para confirmar seu cadastro. Clique no link para finalizar.')
                return redirect('/auth/login')
        except Exception as e:
            # Captura e exibe mensagens de erro
            messages.add_message(request, constants.ERROR, 'Erro ao cadastrar usuário: ' + str(e))
            return render(request, 'cadastro.html', {'nome': nome, 'sobrenome': sobrenome, 'email': email, 'telefone': telefone, 'estado_id': estado_id, 'cidade_nome': cidade_nome})


# Função para confirmar o email do usuário
def confirmar_email(request, uidb64, token):
    try:
        # Decodifica o ID do usuário e recupera o usuário do banco de dados
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
        # Recupera a instância de Ativacao do usuário
        ativacao = Ativacao.objects.get(user=user, confirmation_token=token)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist, Ativacao.DoesNotExist):
        user = None
        ativacao = None

    # Verifica se o usuário e a ativação foram encontrados e se o token ainda é válido
    if user is not None and ativacao is not None and ativacao.__dict__.get('confirmation_token_expiration') is not None and ativacao.__dict__['confirmation_token_expiration'] > timezone.now():
        # Ativa o usuário e remove a instância de Ativacao
        user.is_active = True
        user.save()
        ativacao.delete()
        messages.add_message(request, constants.SUCCESS, 'Email confirmado com sucesso! Você pode agora fazer login.')
        return redirect('/auth/login')
    else:
        # Mensagem de erro para link inválido ou expirado
        messages.add_message(request, constants.ERROR, 'Link de confirmação inválido ou expirado.')
        return redirect('/auth/login')


def logar(request):
    # Processa a requisição GET (exibe o formulário de login)
    if request.method == "GET":
        return render(request, 'login.html')
    # Processa a requisição POST (trata o envio do formulário)
    elif request.method == "POST":
        # Recupera os dados do formulário
        email = request.POST.get('email')
        senha = request.POST.get('senha')

        try:
            # Tenta recuperar o usuário pelo email
            user = User.objects.get(email=email)
            if user.is_active:
                # Se o usuário for um superusuário, redireciona ou bloqueia o acesso
                if user.is_superuser:
                    messages.add_message(request, messages.ERROR, "Superusuários não têm permissão para acessar esta página.")
                    return redirect('/home')  # Substitua '/home' pela URL para onde deseja redirecionar

                # Autentica o usuário
                user = authenticate(request, username=user.username, password=senha)
                # Se a autenticação for bem-sucedida, loga o usuário
                if user is not None:
                    login(request, user)
                    return redirect('/divulgar/novo_pet')
                else:
                    # Mensagem de erro para email ou senha inválidos
                    messages.add_message(request, constants.ERROR, 'Email ou senha inválidos')
                    return render(request, 'login.html')
            else:
                # Mensagem de erro para conta não ativada
                messages.add_message(request, constants.ERROR, 'Conta não ativada')
                return render(request, 'login.html')
        except User.DoesNotExist:
            # Mensagem de erro para email ou senha inválidos
            messages.add_message(request, constants.ERROR, 'Email ou senha inválidos')
            return render(request, 'login.html')


# Função para lidar com a solicitação de recuperação de senha
def esqueceu_senha(request):
    # Processa a requisição GET (exibe o formulário de recuperação de senha)
    if request.method == "GET":
        return render(request, 'esqueceu_senha.html')
    # Processa a requisição POST (trata o envio do formulário)
    elif request.method == "POST":
        # Recupera o email do formulário
        email = request.POST.get('email')

        # Valida se o email foi informado
        if not email:
            messages.add_message(request, constants.ERROR, 'Informe um email válido')
            return render(request, 'esqueceu_senha.html')

        try:
            # Tenta recuperar o usuário pelo email
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Mensagem de erro para usuário não encontrado
            messages.add_message(request, constants.ERROR, 'Usuário com este email não encontrado')
            return render(request, 'esqueceu_senha.html')

        # Gera e salva um token de redefinição de senha
        try:
            token = default_token_generator.make_token(user)
            reset_instance, created = ResetSenha.objects.get_or_create(user=user)
            reset_instance.reset_token = token
            reset_instance.save()
        except Exception as e:
            messages.add_message(request, constants.ERROR, 'Erro ao gerar o token de redefinição de senha. Tente novamente mais tarde.')
            return render(request, 'esqueceu_senha.html')

        # Gera o link de redefinição de senha e envia o email
        try:
            current_site = get_current_site(request)
            domain = current_site.domain
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            reset_link = f'http://{domain}/auth/criar_senha/{uidb64}/{token}/'

            subject = f'Redefinição de senha - {current_site.name}'
            message_html = render_to_string(
                'email_reset_senha.html',
                {
                    'user': user,
                    'domain': domain,
                    'uidb64': uidb64,
                    'token': token,
                    'reset_link': reset_link,
                }
            )
            from_email = settings.EMAIL_HOST_USER
            recipient_list = [email]

            email = EmailMultiAlternatives(subject, '', from_email, recipient_list)
            email.attach_alternative(message_html, "text/html")
            email.send(fail_silently=False)
        except Exception as e:
            messages.add_message(request, constants.ERROR, 'Erro ao enviar o email de redefinição de senha. Tente novamente mais tarde.')
            return render(request, 'esqueceu_senha.html')

        messages.add_message(request, constants.SUCCESS, 'Enviamos um email com instruções para redefinir sua senha.')
        return redirect('/auth/login')


# Função para permitir que o usuário crie uma nova senha
def criar_senha(request, uidb64, token):
    try:
        # Decodifica o ID do usuário e recupera o usuário do banco de dados
        uid = urlsafe_base64_decode(uidb64).decode('utf-8')
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # Verifica se o usuário foi encontrado e se o token é válido
    if user is not None and default_token_generator.check_token(user, token):
        # Processa a requisição POST (trata o envio do formulário)
        if request.method == 'POST':
            # Recupera as novas senhas do formulário
            senha_nova = request.POST.get('senha_nova')
            confirmar_senha = request.POST.get('confirmar_senha')

            # Valida se as senhas coincidem
            if senha_nova != confirmar_senha:
                messages.add_message(request, constants.ERROR, 'As senhas não coincidem')
                return render(request, 'criar_senha.html')

            # Altera a senha do usuário
            try:
                user.set_password(senha_nova)
                user.save()
            except Exception as e:
                messages.add_message(request, constants.ERROR, 'Erro ao alterar a senha. Tente novamente mais tarde.')
                return render(request, 'criar_senha.html', {'uidb64': uidb64, 'token': token})

            messages.add_message(request, constants.SUCCESS, 'Sua senha foi alterada com sucesso. Faça login com sua nova senha.')
            return redirect('/auth/login')
        else:
            # Exibe o formulário para a criação da nova senha
            return render(request, 'criar_senha.html', {'uidb64': uidb64, 'token': token})
    else:
        # Mensagem de erro para link inválido ou expirado
        messages.add_message(request, constants.ERROR, 'Link de redefinição de senha inválido ou expirado.')
        return redirect('/auth/login')