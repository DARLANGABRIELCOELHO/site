# notas.py
# cria uma nota não fiscal para o cliente de venda ou serviço
# cria um label pdf para enviar para o cliente e imprimir em impressora térmica
import os
import sys
from datetime import datetime

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
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


# ── Nota Final de Entrega ──────────────────────────────────────────────────
def gerar_nota_entrega(dados_entrega: dict, ordem: dict) -> str:
    """
    Gera e imprime a nota final de serviço (comprovante de entrega).

    dados_entrega: dict passado para registrar_ordem_entrega()
    ordem:         dict retornado por listar_ordens_servico()
                   (precisa de: id, cliente_nome, cliente_telefone, modelo,
                    cor, tecnico_nome, servicos, total_servicos)
    """
    pasta = os.path.join(os.path.dirname(__file__), '..', 'notas')
    os.makedirs(pasta, exist_ok=True)

    ordem_id      = ordem.get("id") or dados_entrega.get("ordem_servico_id")
    cliente_nome  = ordem.get("cliente_nome") or "Balcão"
    cliente_tel   = ordem.get("cliente_telefone") or ""
    modelo        = ordem.get("modelo", "—")
    cor           = (ordem.get("cor") or "").strip()
    aparelho      = f"{modelo} • {cor}" if cor else modelo
    tecnico       = ordem.get("tecnico_nome") or "—"
    servicos      = ordem.get("servicos", [])
    total_bruto   = float(ordem.get("total_servicos") or 0)
    desconto      = float(dados_entrega.get("desconto") or 0)
    total_liq     = max(0.0, total_bruto - desconto)
    forma_pag     = dados_entrega.get("forma_pagamento") or "—"
    parcelamento  = dados_entrega.get("parcelamento") or "À vista"
    garantia_txt  = dados_entrega.get("garantia") or "Sem garantia"
    data_fim_gar  = dados_entrega.get("data_fim_garantia") or ""
    laudo         = dados_entrega.get("laudo") or ""
    observacoes   = dados_entrega.get("observacoes") or ""
    data_atual    = datetime.now().strftime("%d/%m/%Y %H:%M")

    # Formata data fim garantia
    if data_fim_gar:
        try:
            from datetime import date as _date
            d = _date.fromisoformat(data_fim_gar)
            data_fim_gar_fmt = d.strftime("%d/%m/%Y")
        except Exception:
            data_fim_gar_fmt = data_fim_gar
    else:
        data_fim_gar_fmt = "—"

    nome_arquivo = f"ENTREGA_OS{ordem_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    caminho = os.path.join(pasta, nome_arquivo)

    L = 48  # largura da nota

    def linha(c="-"): return c * L + "\n"
    def centro(txt): return txt.center(L) + "\n"
    def campo(rotulo, valor): return f"{rotulo:<18}{valor}\n"

    with open(caminho, "w", encoding="utf-8") as f:
        # ── Cabeçalho ──────────────────────────────
        f.write(linha("="))
        f.write(centro("iFix"))
        f.write(centro("Assistência Técnica de Eletrônicos"))
        f.write(linha("="))
        f.write(campo("Data:", data_atual))
        f.write(campo("OS#:", f"#{ordem_id}"))
        f.write(linha())

        # ── Cliente / Aparelho ──────────────────────
        f.write("CLIENTE\n")
        f.write(linha())
        f.write(campo("Nome:", cliente_nome))
        if cliente_tel:
            f.write(campo("Telefone:", cliente_tel))
        f.write(campo("Aparelho:", aparelho))
        f.write(campo("Técnico:", tecnico))
        f.write(linha())

        # ── Laudo ───────────────────────────────────
        if laudo:
            f.write("LAUDO TÉCNICO\n")
            f.write(linha())
            # quebra linha a cada 46 chars
            for i in range(0, len(laudo), L - 2):
                f.write(f"  {laudo[i:i + L - 2]}\n")
            f.write(linha())

        # ── Serviços ────────────────────────────────
        f.write("SERVIÇOS REALIZADOS\n")
        f.write(linha())
        for sv in servicos:
            nome_sv = sv.get("nome", "—")
            preco   = float(sv.get("preco") or 0)
            # nome à esquerda, preço à direita
            espaco  = L - len(nome_sv) - len(f"R$ {preco:.2f}") - 2
            f.write(f"  {nome_sv}{'.' * max(1, espaco)}R$ {preco:.2f}\n")
        f.write(linha())

        # ── Valores ─────────────────────────────────
        f.write(campo("Subtotal:", f"R$ {total_bruto:.2f}"))
        if desconto > 0:
            f.write(campo("Desconto:", f"R$ {desconto:.2f}"))
        f.write(campo("TOTAL:", f"R$ {total_liq:.2f}"))
        f.write(campo("Pagamento:", forma_pag))
        if parcelamento and parcelamento != "À vista":
            f.write(campo("Parcelamento:", parcelamento))
        f.write(linha())

        # ── Garantia ────────────────────────────────
        f.write("GARANTIA\n")
        f.write(linha())
        f.write(campo("Período:", garantia_txt))
        if data_fim_gar_fmt != "—":
            f.write(campo("Válida até:", data_fim_gar_fmt))
        f.write(linha())

        # ── Termos e Condições ──────────────────────
        f.write("TERMOS E CONDIÇÕES\n")
        f.write(linha())
        termos = [
            "A garantia cobre o mesmo defeito do reparo realizado,",
            "desde que não haja mau uso, quedas, umidade ou",
            "intervenção de terceiros.",
            "",
            "Aparelhos não retirados em até 90 dias poderão ser",
            "destinados para cobrir despesas do serviço.",
            "",
            "Este documento é o comprovante do serviço prestado.",
            "Guarde-o para acionar a garantia, se necessário.",
        ]
        for t in termos:
            f.write(f"  {t}\n")
        f.write(linha())

        # ── Observações ─────────────────────────────
        if observacoes:
            f.write("OBSERVAÇÕES\n")
            f.write(linha())
            for i in range(0, len(observacoes), L - 2):
                f.write(f"  {observacoes[i:i + L - 2]}\n")
            f.write(linha())

        # ── Rodapé ──────────────────────────────────
        f.write(centro("Obrigado pela preferência!"))
        f.write(centro("iFix — Qualidade e Confiança"))
        f.write(linha("="))

    # Envia para impressão
    if sys.platform.startswith("win"):
        os.startfile(caminho, "print")
    else:
        import subprocess
        subprocess.run(["lp", caminho])

    return caminho


