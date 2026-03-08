from datetime import date
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
    inicializar_banco_vendas()
#=====================================================================
# ordem de serviço
#=====================================================================
# Constantes para os campos da tabela ordem_servico
ORDEM_SERVICO_ID = "id"
ORDEM_SERVICO_TECNICO_ID = "tecnico_id"
ORDEM_SERVICO_STATUS = "status"
ORDEM_SERVICO_CLIENTE_ID = "cliente_id"
ORDEM_SERVICO_IMEI = "imei"
ORDEM_SERVICO_SENHA = "senha"
ORDEM_SERVICO_CONDICAO_ENTRADA = "condicao_entrada"
ORDEM_SERVICO_RELATO_CLIENTE = "relato_cliente"
ORDEM_SERVICO_OBSERVACAO_ENTRADA = "observacao_entrada"
ORDEM_SERVICO_CHECKLIST_ENTRADA = "checklist_entrada"
ORDEM_SERVICO_OBSERVACAO_SAIDA = "observacao_saida"
ORDEM_SERVICO_CHECKLIST_SAIDA = "checklist_saida"
ORDEM_SERVICO_COR = "cor"
ORDEM_SERVICO_MARCA = "marca"
ORDEM_SERVICO_MODELO = "modelo"
ORDEM_SERVICO_SERVICO_ID = "servico_id"
ORDEM_SERVICO_DATA_ENTRADA = "data_entrada"
ORDEM_SERVICO_DATA_SAIDA = "data_saida"
ORDEM_SERVICO_DESCONTO = "desconto"
ORDEM_SERVICO_FORMA_PAGAMENTO = "forma_pagamento"
ORDEM_SERVICO_PARCELAMENTO = "parcelamento"
ORDEM_SERVICO_LAUDO_TECNICO = "laudo_tecnico"
ORDEM_SERVICO_GARANTIA = "garantia"
ORDEM_SERVICO_VALOR_TOTAL = "valor_total"
# Função para criar a tabela de vendas e inserir um registro de teste
def inicializar_banco_ordem_servico():
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ordem_servico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tecnico_id INTEGER,
                status TEXT,
                cliente_id INTEGER,
                imei TEXT,
                senha TEXT,
                condicao_entrada TEXT,
                relato_cliente TEXT,
                observacao_entrada TEXT,
                checklist_entrada TEXT,
                observacao_saida TEXT,
                checklist_saida TEXT,
                cor TEXT,
                marca TEXT,
                modelo TEXT,
                servico_id INTEGER,
                data_entrada TEXT,
                data_saida TEXT,
                desconto REAL,
                forma_pagamento TEXT,
                parcelamento TEXT,
                observacao TEXT,
                garantia TEXT,
                valor_total REAL
            )
        """)

        cursor.execute("SELECT COUNT(*) FROM ordem_servico")
        total_ordem_servico = cursor.fetchone()[0]

        if total_ordem_servico == 0:
            cursor.execute("""
                INSERT INTO ordem_servico (
                    tecnico_id, status, cliente_id, imei, senha, condicao_entrada, 
                    relato_cliente, observacao_entrada, checklist_entrada, observacao_saida, 
                    checklist_saida, cor, marca, modelo, servico_id, data_entrada, 
                    data_saida, desconto, forma_pagamento, parcelamento, laudo_tecnico, 
                    garantia, valor_total
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                1, 1, 1, 1,
                "2023-06-01", 10.0, "cartão de crédito",
                "3x", "Venda realizada com sucesso", "90 dias", 500.0
            ))

        conn.commit()
# Função para obter o próximo ID disponível para ordem de serviço
def obter_proximo_id_ordem_servico():   
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM ordem_servico")
        resultado = cursor.fetchone()
        return resultado[0] + 1 if resultado[0] is not None else 1
