from datetime import datetime, date
import sqlite3
import os
# ======================================================================
# CONFIGURAÇÃO DO BANCO
# ======================================================================
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
# ======================================================================
# PRODUTOS
# ======================================================================
# chave personalizada para o banco de dados produtos
PRODUTO_ID = "id"
PRODUTO_NOME = "name"
PRODUTO_CATEGORIA = "categoria"
PRODUTO_CUSTOS = "custos"
PRODUTO_PRECO = "preco"
PRODUTO_DATA_CADASTRO = "data_cadastro"
PRODUTO_ESTOQUE = "estoque"
PRODUTO_ESTOQUE_MINIMO = "estoque_minimo"
# CRIA A TABELA PRODUTOS E INSERE DADOS INICIAIS SE VAZIA
def inicializar_banco_produtos():
    with get_db_connection() as conn:
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS produtos (
                {PRODUTO_ID} INTEGER PRIMARY KEY AUTOINCREMENT,
                {PRODUTO_NOME} TEXT NOT NULL,
                {PRODUTO_CATEGORIA} TEXT NOT NULL,
                {PRODUTO_CUSTOS} REAL NOT NULL,
                {PRODUTO_PRECO} REAL NOT NULL,
                {PRODUTO_DATA_CADASTRO} TEXT NOT NULL,
                {PRODUTO_ESTOQUE} INTEGER NOT NULL,
                {PRODUTO_ESTOQUE_MINIMO} INTEGER NOT NULL
            )
        """)
        # Verifica se a tabela está vazia antes de inserir dados iniciais
        cursor = conn.execute(f"SELECT COUNT(*) FROM produtos")
        count = cursor.fetchone()[0]
        if count == 0:
            # Insere dados iniciais (exemplo)
            conn.execute(f"""
                INSERT INTO produtos (
                    {PRODUTO_NOME}, {PRODUTO_CATEGORIA}, {PRODUTO_CUSTOS},
                    {PRODUTO_PRECO}, {PRODUTO_DATA_CADASTRO},
                    {PRODUTO_ESTOQUE}, {PRODUTO_ESTOQUE_MINIMO}
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("Produto A", "carregador", 50.0, 100.0, "2023-03-01", 10, 5))
        conn.commit()
# Função para obter o próximo ID disponível para um novo produto
def obter_proximo_id_produto():
    with get_db_connection() as conn:
        cursor = conn.execute(f"SELECT MAX({PRODUTO_ID}) FROM produtos")
        max_id = cursor.fetchone()[0]
        return (max_id + 1) if max_id is not None else 1
# insere um novo produto no banco de dados
def inserir_produto(nome, categoria, custos, preco, data_cadastro, estoque, estoque_minimo):
    novo_id = obter_proximo_id_produto()
    with get_db_connection() as conn:
        conn.execute(f"""
            INSERT INTO produtos (
                {PRODUTO_ID}, {PRODUTO_NOME}, {PRODUTO_CATEGORIA},
                {PRODUTO_CUSTOS}, {PRODUTO_PRECO}, {PRODUTO_DATA_CADASTRO},
                {PRODUTO_ESTOQUE}, {PRODUTO_ESTOQUE_MINIMO}
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (novo_id, nome, categoria, custos, preco, data_cadastro, estoque, estoque_minimo))
        conn.commit()
    return obter_produto(novo_id)
# atualiza as informações de um produto existente no banco de dados
def atualizar_produto(produto_id, nome, categoria, custos, preco, data_cadastro, estoque, estoque_minimo):
    with get_db_connection() as conn:
        conn.execute(f"""
            UPDATE produtos SET
                {PRODUTO_NOME} = ?, {PRODUTO_CATEGORIA} = ?, {PRODUTO_CUSTOS} = ?,
                {PRODUTO_PRECO} = ?, {PRODUTO_DATA_CADASTRO} = ?, {PRODUTO_ESTOQUE} = ?,
                {PRODUTO_ESTOQUE_MINIMO} = ?
            WHERE {PRODUTO_ID} = ?
        """, (nome, categoria, custos, preco, data_cadastro, estoque, estoque_minimo, produto_id))
        conn.commit()
    return obter_produto(produto_id)
# exclui um produto do banco de dados com base no ID fornecido
def excluir_produto(produto_id):
    with get_db_connection() as conn:
        conn.execute(f"DELETE FROM produtos WHERE {PRODUTO_ID} = ?", (produto_id,))
        conn.commit()
