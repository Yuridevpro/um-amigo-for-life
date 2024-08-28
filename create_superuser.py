from django.contrib.auth import get_user_model
from dotenv import load_dotenv
import os
import sys

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Defina as credenciais do superusuário a partir das variáveis de ambiente
SUPERUSER_USERNAME = os.getenv('SUPERUSER_USERNAME')
SUPERUSER_EMAIL = os.getenv('SUPERUSER_EMAIL')
SUPERUSER_PASSWORD = os.getenv('SUPERUSER_PASSWORD')

def create_superuser():
    User = get_user_model()
    print(f"Verificando se o superusuário '{SUPERUSER_USERNAME}' existe...")
    if not User.objects.filter(username=SUPERUSER_USERNAME).exists():
        User.objects.create_superuser(SUPERUSER_USERNAME, SUPERUSER_EMAIL, SUPERUSER_PASSWORD)
        print("Superusuário criado com sucesso!")
    else:
        print("Superusuário já existe.")

if __name__ == '__main__':
    # Configure o ambiente Django
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adote.settings')
    
    try:
        # Configurar Django
        import django
        django.setup()
        
        # Criar superusuário
        create_superuser()
    except Exception as e:
        print(f"Erro ao criar superusuário: {e}")
        sys.exit(1)
