import redis

# Conectar ao Redis
r = redis.StrictRedis('redis://red-cr92gud6l47c73bq8tk0:6379/0', decode_responses=True)

# Testar a conexão
try:
    print("Conectando ao Redis...")
    print(r.ping())  # Deve retornar True
    print("Conexão bem-sucedida!")
except redis.ConnectionError as e:
    print("Erro ao conectar ao Redis:", e)