import re
import json
import sqlite3
import datetime

# 1. Lê e limpa o JSON do JS
with open("C:/Users/darla/Documents/IFIX_SYSTEM/site/SERVIÇOS.JS", "r", encoding="utf-8") as f:
    content = f.read()

content = re.sub(r'//.*', '', content)
start = content.find('{')
end = content.rfind('}') + 1
obj_str = content[start:end]
# Adiciona aspas nas chaves
obj_str = re.sub(r'([{,]\s*)([A-Za-z0-9_]+)\s*:', r'\1"\2":', obj_str)

data = json.loads(obj_str)

# 2. Conecta ao Banco
db_path = 'c:/Users/darla/Documents/IFIX_SYSTEM/site/data/ifix.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Como já tínhamos feito um insert antes com os dados antigos, vamos limpar a tabela de serviços 
# para inserir o novo formato sem duplicar. (Se preferir manter, comente a linha abaixo)
cursor.execute("DELETE FROM servicos")

# 3. Itera o novo JSON e constrói o nome
now_str = datetime.datetime.now().isoformat()
count = 0

for model in data.get("models", []):
    model_prices = data.get("prices", {}).get(model, {})
    for categoria, prices in model_prices.items():
        avista_str = prices.get("avista", "N/A")
        
        if avista_str == "N/A":
            continue
            
        parcelado_str = prices.get("parcelado", "0")
        if parcelado_str == "N/A":
            price_val = 0.0
        else:
            # R$ 220,00 -> 220.00
            clean_str = parcelado_str.replace("R$", "").replace(".", "").replace(",", ".").strip()
            try:
                price_val = float(clean_str)
            except:
                price_val = 0.0
                
        # NOME = MODELS + CATEGORIA
        nome = f"{model} {categoria}"
                
        cursor.execute('''
            INSERT INTO servicos (nome, modelo_celular, categoria, custos, preco, tempo_estimado, observacao, data_cadastro)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (nome, model, categoria, 0.0, price_val, "", "", now_str))
        count += 1

conn.commit()
conn.close()
print(f"[{count}] Serviços inseridos com sucesso!")