# ── Cupom de Venda PDV ─────────────────────────────────────────────────────
def imprimir_venda(venda_id: int, itens: list, cliente_nome: str,
                   forma_pagamento: str, parcelamento: str, total: float) -> str:
    """Gera e imprime o cupom de venda do PDV."""
    pasta = os.path.join(os.path.dirname(__file__), '..', 'notas')
    os.makedirs(pasta, exist_ok=True)

    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M")
    nome_arquivo = f"VENDA_{venda_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    caminho = os.path.join(pasta, nome_arquivo)

    L = 42

    def linha(c="-"): return c * L + "\n"
    def centro(txt): return txt.center(L) + "\n"

    with open(caminho, "w", encoding="utf-8") as f:
        f.write(linha("="))
        f.write(centro("iFix"))
        f.write(centro("Assistência Técnica de Eletrônicos"))
        f.write(linha("="))
        f.write(f"{'Data:':<12}{data_atual}\n")
        f.write(f"{'Venda#:':<12}#{venda_id}\n")
        if cliente_nome and cliente_nome != "Balcão":
            f.write(f"{'Cliente:':<12}{cliente_nome}\n")
        f.write(linha())

        f.write("ITENS\n")
        f.write(linha())
        for item in itens:
            nome  = item.get("nome", "—")
            qtd   = int(item.get("qtd") or item.get("quantidade") or 1)
            preco = float(item.get("preco") or item.get("preco_unitario") or 0)
            sub   = float(item.get("subtotal") or preco * qtd)
            f.write(f"  {nome}\n")
            espaco = L - 4 - len(f"R$ {sub:.2f}")
            f.write(f"  {qtd}x R${preco:.2f}{' ' * max(1, espaco)}R$ {sub:.2f}\n")
        f.write(linha())

        f.write(f"{'TOTAL:':<20}R$ {total:.2f}\n")
        f.write(f"{'Pagamento:':<20}{forma_pagamento}\n")
        if parcelamento and parcelamento != "À vista":
            f.write(f"{'Parcelamento:':<20}{parcelamento}\n")
        f.write(linha())
        f.write(centro("Obrigado pela preferência!"))
        f.write(centro("iFix — Qualidade e Confiança"))
        f.write(linha("="))

    if sys.platform.startswith("win"):
        os.startfile(caminho, "print")
    else:
        import subprocess
        subprocess.run(["lp", caminho])

    return caminho


