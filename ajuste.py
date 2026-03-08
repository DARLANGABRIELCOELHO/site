from datetime import datetime, date, timedelta
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
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def inicializar_estado():
    inicializar_banco_clientes()
    inicializar_banco_tecnicos()
    inicializar_banco_produtos()
    inicializar_banco_celulares()
    inicializar_banco_servicos()
    inicializar_banco_vendas()
    inicializar_banco_checklist_entrada()
    inicializar_banco_condicoes_entrada()
    inicializar_banco_ordem_servico()
    inicializar_banco_ordem_servico_servicos()
    inicializar_banco_ordem_entrega()
    inicializar_banco_ordem_cancelamento()


# ======================================================================
# CONDIÇÕES DE ENTRADA
# ======================================================================
CONDICAO_ENTRADA_ID = "id"
CONDICAO_ENTRADA_LIGA = "liga"
CONDICAO_ENTRADA_ACESSORIOS = "acessorios"
CONDICAO_ENTRADA_JA_ABERTO = "ja_aberto"
CONDICAO_ENTRADA_MOLHADO = "molhado"


def inicializar_banco_condicoes_entrada():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS condicoes_entrada (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                liga INTEGER DEFAULT 0,
                acessorios INTEGER DEFAULT 0,
                ja_aberto INTEGER DEFAULT 0,
                molhado INTEGER DEFAULT 0
            )
        """)
        conn.commit()


def inserir_condicoes_entrada(liga=False, acessorios=False, ja_aberto=False, molhado=False):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO condicoes_entrada (liga, acessorios, ja_aberto, molhado)
            VALUES (?, ?, ?, ?)
        """, (
            int(bool(liga)),
            int(bool(acessorios)),
            int(bool(ja_aberto)),
            int(bool(molhado))
        ))
        conn.commit()
        return cursor.lastrowid


def obter_condicoes_entrada(condicao_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM condicoes_entrada WHERE id = ?", (condicao_id,))
        row = cursor.fetchone()
    return dict(row) if row else None


# ======================================================================
# ORDEM DE SERVIÇO
# ======================================================================
ORDEM_DE_SERVICO_ID = "id"
ORDEM_DE_SERVICO_CHECKLIST_ID = "checklist_id"
ORDEM_DE_SERVICO_CLIENTE_ID = "cliente_id"
ORDEM_DE_SERVICO_MODELO = "modelo"
ORDEM_DE_SERVICO_TECNICO_ID = "tecnico_id"
ORDEM_DE_SERVICO_CONDICAO_ID = "condicao_id"
ORDEM_DE_SERVICO_DATA_CADASTRO = "data_cadastro"
ORDEM_DE_SERVICO_DATA_TERMINO = "data_termino"
ORDEM_DE_SERVICO_STATUS = "status"
ORDEM_DE_SERVICO_OBSERVACOES = "observacoes"
ORDEM_DE_SERVICO_SENHA = "senha"
ORDEM_DE_SERVICO_COR = "cor"
ORDEM_DE_SERVICO_IMEI = "imei"
ORDEM_DE_SERVICO_PRIORIDADE = "prioridade"
ORDEM_DE_SERVICO_RELATO = "relato"
ORDEM_DE_SERVICO_LAUDO = "laudo"


def inicializar_banco_ordem_servico():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ordem_servico (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                checklist_id INTEGER,
                cliente_id INTEGER NOT NULL,
                modelo TEXT NOT NULL,
                tecnico_id INTEGER,
                condicao_id INTEGER,
                data_cadastro TEXT NOT NULL,
                data_termino TEXT,
                status TEXT NOT NULL DEFAULT 'aberta',
                observacoes TEXT,
                senha TEXT,
                cor TEXT,
                imei TEXT,
                prioridade TEXT DEFAULT 'normal',
                relato TEXT,
                laudo TEXT,
                FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                FOREIGN KEY (tecnico_id) REFERENCES tecnicos(id),
                FOREIGN KEY (checklist_id) REFERENCES checklist_entrada(id),
                FOREIGN KEY (condicao_id) REFERENCES condicoes_entrada(id)
            )
        """)
        conn.commit()


def obter_ordem_servico(ordem_servico_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ordem_servico WHERE id = ?", (ordem_servico_id,))
        row = cursor.fetchone()
    return dict(row) if row else None


def pesquisar_ordem_servico(criterio, valor):
    colunas_validas = {
        ORDEM_DE_SERVICO_ID,
        ORDEM_DE_SERVICO_CLIENTE_ID,
        ORDEM_DE_SERVICO_MODELO,
        ORDEM_DE_SERVICO_TECNICO_ID,
        ORDEM_DE_SERVICO_STATUS,
        ORDEM_DE_SERVICO_IMEI,
        ORDEM_DE_SERVICO_PRIORIDADE,
    }

    if criterio not in colunas_validas:
        raise ValueError(f"Critério de pesquisa inválido: {criterio}")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = f"SELECT * FROM ordem_servico WHERE {criterio} = ?"
        cursor.execute(query, (valor,))
        return [dict(row) for row in cursor.fetchall()]


def excluir_ordem_servico(ordem_servico_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ordem_servico WHERE id = ?", (ordem_servico_id,))
        conn.commit()
        return cursor.rowcount > 0


# ======================================================================
# ORDEM DE SERVIÇO -> SERVIÇOS (LISTA DE IDS)
# ======================================================================
ORDEM_SERVICO_SERVICOS_ID = "id"
ORDEM_SERVICO_SERVICOS_ORDEM_ID = "ordem_servico_id"
ORDEM_SERVICO_SERVICOS_SERVICO_ID = "servico_id"
ORDEM_SERVICO_SERVICOS_NOME_SNAPSHOT = "nome_servico_snapshot"
ORDEM_SERVICO_SERVICOS_PRECO_SNAPSHOT = "preco_servico_snapshot"
ORDEM_SERVICO_SERVICOS_CUSTO_SNAPSHOT = "custo_servico_snapshot"


def inicializar_banco_ordem_servico_servicos():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ordem_servico_servicos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ordem_servico_id INTEGER NOT NULL,
                servico_id INTEGER NOT NULL,
                nome_servico_snapshot TEXT NOT NULL,
                preco_servico_snapshot REAL,
                custo_servico_snapshot REAL,
                FOREIGN KEY (ordem_servico_id) REFERENCES ordem_servico(id) ON DELETE CASCADE,
                FOREIGN KEY (servico_id) REFERENCES servicos(id)
            )
        """)
        conn.commit()


