# ordemdeserviço.py
# cria uma ordem de serviço para o cliente de serviço
import os
from datetime import datetime
import data.database as db
def criar_ordem_servico(cliente, servico, total, forma_pagamento, parcelamento, observacao, garantia):
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    nome_arquivo = f"ordem_servico_{data_atual.replace('/', '_').replace(':', '_')}.txt"
    caminho_arquivo = os.path.join("ordem_servico", nome_arquivo)
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        f.write(f"ORDEM DE SERVIÇO\n")
        f.write(f"Data: {data_atual}\n")
        f.write(f"Cliente: {cliente}\n")
        f.write(f"Serviço: {servico}\n")
        f.write(f"Total: {total}\n")
        f.write(f"Forma de Pagamento: {forma_pagamento}\n")
        f.write(f"Parcelamento: {parcelamento}\n")
        f.write(f"Observação: {observacao}\n")
        f.write(f"Garantia: {garantia}\n")
    return caminho_arquivo
