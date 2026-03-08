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
# lista garantias ativas (data_fim_garantia >= hoje) com dados do cliente e OS
def listar_garantias_ativas():
    hoje = date.today().isoformat()
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT oe.id, oe.ordem_servico_id, oe.garantia, oe.data_fim_garantia,
                   oe.valor_total, oe.forma_pagamento, oe.data,
                   c.nome AS cliente_nome, c.telefone AS cliente_telefone,
                   os.modelo, os.status AS os_status
            FROM ordem_entrega oe
            JOIN clientes c ON oe.cliente_id = c.id
            JOIN ordem_servico os ON oe.ordem_servico_id = os.id
            WHERE oe.data_fim_garantia IS NOT NULL
              AND oe.data_fim_garantia >= ?
            ORDER BY oe.data_fim_garantia ASC
        """, (hoje,))
        return [dict(row) for row in cursor.fetchall()]

# calcula todos os KPIs do dashboard para um período (data_inicio como string ISO ou None)
def calcular_kpis(data_inicio: str = None):
    with get_db_connection() as conn:
        c = conn.cursor()

        filtro_os  = "AND os.data_cadastro >= ?"  if data_inicio else ""
        filtro_oe  = "AND oe.data >= ?"           if data_inicio else ""
        args_os    = (data_inicio,)                if data_inicio else ()
        args_oe    = (data_inicio,)                if data_inicio else ()

        # Faturamento e OS entregues
        c.execute(f"""
            SELECT COUNT(*) AS entregues, COALESCE(SUM(oe.valor_total),0) AS faturamento
            FROM ordem_entrega oe WHERE 1=1 {filtro_oe}
        """, args_oe)
        r = dict(c.fetchone())
        faturamento  = r["faturamento"]
        os_entregues = r["entregues"]

        # Gastos (custo dos serviços nas OS do período)
        c.execute(f"""
            SELECT COALESCE(SUM(oss.custo_servico_snapshot),0) AS gastos
            FROM ordem_servico_servicos oss
            JOIN ordem_servico os ON oss.ordem_servico_id = os.id
            WHERE 1=1 {filtro_os}
        """, args_os)
        gastos = dict(c.fetchone())["gastos"]

        # OS Total e Pendentes
        c.execute(f"""
            SELECT COUNT(*) AS total,
                   COUNT(CASE WHEN os.status IN ('aberta','pendente') THEN 1 END) AS pendentes
            FROM ordem_servico os WHERE 1=1 {filtro_os}
        """, args_os)
        r = dict(c.fetchone())
        os_total    = r["total"]
        os_pendentes= r["pendentes"]

        # Cancelamentos
        c.execute(f"""
            SELECT COUNT(*) AS cancelados
            FROM ordem_cancelamento oc
            JOIN ordem_servico os ON oc.ordem_servico_id = os.id
            WHERE 1=1 {filtro_os}
        """, args_os)
        os_cancelados = dict(c.fetchone())["cancelados"]

        # OS com garantia ativa (retornos de garantia) — aproximação por OS entregues com garantia no período
        c.execute(f"""
            SELECT COUNT(*) AS com_garantia
            FROM ordem_entrega oe
            WHERE oe.garantia IS NOT NULL AND oe.garantia != '' {filtro_oe}
        """, args_oe)
        os_com_garantia = dict(c.fetchone())["com_garantia"]

        # Custo e potencial do estoque (produtos)
        c.execute("""
            SELECT COALESCE(SUM(custos * estoque),0)  AS custo_estoque,
                   COALESCE(SUM(preco  * estoque),0)  AS potencial_estoque
            FROM produtos
        """)
        r = dict(c.fetchone())
        custo_estoque     = r["custo_estoque"]
        potencial_estoque = r["potencial_estoque"]

    lucro        = faturamento - gastos
    ticket_medio = faturamento / os_entregues if os_entregues > 0 else 0
    taxa_garantia  = (os_com_garantia / os_entregues * 100) if os_entregues > 0 else 0
    taxa_cancelam  = (os_cancelados   / os_total     * 100) if os_total     > 0 else 0
    roi_estoque    = (lucro / custo_estoque * 100) if custo_estoque > 0 else 0

    def brl(v): return f"R$ {v:,.2f}".replace(",","X").replace(".",",").replace("X",".")

    return {
        "taxa_garantia":      f"{taxa_garantia:.1f}%",
        "os_total":           str(os_total),
        "faturamento":        brl(faturamento),
        "gastos":             brl(gastos),
        "custo_estoque":      brl(custo_estoque),
        "lucro_liquido":      brl(lucro),
        "ticket_medio":       brl(ticket_medio),
        "os_entregues":       str(os_entregues),
        "os_pendentes":       str(os_pendentes),
        "taxa_cancelamento":  f"{taxa_cancelam:.1f}%",
        "roi_estoque":        f"{roi_estoque:.1f}%",
        "potencial_estoque":  brl(potencial_estoque),
    }

# lista todos os clientes cadastrados no banco de dados
def listar_clientes():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clientes ORDER BY nome")
        return [dict(row) for row in cursor.fetchall()]
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
# lista todos os técnicos com contagem de OS por status
def listar_tecnicos():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                t.id, t.nome, t.telefone, t.especialidade, t.data_cadastro,
                COUNT(CASE WHEN os.status IN ('aberta','em_andamento') THEN 1 END) AS os_andamento,
                COUNT(CASE WHEN os.status = 'entregue' THEN 1 END)                AS os_concluidas,
                COUNT(CASE WHEN os.status = 'pendente' THEN 1 END)                AS os_pendentes,
                COUNT(os.id)                                                       AS os_total
            FROM tecnicos t
            LEFT JOIN ordem_servico os ON os.tecnico_id = t.id
            GROUP BY t.id
            ORDER BY t.nome
        """)
        return [dict(row) for row in cursor.fetchall()]

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
# -----------------------------------------------------------------------------
# PRODUTOS
# ---------------------------------------------------------------------
# chave personalizada para o banco de dados produtos
# PRODUTOS
PRODUTO_ID = "id"
PRODUTO_NOME = "nome"
PRODUTO_CATEGORIA = "categoria"
PRODUTO_CUSTOS = "custos"
PRODUTO_PRECO = "preco"
PRODUTO_DATA_CADASTRO = "data_cadastro"
PRODUTO_ESTOQUE = "estoque"
PRODUTO_ESTOQUE_MINIMO = "estoque_minimo"
# inicializa o banco de dados para a tabela de produtos, criando a tabela se ela não existir e inserindo um produto de exemplo se a tabela estiver vazia
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

        cursor = conn.execute("SELECT COUNT(*) FROM produtos")
        count = cursor.fetchone()[0]

        if count == 0:
            conn.execute(f"""
                INSERT INTO produtos (
                    {PRODUTO_NOME}, {PRODUTO_CATEGORIA}, {PRODUTO_CUSTOS},
                    {PRODUTO_PRECO}, {PRODUTO_DATA_CADASTRO},
                    {PRODUTO_ESTOQUE}, {PRODUTO_ESTOQUE_MINIMO}
                ) VALUES (?, ?, ?, ?, ?, ?, ?)
            """, ("Produto A", "carregador", 50.0, 100.0, "2023-03-01", 10, 5))

        conn.commit()
