# historicoentrega.py — Histórico de Entregas (ModernDialog)
import os
import sys
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFrame,
    QSpacerItem, QSizePolicy, QMessageBox, QScrollArea,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db
from component.base_dialog import ModernDialog

try:
    from component.svg_utils import svg_para_pixmap
    _SVG_OK = True
except Exception:
    _SVG_OK = False


# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _fmt_data(data_str: str) -> str:
    try:
        return datetime.fromisoformat(data_str).strftime("%d/%m/%Y")
    except Exception:
        return data_str or "—"


def _fmt_valor(v) -> str:
    try:
        return f"R$ {float(v):.2f}"
    except Exception:
        return "—"


def _badge(texto: str, cor_fundo: str, cor_texto: str) -> QLabel:
    lbl = QLabel(texto)
    lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
    lbl.setStyleSheet(f"""
        background-color: {cor_fundo};
        color: {cor_texto};
        border-radius: 4px;
        padding: 3px 10px;
        font-size: 10px;
        font-weight: 700;
    """)
    return lbl


# ──────────────────────────────────────────────
# EntregaCard
# ──────────────────────────────────────────────

class EntregaCard(QFrame):
    def __init__(self, entrega: dict, on_excluir, on_imprimir):
        super().__init__()
        self.setObjectName("entrega_card")
        self.setFixedWidth(320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        # ── Cabeçalho ──
        header = QHBoxLayout()
        ico = QLabel()
        ico.setObjectName("icone_card")
        if _SVG_OK:
            ico.setPixmap(svg_para_pixmap("fi-sr-smartphone.svg", "#F26522", 18, 18))
        else:
            ico.setText("📱")

        info = QVBoxLayout()
        info.setSpacing(2)
        lbl_cliente = QLabel(entrega.get("cliente_nome") or "—")
        lbl_cliente.setObjectName("txt_branca_bold")
        lbl_cliente.setWordWrap(True)
        modelo = entrega.get("modelo") or "—"
        cor_apar = (entrega.get("cor") or "").strip()
        lbl_modelo = QLabel(f"{modelo} • {cor_apar}" if cor_apar else modelo)
        lbl_modelo.setObjectName("txt_cinza")
        info.addWidget(lbl_cliente)
        info.addWidget(lbl_modelo)

        header.addWidget(ico)
        header.addLayout(info)
        header.addItem(QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        lbl_id = QLabel(f"#{entrega['id']}")
        lbl_id.setObjectName("txt_cinza")
        header.addWidget(lbl_id)

        btn_print = QPushButton()
        btn_print.setObjectName("btn_imprimir")
        btn_print.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_print.setFixedSize(26, 26)
        if _SVG_OK:
            btn_print.setIcon(QIcon(svg_para_pixmap("fi-sr-print.svg", "#94A3B8", 13, 13)))
            btn_print.setIconSize(QSize(13, 13))
        else:
            btn_print.setText("🖨")
        btn_print.clicked.connect(lambda: on_imprimir(entrega))
        header.addWidget(btn_print)

        btn_del = QPushButton()
        btn_del.setObjectName("btn_lixeira")
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setFixedSize(26, 26)
        if _SVG_OK:
            btn_del.setIcon(QIcon(svg_para_pixmap("fi-sr-trash.svg", "#EF4444", 13, 13)))
            btn_del.setIconSize(QSize(13, 13))
        else:
            btn_del.setText("🗑")
        btn_del.clicked.connect(lambda: on_excluir(entrega["id"]))
        header.addWidget(btn_del)
        layout.addLayout(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName("sep_card")
        layout.addWidget(sep)

        # ── Meta ──
        meta = QHBoxLayout()
        meta.setSpacing(12)

        meta_data = QHBoxLayout()
        meta_data.setSpacing(4)
        if _SVG_OK:
            ico_d = QLabel()
            ico_d.setPixmap(svg_para_pixmap("fi-sr-clock.svg", "#64748B", 11, 11))
            meta_data.addWidget(ico_d)
        lbl_data = QLabel(_fmt_data(entrega.get("data", "")))
        lbl_data.setObjectName("txt_cinza_pequeno")
        meta_data.addWidget(lbl_data)
        meta.addLayout(meta_data)

        meta_tec = QHBoxLayout()
        meta_tec.setSpacing(4)
        if _SVG_OK:
            ico_t = QLabel()
            ico_t.setPixmap(svg_para_pixmap("fi-sr-tools.svg", "#64748B", 11, 11))
            meta_tec.addWidget(ico_t)
        lbl_tec = QLabel(entrega.get("tecnico_nome") or "Sem técnico")
        lbl_tec.setObjectName("txt_cinza_pequeno")
        meta_tec.addWidget(lbl_tec)
        meta.addLayout(meta_tec)
        meta.addItem(QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addLayout(meta)

        # OS vinculada
        os_id = entrega.get("ordem_servico_id")
        if os_id:
            lbl_os = QLabel(f"OS #{os_id}")
            lbl_os.setObjectName("txt_cinza_pequeno")
            layout.addWidget(lbl_os)

        # Laudo
        laudo = (entrega.get("laudo") or "").strip()
        if laudo:
            lbl_lt = QLabel("Laudo:")
            lbl_lt.setObjectName("txt_cinza_pequeno")
            lbl_lv = QLabel(laudo[:90] + ("…" if len(laudo) > 90 else ""))
            lbl_lv.setObjectName("txt_branca")
            lbl_lv.setWordWrap(True)
            layout.addWidget(lbl_lt)
            layout.addWidget(lbl_lv)

        # Garantia badge
        garantia = entrega.get("garantia")
        badges_row = QHBoxLayout()
        badges_row.setAlignment(Qt.AlignmentFlag.AlignLeft)
        if garantia:
            badges_row.addWidget(_badge(garantia, "rgba(74,222,128,0.15)", "#4ADE80"))
            if entrega.get("data_fim_garantia"):
                lbl_fim = QLabel(f"até {_fmt_data(entrega['data_fim_garantia'])}")
                lbl_fim.setObjectName("txt_cinza_pequeno")
                badges_row.addWidget(lbl_fim)
        else:
            badges_row.addWidget(_badge("Sem garantia", "rgba(100,116,139,0.15)", "#94A3B8"))
        badges_row.addItem(QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addLayout(badges_row)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setObjectName("sep_card")
        layout.addWidget(sep2)

        # ── Rodapé ──
        forma = entrega.get("forma_pagamento") or "—"
        parcelas = entrega.get("parcelamento") or ""
        foot = QHBoxLayout()
        lbl_pag = QLabel(f"{forma}  {parcelas}".strip())
        lbl_pag.setObjectName("txt_cinza_pequeno")
        lbl_total = QLabel(_fmt_valor(entrega.get("valor_total")))
        lbl_total.setObjectName("txt_laranja_bold")
        foot.addWidget(lbl_pag)
        foot.addItem(QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        foot.addWidget(lbl_total)
        layout.addLayout(foot)


# ──────────────────────────────────────────────
# Dialog principal
# ──────────────────────────────────────────────

class HistoricoEntregaDialog(ModernDialog):
    def __init__(self, parent=None):
        super().__init__("Histórico de Entregas", 1060, 660, parent)
        self._build()
        self._aplicar_estilos()
        self._carregar()

    def _build(self):
        # Busca
        self.edit_busca = QLineEdit()
        self.edit_busca.setPlaceholderText("Buscar por cliente, técnico, modelo ou ID...")
        self.edit_busca.setObjectName("busca_input")
        if _SVG_OK:
            act = QAction(
                QIcon(svg_para_pixmap("fi-sr-search.svg", "#64748B", 16, 16)), "",
                self.edit_busca
            )
            self.edit_busca.addAction(act, QLineEdit.ActionPosition.LeadingPosition)
        self.edit_busca.textChanged.connect(self._carregar)
        self.content_layout.addWidget(self.edit_busca)

        # Scroll + grid
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setObjectName("scroll_area")
        self._scroll_content = QWidget()
        self._scroll_content.setObjectName("scroll_content")
        self._grid = QGridLayout(self._scroll_content)
        self._grid.setSpacing(14)
        self._grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll.setWidget(self._scroll_content)
        self.content_layout.addWidget(scroll)

    def _carregar(self):
        for i in reversed(range(self._grid.count())):
            w = self._grid.itemAt(i).widget()
            if w:
                w.setParent(None)

        filtro = self.edit_busca.text().strip()
        try:
            entregas = db.listar_entregas(filtro)
        except Exception as e:
            lbl = QLabel(f"Erro ao carregar entregas: {e}")
            lbl.setObjectName("txt_cinza")
            self._grid.addWidget(lbl, 0, 0)
            return

        if not entregas:
            lbl = QLabel("Nenhuma entrega encontrada.")
            lbl.setObjectName("txt_cinza")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._grid.addWidget(lbl, 0, 0)
            return

        row, col = 0, 0
        for e in entregas:
            card = EntregaCard(e, self._excluir, self._imprimir)
            self._grid.addWidget(card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

    def _imprimir(self, entrega: dict):
        try:
            from component.notas import gerar_nota_entrega
            os_id = entrega.get("ordem_servico_id")
            servicos = db.obter_servicos_da_ordem(os_id) if os_id else []
            total_servicos = sum(float(s.get("preco_servico_snapshot") or 0) for s in servicos)

            dados_entrega = {
                "ordem_servico_id":  os_id,
                "condicao":          entrega.get("condicao"),
                "cliente_id":        entrega.get("cliente_id"),
                "tecnico_id":        entrega.get("tecnico_id"),
                "data":              entrega.get("data"),
                "observacoes":       entrega.get("observacoes"),
                "laudo":             entrega.get("laudo"),
                "desconto":          entrega.get("desconto", 0),
                "forma_pagamento":   entrega.get("forma_pagamento"),
                "parcelamento":      entrega.get("parcelamento"),
                "garantia":          entrega.get("garantia"),
                "data_fim_garantia": entrega.get("data_fim_garantia"),
                "valor_total":       entrega.get("valor_total"),
            }
            ordem = {
                "id":                os_id,
                "cliente_nome":      entrega.get("cliente_nome") or "Balcão",
                "cliente_telefone":  entrega.get("cliente_telefone") or "",
                "modelo":            entrega.get("modelo") or "—",
                "cor":               entrega.get("cor") or "",
                "tecnico_nome":      entrega.get("tecnico_nome") or "—",
                "servicos": [
                    {"nome": s.get("nome_servico_snapshot", "—"),
                     "preco": s.get("preco_servico_snapshot", 0)}
                    for s in servicos
                ],
                "total_servicos": total_servicos,
            }
            gerar_nota_entrega(dados_entrega, ordem)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao imprimir:\n{e}")

    def _excluir(self, entrega_id: int):
        resp = QMessageBox.question(
            self, "Excluir entrega",
            f"Excluir entrega #{entrega_id}?\nIsso não reverterá o status da OS.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp != QMessageBox.StandardButton.Yes:
            return
        try:
            db.excluir_ordem_entrega(entrega_id)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao excluir:\n{e}")
            return
        self._carregar()

    def _aplicar_estilos(self):
        self._card.setStyleSheet(self._card.styleSheet() + """
        QWidget { background-color: #0F172A; font-family: 'Poppins', 'Montserrat', sans-serif; }
        QLineEdit#busca_input {
            background-color: #0B1120; border: 1px solid #1E293B;
            border-radius: 8px; padding: 10px 14px; color: #FFFFFF; font-size: 13px;
        }
        QLineEdit#busca_input:focus { border: 1px solid #F26522; }
        QScrollArea#scroll_area { border: none; background-color: transparent; }
        QWidget#scroll_content { background-color: transparent; }
        QScrollBar:vertical { border: none; background-color: #0B1120; width: 8px; border-radius: 4px; }
        QScrollBar::handle:vertical { background-color: #1E293B; min-height: 20px; border-radius: 4px; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }
        QFrame#entrega_card {
            background-color: #0B1120; border: 1px solid #1E293B; border-radius: 12px;
        }
        QLabel#icone_card { background-color: #1E293B; border-radius: 6px; padding: 5px; }
        QLabel#txt_branca_bold { color: #FFFFFF; font-size: 13px; font-weight: 700; }
        QLabel#txt_branca      { color: #FFFFFF; font-size: 12px; }
        QLabel#txt_cinza       { color: #64748B; font-size: 12px; }
        QLabel#txt_cinza_pequeno { color: #64748B; font-size: 11px; }
        QLabel#txt_laranja     { color: #F26522; font-size: 12px; font-weight: 600; }
        QLabel#txt_laranja_bold { color: #F26522; font-size: 14px; font-weight: 700; }
        QFrame#sep_card { background-color: #1E293B; max-height: 1px; border: none; }
        QPushButton#btn_imprimir { background-color: transparent; border: none; }
        QPushButton#btn_imprimir:hover { background-color: rgba(148,163,184,0.1); border-radius: 4px; }
        QPushButton#btn_lixeira { background-color: transparent; border: none; }
        QPushButton#btn_lixeira:hover { background-color: rgba(239,68,68,0.1); border-radius: 4px; }
        """)
