import redis
import os

# Obtém o URL do Redis a partir das variáveis de ambiente
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')  # Valor padrão para desenvolvimento local

# Conectar ao Redis
r = redis.StrictRedis.from_url(REDIS_URL, decode_responses=True)

# Testar a conexão
try:
    print("Conectando ao Redis...")
    print(r.ping())  # Deve retornar True
    print("Conexão bem-sucedida!")
except redis.ConnectionError as e:
    print("Erro ao conectar ao Redis:", e)
