import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__))))
import data.database as db

print("Técnicos:", db.listar_tecnicos())
try:
    db.excluir_tecnico(1)
    print("Sucesso!")
except Exception as e:
    import traceback
    traceback.print_exc()
