# import redis
# import os

# # Conectar ao Redis
# r = redis.StrictRedis(
#     host=os.getenv('REDIS_HOST', 'red-cr92gud6l47c73bq8tk0'),
#     port=os.getenv('REDIS_PORT', 6379),
#     db=0
# )

# # Testar a conexão
# try:
#     print("Conectando ao Redis...")
#     print(r.ping())  # Deve retornar True
#     print("Conexão bem-sucedida!")
# except redis.ConnectionError as e:
#     print("Erro ao conectar ao Redis:", e)

