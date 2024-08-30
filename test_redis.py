import redis

# Conectar ao Redis
r = redis.StrictRedis(host='localhost', port=6379, db=0)

# Testar a conexão
try:
    print("Conectando ao Redis...")
    print(r.ping())  # Deve retornar True
    print("Conexão bem-sucedida!")
except redis.ConnectionError as e:
    print("Erro ao conectar ao Redis:", e)
