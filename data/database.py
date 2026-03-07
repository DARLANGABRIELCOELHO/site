# funçoes de dados da pagina clientes
def clientes():
    
    return [
        {"id": 1, 
        "name": "Cliente A",
        "numero": "15555-1234",
        "documento": "123.456.789-00",
        "endereco": "Rua A, 123",
        "observacao": "Cliente VIP",
        "data_cadastro": "2023-01-01",
        "ordem_servico": []},
        ]
# funçoes de dados da pagina tecnicos
def tecnicos():
    return [
        {"id": 1, 
        "name": "Técnico A",
        "numero": "15555-5678",
        "especialidade": "android",
        "data_cadastro": "2023-02-01",
        "ordem_servico": []},
        ]
# funçoes de dados da pagina catalogo
def produtos():
    return [
        {"id": 1, 
        "name": "Produto A",
        "categoria": "carregador",
        "custos": 50.0,
        "preco": 100.0,
        "data_cadastro": "2023-03-01",
        "estoque": 10,
        "estoque_minimo": 5}
        ]
def celulares():
    return [
        {"id": 1, 
        "modelo": "Celular A",
        "marca": "Marca A",
        "cor": "Preto",
        "imei": "1234567890",
        "data_cadastro": "2023-04-01",
        "custos_de_aquisicao": 200.0,
        "custos_de_reparo": 50.0,
        "preco": 400.0,
        "condicao": "bom",
        "fotos": ["foto1.jpg", "foto2.jpg"]
        }
        ]
def servicos():
    return [
        {"id": 1, 
        "name": "Serviço A",
        "modelo_celular": "Celular A",
        "categoria": "Reparo de tela",
        "custos": 50.0,
        "preco": 100.0,
        "tempo_estimado": "2 horas",
        "observacao": "Garantia de 3 meses",
        "data_cadastro": "2023-05-01"}
        ]
# funçoes de dados da pagina vendas
def vendas():
    return [
        {"id": 1, 
        "cliente_id": 1,
        "produto_id": 1,
        "celular_id": 1,
        "servico_id": 1,
        "data_venda": "2023-06-01",
        "desconto": 10.0,
        "forma_pagamento": "cartão de crédito",
        "parcelamento": "3x",
        "observacao": "Venda realizada com sucesso",
        "garantia": "90 dias",
        "valor_total": 500.0}
        ]
# funçoes de dados da pagina laboratorio/garantia
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
