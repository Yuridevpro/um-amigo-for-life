import os
import sys
from django.core.wsgi import get_wsgi_application
from pathlib import Path


# Definindo o diretório do projeto como raiz para imports
root = Path(__file__).resolve().parent.parent
sys.path.append(str(root))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'adote.settings')

application = get_wsgi_application()