#========================================================================================================================================
# importações   
#========================================================================================================================================
from datetime import date
import sqlite3

#========================================================================================================================================
# Configuração do banco
#========================================================================================================================================
DB_PATH = "ifix.db"

# CONECTA AO BANCO DE DADOS SQLite
def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

# INICIALIZA O ESTADO DO BANCO DE DADOS (CRIA TABELAS E DADOS INICIAIS)
def inicializar_estado():
    inicializar_banco()
# ========================================================================================================================================
# funções de dados da página tecnicos
# ========================================================================================================================================
# Chaves padronizadas para os campos do técnico (usadas como referência)
CAMPO_ID = "id"
CAMPO_NOME = "nome"
CAMPO_TELEFONE = "telefone"
CAMPO_ESPECIALIDADE = "especialidade"
CAMPO_DATA_CADASTRO = "data_cadastro"
CAMPO_ORDENS_SERVICO = "ordens_servico"  # Não utilizado diretamente no banco
# CRIA A TABELA TECNICOS E INSERE DADOS INICIAIS SE VAZIA
def inicializar_banco():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Cria a tabela tecnicos
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tecnicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            telefone TEXT NOT NULL,
            especialidade TEXT NOT NULL,
            data_cadastro TEXT NOT NULL,
            ordens_servico INTEGER DEFAULT 0
        )
    ''')
    
    # Verifica se a tabela está vazia e insere dados iniciais
    cursor.execute("SELECT COUNT(*) FROM tecnicos")
    if cursor.fetchone()[0] == 0:
        dados_iniciais = [
            ("Técnico A", "15555-5678", "android", "2023-02-01", 0)
        ]
        cursor.executemany('''
            INSERT INTO tecnicos (nome, telefone, especialidade, data_cadastro, ordens_servico)
            VALUES (?, ?, ?, ?, ?)
        ''', dados_iniciais)
    
    conn.commit()
    conn.close()



# ----------------------------------------------------------------------------------------------------------------------------------------
# RETORNA UM TECNICO PELO ID
# ----------------------------------------------------------------------------------------------------------------------------------------
def obter_tecnico(tecnico_id):
    conn = get_db_connection()
    tecnico = conn.execute(
        "SELECT id, nome, telefone, especialidade, data_cadastro, ordens_servico FROM tecnicos WHERE id = ?",
        (tecnico_id,)
    ).fetchone()
    conn.close()
    return dict(tecnico) if tecnico else None

# ----------------------------------------------------------------------------------------------------------------------------------------
# INSERE UM NOVO TECNICO
# ----------------------------------------------------------------------------------------------------------------------------------------
def inserir_tecnico(nome, telefone, especialidade):
    conn = get_db_connection()
    hoje = date.today().isoformat()  # formato YYYY-MM-DD
    cursor = conn.execute('''
        INSERT INTO tecnicos (nome, telefone, especialidade, data_cadastro)
        VALUES (?, ?, ?, ?)
    ''', (nome, telefone, especialidade, hoje))
    novo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return obter_tecnico(novo_id)

# ----------------------------------------------------------------------------------------------------------------------------------------
# ATUALIZA AS INFORMAÇÕES DE UM TECNICO EXISTENTE
# ----------------------------------------------------------------------------------------------------------------------------------------
def atualizar_tecnico(tecnico_id, nome, telefone, especialidade):
    conn = get_db_connection()
    conn.execute('''
        UPDATE tecnicos
        SET nome = ?, telefone = ?, especialidade = ?
        WHERE id = ?
    ''', (nome, telefone, especialidade, tecnico_id))
    conn.commit()
    conn.close()
    
    return obter_tecnico(tecnico_id)
