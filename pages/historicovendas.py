# historicovendas.py — Histórico de Vendas (ModernDialog)
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


# ──────────────────────────────────────────────
# VendaCard
# ──────────────────────────────────────────────

class VendaCard(QFrame):
    def __init__(self, venda: dict, on_excluir, on_imprimir):
        super().__init__()
        self.setObjectName("venda_card")
        self.setFixedWidth(320)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 16)
        layout.setSpacing(10)

        # ── Cabeçalho ──
        header = QHBoxLayout()
        ico = QLabel()
        ico.setObjectName("icone_card")
        if _SVG_OK:
            ico.setPixmap(svg_para_pixmap("fi-sr-receipt.svg", "#F26522", 18, 18))
        else:
            ico.setText("🧾")

        info = QVBoxLayout()
        info.setSpacing(2)
        lbl_cliente = QLabel(venda.get("cliente_nome") or "Balcão")
        lbl_cliente.setObjectName("txt_branca_bold")
        lbl_cliente.setWordWrap(True)
        lbl_data = QLabel(_fmt_data(venda.get("data_venda", "")))
        lbl_data.setObjectName("txt_cinza")
        info.addWidget(lbl_cliente)
        info.addWidget(lbl_data)

        header.addWidget(ico)
        header.addLayout(info)
        header.addItem(QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        lbl_id = QLabel(f"#{venda['id']}")
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
        btn_print.clicked.connect(lambda: on_imprimir(venda))
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
        btn_del.clicked.connect(lambda: on_excluir(venda["id"]))
        header.addWidget(btn_del)
        layout.addLayout(header)

        sep = QFrame()
        sep.setFrameShape(QFrame.Shape.HLine)
        sep.setObjectName("sep_card")
        layout.addWidget(sep)

        # ── Itens ──
        itens = venda.get("itens", [])
        if itens:
            lbl_it = QLabel("Itens:")
            lbl_it.setObjectName("txt_cinza_pequeno")
            layout.addWidget(lbl_it)
            for item in itens:
                row = QHBoxLayout()
                lbl_nome = QLabel(f"{item.get('qtd', 1)}× {item.get('nome', '—')}")
                lbl_nome.setObjectName("txt_branca")
                lbl_nome.setWordWrap(True)
                lbl_sub = QLabel(_fmt_valor(item.get("subtotal")))
                lbl_sub.setObjectName("txt_laranja")
                row.addWidget(lbl_nome)
                row.addItem(QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
                row.addWidget(lbl_sub)
                layout.addLayout(row)
        else:
            lbl_sem = QLabel("Venda avulsa")
            lbl_sem.setObjectName("txt_cinza")
            layout.addWidget(lbl_sem)

        sep2 = QFrame()
        sep2.setFrameShape(QFrame.Shape.HLine)
        sep2.setObjectName("sep_card")
        layout.addWidget(sep2)

        # ── Rodapé ──
        forma = venda.get("forma_pagamento") or "—"
        parcelas = venda.get("parcelamento") or ""
        foot = QHBoxLayout()
        lbl_pag = QLabel(f"{forma}  {parcelas}".strip())
        lbl_pag.setObjectName("txt_cinza_pequeno")
        lbl_total = QLabel(_fmt_valor(venda.get("valor_total")))
        lbl_total.setObjectName("txt_laranja_bold")
        foot.addWidget(lbl_pag)
        foot.addItem(QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        foot.addWidget(lbl_total)
        layout.addLayout(foot)


# ──────────────────────────────────────────────
# Dialog principal
# ──────────────────────────────────────────────

class HistoricoVendasDialog(ModernDialog):
    def __init__(self, parent=None):
        super().__init__("Histórico de Vendas", 1060, 660, parent)
        self._build()
        self._aplicar_estilos()
        self._carregar()

    def _build(self):
        # Busca
        self.edit_busca = QLineEdit()
        self.edit_busca.setPlaceholderText("Buscar por cliente, forma de pagamento ou ID...")
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
            vendas = db.listar_vendas(filtro)
        except Exception as e:
            lbl = QLabel(f"Erro ao carregar vendas: {e}")
            lbl.setObjectName("txt_cinza")
            self._grid.addWidget(lbl, 0, 0)
            return

        if not vendas:
            lbl = QLabel("Nenhuma venda encontrada.")
            lbl.setObjectName("txt_cinza")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self._grid.addWidget(lbl, 0, 0)
            return

        row, col = 0, 0
        for v in vendas:
            card = VendaCard(v, self._excluir, self._imprimir)
            self._grid.addWidget(card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

    def _imprimir(self, venda: dict):
        try:
            from component.notas import imprimir_venda
            imprimir_venda(
                venda_id=venda["id"],
                itens=venda.get("itens", []),
                cliente_nome=venda.get("cliente_nome") or "Balcão",
                forma_pagamento=venda.get("forma_pagamento") or "—",
                parcelamento=venda.get("parcelamento") or "À vista",
                total=float(venda.get("valor_total") or 0),
                desconto=float(venda.get("desconto") or 0),
            )
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao imprimir:\n{e}")

    def _excluir(self, venda_id: int):
        resp = QMessageBox.question(
            self, "Excluir venda",
            f"Excluir venda #{venda_id}? O estoque será restaurado.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp != QMessageBox.StandardButton.Yes:
            return
        try:
            db.excluir_venda(venda_id)
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
        QFrame#venda_card {
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
