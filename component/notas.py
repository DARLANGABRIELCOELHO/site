# notas.py
# cria uma nota não fiscal para o cliente de venda ou serviço 
# cria um label pdf para enviar para o cliente e imprimir em impressora térmica 
import os
from datetime import datetime
import data.database as db
# criar nota de venda
def criar_nota_venda(cliente, produtos, servicos, total, forma_pagamento, parcelamento, observacao, garantia):
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    nome_arquivo = f"nota_{data_atual.replace('/', '_').replace(':', '_')}.txt"
    caminho_arquivo = os.path.join("notas", nome_arquivo)
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        f.write(f"NOTA NÃO FISCAL\n")
        f.write(f"Data: {data_atual}\n")
        f.write(f"Cliente: {cliente}\n")
        f.write(f"Produtos: {produtos}\n")
        f.write(f"Serviços: {servicos}\n")
        f.write(f"Total: {total}\n")
        f.write(f"Forma de Pagamento: {forma_pagamento}\n")
        f.write(f"Parcelamento: {parcelamento}\n")
        f.write(f"Observação: {observacao}\n")
        f.write(f"Garantia: {garantia}\n")
    return caminho_arquivo
# criar nota de ordem de serviço
def criar_nota_servico(cliente, servicos, total, forma_pagamento, parcelamento, observacao, garantia):
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    nome_arquivo = f"nota_{data_atual.replace('/', '_').replace(':', '_')}.txt"
    caminho_arquivo = os.path.join("notas", nome_arquivo)
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        f.write(f"NOTA NÃO FISCAL\n")
        f.write(f"Data: {data_atual}\n")
        f.write(f"Cliente: {cliente}\n")
        f.write(f"Serviços: {servicos}\n")
        f.write(f"Total: {total}\n")
        f.write(f"Forma de Pagamento: {forma_pagamento}\n")
        f.write(f"Parcelamento: {parcelamento}\n")
        f.write(f"Observação: {observacao}\n")
        f.write(f"Garantia: {garantia}\n")
    return caminho_arquivo 
# criar nota ordem de finalização de serviço 
def criar_nota_fim_servico(cliente, servicos, total, forma_pagamento, parcelamento, observacao, garantia):
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    nome_arquivo = f"nota_{data_atual.replace('/', '_').replace(':', '_')}.txt"
    caminho_arquivo = os.path.join("notas", nome_arquivo)
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        f.write(f"NOTA NÃO FISCAL\n")
        f.write(f"Data: {data_atual}\n")
        f.write(f"Cliente: {cliente}\n")
        f.write(f"Serviços: {servicos}\n")
        f.write(f"Total: {total}\n")
        f.write(f"Forma de Pagamento: {forma_pagamento}\n")
        f.write(f"Parcelamento: {parcelamento}\n")
        f.write(f"Observação: {observacao}\n")
        f.write(f"Garantia: {garantia}\n")
    return caminho_arquivo 
# criar nota cancelamento de serviço 
def criar_nota_cancelamento_servico(cliente, servicos, total, forma_pagamento, parcelamento, observacao, garantia):
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    nome_arquivo = f"nota_{data_atual.replace('/', '_').replace(':', '_')}.txt"
    caminho_arquivo = os.path.join("notas", nome_arquivo)
    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        f.write(f"NOTA NÃO FISCAL\n")
        f.write(f"Data: {data_atual}\n")
        f.write(f"Cliente: {cliente}\n")
        f.write(f"Serviços: {servicos}\n")
        f.write(f"Total: {total}\n")
        f.write(f"Forma de Pagamento: {forma_pagamento}\n")
        f.write(f"Parcelamento: {parcelamento}\n")
        f.write(f"Observação: {observacao}\n")
        f.write(f"Garantia: {garantia}\n")
    return caminho_arquivo   