# obtém um produto do banco de dados com base no ID fornecido
def obter_produto(produto_id):
    with get_db_connection() as conn:
        row = conn.execute(f"""
            SELECT * FROM produtos WHERE {PRODUTO_ID} = ?
        """, (produto_id,)).fetchone()
    return dict(row) if row else None
# insere um novo produto no banco de dados
def inserir_produto(nome, categoria, custos, preco, data_cadastro, estoque, estoque_minimo):
    with get_db_connection() as conn:
        cursor = conn.execute(f"""
            INSERT INTO produtos (
                {PRODUTO_NOME}, {PRODUTO_CATEGORIA}, {PRODUTO_CUSTOS},
                {PRODUTO_PRECO}, {PRODUTO_DATA_CADASTRO},
                {PRODUTO_ESTOQUE}, {PRODUTO_ESTOQUE_MINIMO}
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (nome, categoria, custos, preco, data_cadastro, estoque, estoque_minimo))
        conn.commit()
        novo_id = cursor.lastrowid
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
# lista todos os produtos ordenados por nome
def listar_produtos(filtro: str = ""):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if filtro:
            cursor.execute("SELECT * FROM produtos WHERE nome LIKE ? OR categoria LIKE ? ORDER BY nome",
                           (f"%{filtro}%", f"%{filtro}%"))
        else:
            cursor.execute("SELECT * FROM produtos ORDER BY nome")
        return [dict(row) for row in cursor.fetchall()]

# exclui um produto do banco de dados com base no ID fornecido
def excluir_produto(produto_id):
    with get_db_connection() as conn:
        conn.execute(f"DELETE FROM produtos WHERE {PRODUTO_ID} = ?", (produto_id,))
        conn.commit()
#-----------------------------------------------------------------------------
# CELULARES
#-----------------------------------------------------------------------------
# chave personalizada para o banco de dados celulares
CELULAR_ID = "id"
CELULAR_MODELO = "modelo"
CELULAR_MARCA = "marca"
CELULAR_COR = "cor"
CELULAR_IMEI = "imei"
CELULAR_DATA_CADASTRO = "data_cadastro"
CELULAR_CUSTO_AQUISICAO = "custos_de_aquisicao"
CELULAR_CUSTO_REPARO = "custos_de_reparo"
CELULAR_PRECO = "preco"
CELULAR_CONDICAO = "condicao"
CELULAR_FOTOS = "fotos"
CELULAR_OBSERVACAO = "observacao"
# inicializa o banco de dados para celulares, criando a tabela e inserindo um registro de exemplo
CELULAR_ID = "id"
CELULAR_MODELO = "modelo"
CELULAR_MARCA = "marca"
CELULAR_COR = "cor"
CELULAR_IMEI = "imei"
CELULAR_DATA_CADASTRO = "data_cadastro"
CELULAR_CUSTO_AQUISICAO = "custos_de_aquisicao"
CELULAR_CUSTO_REPARO = "custos_de_reparo"
CELULAR_PRECO = "preco"
CELULAR_CONDICAO = "condicao"
CELULAR_FOTOS = "fotos"
CELULAR_OBSERVACAO = "observacao"
# inicializa o banco de dados para celulares, criando a tabela e inserindo um registro de exemplo
def inicializar_banco_celulares():
    with get_db_connection() as conn:
        conn.execute(f"""
            CREATE TABLE IF NOT EXISTS celulares (
                {CELULAR_ID} INTEGER PRIMARY KEY AUTOINCREMENT,
                {CELULAR_MODELO} TEXT NOT NULL,
                {CELULAR_MARCA} TEXT NOT NULL,
                {CELULAR_COR} TEXT NOT NULL,
                {CELULAR_IMEI} TEXT NOT NULL UNIQUE,
                {CELULAR_DATA_CADASTRO} TEXT NOT NULL,
                {CELULAR_CUSTO_AQUISICAO} REAL NOT NULL,
                {CELULAR_CUSTO_REPARO} REAL NOT NULL,
                {CELULAR_PRECO} REAL NOT NULL,
                {CELULAR_CONDICAO} TEXT NOT NULL,
                {CELULAR_FOTOS} TEXT NOT NULL,
                {CELULAR_OBSERVACAO} TEXT NOT NULL
            )
        """)

        cursor = conn.execute("SELECT COUNT(*) FROM celulares")
        total = cursor.fetchone()[0]

        if total == 0:
            conn.execute(f"""
                INSERT INTO celulares (
                    {CELULAR_MODELO}, {CELULAR_MARCA}, {CELULAR_COR}, {CELULAR_IMEI},
                    {CELULAR_DATA_CADASTRO}, {CELULAR_CUSTO_AQUISICAO},
                    {CELULAR_CUSTO_REPARO}, {CELULAR_PRECO},
                    {CELULAR_CONDICAO}, {CELULAR_FOTOS}, {CELULAR_OBSERVACAO}
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                "Celular A",
                "Marca A",
                "Preto",
                "1234567890",
                "2023-04-01",
                200.0,
                50.0,
                400.0,
                "bom",
                "foto1.jpg,foto2.jpg",
                "Celular em bom estado, com pequenas marcas de uso"
            ))

        conn.commit()

