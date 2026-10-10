
import os
import psycopg
from dotenv import load_dotenv

load_dotenv()

try:
    with psycopg.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        sslmode=os.getenv("DB_SSLMODE", "require"),
        connect_timeout=15,
    ) as conexao:
        with conexao.cursor() as cursor:
            cursor.execute("SELECT current_database();")
            banco = cursor.fetchone()[0]

        print("Conexão realizada com sucesso!")
        print(f"Banco conectado: {banco}")

except Exception as erro:
    print("Não foi possível conectar ao banco.")
    print(f"Erro: {erro}")
