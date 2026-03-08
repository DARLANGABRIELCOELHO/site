from datetime import datetime, date
import sqlite3
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "ifix.db")

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_estado():
    inicializar_banco_clientes()
    inicializar_banco_tecnicos()
    inicializar_banco_produtos()
    inicializar_banco_celulares()
    inicializar_banco_servicos()

# -----------------------------------------------------------------------------
# SERVIÇOS
# -----------------------------------------------------------------------------
# CHAVE DE DADOS PARA SERVIÇOS
SERVICO_ID = "id"
SERVICO_NOME = "nome"
SERVICO_MODELO_CELULAR = "modelo_celular"
SERVICO_CATEGORIA = "categoria"
SERVICO_CUSTOS = "custos"
SERVICO_PRECO = "preco"
SERVICO_TEMPO_ESTIMADO = "tempo_estimado"
SERVICO_OBSERVACAO = "observacao"
SERVICO_DATA_CADASTRO = "data_cadastro"
# INICIALIZAÇÃO DO BANCO DE DADOS PARA SERVIÇOS
def inicializar_banco_servicos():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS servicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                modelo_celular TEXT,
                categoria TEXT,
                custos REAL,
                preco REAL,
                tempo_estimado TEXT,
                observacao TEXT,
                data_cadastro TEXT
            )
        """)

        cursor.execute("SELECT COUNT(*) FROM servicos")
        total = cursor.fetchone()[0]

        if total == 0:
            cursor.execute("""
                INSERT INTO servicos (
                    nome, modelo_celular, categoria, custos, preco,
                    tempo_estimado, observacao, data_cadastro
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "Serviço A",
                "Celular A",
                "Reparo de tela",
                50.0,
                100.0,
                "2 horas",
                "Garantia de 3 meses",
                "2023-05-01"
            ))

        conn.commit()

def obter_servicos():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM servicos")
        resultados = cursor.fetchall()
    return [dict(row) for row in resultados]

def obter_servico(servico_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM servicos WHERE id = ?", (servico_id,))
        row = cursor.fetchone()
    return dict(row) if row else None
# INSERÇÃO DE SERVIÇOS
def inserir_servico(nome, modelo_celular, categoria, custos, preco, tempo_estimado, observacao, data_cadastro):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO servicos (
                nome, modelo_celular, categoria, custos, preco,
                tempo_estimado, observacao, data_cadastro
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (nome, modelo_celular, categoria, custos, preco, tempo_estimado, observacao, data_cadastro))
        conn.commit()
        novo_id = cursor.lastrowid
    return obter_servico(novo_id)
# ATUALIZAÇÃO DE SERVIÇOS
def atualizar_servico(servico_id, nome, modelo_celular, categoria, custos, preco, tempo_estimado, observacao, data_cadastro):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE servicos
            SET nome = ?, modelo_celular = ?, categoria = ?, custos = ?, preco = ?,
                tempo_estimado = ?, observacao = ?, data_cadastro = ?
            WHERE id = ?
        """, (nome, modelo_celular, categoria, custos, preco, tempo_estimado, observacao, data_cadastro, servico_id))
        conn.commit()
    return obter_servico(servico_id)
# PESQUISA DE SERVIÇOS 
def obter_modelos_distintos(termo=""):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if termo:
            cursor.execute(
                "SELECT DISTINCT modelo_celular FROM servicos WHERE modelo_celular LIKE ? ORDER BY modelo_celular",
                (f"%{termo}%",)
            )
        else:
            cursor.execute("SELECT DISTINCT modelo_celular FROM servicos ORDER BY modelo_celular")
        resultados = cursor.fetchall()
    return [row["modelo_celular"] for row in resultados if row["modelo_celular"]]
# pesquisa de categorias distintas para preenchimento automático do campo de categoria
def obter_categorias_distintas(termo=""):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if termo:
            cursor.execute(
                "SELECT DISTINCT categoria FROM servicos WHERE categoria LIKE ? ORDER BY categoria",
                (f"%{termo}%",)
            )
        else:
            cursor.execute("SELECT DISTINCT categoria FROM servicos ORDER BY categoria")
        resultados = cursor.fetchall()
    return [row["categoria"] for row in resultados if row["categoria"]]
# EXCLUSÃO DE SERVIÇOS
def excluir_servico(servico_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM servicos WHERE id = ?", (servico_id,))
        conn.commit()
