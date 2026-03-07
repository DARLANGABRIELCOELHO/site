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
    inicializar_banco_celulares()
    inicializar_banco_servicos()

# ======================================================================
# CLIENTES
# ======================================================================
# Chaves padronizadas para os campos do cliente (usadas como referência)
CLIENTE_ID = "id"
CLIENTE_NOME = "nome"
CLIENTE_TELEFONE = "telefone"
CLIENTE_DOCUMENTO = "documento"
CLIENTE_ENDERECO = "endereco"
CLIENTE_OBSERVACOES = "observacoes"
CLIENTE_DATA_CADASTRO = "data_cadastro"
CLIENTE_ORDENS_SERVICO = "ordens_servico"
# CRIA A TABELA CLIENTES E INSERE DADOS INICIAIS SE VAZIA
def inicializar_banco_clientes():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clientes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                telefone TEXT,
                documento TEXT,
                endereco TEXT,
                observacoes TEXT,
                data_cadastro TEXT
            )
        """)

        cursor.execute("SELECT COUNT(*) FROM clientes")
        if cursor.fetchone()[0] == 0:
            cursor.execute("""
                INSERT INTO clientes (nome, telefone, documento, endereco, observacoes, data_cadastro)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                "Cliente A",
                "15555-1234",
                "123.456.789-00",
                "Rua A, 123",
                "Cliente VIP",
                "01/01/2023"
            ))
            conn.commit()
# Função para obter o próximo ID disponível para um novo cliente
def proximo_id_cliente():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM clientes")
        max_id = cursor.fetchone()[0]
        return (max_id or 0) + 1
# Função para obter o próximo ID disponível para um novo técnico
def obter_cliente(cliente_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
        row = cursor.fetchone()
    return dict(row) if row else None
# insere um novo cliente no banco de dados
def inserir_cliente(nome, telefone, documento, endereco, observacoes):
    data_cadastro = datetime.now().strftime("%d/%m/%Y")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clientes (nome, telefone, documento, endereco, observacoes, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nome, telefone, documento, endereco, observacoes, data_cadastro))
        conn.commit()
        return cursor.lastrowid
# atualiza as informações de um cliente existente no banco de dados
def atualizar_cliente(cliente_id, nome, telefone, documento, endereco, observacoes):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE clientes
            SET nome = ?, telefone = ?, documento = ?, endereco = ?, observacoes = ?
            WHERE id = ?
        """, (nome, telefone, documento, endereco, observacoes, cliente_id))
        conn.commit()
    return obter_cliente(cliente_id)
# exclui um cliente do banco de dados com base no ID fornecido
def excluir_cliente(cliente_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM clientes WHERE id = ?", (cliente_id,))
        conn.commit()

# ======================================================================
# TÉCNICOS
# ======================================================================
# Chaves padronizadas para os campos do técnico (usadas como referência)
TECNICO_ID = "id"
TECNICO_NOME = "nome"
TECNICO_TELEFONE = "telefone"
TECNICO_ESPECIALIDADE = "especialidade"
TECNICO_DATA_CADASTRO = "data_cadastro"
TECNICO_ORDENS_SERVICO = "ordens_servico"
# CRIA A TABELA TECNICOS E INSERE DADOS INICIAIS SE VAZIA
def inicializar_banco_tecnicos():
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS tecnicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nome TEXT NOT NULL,
                telefone TEXT NOT NULL,
                especialidade TEXT NOT NULL,
                data_cadastro TEXT NOT NULL,
                ordens_servico INTEGER DEFAULT 0
            )
        """)

        cursor.execute("SELECT COUNT(*) FROM tecnicos")
        if cursor.fetchone()[0] == 0:
            dados_iniciais = [
                ("Técnico A", "15555-5678", "android", "2023-02-01", 0)
            ]
            cursor.executemany("""
                INSERT INTO tecnicos (nome, telefone, especialidade, data_cadastro, ordens_servico)
                VALUES (?, ?, ?, ?, ?)
            """, dados_iniciais)

        conn.commit()
# Função para obter o próximo ID disponível para um novo técnico
def obter_tecnico(tecnico_id):
    with get_db_connection() as conn:
        tecnico = conn.execute("""
            SELECT id, nome, telefone, especialidade, data_cadastro, ordens_servico
            FROM tecnicos
            WHERE id = ?
        """, (tecnico_id,)).fetchone()

    return dict(tecnico) if tecnico else None
# insere um novo técnico no banco de dados
def inserir_tecnico(nome, telefone, especialidade):
    hoje = date.today().isoformat()
    with get_db_connection() as conn:
        cursor = conn.execute("""
            INSERT INTO tecnicos (nome, telefone, especialidade, data_cadastro)
            VALUES (?, ?, ?, ?)
        """, (nome, telefone, especialidade, hoje))
        conn.commit()
        novo_id = cursor.lastrowid

    return obter_tecnico(novo_id)