# obtem um celular pelo ID, retornando um dicionário com os dados ou None se não encontrado
def obter_celular(celular_id):
    with get_db_connection() as conn:
        row = conn.execute(
            f"SELECT * FROM celulares WHERE {CELULAR_ID} = ?",
            (celular_id,)
        ).fetchone()
    return dict(row) if row else None
# insere um novo celular no banco de dados, retornando o registro criado com o ID gerado
def inserir_celular(modelo, marca, cor, imei, data_cadastro, custos_de_aquisicao, custos_de_reparo, preco, condicao, fotos, observacao):
    with get_db_connection() as conn:
        cursor = conn.execute(f"""
            INSERT INTO celulares (
                {CELULAR_MODELO}, {CELULAR_MARCA}, {CELULAR_COR}, {CELULAR_IMEI},
                {CELULAR_DATA_CADASTRO}, {CELULAR_CUSTO_AQUISICAO},
                {CELULAR_CUSTO_REPARO}, {CELULAR_PRECO}, {CELULAR_CONDICAO},
                {CELULAR_FOTOS}, {CELULAR_OBSERVACAO}
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            modelo, marca, cor, imei, data_cadastro,
            custos_de_aquisicao, custos_de_reparo, preco,
            condicao, ",".join(fotos), observacao
        ))
        conn.commit()
        novo_id = cursor.lastrowid
    return obter_celular(novo_id)
# atualiza um celular existente pelo ID, retornando o registro atualizado ou None se não encontrado
def atualizar_celular(celular_id, modelo, marca, cor, imei, data_cadastro, custos_de_aquisicao, custos_de_reparo, preco, condicao, fotos, observacao):
    with get_db_connection() as conn:
        conn.execute(f"""
            UPDATE celulares SET
                {CELULAR_MODELO} = ?, {CELULAR_MARCA} = ?, {CELULAR_COR} = ?, {CELULAR_IMEI} = ?,
                {CELULAR_DATA_CADASTRO} = ?, {CELULAR_CUSTO_AQUISICAO} = ?,
                {CELULAR_CUSTO_REPARO} = ?, {CELULAR_PRECO} = ?, {CELULAR_CONDICAO} = ?, {CELULAR_FOTOS} = ?, {CELULAR_OBSERVACAO} = ?
            WHERE {CELULAR_ID} = ?
        """, (
            modelo, marca, cor, imei, data_cadastro,
            custos_de_aquisicao, custos_de_reparo, preco,
            condicao, ",".join(fotos), observacao, celular_id
        ))
        conn.commit()
    return obter_celular(celular_id)
# exclui um celular pelo ID, retornando True se excluído ou False se não encontrado
def excluir_celular(celular_id):
    with get_db_connection() as conn:
        conn.execute(f"DELETE FROM celulares WHERE {CELULAR_ID} = ?", (celular_id,))
        conn.commit()

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
# lista todos os serviços com filtro opcional por nome ou categoria
def listar_servicos(filtro: str = ""):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        if filtro:
            cursor.execute("SELECT * FROM servicos WHERE nome LIKE ? OR categoria LIKE ? ORDER BY nome",
                           (f"%{filtro}%", f"%{filtro}%"))
        else:
            cursor.execute("SELECT * FROM servicos ORDER BY nome")
        return [dict(row) for row in cursor.fetchall()]

# FUNÇÃO PARA OBTER O PROXIMO ID DISPONÍVEL PARA SERVIÇOS
def obter_servicos():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM servicos")
        resultados = cursor.fetchall()
    return [dict(row) for row in resultados]
# obtém um serviço pelo ID, retornando um dicionário com os dados ou None se não encontrado
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
def pesquisar_servicos(modelo_celular="", categoria=""):
    with get_db_connection() as conn:
        cursor = conn.cursor()

        query = "SELECT * FROM servicos WHERE 1=1"
        parametros = []

        if modelo_celular.strip():
            query += " AND modelo_celular LIKE ?"
            parametros.append(f"%{modelo_celular}%")

        if categoria.strip():
            query += " AND categoria LIKE ?"
            parametros.append(f"%{categoria}%")

        cursor.execute(query, parametros)
        resultados = cursor.fetchall()

    return [dict(row) for row in resultados]
# obtém modelos distintos para preenchimento automático
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
#========================================================================================================================================
# funçoes de dados da pagina vendas
#========================================================================================================================================
# Constantes para os campos da tabela vendas
VENDAS_ID = "id"
VENDAS_CLIENTE_ID = "cliente_id"
VENDAS_PRODUTO_ID = "produto_id"
VENDAS_CELULAR_ID = "celular_id"
VENDAS_SERVICO_ID = "servico_id"
VENDAS_DATA_VENDA = "data_venda"
VENDAS_DESCONTO = "desconto"
VENDAS_FORMA_PAGAMENTO = "forma_pagamento"
VENDAS_PARCELAMENTO = "parcelamento"
VENDAS_OBSERVACAO = "observacao"
VENDAS_GARANTIA = "garantia"
VENDAS_VALOR_TOTAL = "valor_total"
# Função para criar a tabela de vendas e inserir um registro de teste
def inicializar_banco_vendas():
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vendas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                cliente_id INTEGER,
                produto_id INTEGER,
                celular_id INTEGER,
                servico_id INTEGER,
                data_venda TEXT,
                desconto REAL,
                forma_pagamento TEXT,
                parcelamento TEXT,
                observacao TEXT,
                garantia TEXT,
                valor_total REAL
            )
        """)

        cursor.execute("SELECT COUNT(*) FROM vendas")
        total_vendas = cursor.fetchone()[0]

        if total_vendas == 0:
            cursor.execute("""
                INSERT INTO vendas (
                    cliente_id, produto_id, celular_id, servico_id,
                    data_venda, desconto, forma_pagamento,
                    parcelamento, observacao, garantia, valor_total
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                1, 1, 1, 1,
                "2023-06-01", 10.0, "cartão de crédito",
                "3x", "Venda realizada com sucesso", "90 dias", 500.0
            ))

        conn.commit()
# Função para obter o próximo ID disponível para vendas
def obter_proximo_id_vendas():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(id) FROM vendas")
        resultado = cursor.fetchone()
        return resultado[0] + 1 if resultado[0] is not None else 1
# Função para registrar uma nova venda, atualizando o estoque do produto se aplicável
def registrar_venda(cliente_id, produto_id, celular_id, servico_id, desconto,
                    forma_pagamento, parcelamento, observacao, garantia, valor_total):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        data_venda = date.today().isoformat()

        if produto_id is not None:
            cursor.execute("SELECT estoque FROM produtos WHERE id = ?", (produto_id,))
            produto = cursor.fetchone()

            if not produto:
                raise ValueError("Produto não encontrado.")

            if produto["estoque"] <= 0:
                raise ValueError("Estoque insuficiente para concluir a venda.")

        cursor.execute("""
            INSERT INTO vendas (
                cliente_id, produto_id, celular_id, servico_id,
                data_venda, desconto, forma_pagamento,
                parcelamento, observacao, garantia, valor_total
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cliente_id, produto_id, celular_id, servico_id,
            data_venda, desconto, forma_pagamento,
            parcelamento, observacao, garantia, valor_total
        ))

        venda_id = cursor.lastrowid

        if produto_id is not None:
            cursor.execute(
                "UPDATE produtos SET estoque = estoque - 1 WHERE id = ?",
                (produto_id,)
            )

        conn.commit()
        return venda_id
