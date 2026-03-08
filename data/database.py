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
    inicializar_banco_vendas()


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
