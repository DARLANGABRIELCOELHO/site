# whatsapp.py — abre conversa do WhatsApp com o cliente da OS
import sys
import os
import webbrowser
import urllib.parse

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db


def chamar_cliente_whatsapp(ordem_id: int):
    """Abre o WhatsApp Web com mensagem pré-preenchida para o cliente da OS."""
    ordens = db.listar_ordens_servico(filtro=str(ordem_id))
    ordem = next((o for o in ordens if o["id"] == ordem_id), None)

    if not ordem:
        raise ValueError(f"OS #{ordem_id} não encontrada.")

    telefone = (ordem.get("cliente_telefone") or "").strip()
    if not telefone:
        raise ValueError("Cliente sem telefone cadastrado.")

    # Remove tudo que não é dígito
    telefone = "".join(ch for ch in telefone if ch.isdigit())

    if len(telefone) < 8:
        raise ValueError(f"Telefone inválido: {telefone}")

    # Garante código do Brasil
    if not telefone.startswith("55"):
        telefone = "55" + telefone

    mensagem = (
        f"Olá! Aqui é da iFix. "
        f"Sua OS #{ordem_id} ({ordem.get('modelo', '')}) "
        f"está com status: {ordem.get('status', '')}. "
        f"Qualquer dúvida estamos à disposição!"
    )

    url = f"https://wa.me/{telefone}?text={urllib.parse.quote(mensagem)}"
    webbrowser.open(url)