def obter_servicos_da_ordem(ordem_servico_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT * FROM ordem_servico_servicos
            WHERE ordem_servico_id = ?
            ORDER BY id
        """, (ordem_servico_id,))
        return [dict(row) for row in cursor.fetchall()]


def vincular_servicos_na_ordem(ordem_servico_id, servico_ids):
    """
    Recebe uma lista de IDs de serviço, ex: [1, 3, 7]
    """
    if not servico_ids:
        return

    with get_db_connection() as conn:
        cursor = conn.cursor()

        for servico_id in servico_ids:
            cursor.execute("""
                SELECT id, nome, preco, custos
                FROM servicos
                WHERE id = ?
            """, (servico_id,))
            servico = cursor.fetchone()

            if not servico:
                raise ValueError(f"Serviço não encontrado: id={servico_id}")

            cursor.execute("""
                INSERT INTO ordem_servico_servicos (
                    ordem_servico_id,
                    servico_id,
                    nome_servico_snapshot,
                    preco_servico_snapshot,
                    custo_servico_snapshot
                )
                VALUES (?, ?, ?, ?, ?)
            """, (
                ordem_servico_id,
                servico["id"],
                servico["nome"],
                servico["preco"],
                servico["custos"]
            ))

        conn.commit()


def registrar_ordem_servico(dados, servico_ids=None):
    """
    dados = dict com os campos da OS
    servico_ids = lista de ids de serviço, ex: [1, 2, 5]
    """
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO ordem_servico (
                checklist_id,
                cliente_id,
                modelo,
                tecnico_id,
                condicao_id,
                data_cadastro,
                data_termino,
                status,
                observacoes,
                senha,
                cor,
                imei,
                prioridade,
                relato,
                laudo
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            dados.get(ORDEM_DE_SERVICO_CHECKLIST_ID),
            dados.get(ORDEM_DE_SERVICO_CLIENTE_ID),
            dados.get(ORDEM_DE_SERVICO_MODELO),
            dados.get(ORDEM_DE_SERVICO_TECNICO_ID),
            dados.get(ORDEM_DE_SERVICO_CONDICAO_ID),
            dados.get(ORDEM_DE_SERVICO_DATA_CADASTRO, datetime.now().isoformat()),
            dados.get(ORDEM_DE_SERVICO_DATA_TERMINO),
            dados.get(ORDEM_DE_SERVICO_STATUS, "aberta"),
            dados.get(ORDEM_DE_SERVICO_OBSERVACOES),
            dados.get(ORDEM_DE_SERVICO_SENHA),
            dados.get(ORDEM_DE_SERVICO_COR),
            dados.get(ORDEM_DE_SERVICO_IMEI),
            dados.get(ORDEM_DE_SERVICO_PRIORIDADE, "normal"),
            dados.get(ORDEM_DE_SERVICO_RELATO),
            dados.get(ORDEM_DE_SERVICO_LAUDO)
        ))

        ordem_servico_id = cursor.lastrowid
        conn.commit()

    if servico_ids:
        vincular_servicos_na_ordem(ordem_servico_id, servico_ids)

    return ordem_servico_id


# ======================================================================
# BUSCA DE SERVIÇOS POR MODELO
# ======================================================================
def pesquisar_servicos_por_modelo(modelo):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT *
            FROM servicos
            WHERE modelo_celular LIKE ?
            ORDER BY nome
        """, (f"%{modelo}%",))
        return [dict(row) for row in cursor.fetchall()]


