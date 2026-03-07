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
# ========================================================================================================================================
# funções de dados da página tecnicos
# ========================================================================================================================================

# Dados iniciais de exemplo (serão usados na inicialização do banco)
def tecnicos():
    return [
        {
            "id": 1,
            "nome": "Técnico A",
            "telefone": "15555-5678",
            "especialidade": "android",
            "data_cadastro": "2023-02-01",
            "ordens_servico": []
        }
    ]
#-----------------------------------------------------------------------------------------------------------------------------------------
# Chaves padronizadas para os campos do técnico (usadas como referência)
#-----------------------------------------------------------------------------------------------------------------------------------------
CAMPO_ID = "id"
CAMPO_NOME = "nome"
CAMPO_TELEFONE = "telefone"
CAMPO_ESPECIALIDADE = "especialidade"
CAMPO_DATA_CADASTRO = "data_cadastro"
CAMPO_ORDENS_SERVICO = "ordens_servico"

# Banco de dados em memória (lista de dicionários)
_tecnicos = []
_banco_inicializado = False

# ----------------------------------------------------------------------------------------------------------------------------------------
# INICIALIZA O BANCO DE DADOS TABELA TECNICO
# ----------------------------------------------------------------------------------------------------------------------------------------
def inicializar_banco_tecnico():
    global _tecnicos, _banco_inicializado
    if not _banco_inicializado:
        _tecnicos = tecnicos()  # carrega dados iniciais
        _banco_inicializado = True

# ----------------------------------------------------------------------------------------------------------------------------------------
# RETORNA O PRÓXIMO ID TECNICO DISPONÍVEL
# ----------------------------------------------------------------------------------------------------------------------------------------
def proximo_id_tecnico():
    if not _tecnicos:
        return 1
    return max(t[CAMPO_ID] for t in _tecnicos) + 1

# ----------------------------------------------------------------------------------------------------------------------------------------
# RETORNA UM TECNICO PELO ID
# ----------------------------------------------------------------------------------------------------------------------------------------
def obter_tecnico(tecnico_id):
    for t in _tecnicos:
        if t[CAMPO_ID] == tecnico_id:
            return t
    return None

# ----------------------------------------------------------------------------------------------------------------------------------------
# INSERE UM NOVO TECNICO
# ----------------------------------------------------------------------------------------------------------------------------------------
def inserir_tecnico(nome, telefone, especialidade):
    novo_id = proximo_id_tecnico()
    hoje = date.today().isoformat()  # formato YYYY-MM-DD
    novo_tecnico = {
        CAMPO_ID: novo_id,
        CAMPO_NOME: nome,
        CAMPO_TELEFONE: telefone,
        CAMPO_ESPECIALIDADE: especialidade,
        CAMPO_DATA_CADASTRO: hoje,
        CAMPO_ORDENS_SERVICO: []
    }
    _tecnicos.append(novo_tecnico)
    return novo_tecnico

# ----------------------------------------------------------------------------------------------------------------------------------------
# ATUALIZA AS INFORMAÇÕES DE UM TECNICO EXISTENTE
# ----------------------------------------------------------------------------------------------------------------------------------------
def atualizar_tecnico(tecnico_id, nome, telefone, especialidade):
    tecnico = obter_tecnico(tecnico_id)
    if tecnico:
        tecnico[CAMPO_NOME] = nome
        tecnico[CAMPO_TELEFONE] = telefone
        tecnico[CAMPO_ESPECIALIDADE] = especialidade
        return tecnico
    return None