# ── Imprimir OS ────────────────────────────────────────────────────────────
def imprimir_os(ordem_id: int) -> str:
    """Gera arquivo .txt com os dados da OS e envia para impressão."""
    pasta = os.path.join(os.path.dirname(__file__), '..', 'notas')
    os.makedirs(pasta, exist_ok=True)

    ordem = db.obter_ordem_servico(ordem_id)
    if not ordem:
        raise ValueError(f"OS #{ordem_id} não encontrada.")

    servicos = db.obter_servicos_da_ordem(ordem_id)

    # Nome do cliente
    cliente_nome = "Balcão"
    cliente_tel = ""
    try:
        with db.get_db_connection() as conn:
            cursor = conn.cursor()
            if ordem.get("cliente_id"):
                cursor.execute(
                    "SELECT nome, telefone FROM clientes WHERE id = ?",
                    (ordem["cliente_id"],)
                )
                row = cursor.fetchone()
                if row:
                    cliente_nome = row["nome"]
                    cliente_tel = row["telefone"] or ""
    except Exception:
        pass

    # Nome do técnico
    tecnico_nome = "—"
    try:
        with db.get_db_connection() as conn:
            cursor = conn.cursor()
            if ordem.get("tecnico_id"):
                cursor.execute(
                    "SELECT nome FROM tecnicos WHERE id = ?",
                    (ordem["tecnico_id"],)
                )
                row = cursor.fetchone()
                if row:
                    tecnico_nome = row["nome"]
    except Exception:
        pass

    total = sum(float(s.get("preco_servico_snapshot") or 0) for s in servicos)
    data_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    nome_arquivo = f"OS_{ordem_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    caminho = os.path.join(pasta, nome_arquivo)

    with open(caminho, "w", encoding="utf-8") as f:
        f.write("=" * 42 + "\n")
        f.write("         ORDEM DE SERVIÇO\n")
        f.write("=" * 42 + "\n")
        f.write(f"OS#:        {ordem_id}\n")
        f.write(f"Data:       {data_atual}\n")
        f.write(f"Cliente:    {cliente_nome}\n")
        if cliente_tel:
            f.write(f"Telefone:   {cliente_tel}\n")
        f.write(f"Aparelho:   {ordem.get('modelo', '—')}\n")
        f.write(f"IMEI:       {ordem.get('imei') or '—'}\n")
        f.write(f"Técnico:    {tecnico_nome}\n")
        f.write(f"Status:     {ordem.get('status', '—')}\n")
        f.write(f"Prioridade: {ordem.get('prioridade', '—')}\n")
        f.write("-" * 42 + "\n")
        f.write("DEFEITO RELATADO:\n")
        f.write(f"{ordem.get('relato') or '—'}\n")
        f.write("-" * 42 + "\n")
        f.write("SERVIÇOS:\n")
        for s in servicos:
            preco = float(s.get("preco_servico_snapshot") or 0)
            f.write(f"  - {s['nome_servico_snapshot']}: R$ {preco:.2f}\n")
        f.write("-" * 42 + "\n")
        f.write(f"TOTAL: R$ {total:.2f}\n")
        f.write("=" * 42 + "\n")

    # Envia para impressão
    if sys.platform.startswith("win"):
        os.startfile(caminho, "print")
    else:
        import subprocess
        subprocess.run(["lp", caminho])

    return caminho
