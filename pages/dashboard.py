import sys
import os
from datetime import date, timedelta

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QSpacerItem,
    QSizePolicy, QScrollArea, QButtonGroup
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db

try:
    from component.svg_utils import svg_para_pixmap
    _SVG_OK = True
except Exception:
    _SVG_OK = False

# Mapeamento: identificador → arquivo SVG em svg/
_ICONE_SVG = {
    # Assistência
    "os_total":            "fi-sr-tools.svg",
    "os_entregues":        "fi-sr-badge-check.svg",
    "os_pendentes":        "fi-sr-clock.svg",
    "taxa_cancelamento":   "fi-sr-ban.svg",
    "taxa_garantia":       "fi-sr-shield-check.svg",
    # Estoque
    "custo_estoque":       "fi-sr-box.svg",
    "potencial_estoque":   "fi-sr-chart-line-up.svg",
    "roi_estoque":         "fi-sr-chart-mixed.svg",
    # Financeiro
    "faturamento":         "fi-sr-money-bill-wave.svg",
    "lucro_liquido":       "fi-sr-chart-line-up.svg",
    "gastos":              "fi-sr-chart-mixed.svg",
    "ticket_medio":        "fi-sr-ticket.svg",
    # Controle
    "item_mais_vendido":   "fi-sr-trophy.svg",
    "servico_mais_prestado": "fi-sr-tools.svg",
    "melhor_cliente":      "fi-sr-crown.svg",
    "estoque_baixo":       "fi-sr-triangle-warning.svg",
}

# ──────────────────────────────────────────────
# Períodos
# ──────────────────────────────────────────────
PERIODOS = {
    "1 Dia":      timedelta(days=1),
    "1 Semana":   timedelta(weeks=1),
    "1 Quinzena": timedelta(days=15),
    "1 Mês":      timedelta(days=30),
    "3 Meses":    timedelta(days=90),
    "Tudo":       None,
}

MODOS_FIN = ["Serviços", "Vendas", "Ambos"]

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def _icone_bg(cor: str) -> str:
    return {
        "#F26522": "rgba(242,101,34,0.12)",
        "#4ADE80": "rgba(74,222,128,0.12)",
        "#EAB308": "rgba(234,179,8,0.12)",
        "#38BDF8": "rgba(56,189,248,0.12)",
        "#A78BFA": "rgba(167,139,250,0.12)",
    }.get(cor, "rgba(255,255,255,0.06)")


def _section_label(texto: str) -> QLabel:
    lbl = QLabel(texto)
    lbl.setObjectName("section_label")
    return lbl


def _separator() -> QFrame:
    f = QFrame()
    f.setFrameShape(QFrame.Shape.HLine)
    f.setObjectName("separator")
    return f


# ──────────────────────────────────────────────
# DashboardCard — card reutilizável
# ──────────────────────────────────────────────

