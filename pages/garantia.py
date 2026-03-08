import sys
import os
from datetime import date

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QLineEdit, QPushButton, QFrame,
    QSpacerItem, QSizePolicy, QScrollArea, QGridLayout,
    QButtonGroup
)
from PyQt6.QtCore import Qt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db


# ──────────────────────────────────────────────
# COMPONENTES
# ──────────────────────────────────────────────

class StatCard(QFrame):
    def __init__(self, titulo: str, valor: str, icone: str, subtitulo: str = None):
        super().__init__()
        self.setObjectName("stat_card")
        self.setMinimumHeight(110)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(4)

        top = QHBoxLayout()
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("stat_titulo")
        lbl_icone = QLabel(icone)
        lbl_icone.setObjectName("stat_icone")
        lbl_icone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top.addWidget(lbl_titulo)
        top.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        top.addWidget(lbl_icone)
        layout.addLayout(top)

        self.lbl_valor = QLabel(valor)
        self.lbl_valor.setObjectName("stat_valor")
        layout.addWidget(self.lbl_valor)

        if subtitulo:
            lbl_sub = QLabel(subtitulo)
            lbl_sub.setObjectName("stat_subtitulo")
            layout.addWidget(lbl_sub)

        layout.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))


class GarantiaCard(QFrame):
    """Card de uma garantia ativa."""
    def __init__(self, garantia: dict):
        super().__init__()
        self.setObjectName("garantia_card")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(10)

        # ─ Linha 1: cliente + OS id ─
        top = QHBoxLayout()
        lbl_cliente = QLabel(garantia.get("cliente_nome", "—"))
        lbl_cliente.setObjectName("g_cliente")
        lbl_os = QLabel(f"OS #{garantia.get('ordem_servico_id', '?')}")
        lbl_os.setObjectName("g_tag")
        top.addWidget(lbl_cliente)
        top.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        top.addWidget(lbl_os)
        layout.addLayout(top)

        # ─ Linha 2: modelo ─
        lbl_modelo = QLabel(f"📱 {garantia.get('modelo', '—')}")
        lbl_modelo.setObjectName("g_modelo")
        layout.addWidget(lbl_modelo)

        # ─ Linha 3: tipo de garantia ─
        lbl_tipo = QLabel(f"🛡️ {garantia.get('garantia', '—')}")
        lbl_tipo.setObjectName("g_info")
        layout.addWidget(lbl_tipo)

        # ─ Linha 4: datas ─
        datas_layout = QHBoxLayout()
        data_entrega = garantia.get("data", "")
        data_fim = garantia.get("data_fim_garantia", "")

        # Calcula dias restantes
        try:
            fim = date.fromisoformat(data_fim)
            dias = (fim - date.today()).days
            cor_dias = "#4ADE80" if dias > 30 else ("#FDE047" if dias > 7 else "#F87171")
            txt_dias = f"{dias}d restantes"
        except Exception:
            cor_dias = "#64748B"
            txt_dias = "—"

        lbl_entrega = QLabel(f"Entrega: {data_entrega[:10] if data_entrega else '—'}")
        lbl_entrega.setObjectName("g_info")

        lbl_fim = QLabel(f"Vence: {data_fim or '—'}")
        lbl_fim.setObjectName("g_info")

        lbl_dias = QLabel(txt_dias)
        lbl_dias.setStyleSheet(f"color: {cor_dias}; font-size: 11px; font-weight: 700;")

        datas_layout.addWidget(lbl_entrega)
        datas_layout.addWidget(lbl_fim)
        datas_layout.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        datas_layout.addWidget(lbl_dias)
        layout.addLayout(datas_layout)

        # ─ Linha 5: valor ─
        valor = garantia.get("valor_total")
        if valor is not None:
            lbl_valor = QLabel(f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
            lbl_valor.setObjectName("g_valor")
            layout.addWidget(lbl_valor)


# ──────────────────────────────────────────────
# TELA PRINCIPAL
# ──────────────────────────────────────────────

class GarantiasRMAScreen(QWidget):
    def __init__(self):
        super().__init__()
        db.inicializar_estado()
        self.initUI()

    def initUI(self):
        self.setMinimumSize(1000, 700)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(25)

        # ─ Cabeçalho ─
        header = QHBoxLayout()
        titulos = QVBoxLayout()
        titulos.setSpacing(0)
        lbl_titulo = QLabel("GARANTIAS & RMA")
        lbl_titulo.setObjectName("title_main")
        lbl_sub = QLabel("Gestão de coberturas e retornos")
        lbl_sub.setObjectName("subtitle")
        titulos.addWidget(lbl_titulo)
        titulos.addWidget(lbl_sub)
        header.addLayout(titulos)
        header.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.main_layout.addLayout(header)

        # ─ Cards de Estatísticas ─
        self.card_ativas  = StatCard("Garantias Ativas",  "0",       "🛡️")
        self.card_vencendo = StatCard("Vencem em 7 dias", "0",       "⏱️")
        self.card_custo   = StatCard("Valor Coberto",     "R$ 0,00", "💰", "total em serviços com garantia")

        stats = QHBoxLayout()
        stats.setSpacing(20)
        stats.addWidget(self.card_ativas)
        stats.addWidget(self.card_vencendo)
        stats.addWidget(self.card_custo)
        self.main_layout.addLayout(stats)

        # ─ Abas ─
        abas_layout = QHBoxLayout()
        self.grupo_abas = QButtonGroup(self)
        for i, texto in enumerate(["🛡️ Coberturas Ativas", "↺ Retornos (RMA)"]):
            btn = QPushButton(texto)
            btn.setObjectName("btn_aba")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.grupo_abas.addButton(btn, i)
            abas_layout.addWidget(btn)
            if i == 0:
                btn.setChecked(True)
        abas_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.grupo_abas.idClicked.connect(self._mudar_aba)
        self.main_layout.addLayout(abas_layout)

        # ─ Busca ─
        self.edit_busca = QLineEdit()
        self.edit_busca.setPlaceholderText("🔍 Buscar por cliente, OS ou modelo...")
        self.edit_busca.textChanged.connect(lambda t: self._carregar_garantias(filtro=t))
        self.main_layout.addWidget(self.edit_busca)

        # ─ Scroll + Grid ─
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_area")

        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scroll_content")

        self.grid = QGridLayout(self.scroll_content)
        self.grid.setSpacing(20)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

        self.aplicar_estilos()
        self._carregar_garantias()

    # ─ Lógica ─────────────────────────────────

    def _carregar_garantias(self, filtro: str = ""):
        # Limpa grid
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.deleteLater()

        garantias = db.listar_garantias_ativas()

        if filtro:
            f = filtro.lower()
            garantias = [
                g for g in garantias
                if f in (g.get("cliente_nome") or "").lower()
                or f in str(g.get("ordem_servico_id") or "")
                or f in (g.get("modelo") or "").lower()
            ]

        # Atualiza stats
        total = len(garantias)
        vencendo = sum(
            1 for g in garantias
            if g.get("data_fim_garantia") and
               (date.fromisoformat(g["data_fim_garantia"]) - date.today()).days <= 7
        )
        valor_total = sum(g.get("valor_total") or 0 for g in garantias)

        self.card_ativas.lbl_valor.setText(str(total))
        self.card_vencendo.lbl_valor.setText(str(vencendo))
        self.card_custo.lbl_valor.setText(
            f"R$ {valor_total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

        if not garantias:
            lbl = QLabel("Nenhuma garantia ativa encontrada.")
            lbl.setObjectName("empty_text")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid.addWidget(lbl, 0, 0, 1, 2)
            return

        row, col = 0, 0
        for g in garantias:
            card = GarantiaCard(g)
            self.grid.addWidget(card, row, col)
            col += 1
            if col > 1:
                col = 0
                row += 1

    def _mudar_aba(self, index: int):
        # Aba 1 (RMA) ainda sem implementação — mostra estado vazio
        self._carregar_garantias(filtro=self.edit_busca.text())

    # ─ Estilos ────────────────────────────────

    def aplicar_estilos(self):
        self.setStyleSheet("""
        QWidget {
            background-color: #0F172A;
            font-family: 'Poppins', 'Montserrat', sans-serif;
        }

        QLabel#title_main { color: #FFFFFF; font-size: 24px; font-weight: 700; }
        QLabel#subtitle   { color: #64748B; font-size: 12px; font-weight: 600; }

        /* Stats */
        QFrame#stat_card {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 12px;
        }
        QLabel#stat_titulo   { color: #64748B; font-size: 12px; font-weight: 600; }
        QLabel#stat_valor    { color: #FFFFFF;  font-size: 28px; font-weight: 700; }
        QLabel#stat_subtitulo{ color: #64748B; font-size: 10px; }
        QLabel#stat_icone {
            background-color: rgba(242,101,34,0.1);
            color: #F26522;
            font-size: 16px;
            border-radius: 8px;
            min-width: 36px; max-width: 36px;
            min-height: 36px; max-height: 36px;
        }

        /* Abas */
        QPushButton#btn_aba {
            background-color: transparent;
            color: #64748B;
            border: 1px solid #1E293B;
            border-radius: 6px;
            padding: 8px 16px;
            font-size: 13px;
            font-weight: 600;
        }
        QPushButton#btn_aba:checked {
            background-color: rgba(242,101,34,0.1);
            color: #F26522;
            border: 1px solid #F26522;
        }
        QPushButton#btn_aba:hover:!checked { background-color: #0B1120; }

        /* Busca */
        QLineEdit {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 8px;
            padding: 12px;
            color: #FFFFFF;
            font-size: 13px;
        }
        QLineEdit:focus { border: 1px solid #F26522; }

        /* Scroll */
        QScrollArea#scroll_area { border: none; background-color: transparent; }
        QWidget#scroll_content  { background-color: transparent; }
        QScrollBar:vertical { border: none; background-color: #0B1120; width: 8px; border-radius: 4px; }
        QScrollBar::handle:vertical { background-color: #1E293B; min-height: 20px; border-radius: 4px; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }

        /* Card de Garantia */
        QFrame#garantia_card {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 12px;
        }
        QFrame#garantia_card:hover { border: 1px solid #64748B; }

        QLabel#g_cliente { color: #FFFFFF; font-size: 15px; font-weight: 700; }
        QLabel#g_tag {
            background-color: rgba(242,101,34,0.1);
            color: #F26522;
            font-size: 10px;
            font-weight: 700;
            border-radius: 4px;
            padding: 3px 8px;
        }
        QLabel#g_modelo { color: #94A3B8; font-size: 13px; }
        QLabel#g_info   { color: #64748B; font-size: 11px; }
        QLabel#g_valor  { color: #F26522; font-size: 14px; font-weight: 700; }

        /* Estado vazio */
        QLabel#empty_text { color: #64748B; font-size: 14px; font-weight: 600; }
        """)
