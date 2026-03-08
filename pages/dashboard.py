import sys
import os
from datetime import date, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QSpacerItem,
    QSizePolicy, QScrollArea, QButtonGroup
)
from PyQt6.QtCore import Qt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db


# ──────────────────────────────────────────────
# Períodos disponíveis nos filtros
# ──────────────────────────────────────────────
PERIODOS = {
    "1 Dia":      timedelta(days=1),
    "1 Semana":   timedelta(weeks=1),
    "1 Quinzena": timedelta(days=15),
    "1 Mês":      timedelta(days=30),
    "3 Meses":    timedelta(days=90),
    "Tudo":       None,
}


# ──────────────────────────────────────────────
# COMPONENTES
# ──────────────────────────────────────────────

def _icone_bg(cor: str) -> str:
    mapa = {
        "#F26522": "rgba(242,101,34,0.1)",
        "#4ADE80": "rgba(74,222,128,0.1)",
        "#EAB308": "rgba(234,179,8,0.1)",
    }
    return mapa.get(cor, "rgba(255,255,255,0.05)")


class DashboardCard(QFrame):
    def __init__(self, titulo: str, valor: str, subtitulo: str,
                 icone: str, cor_icone: str, destaque: bool = False):
        super().__init__()
        self.setObjectName("card_dash_destaque" if destaque else "card_dash")
        self.setFixedSize(250, 160)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        # ─ Linha 1: título + ícone ─
        top = QHBoxLayout()
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("card_titulo")
        lbl_titulo.setWordWrap(True)
        top.addWidget(lbl_titulo)
        top.addItem(QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        lbl_icone = QLabel(icone)
        lbl_icone.setObjectName("card_icone")
        lbl_icone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icone.setStyleSheet(
            f"color: {cor_icone}; background-color: {_icone_bg(cor_icone)};"
        )
        top.addWidget(lbl_icone)
        layout.addLayout(top)

        layout.addItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # ─ Linha 2: valor (atualizado dinamicamente) ─
        self.lbl_valor = QLabel(valor)
        self.lbl_valor.setObjectName("card_valor")
        layout.addWidget(self.lbl_valor)

        # ─ Linha 3: subtítulo ─
        lbl_sub = QLabel(subtitulo)
        lbl_sub.setObjectName("card_subtitulo")
        layout.addWidget(lbl_sub)


# ──────────────────────────────────────────────
# TELA PRINCIPAL
# ──────────────────────────────────────────────

class DashboardScreen(QWidget):

    # (titulo, subtítulo, ícone, cor, destaque, chave_kpi)
    _ESTRUTURA = [
        ("Taxa de Garantia",   "Retorno sobre serviços",    "🛡️", "#F26522", False, "taxa_garantia"),
        ("Ordens de Serviço",  "Total gerado no período",   "🔧", "#F26522", False, "os_total"),
        ("Faturamento",        "Receita bruta realizada",   "💲", "#4ADE80", False, "faturamento"),
        ("Gastos (Peças)",     "Custo operacional direto",  "📉", "#F26522", False, "gastos"),
        ("Custo Estoque",      "Capital investido",         "📦", "#F26522", False, "custo_estoque"),
        ("Lucro Líquido",      "Faturamento - Gastos",      "📈", "#4ADE80", True,  "lucro_liquido"),
        ("Ticket Médio",       "Por serviço realizado",     "💳", "#F26522", False, "ticket_medio"),
        ("OS Entregues",       "Serviços finalizados",      "✅", "#4ADE80", False, "os_entregues"),
        ("OS Pendentes",       "Em fila ou reparo",         "⚠️", "#EAB308", False, "os_pendentes"),
        ("Taxa Cancelamento",  "Serviços não aprovados",    "🚫", "#F26522", False, "taxa_cancelamento"),
        ("ROI s/ Estoque",     "Retorno sobre investimento","📊", "#F26522", False, "roi_estoque"),
        ("Potencial Estoque",  "Valor de venda total",      "📦", "#F26522", False, "potencial_estoque"),
    ]

    def __init__(self):
        super().__init__()
        db.inicializar_estado()
        self._periodo_ativo = "1 Mês"
        self._cards: dict[str, DashboardCard] = {}
        self.initUI()

    def initUI(self):
        self.setMinimumSize(1100, 800)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(25)

        # ─ Cabeçalho ─
        header = QHBoxLayout()
        titulos = QVBoxLayout()
        titulos.setSpacing(0)
        lbl_titulo = QLabel("Dashboard")
        lbl_titulo.setObjectName("title_main")
        lbl_sub = QLabel("Visão geral do negócio")
        lbl_sub.setObjectName("subtitle")
        titulos.addWidget(lbl_titulo)
        titulos.addWidget(lbl_sub)
        header.addLayout(titulos)
        header.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.main_layout.addLayout(header)

        # ─ Filtros de período ─
        filtros_layout = QHBoxLayout()
        filtros_layout.setSpacing(10)
        self.grupo_filtros = QButtonGroup(self)

        for i, texto in enumerate(PERIODOS):
            btn = QPushButton(texto)
            btn.setObjectName("btn_filtro")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.grupo_filtros.addButton(btn, i)
            filtros_layout.addWidget(btn)
            if texto == self._periodo_ativo:
                btn.setChecked(True)

        self.grupo_filtros.idClicked.connect(self._mudar_periodo)
        filtros_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.main_layout.addLayout(filtros_layout)

        # ─ Scroll + grid de cards ─
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("scroll_area")

        scroll_content = QWidget()
        scroll_content.setObjectName("scroll_content")

        grid = QGridLayout(scroll_content)
        grid.setSpacing(20)
        grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        row, col = 0, 0
        for titulo, sub, icone, cor, dest, chave in self._ESTRUTURA:
            card = DashboardCard(titulo, "—", sub, icone, cor, dest)
            self._cards[chave] = card
            grid.addWidget(card, row, col)
            col += 1
            if col > 3:
                col = 0
                row += 1

        scroll_area.setWidget(scroll_content)
        self.main_layout.addWidget(scroll_area)

        self.aplicar_estilos()
        self._atualizar_cards()

    # ─ Lógica ─────────────────────────────────

    def _atualizar_cards(self):
        delta = PERIODOS[self._periodo_ativo]
        data_inicio = (date.today() - delta).isoformat() if delta else None
        kpis = db.calcular_kpis(data_inicio)
        for chave, card in self._cards.items():
            card.lbl_valor.setText(kpis.get(chave, "—"))

    def _mudar_periodo(self, index: int):
        self._periodo_ativo = list(PERIODOS.keys())[index]
        self._atualizar_cards()

    # ─ Estilos ────────────────────────────────

    def aplicar_estilos(self):
        self.setStyleSheet("""
        QWidget {
            background-color: #0F172A;
            font-family: 'Poppins', 'Montserrat', sans-serif;
        }

        QLabel#title_main { color: #FFFFFF; font-size: 28px; font-weight: 700; }
        QLabel#subtitle   { color: #64748B; font-size: 12px; font-weight: 600; }

        /* Filtros de período */
        QPushButton#btn_filtro {
            background-color: transparent;
            color: #64748B;
            border: 1px solid #1E293B;
            border-radius: 16px;
            padding: 8px 18px;
            font-size: 12px;
            font-weight: 600;
        }
        QPushButton#btn_filtro:hover   { background-color: #1E293B; color: #FFFFFF; }
        QPushButton#btn_filtro:checked { background-color: #F26522; color: #FFFFFF; border: 1px solid #F26522; }

        /* Scroll */
        QScrollArea#scroll_area { border: none; background-color: transparent; }
        QWidget#scroll_content  { background-color: transparent; }
        QScrollBar:vertical { border: none; background-color: #0B1120; width: 8px; border-radius: 4px; }
        QScrollBar::handle:vertical { background-color: #1E293B; min-height: 20px; border-radius: 4px; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }

        /* Cards */
        QFrame#card_dash, QFrame#card_dash_destaque {
            background-color: #0B1120;
            border-radius: 12px;
        }
        QFrame#card_dash          { border: 1px solid #1E293B; }
        QFrame#card_dash_destaque { border: 1px solid #F26522; background-color: rgba(242,101,34,0.03); }

        QLabel#card_titulo    { color: #64748B; font-size: 12px; font-weight: 600; }
        QLabel#card_valor     { color: #FFFFFF; font-size: 24px; font-weight: 700; }
        QLabel#card_subtitulo { color: #64748B; font-size: 11px; }

        QLabel#card_icone {
            font-size: 16px; border-radius: 8px;
            min-width: 32px; max-width: 32px;
            min-height: 32px; max-height: 32px;
        }
        """)
