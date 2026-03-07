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
# celulares
# ======================================================================
# chave personalizada para o banco de dados produtos
# celulares
CELULAR_ID = "id"


def celulares():
    return [
        {"id": 1, 
        "modelo": "Celular A",
        "marca": "Marca A",
        "cor": "Preto",
        "imei": "1234567890",
        "data_cadastro": "2023-04-01",
        "custos_de_aquisicao": 200.0,
        "custos_de_reparo": 50.0,
        "preco": 400.0,
        "condicao": "bom",
        "fotos": ["foto1.jpg", "foto2.jpg"]
        }
        ]