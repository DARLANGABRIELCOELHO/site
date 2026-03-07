
#========================================================================================================================================
# importações   
#========================================================================================================================================
from datetime import datetime
import sqlite3
#========================================================================================================================================
# Configuração do banco
#========================================================================================================================================
DB_PATH = "ifix.db"
# INICIALIZA O ESTADO DO BANCO DE DADOS
def inicializar_estado():
    """Garante que o banco de dados esteja pronto."""
    inicializar_banco()
# CONECTA AO BANCO DE DADOS SQLite
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn
#========================================================================================================================================
# funcoes de dados da pagina clientes
#========================================================================================================================================
# Chaves padronizadas para os campos do cliente (usadas como referência)
CAMPO_ID = "id"
CAMPO_NOME = "nome"
CAMPO_TELEFONE = "telefone"
CAMPO_DOCUMENTO = "documento"
CAMPO_ENDERECO = "endereco"
CAMPO_OBSERVACOES = "observacoes"
CAMPO_DATA_CADASTRO = "data_cadastro"
CAMPO_ORDENS_SERVICO = "ordens_servico"  # Não utilizado diretamente no banco

# INICIALIZA O BANCO DE DADOS TABELA CLIENTE
def inicializar_banco():
    """Cria a tabela e insere um exemplo se estiver vazia."""
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
            """, ("Cliente A", "15555-1234", "123.456.789-00", "Rua A, 123", "Cliente VIP", "01/01/2023"))
            conn.commit()
# RETORNA O PRÓXIMO ID CLIENTE DISPONÍVEL
def proximo_id_cliente():
    """Retorna o próximo ID disponível (caso necessário)."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM clientes")
        max_id = cursor.fetchone()[0]
        return (max_id or 0) + 1
# RETORNA UM CLIENTE PELO ID
def obter_cliente(cliente_id):
    """Retorna um cliente pelo ID."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes WHERE id = ?", (cliente_id,))
        row = cursor.fetchone()
    return dict(row) if row else None
# INSERE UM NOVO CLIENTE
def inserir_cliente(nome, telefone, documento, endereco, observacoes):
    """Insere um novo cliente no banco de dados."""
    data_cadastro = datetime.now().strftime("%d/%m/%Y")
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO clientes (nome, telefone, documento, endereco, observacoes, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (nome, telefone, documento, endereco, observacoes, data_cadastro))
        conn.commit()
        return cursor.lastrowid
# ATUALIZA AS INFORMAÇÕES DE UM CLIENTE EXISTENTE
def atualizar_cliente(cliente_id, nome, telefone, documento, endereco, observacoes):
    """Atualiza as informações de um cliente existente."""
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE clientes
            SET nome = ?, telefone = ?, documento = ?, endereco = ?, observacoes = ?
            WHERE id = ?
        """, (nome, telefone, documento, endereco, observacoes, cliente_id))
        conn.commit()
# APAGAR CLIENTE EXISTENTE 
#========================================================================================================================================
# funçoes de dados da pagina tecnicos
#========================================================================================================================================
def tecnicos():
    return [
        {"id": 1, 
        "name": "Técnico A",
        "numero": "15555-5678",
        "especialidade": "android",
        "data_cadastro": "2023-02-01",
        "ordem_servico": []},
        ]
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