# Função para pesquisar vendas com base em um critério e valor específico
def pesquisar_vendas(criterio, valor):
    campos_permitidos = {
        "cliente_id",
        "produto_id",
        "celular_id",
        "servico_id",
        "forma_pagamento",
        "data_venda"
    }

    if criterio not in campos_permitidos:
        raise ValueError("Critério de pesquisa inválido.")

    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = f"SELECT * FROM vendas WHERE {criterio} = ?"
        cursor.execute(query, (valor,))
        resultados = cursor.fetchall()

    return [dict(row) for row in resultados]
# Função para excluir uma venda, restaurando o estoque do produto se aplicável
def excluir_venda(venda_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()

        cursor.execute("SELECT produto_id FROM vendas WHERE id = ?", (venda_id,))
        resultado = cursor.fetchone()

        if resultado:
            produto_id = resultado["produto_id"]

            cursor.execute("DELETE FROM vendas WHERE id = ?", (venda_id,))

            if produto_id is not None:
                cursor.execute(
                    "UPDATE produtos SET estoque = estoque + 1 WHERE id = ?",
                    (produto_id,)
                )

            conn.commit()
#========================================================================================================================================
# funçoes de dados da pagina laboratorio/garantia
#========================================================================================================================================
# =====================================================================
# CHECKLIST DE ENTRADA
# =====================================================================
# Constantes para os campos do checklist de entrada
CHECKLIST_ENTRADA_ID = "id"
CHECKLIST_COL_WIFI = "wifi"
CHECKLIST_COL_BLUETOOTH = "bluetooth"
CHECKLIST_COL_SINAL = "sinal"
CHECKLIST_COL_BIOMETRIA = "biometria"
CHECKLIST_COL_CHIP_SIM = "chip_sim"
CHECKLIST_COL_TELA = "tela"
CHECKLIST_COL_TOUCH = "touch"
CHECKLIST_COL_CAMERA_FRONTAL = "camera_frontal"
CHECKLIST_COL_CAMERA_TRASEIRA = "camera_traseira"
CHECKLIST_COL_FLASH = "flash"
CHECKLIST_COL_SENSOR_PROX = "sensor_prox"
CHECKLIST_COL_CARREGAMENTO = "carregamento"
CHECKLIST_COL_MICROFONE = "microfone"
CHECKLIST_COL_ALTO_FALANTE = "alto_falante"
CHECKLIST_COL_AURICULAR = "auricular"
CHECKLIST_COL_VIBRACAO = "vibracao"
CHECKLIST_COL_BOTOES = "botoes"
# Inicializa o banco de dados para checklist de entrada
def inicializar_banco_checklist_entrada():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS checklist_entrada (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                ordem_servico_id INTEGER,
                wifi TEXT,
                bluetooth TEXT,
                sinal TEXT,
                biometria TEXT,
                chip_sim TEXT,
                tela TEXT,
                touch TEXT,
                camera_frontal TEXT,
                camera_traseira TEXT,
                flash TEXT,
                sensor_prox TEXT,
                carregamento TEXT,
                microfone TEXT,
                alto_falante TEXT,
                auricular TEXT,
                vibracao TEXT,
                botoes TEXT
            )
        """)
        conn.commit()
# Obtem um checklist de entrada por ordem de serviço
def obter_checklist_entrada_por_ordem_servico(ordem_servico_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM checklist_entrada WHERE ordem_servico_id = ?",
            (ordem_servico_id,)
        )
        resultado = cursor.fetchone()
        return dict(resultado) if resultado else None
# Obtem um checklist de entrada por id
def obter_checklist_entrada_por_id(checklist_entrada_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM checklist_entrada WHERE id = ?",
            (checklist_entrada_id,)
        )
        resultado = cursor.fetchone()
        return dict(resultado) if resultado else None
# Insere um novo checklist de entrada
def inserir_checklist_entrada(
    ordem_servico_id, wifi, bluetooth, sinal, biometria, chip_sim, tela, touch,
    camera_frontal, camera_traseira, flash, sensor_prox, carregamento,
    microfone, alto_falante, auricular, vibracao, botoes
):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO checklist_entrada (
                ordem_servico_id, wifi, bluetooth, sinal, biometria, chip_sim, tela, touch,
                camera_frontal, camera_traseira, flash, sensor_prox, carregamento,
                microfone, alto_falante, auricular, vibracao, botoes
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            ordem_servico_id, wifi, bluetooth, sinal, biometria, chip_sim, tela, touch,
            camera_frontal, camera_traseira, flash, sensor_prox, carregamento,
            microfone, alto_falante, auricular, vibracao, botoes
        ))
        conn.commit()
        return cursor.lastrowid

def vincular_checklist_na_ordem(checklist_id, ordem_servico_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE checklist_entrada SET ordem_servico_id = ? WHERE id = ?",
            (ordem_servico_id, checklist_id)
        )
        conn.commit()
# Atualiza um checklist de entrada
def atualizar_checklist_entrada(
    checklist_entrada_id, wifi, bluetooth, sinal, biometria, chip_sim, tela, touch,
    camera_frontal, camera_traseira, flash, sensor_prox, carregamento,
    microfone, alto_falante, auricular, vibracao, botoes
):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE checklist_entrada
            SET wifi = ?, bluetooth = ?, sinal = ?, biometria = ?, chip_sim = ?, tela = ?, touch = ?,
                camera_frontal = ?, camera_traseira = ?, flash = ?, sensor_prox = ?, carregamento = ?,
                microfone = ?, alto_falante = ?, auricular = ?, vibracao = ?, botoes = ?
            WHERE id = ?
        """, (
            wifi, bluetooth, sinal, biometria, chip_sim, tela, touch,
            camera_frontal, camera_traseira, flash, sensor_prox, carregamento,
            microfone, alto_falante, auricular, vibracao, botoes,
            checklist_entrada_id
        ))
        conn.commit()
# Exclui um checklist de entrada
def excluir_checklist_entrada(checklist_entrada_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM checklist_entrada WHERE id = ?", (checklist_entrada_id,))
        conn.commit()
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