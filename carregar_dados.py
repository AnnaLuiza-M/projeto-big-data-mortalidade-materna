
import os
from pathlib import Path

import pandas as pd
import psycopg
from dotenv import load_dotenv
from psycopg import sql

# Carrega as configurações do arquivo .env
load_dotenv()

PASTA_DADOS = Path("dados/tratados")

ARQUIVOS = {
    "ripsa_2_01": "RIPSA 2.01 tratado.csv",
    "ripsa_2_02": "RIPSA 2.02 tratado.csv",
}


def converter_tipo(tipo):
    """Converte os tipos do Pandas para tipos do PostgreSQL."""
    if pd.api.types.is_integer_dtype(tipo):
        return "BIGINT"

    if pd.api.types.is_float_dtype(tipo):
        return "DOUBLE PRECISION"

    return "TEXT"


def preparar_valor(valor):
    """Converte valores ausentes em NULL e tipos NumPy em tipos Python."""
    if pd.isna(valor):
        return None

    if hasattr(valor, "item"):
        return valor.item()

    return valor


def main():
    # Configurações de conexão com o PostgreSQL da Aiven
    configuracao = {
        "host": os.getenv("DB_HOST"),
        "port": os.getenv("DB_PORT"),
        "dbname": os.getenv("DB_NAME"),
        "user": os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "sslmode": os.getenv("DB_SSLMODE", "require"),
        "connect_timeout": 15,
    }

    # Confere se as configurações necessárias foram preenchidas
    obrigatorias = ["host", "port", "dbname", "user", "password"]

    for chave in obrigatorias:
        if not configuracao[chave]:
            raise ValueError(
                f"A configuração {chave} não foi encontrada no .env."
            )

    # Abre a conexão com o banco
    with psycopg.connect(**configuracao) as conexao:
        with conexao.cursor() as cursor:

            for tabela, nome_arquivo in ARQUIVOS.items():
                caminho = PASTA_DADOS / nome_arquivo

                # Confere se o CSV existe
                if not caminho.exists():
                    raise FileNotFoundError(
                        f"Arquivo não encontrado: {caminho}"
                    )

                # Lê os dados tratados
                df = pd.read_csv(caminho)

                # Cria a tabela caso ela ainda não exista
                definicoes = [
                    sql.SQL("{} {}").format(
                        sql.Identifier(coluna),
                        sql.SQL(converter_tipo(df[coluna].dtype)),
                    )
                    for coluna in df.columns
                ]

                cursor.execute(
                    sql.SQL("CREATE TABLE IF NOT EXISTS {} ({})").format(
                        sql.Identifier(tabela),
                        sql.SQL(", ").join(definicoes),
                    )
                )

                # Verifica se a tabela já possui registros
                cursor.execute(
                    sql.SQL("SELECT EXISTS (SELECT 1 FROM {} LIMIT 1)").format(
                        sql.Identifier(tabela)
                    )
                )

                tabela_preenchida = cursor.fetchone()[0]

                if tabela_preenchida:
                    print(
                        f"Tabela {tabela} já possui dados. "
                        "Carga ignorada."
                    )
                    continue

                # Prepara as colunas e os parâmetros do INSERT
                colunas_sql = sql.SQL(", ").join(
                    sql.Identifier(coluna) for coluna in df.columns
                )

                marcadores = sql.SQL(", ").join(
                    sql.Placeholder() for _ in df.columns
                )

                comando = sql.SQL(
                    "INSERT INTO {} ({}) VALUES ({})"
                ).format(
                    sql.Identifier(tabela),
                    colunas_sql,
                    marcadores,
                )

                # Converte as linhas para valores aceitos pelo PostgreSQL
                registros = [
                    tuple(preparar_valor(valor) for valor in linha)
                    for linha in df.itertuples(index=False, name=None)
                ]

                # Insere os registros
                if registros:
                    cursor.executemany(comando, registros)

                print(
                    f"Tabela {tabela}: "
                    f"{len(registros)} registros carregados."
                )

        # Confirma a transação quando as operações terminam
        conexao.commit()

    print("\nProcesso de carga finalizado.")


if __name__ == "__main__":
    main()