# Função para registrar uma nova ordem de serviço
def registrar_ordem_servico(tecnico_id, status, cliente_id, imei, senha, condicao_entrada, 
                    relato_cliente, observacao_entrada, checklist_entrada, observacao_saida, 
                    checklist_saida, cor, marca, modelo, servico_id, data_entrada, 
                    data_saida, desconto, forma_pagamento, parcelamento, laudo_tecnico, 
                    garantia, valor_total):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        data_entrada = date.today().isoformat()

        if servico_id is not None:
            cursor.execute("SELECT estoque FROM servicos WHERE id = ?", (servico_id,))
            servico = cursor.fetchone()

            if not servico:
                raise ValueError("Serviço não encontrado.")

            if servico["estoque"] <= 0:
                raise ValueError("Estoque insuficiente para concluir a venda.")

        cursor.execute("""
            INSERT INTO ordem_servico (
                tecnico_id, status, cliente_id, imei, senha, condicao_entrada, 
                relato_cliente, observacao_entrada, checklist_entrada, observacao_saida, 
                checklist_saida, cor, marca, modelo, servico_id, data_entrada, 
                data_saida, desconto, forma_pagamento,
                parcelamento, observacao, garantia, valor_total
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            tecnico_id, status, cliente_id, imei, senha, condicao_entrada, 
            relato_cliente, observacao_entrada, checklist_entrada, observacao_saida, 
            checklist_saida, cor, marca, modelo, servico_id,
            data_entrada, data_saida, desconto, forma_pagamento,
            parcelamento, observacao, garantia, valor_total
        ))

        ordem_servico_id = cursor.lastrowid

        if servico_id is not None:
            cursor.execute(
                "UPDATE servicos SET estoque = estoque - 1 WHERE id = ?",
                (servico_id,)
            )

        conn.commit()
        return ordem_servico_id
# função atualizar ordem de serviço
def atualizar_ordem_servico(ordem_servico_id, tecnico_id, status, cliente_id, imei, senha, condicao_entrada, 
                    relato_cliente, observacao_entrada, checklist_entrada, observacao_saida, 
                    checklist_saida, cor, marca, modelo, servico_id, data_entrada, 
                    data_saida, desconto, forma_pagamento,
                    parcelamento, observacao, garantia, valor_total):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE ordem_servico SET
                tecnico_id = ?,
                status = ?,
                cliente_id = ?,
                imei = ?,
                senha = ?,
                condicao_entrada = ?,
                relato_cliente = ?,
                observacao_entrada = ?,
                checklist_entrada = ?,
                observacao_saida = ?,
                checklist_saida = ?,
                cor = ?,
                marca = ?,
                modelo = ?,
                servico_id = ?,
                data_entrada = ?,
                data_saida = ?,
                desconto = ?,
                forma_pagamento = ?,
                parcelamento = ?,
                observacao = ?,
                garantia = ?,
                valor_total = ?
            WHERE id = ?
        """, (
            tecnico_id, status, cliente_id, imei, senha, condicao_entrada, 
            relato_cliente, observacao_entrada, checklist_entrada, observacao_saida, 
            checklist_saida, cor, marca, modelo, servico_id,
            data_entrada, data_saida, desconto, forma_pagamento,
            parcelamento, observacao, garantia, valor_total, ordem_servico_id
        ))
        conn.commit()   
# Função para pesquisar ordem de serviço com base em um critério e valor específico
def pesquisar_ordem_servico(criterio, valor):
    campos_permitidos = {
        "cliente_id",
        "servico_id",
        "forma_pagamento",
        "data_entrada",
        "data_saida",
        "desconto",
        "parcelamento",
        "observacao",
        "garantia",
        "valor_total"
    }

    if criterio not in campos_permitidos:
        raise ValueError("Critério de pesquisa inválido.")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = f"SELECT * FROM ordem_servico WHERE {criterio} = ?"
        cursor.execute(query, (valor,))
        resultados = cursor.fetchall()

    return [dict(row) for row in resultados]
# Função para excluir uma ordem de serviço
def excluir_ordem_servico(ordem_servico_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT servico_id FROM ordem_servico WHERE id = ?", (ordem_servico_id,))
        resultado = cursor.fetchone()

        if resultado:
            servico_id = resultado["servico_id"]

            cursor.execute("DELETE FROM ordem_servico WHERE id = ?", (ordem_servico_id,))

            if servico_id is not None:
                cursor.execute(
                    "UPDATE servicos SET estoque = estoque + 1 WHERE id = ?",
                    (servico_id,)
                )

            conn.commit()