# ======================================================================
# ORDEM DE ENTREGA / FECHAMENTO DA OS
# ======================================================================
ORDEM_DE_ENTREGA_ID = "id"
ORDEM_DE_ENTREGA_ORDEM_SERVICO_ID = "ordem_servico_id"
ORDEM_DE_ENTREGA_CONDICAO = "condicao"
ORDEM_DE_ENTREGA_CHECKLIST_ID = "checklist_id"
ORDEM_DE_ENTREGA_CLIENTE_ID = "cliente_id"
ORDEM_DE_ENTREGA_TECNICO_ID = "tecnico_id"
ORDEM_DE_ENTREGA_DATA = "data"
ORDEM_DE_ENTREGA_OBSERVACOES = "observacoes"
ORDEM_DE_ENTREGA_LAUDO = "laudo"
ORDEM_DE_ENTREGA_DESCONTO = "desconto"
ORDEM_DE_ENTREGA_FORMA_PAGAMENTO = "forma_pagamento"
ORDEM_DE_ENTREGA_PARCELAMENTO = "parcelamento"
ORDEM_DE_ENTREGA_GARANTIA = "garantia"
ORDEM_DE_ENTREGA_DATA_FIM_GARANTIA = "data_fim_garantia"
ORDEM_DE_ENTREGA_VALOR_TOTAL = "valor_total"


def inicializar_banco_ordem_entrega():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ordem_entrega (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ordem_servico_id INTEGER NOT NULL UNIQUE,
                condicao TEXT,
                checklist_id INTEGER,
                cliente_id INTEGER NOT NULL,
                tecnico_id INTEGER,
                data TEXT NOT NULL,
                observacoes TEXT,
                laudo TEXT,
                desconto REAL DEFAULT 0,
                forma_pagamento TEXT,
                parcelamento TEXT,
                garantia TEXT,
                data_fim_garantia TEXT,
                valor_total REAL,
                FOREIGN KEY (ordem_servico_id) REFERENCES ordem_servico(id),
                FOREIGN KEY (cliente_id) REFERENCES clientes(id),
                FOREIGN KEY (tecnico_id) REFERENCES tecnicos(id),
                FOREIGN KEY (checklist_id) REFERENCES checklist_entrada(id)
            )
        """)
        conn.commit()


def obter_ordem_entrega(ordem_entrega_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ordem_entrega WHERE id = ?", (ordem_entrega_id,))
        row = cursor.fetchone()
    return dict(row) if row else None


def registrar_ordem_entrega(dados):
    """
    Fecha a OS e gera o documento de entrega.
    Também atualiza o status da ordem para 'entregue' e grava data_termino.
    """
    ordem_servico_id = dados.get(ORDEM_DE_ENTREGA_ORDEM_SERVICO_ID)
    if not ordem_servico_id:
        raise ValueError("ordem_servico_id é obrigatório para registrar a entrega.")

    garantia_texto = dados.get(ORDEM_DE_ENTREGA_GARANTIA)
    data_fim_garantia = dados.get(ORDEM_DE_ENTREGA_DATA_FIM_GARANTIA)

    if garantia_texto and not data_fim_garantia:
        # regra simples para "90 dias"
        texto = garantia_texto.lower().strip()
        if "90" in texto and "dia" in texto:
            data_fim_garantia = (date.today() + timedelta(days=90)).isoformat()

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO ordem_entrega (
                ordem_servico_id,
                condicao,
                checklist_id,
                cliente_id,
                tecnico_id,
                data,
                observacoes,
                laudo,
                desconto,
                forma_pagamento,
                parcelamento,
                garantia,
                data_fim_garantia,
                valor_total
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ordem_servico_id,
            dados.get(ORDEM_DE_ENTREGA_CONDICAO),
            dados.get(ORDEM_DE_ENTREGA_CHECKLIST_ID),
            dados.get(ORDEM_DE_ENTREGA_CLIENTE_ID),
            dados.get(ORDEM_DE_ENTREGA_TECNICO_ID),
            dados.get(ORDEM_DE_ENTREGA_DATA, datetime.now().isoformat()),
            dados.get(ORDEM_DE_ENTREGA_OBSERVACOES),
            dados.get(ORDEM_DE_ENTREGA_LAUDO),
            dados.get(ORDEM_DE_ENTREGA_DESCONTO, 0.0),
            dados.get(ORDEM_DE_ENTREGA_FORMA_PAGAMENTO),
            dados.get(ORDEM_DE_ENTREGA_PARCELAMENTO),
            garantia_texto,
            data_fim_garantia,
            dados.get(ORDEM_DE_ENTREGA_VALOR_TOTAL)
        ))

        ordem_entrega_id = cursor.lastrowid

        cursor.execute("""
            UPDATE ordem_servico
            SET status = ?, data_termino = ?, laudo = COALESCE(?, laudo)
            WHERE id = ?
        """, (
            "entregue",
            datetime.now().isoformat(),
            dados.get(ORDEM_DE_ENTREGA_LAUDO),
            ordem_servico_id
        ))

        conn.commit()

    return ordem_entrega_id


def pesquisar_ordem_entrega(criterio, valor):
    colunas_validas = {
        ORDEM_DE_ENTREGA_ID,
        ORDEM_DE_ENTREGA_ORDEM_SERVICO_ID,
        ORDEM_DE_ENTREGA_CLIENTE_ID,
        ORDEM_DE_ENTREGA_TECNICO_ID,
    }

    if criterio not in colunas_validas:
        raise ValueError(f"Critério de pesquisa inválido: {criterio}")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = f"SELECT * FROM ordem_entrega WHERE {criterio} = ?"
        cursor.execute(query, (valor,))
        return [dict(row) for row in cursor.fetchall()]


def excluir_ordem_entrega(ordem_entrega_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ordem_entrega WHERE id = ?", (ordem_entrega_id,))
        conn.commit()
        return cursor.rowcount > 0


# ======================================================================
# ORDEM DE CANCELAMENTO
# ======================================================================
ORDEM_DE_CANCELAMENTO_ID = "id"
ORDEM_DE_CANCELAMENTO_ORDEM_SERVICO_ID = "ordem_servico_id"
ORDEM_DE_CANCELAMENTO_MOTIVO = "motivo"
ORDEM_DE_CANCELAMENTO_OBSERVACAO = "observacao"


def inicializar_banco_ordem_cancelamento():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS ordem_cancelamento (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ordem_servico_id INTEGER NOT NULL UNIQUE,
                motivo TEXT NOT NULL,
                observacao TEXT,
                FOREIGN KEY (ordem_servico_id) REFERENCES ordem_servico(id)
            )
        """)
        conn.commit()