# atualiza as informações de um técnico existente no banco de dados
def atualizar_tecnico(tecnico_id, nome, telefone, especialidade):
    with get_db_connection() as conn:
        conn.execute("""
            UPDATE tecnicos
            SET nome = ?, telefone = ?, especialidade = ?
            WHERE id = ?
        """, (nome, telefone, especialidade, tecnico_id))
        conn.commit()

    return obter_tecnico(tecnico_id)
# exclui um técnico do banco de dados com base no ID fornecido
def excluir_tecnico(tecnico_id):
    with get_db_connection() as conn:
        conn.execute("DELETE FROM tecnicos WHERE id = ?", (tecnico_id,))
        conn.commit()
#========================================================================================================================================
# funçoes de dados da pagina catalogo
#========================================================================================================================================
def produtos():
    return [
        {"id": 1, 
        "name": "Produto A",
        "categoria": "carregador",
        "custos": 50.0,
        "preco": 100.0,
        "data_cadastro": "2023-03-01",
        "estoque": 10,
        "estoque_minimo": 5}
        ]
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
def servicos():
    return [
        {"id": 1, 
        "name": "Serviço A",
        "modelo_celular": "Celular A",
        "categoria": "Reparo de tela",
        "custos": 50.0,
        "preco": 100.0,
        "tempo_estimado": "2 horas",
        "observacao": "Garantia de 3 meses",
        "data_cadastro": "2023-05-01"}
        ]
#========================================================================================================================================
# funçoes de dados da pagina vendas
#========================================================================================================================================
def vendas():
    return [
        {"id": 1, 
        "cliente_id": 1,
        "produto_id": 1,
        "celular_id": 1,
        "servico_id": 1,
        "data_venda": "2023-06-01",
        "desconto": 10.0,
        "forma_pagamento": "cartão de crédito",
        "parcelamento": "3x",
        "observacao": "Venda realizada com sucesso",
        "garantia": "90 dias",
        "valor_total": 500.0}
        ]
#========================================================================================================================================
# funçoes de dados da pagina laboratorio/garantia
#========================================================================================================================================
def ordens_de_servico():
    return [
        {
            "id": 1,
            "cliente_id": 1,
            "tecnico_id": 1,
            "modelo_celular": "Celular A",
            "celular_cor": "Preto",
            "senha": "1234",
            "condicao_de_entrada": {
                "molhado?": False,
                "ligado?": True,
                "aberto?": False,
                "acessorios?": True
            },
            "checklist": {
                "wi-fi": True,
                "Bluetooth": True,
                "Sinal Rede": True,
                "Biometria": True,
                "Leitura Chip": True,
                "Tela / Touch": True,
                "Câm. Frontal": True,
                "Câm. Traseira": True,
                "Flash": True,
                "Sensor Prox.": True,
                "Conector Carga": True,
                "Microfone": True,
                "Auricular": True,
                "Vibrar": True,
                "Botões": True
            },
            "defeito_reclamado": "Tela quebrada",
            "servico_id": 1,
            "data_abertura": "2023-07-01",
            "data_fechamento": None,
            "status": "aberta",
            "observacao": "Ordem de serviço aberta",
            "garantia": "90 dias",
            "finalizada?": False
        }
    ]
def ordem_de_entrega():
    return [
        {
            "id": 1,
            "ordem_servico_id": 1,
            "imei": "1234567890",
            "tempo de garantia": "90 dias",
            "data_entrega": "2023-07-10",
            "data_fim_garantia": "data entrega + tempo de garantia",
            "observacao": "Ordem de serviço entregue ao cliente",
            "checklist_entrega": {
                "wi-fi": True,
                "Bluetooth": True,
                "Sinal Rede": True,
                "Biometria": True,
                "Leitura Chip": True,
                "Tela / Touch": True,
                "Câm. Frontal": True,
                "Câm. Traseira": True,
                "Flash": True,
                "Sensor Prox.": True,
                "Conector Carga": True,
                "Microfone": True,
                "Auricular": True,
                "Vibrar": True,
                "Botões": True
            },
            "laudo_tecnico": "Reparo realizado com sucesso, garantia de 90 dias",
            "termos de garantia": "Garantia cobre defeitos de fabricação, não cobre danos acidentais",
            "serviços prestasdos":[servicos()],
            "forma de pagamento": "cartão de crédito",
            "parcelamento:": "3x",
            "valor_total": 500.0
        }
    ]
def ordem_de_cancelamento():
    return [
        {
            "id": 1,
            "ordem_servico_id": 1,
            "data_cancelamento": "2023-07-05",
            "motivo_cancelamento": "Cliente desistiu do serviço",
            "observacao": "Ordem de serviço cancelada pelo cliente"
        }
    ]