class DashboardCard(QFrame):
    def __init__(self, titulo: str, valor: str, subtitulo: str,
                 icone: str, cor_icone: str, destaque: bool = False,
                 valor_pequeno: bool = False):
        super().__init__()
        self.setObjectName("card_dash_destaque" if destaque else "card_dash")
        self.setFixedSize(230, 150)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)

        # Linha 1: título + ícone
        top = QHBoxLayout()
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("card_titulo")
        lbl_titulo.setWordWrap(True)
        top.addWidget(lbl_titulo)
        top.addItem(QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        lbl_icone = QLabel()
        lbl_icone.setObjectName("card_icone")
        lbl_icone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_icone.setStyleSheet(
            f"background-color: {_icone_bg(cor_icone)};"
        )
        # Tenta renderizar o SVG correspondente à chave do ícone
        svg_file = _ICONE_SVG.get(icone, "")
        if _SVG_OK and svg_file:
            lbl_icone.setPixmap(svg_para_pixmap(svg_file, cor_icone, 16, 16))
        else:
            lbl_icone.setText(icone)
            lbl_icone.setStyleSheet(
                f"color: {cor_icone}; background-color: {_icone_bg(cor_icone)};"
            )
        top.addWidget(lbl_icone)
        layout.addLayout(top)

        layout.addItem(QSpacerItem(20, 6, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Linha 2: valor
        self.lbl_valor = QLabel(valor)
        self.lbl_valor.setObjectName("card_valor_small" if valor_pequeno else "card_valor")
        self.lbl_valor.setWordWrap(True)
        layout.addWidget(self.lbl_valor)

        # Linha 3: subtítulo
        lbl_sub = QLabel(subtitulo)
        lbl_sub.setObjectName("card_subtitulo")
        layout.addWidget(lbl_sub)


# ──────────────────────────────────────────────
# TecnicoCard
# ──────────────────────────────────────────────

class TecnicoCard(QFrame):
    def __init__(self, nome: str, faturamento: str, gastos: str, lucro: str):
        super().__init__()
        self.setObjectName("card_tecnico")
        self.setFixedSize(260, 150)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 18, 18, 18)
        layout.setSpacing(6)

        # Cabeçalho: avatar + nome
        top = QHBoxLayout()
        lbl_av = QLabel()
        lbl_av.setObjectName("tec_avatar")
        lbl_av.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if _SVG_OK:
            lbl_av.setPixmap(svg_para_pixmap("fi-sr-user.svg", "#F26522", 16, 16))
        else:
            lbl_av.setText("👤")
        top.addWidget(lbl_av)
        lbl_nome = QLabel(nome)
        lbl_nome.setObjectName("tec_nome")
        top.addWidget(lbl_nome)
        top.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addLayout(top)

        layout.addItem(QSpacerItem(10, 4, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # Stats grid: 3 colunas
        stats = QHBoxLayout()
        stats.setSpacing(8)
        for label, val, cor in [("Fat.", faturamento, "#4ADE80"), ("Gastos", gastos, "#F26522"), ("Lucro", lucro, "#38BDF8")]:
            col = QVBoxLayout()
            col.setSpacing(2)
            lbl_l = QLabel(label)
            lbl_l.setObjectName("tec_stat_label")
            lbl_v = QLabel(val)
            lbl_v.setObjectName("tec_stat_val")
            lbl_v.setStyleSheet(f"color: {cor};")
            col.addWidget(lbl_l)
            col.addWidget(lbl_v)
            stats.addLayout(col)
        layout.addLayout(stats)


# ──────────────────────────────────────────────
# TELA PRINCIPAL
# ──────────────────────────────────────────────

class DashboardScreen(QWidget):

    # ── Estrutura estática das seções ──────────
    # Grid 1 — Assistência
    # O 3.º item (icone) agora é a CHAVE usada em _ICONE_SVG; se não tiver SVG, cai no emoji.
    _ASSISTENCIA = [
        ("Ordens de Serviço",  "Total no período",          "os_total",          "#F26522", False, "os_total"),
        ("OS Entregues",       "Serviços finalizados",       "os_entregues",      "#4ADE80", False, "os_entregues"),
        ("OS Pendentes",       "Em fila ou reparo",          "os_pendentes",      "#EAB308", False, "os_pendentes"),
        ("Taxa Cancelamento",  "Serviços não aprovados",     "taxa_cancelamento", "#F26522", False, "taxa_cancelamento"),
        ("Taxa de Garantia",   "Retorno pós-entrega",        "taxa_garantia",     "#38BDF8", False, "taxa_garantia"),
    ]

    # Grid 2 — Vendas (Estoque)
    _VENDAS_ESTOQUE = [
        ("Custo Estoque",      "Capital investido",          "custo_estoque",     "#F26522", False, "custo_estoque"),
        ("Potencial Estoque",  "Valor de venda total",       "potencial_estoque", "#4ADE80", False, "potencial_estoque"),
        ("ROI s/ Estoque",     "Retorno sobre investimento", "roi_estoque",       "#38BDF8", False, "roi_estoque"),
    ]

    # Grid 3 — Financeiro (dinâmico via filtro)
    _FINANCEIRO = [
        ("Faturamento",   "Receita bruta realizada",  "faturamento",   "#4ADE80", True,  "faturamento"),
        ("Lucro Líquido", "Faturamento − Gastos",     "lucro_liquido", "#4ADE80", False, "lucro_liquido"),
        ("Gastos",        "Custo operacional direto", "gastos",        "#F26522", False, "gastos"),
        ("Ticket Médio",  "Valor médio por operação", "ticket_medio",  "#38BDF8", False, "ticket_medio"),
    ]

    # Grid 4 — Controle
    _CONTROLE = [
        ("Item mais Vendido",      "Produto com maior saída",   "item_mais_vendido",     "#EAB308", False, "item_mais_vendido",     True),
        ("Serviço mais Prestado",  "Serviço com maior demanda", "servico_mais_prestado", "#F26522", False, "servico_mais_prestado", True),
        ("Melhor Cliente",         "Maior retorno financeiro",  "melhor_cliente",        "#4ADE80", True,  "melhor_cliente",        True),
        ("Estoque Baixo",          "Produtos com ≤ 3 unidades", "estoque_baixo",         "#EAB308", False, "estoque_baixo",         False),
    ]

    def __init__(self):
        super().__init__()
        db.inicializar_estado()
        self._periodo_ativo = "1 Mês"
        self._modo_fin = "Ambos"          # filtro do bloco financeiro
        self._cards: dict[str, DashboardCard] = {}
        self._tec_container: QWidget | None = None
        self._tec_layout: QHBoxLayout | None = None
        self.initUI()

    # ──────────────────────────────────────────
    # UI
    # ──────────────────────────────────────────

    def initUI(self):
        self.setMinimumSize(1100, 800)

        outer = QVBoxLayout(self)
        outer.setContentsMargins(40, 40, 40, 40)
        outer.setSpacing(0)

        # ─ Cabeçalho ─
        header = QHBoxLayout()
        titulos = QVBoxLayout()
        titulos.setSpacing(0)
        lbl_t = QLabel("Dashboard")
        lbl_t.setObjectName("title_main")
        lbl_s = QLabel("Visão geral do negócio")
        lbl_s.setObjectName("subtitle")
        titulos.addWidget(lbl_t)
        titulos.addWidget(lbl_s)
        header.addLayout(titulos)
        header.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        outer.addLayout(header)
        outer.addSpacing(20)

        # ─ Filtros de período ─
        fil_layout = QHBoxLayout()
        fil_layout.setSpacing(8)
        self.grupo_filtros = QButtonGroup(self)
        for i, texto in enumerate(PERIODOS):
            btn = QPushButton(texto)
            btn.setObjectName("btn_filtro")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.grupo_filtros.addButton(btn, i)
            fil_layout.addWidget(btn)
            if texto == self._periodo_ativo:
                btn.setChecked(True)
        self.grupo_filtros.idClicked.connect(self._mudar_periodo)
        fil_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        outer.addLayout(fil_layout)
        outer.addSpacing(25)

        # ─ Scroll ─
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("scroll_area")

        self._scroll_content = QWidget()
        self._scroll_content.setObjectName("scroll_content")

        self._content_layout = QVBoxLayout(self._scroll_content)
        self._content_layout.setSpacing(30)
        self._content_layout.setContentsMargins(0, 0, 10, 20)
        self._content_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        # ── Bloco 1: Assistência ──
        self._content_layout.addWidget(_section_label("Assistência Técnica"))
        self._content_layout.addWidget(_separator())
        row1 = QHBoxLayout()
        row1.setSpacing(16)
        row1.setAlignment(Qt.AlignmentFlag.AlignLeft)
        for titulo, sub, icone, cor, dest, chave in self._ASSISTENCIA:
            card = DashboardCard(titulo, "—", sub, icone, cor, dest)
            self._cards[chave] = card
            row1.addWidget(card)
        self._content_layout.addLayout(row1)

        # ── Bloco 2: Estoque ──
        self._content_layout.addSpacing(5)
        self._content_layout.addWidget(_section_label("Estoque"))
        self._content_layout.addWidget(_separator())
        row2 = QHBoxLayout()
        row2.setSpacing(16)
        row2.setAlignment(Qt.AlignmentFlag.AlignLeft)
        for titulo, sub, icone, cor, dest, chave in self._VENDAS_ESTOQUE:
            card = DashboardCard(titulo, "—", sub, icone, cor, dest)
            self._cards[chave] = card
            row2.addWidget(card)
        self._content_layout.addLayout(row2)

        # ── Bloco 3: Financeiro ──
        self._content_layout.addSpacing(5)
        fin_header = QHBoxLayout()
        fin_header.setSpacing(12)
        fin_header.addWidget(_section_label("Financeiro"))
        fin_header.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.grupo_fin = QButtonGroup(self)
        for i, modo in enumerate(MODOS_FIN):
            btn = QPushButton(modo)
            btn.setObjectName("btn_filtro_mini")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            self.grupo_fin.addButton(btn, i)
            fin_header.addWidget(btn)
            if modo == self._modo_fin:
                btn.setChecked(True)
        self.grupo_fin.idClicked.connect(self._mudar_modo_fin)
        self._content_layout.addLayout(fin_header)
        self._content_layout.addWidget(_separator())

        row3 = QHBoxLayout()
        row3.setSpacing(16)
        row3.setAlignment(Qt.AlignmentFlag.AlignLeft)
        for titulo, sub, icone, cor, dest, chave in self._FINANCEIRO:
            card = DashboardCard(titulo, "—", sub, icone, cor, dest)
            self._cards[chave] = card
            row3.addWidget(card)
        self._content_layout.addLayout(row3)

        # ── Bloco 4: Controle ──
        self._content_layout.addSpacing(5)
        self._content_layout.addWidget(_section_label("Controle"))
        self._content_layout.addWidget(_separator())
        row4 = QHBoxLayout()
        row4.setSpacing(16)
        row4.setAlignment(Qt.AlignmentFlag.AlignLeft)
        for titulo, sub, icone, cor, dest, chave, pequeno in self._CONTROLE:
            card = DashboardCard(titulo, "—", sub, icone, cor, dest, valor_pequeno=pequeno)
            self._cards[chave] = card
            row4.addWidget(card)
        self._content_layout.addLayout(row4)

        # ── Bloco 5: Técnicos ──
        self._content_layout.addSpacing(5)
        self._content_layout.addWidget(_section_label("Técnicos"))
        self._content_layout.addWidget(_separator())

        self._tec_container = QWidget()
        self._tec_layout = QHBoxLayout(self._tec_container)
        self._tec_layout.setSpacing(16)
        self._tec_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self._tec_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.addWidget(self._tec_container)

        self._content_layout.addItem(
            QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

        scroll_area.setWidget(self._scroll_content)
        outer.addWidget(scroll_area)

        self.aplicar_estilos()
        self._atualizar_tudo()

    # ──────────────────────────────────────────
    # Lógica
    # ──────────────────────────────────────────

    def _data_inicio(self) -> str | None:
        delta = PERIODOS[self._periodo_ativo]
        return (date.today() - delta).isoformat() if delta else None

    def _atualizar_tudo(self):
        di = self._data_inicio()
        self._atualizar_assistencia(di)
        self._atualizar_estoque(di)
        self._atualizar_financeiro(di)
        self._atualizar_controle(di)
        self._atualizar_tecnicos(di)

    def _atualizar_assistencia(self, di):
        try:
            kpis = db.calcular_kpis(di)
            for chave in ("os_total", "os_entregues", "os_pendentes", "taxa_cancelamento", "taxa_garantia"):
                if chave in self._cards:
                    self._cards[chave].lbl_valor.setText(kpis.get(chave, "—"))
        except Exception:
            pass

    def _atualizar_estoque(self, di):
        try:
            kpis = db.calcular_kpis(di)
            for chave in ("custo_estoque", "potencial_estoque", "roi_estoque"):
                if chave in self._cards:
                    self._cards[chave].lbl_valor.setText(kpis.get(chave, "—"))
        except Exception:
            pass

    def _atualizar_financeiro(self, di):
        try:
            modo = self._modo_fin.lower().replace("ó", "o").replace("é", "e")  # "ambos"/"servicos"/"vendas"
            mapa = {"servicos": "servicos", "vendas": "vendas", "ambos": "ambos"}
            modo_db = mapa.get(modo, "ambos")
            kpis = db.calcular_kpis_financeiro(di, modo_db)
            for chave in ("faturamento", "lucro_liquido", "gastos", "ticket_medio"):
                if chave in self._cards:
                    self._cards[chave].lbl_valor.setText(kpis.get(chave, "—"))
        except Exception:
            pass

    def _atualizar_controle(self, di):
        try:
            kpis = db.calcular_controle_kpis(di)
            for chave in ("item_mais_vendido", "servico_mais_prestado", "melhor_cliente", "estoque_baixo"):
                if chave in self._cards:
                    self._cards[chave].lbl_valor.setText(kpis.get(chave, "—"))
        except Exception:
            pass

    def _atualizar_tecnicos(self, di):
        if not self._tec_layout:
            return
        # Limpa cards antigos
        while self._tec_layout.count():
            item = self._tec_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        try:
            tecnicos = db.calcular_kpis_tecnicos(di)
            if not tecnicos:
                lbl = QLabel("Nenhum técnico cadastrado.")
                lbl.setObjectName("subtitle")
                self._tec_layout.addWidget(lbl)
                return
            for t in tecnicos:
                card = TecnicoCard(t["nome"], t["faturamento"], t["gastos"], t["lucro"])
                self._tec_layout.addWidget(card)
        except Exception:
            pass

    def _mudar_periodo(self, index: int):
        self._periodo_ativo = list(PERIODOS.keys())[index]
        self._atualizar_tudo()

    def _mudar_modo_fin(self, index: int):
        self._modo_fin = MODOS_FIN[index]
        self._atualizar_financeiro(self._data_inicio())

    # ──────────────────────────────────────────
    # Estilos
    # ──────────────────────────────────────────

    def aplicar_estilos(self):
        self.setStyleSheet("""
        QWidget {
            background-color: #0F172A;
            font-family: 'Poppins', 'Montserrat', sans-serif;
        }

        QLabel#title_main { color: #FFFFFF; font-size: 28px; font-weight: 700; }
        QLabel#subtitle   { color: #64748B; font-size: 12px; font-weight: 600; }

        QLabel#section_label {
            color: #FFFFFF;
            font-size: 15px;
            font-weight: 700;
            padding-top: 4px;
        }
        QFrame#separator {
            background-color: #1E293B;
            max-height: 1px;
            border: none;
        }

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

        /* Filtro mini (financeiro) */
        QPushButton#btn_filtro_mini {
            background-color: transparent;
            color: #64748B;
            border: 1px solid #1E293B;
            border-radius: 12px;
            padding: 5px 14px;
            font-size: 11px;
            font-weight: 600;
        }
        QPushButton#btn_filtro_mini:hover   { background-color: #1E293B; color: #FFFFFF; }
        QPushButton#btn_filtro_mini:checked { background-color: #1E3A5F; color: #38BDF8; border: 1px solid #38BDF8; }

        /* Scroll */
        QScrollArea#scroll_area { border: none; background-color: transparent; }
        QWidget#scroll_content  { background-color: transparent; }
        QScrollBar:vertical { border: none; background-color: #0B1120; width: 8px; border-radius: 4px; }
        QScrollBar::handle:vertical { background-color: #1E293B; min-height: 20px; border-radius: 4px; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }

        /* Cards padrão */
        QFrame#card_dash, QFrame#card_dash_destaque {
            background-color: #0B1120;
            border-radius: 12px;
        }
        QFrame#card_dash          { border: 1px solid #1E293B; }
        QFrame#card_dash_destaque { border: 1px solid #F26522; background-color: rgba(242,101,34,0.04); }

        QLabel#card_titulo     { color: #64748B; font-size: 11px; font-weight: 600; }
        QLabel#card_valor      { color: #FFFFFF; font-size: 22px; font-weight: 700; }
        QLabel#card_valor_small{ color: #FFFFFF; font-size: 13px; font-weight: 700; }
        QLabel#card_subtitulo  { color: #475569; font-size: 10px; }

        QLabel#card_icone {
            font-size: 15px; border-radius: 8px;
            min-width: 30px; max-width: 30px;
            min-height: 30px; max-height: 30px;
        }

        /* Cards de Técnicos */
        QFrame#card_tecnico {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 12px;
        }
        QFrame#card_tecnico:hover { border: 1px solid #334155; }

        QLabel#tec_avatar {
            background-color: rgba(242,101,34,0.1);
            color: #F26522;
            border-radius: 12px;
            min-width: 28px; max-width: 28px;
            min-height: 28px; max-height: 28px;
            font-size: 14px;
        }
        QLabel#tec_nome       { color: #FFFFFF; font-size: 13px; font-weight: 700; }
        QLabel#tec_stat_label { color: #64748B; font-size: 10px; font-weight: 600; }
        QLabel#tec_stat_val   { font-size: 11px; font-weight: 700; }
        """)