def obter_ordem_cancelamento(ordem_cancelamento_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM ordem_cancelamento WHERE id = ?", (ordem_cancelamento_id,))
        row = cursor.fetchone()
    return dict(row) if row else None


def registrar_ordem_cancelamento(dados):
    """
    Cancela a OS e registra o motivo.
    Também atualiza o status da ordem para 'cancelada'.
    """
    ordem_servico_id = dados.get(ORDEM_DE_CANCELAMENTO_ORDEM_SERVICO_ID)
    if not ordem_servico_id:
        raise ValueError("ordem_servico_id é obrigatório para cancelar a OS.")

    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO ordem_cancelamento (ordem_servico_id, motivo, observacao)
            VALUES (?, ?, ?)
        """, (
            ordem_servico_id,
            dados.get(ORDEM_DE_CANCELAMENTO_MOTIVO),
            dados.get(ORDEM_DE_CANCELAMENTO_OBSERVACAO)
        ))

        cancelamento_id = cursor.lastrowid

        cursor.execute("""
            UPDATE ordem_servico
            SET status = ?, data_termino = ?
            WHERE id = ?
        """, (
            "cancelada",
            datetime.now().isoformat(),
            ordem_servico_id
        ))

        conn.commit()

    return cancelamento_id


def pesquisar_ordem_cancelamento(criterio, valor):
    colunas_validas = {
        ORDEM_DE_CANCELAMENTO_ID,
        ORDEM_DE_CANCELAMENTO_ORDEM_SERVICO_ID
    }

    if criterio not in colunas_validas:
        raise ValueError(f"Critério de pesquisa inválido: {criterio}")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = f"SELECT * FROM ordem_cancelamento WHERE {criterio} = ?"
        cursor.execute(query, (valor,))
        return [dict(row) for row in cursor.fetchall()]


def excluir_ordem_cancelamento(ordem_cancelamento_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM ordem_cancelamento WHERE id = ?", (ordem_cancelamento_id,))
        conn.commit()
        return cursor.rowcount > 0