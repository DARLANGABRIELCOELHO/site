import sys
import os
from datetime import date

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QSpacerItem,
    QSizePolicy, QScrollArea, QMessageBox,
    QCalendarWidget, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize, QDate, pyqtSignal
from PyQt6.QtGui import QIcon, QTextCharFormat, QColor, QFont

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db
from component.novadespesa import NovaDespesaWindow

try:
    from component.svg_utils import svg_para_pixmap
    _SVG_OK = True
except Exception:
    _SVG_OK = False

MESES_PT = [
    "", "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
    "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
]

COR_BG       = "#0F172A"
COR_PANEL    = "#0B1120"
COR_BORDA    = "#1E293B"
COR_ACCENT   = "#F26522"
COR_TEXTO    = "#FFFFFF"
COR_MUTED    = "#64748B"
COR_VERDE    = "#4ADE80"
COR_VERMELHO = "#EF4444"
COR_AMARELO  = "#EAB308"


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def _cor_categoria(categoria: str) -> str:
    mapa = {
        "Aluguel": "#F26522", "Energia": "#EAB308", "Água": "#38BDF8",
        "Internet": "#818CF8", "Telefone": "#A78BFA", "Fornecedor": "#34D399",
        "Salário": "#4ADE80", "Material": "#FB923C", "Marketing": "#F472B6",
        "Outros": "#64748B",
    }
    return mapa.get(categoria, "#64748B")


_ICONE_RECORRENCIA = {
    "semanal":   "↻ Semanal",
    "quinzenal": "↻ Quinzenal",
    "mensal":    "↻ Mensal",
}


# ─────────────────────────────────────────────────────────────────────────────
# COMPONENTE: Card de despesa na lista
# ─────────────────────────────────────────────────────────────────────────────

class DespesaItem(QFrame):
    def __init__(self, despesa: dict, on_excluir):
        super().__init__()
        self.setObjectName("despesa_item")
        self.setFixedHeight(68)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 10, 16, 10)
        layout.setSpacing(12)

        # Ponto de cor da categoria
        dot = QLabel("●")
        dot.setFixedWidth(14)
        cor_cat = _cor_categoria(despesa.get("categoria", "Outros"))
        dot.setStyleSheet(f"color: {cor_cat}; font-size: 10px;")
        layout.addWidget(dot)

        # Descrição + info
        info = QVBoxLayout()
        info.setSpacing(2)

        lbl_desc = QLabel(despesa.get("descricao", ""))
        lbl_desc.setObjectName("despesa_desc")
        info.addWidget(lbl_desc)

        recorrencia = despesa.get("recorrencia", "") or ""
        tag_rec = _ICONE_RECORRENCIA.get(recorrencia.lower(), "")
        texto_sub = f"{despesa.get('categoria', '')}  •  {despesa.get('forma_pagamento', '')}"
        if tag_rec:
            texto_sub += f"  •  {tag_rec}"
        lbl_cat = QLabel(texto_sub)
        lbl_cat.setObjectName("despesa_cat")
        info.addWidget(lbl_cat)

        layout.addLayout(info, 1)

        # Valor
        valor = despesa.get("valor", 0)
        lbl_valor = QLabel(f"R$ {valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", "."))
        lbl_valor.setObjectName("despesa_valor")
        layout.addWidget(lbl_valor)

        # Botão excluir
        btn_del = QPushButton()
        btn_del.setObjectName("btn_lixeira")
        btn_del.setFixedSize(28, 28)
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        if _SVG_OK:
            btn_del.setIcon(QIcon(svg_para_pixmap("fi-sr-trash.svg", "#64748B", 13, 13)))
            btn_del.setIconSize(QSize(13, 13))
        else:
            btn_del.setText("🗑")
        btn_del.clicked.connect(lambda: on_excluir(despesa["id"]))
        layout.addWidget(btn_del)


# ─────────────────────────────────────────────────────────────────────────────
# COMPONENTE: Calendário (QCalendarWidget nativo estilizado)
# ─────────────────────────────────────────────────────────────────────────────

class CalendarioWidget(QFrame):
    dia_selecionado = pyqtSignal(date)
    mes_alterado    = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("calendario_frame")
        self._dias_com_despesa = set()
        self._build_ui()
        self._aplicar_estilos()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 16, 16, 16)
        layout.setSpacing(0)

        self._cal = QCalendarWidget()
        self._cal.setGridVisible(False)
        self._cal.setVerticalHeaderFormat(QCalendarWidget.VerticalHeaderFormat.NoVerticalHeader)
        self._cal.setFirstDayOfWeek(Qt.DayOfWeek.Sunday)
        self._cal.setSelectedDate(QDate.currentDate())
        self._cal.selectionChanged.connect(self._on_selecao_mudou)
        self._cal.currentPageChanged.connect(self._on_pagina_mudou)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 80))
        self._cal.setGraphicsEffect(shadow)

        layout.addWidget(self._cal)
        self._destacar_hoje()

    def _destacar_hoje(self):
        fmt_hoje = QTextCharFormat()
        fmt_hoje.setBackground(QColor(COR_VERDE))
        fmt_hoje.setForeground(QColor("#000000"))
        fmt_hoje.setFontWeight(QFont.Weight.Bold)
        self._cal.setDateTextFormat(QDate.currentDate(), fmt_hoje)

    def _on_selecao_mudou(self):
        qd = self._cal.selectedDate()
        d  = date(qd.year(), qd.month(), qd.day())
        self.dia_selecionado.emit(d)

    def _on_pagina_mudou(self, ano: int, mes: int):
        self.mes_alterado.emit(mes, ano)

    def atualizar_marcadores(self, dias_com_despesa: list):
        """Marca dias com despesa em vermelho; limpa os demais."""
        # Limpa formato dos dias do mês atual
        qd_atual = self._cal.selectedDate()
        import calendar as _cal_mod
        _, n_dias = _cal_mod.monthrange(qd_atual.year(), qd_atual.month())
        fmt_limpo = QTextCharFormat()
        for d in range(1, n_dias + 1):
            self._cal.setDateTextFormat(QDate(qd_atual.year(), qd_atual.month(), d), fmt_limpo)

        # Re-aplica destaque do dia atual
        self._destacar_hoje()

        # Marca dias com despesa
        fmt_despesa = QTextCharFormat()
        fmt_despesa.setBackground(QColor(242, 101, 34, 60))   # laranja translúcido
        fmt_despesa.setForeground(QColor(COR_ACCENT))
        fmt_despesa.setFontWeight(QFont.Weight.Bold)
        for dia in dias_com_despesa:
            self._cal.setDateTextFormat(
                QDate(qd_atual.year(), qd_atual.month(), dia), fmt_despesa
            )

    def mes_atual(self):
        return self._cal.monthShown()

    def ano_atual(self):
        return self._cal.yearShown()

    def _aplicar_estilos(self):
        self.setStyleSheet(f"""
        QFrame#calendario_frame {{
            background-color: {COR_PANEL};
            border: 1px solid {COR_BORDA};
            border-radius: 14px;
        }}
        QCalendarWidget {{
            background-color: {COR_PANEL};
            border-radius: 10px;
        }}
        QCalendarWidget QWidget {{
            background-color: {COR_PANEL};
            alternate-background-color: {COR_BG};
        }}
        QCalendarWidget QToolButton {{
            color: {COR_TEXTO};
            font-size: 14px;
            font-weight: 600;
            background-color: {COR_BG};
            border: 1px solid {COR_BORDA};
            border-radius: 8px;
            padding: 6px 10px;
            margin: 4px;
            min-width: 90px;
        }}
        QCalendarWidget QToolButton:hover {{
            background-color: {COR_ACCENT};
            border-color: {COR_ACCENT};
        }}
        QCalendarWidget QMenu {{
            background-color: {COR_PANEL};
            color: {COR_TEXTO};
            border: 1px solid {COR_BORDA};
            border-radius: 8px;
        }}
        QCalendarWidget QSpinBox {{
            color: {COR_TEXTO};
            background-color: {COR_PANEL};
            selection-background-color: {COR_ACCENT};
            border: 1px solid {COR_BORDA};
            border-radius: 6px;
            padding: 4px;
        }}
        QCalendarWidget QAbstractItemView:enabled {{
            font-size: 13px;
            color: {COR_TEXTO};
            background-color: {COR_PANEL};
            selection-background-color: {COR_ACCENT};
            selection-color: white;
            outline: 0;
            border: none;
        }}
        QCalendarWidget QAbstractItemView:disabled {{
            color: #334155;
        }}
        QCalendarWidget QTableView {{
            border: none;
        }}
        QCalendarWidget QHeaderView {{
            background-color: {COR_PANEL};
            color: {COR_MUTED};
            font-size: 12px;
            font-weight: 700;
            border: none;
        }}
        """)


# ─────────────────────────────────────────────────────────────────────────────
# TELA PRINCIPAL
# ─────────────────────────────────────────────────────────────────────────────

class DespesasScreen(QWidget):
    def __init__(self):
        super().__init__()
        db.inicializar_estado()
        self._data_sel = date.today()
        self._initUI()
        self._aplicar_estilos()
        self._carregar_tudo()

    def _initUI(self):
        self.setMinimumSize(1000, 700)
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ─── Coluna esquerda: calendário + resumo ─────────────────────────
        col_esq = QVBoxLayout()
        col_esq.setContentsMargins(32, 32, 16, 32)
        col_esq.setSpacing(20)

        header_esq = QVBoxLayout()
        lbl_titulo = QLabel("DESPESAS")
        lbl_titulo.setObjectName("title_main")
        lbl_sub = QLabel("Controle financeiro de gastos")
        lbl_sub.setObjectName("subtitle")
        header_esq.addWidget(lbl_titulo)
        header_esq.addWidget(lbl_sub)
        col_esq.addLayout(header_esq)

        self.calendario = CalendarioWidget()
        self.calendario.dia_selecionado.connect(self._on_dia_selecionado)
        self.calendario.mes_alterado.connect(self._on_mes_alterado)
        col_esq.addWidget(self.calendario)

        # Resumo do mês
        self.frame_resumo = QFrame()
        self.frame_resumo.setObjectName("frame_resumo")
        resumo_layout = QVBoxLayout(self.frame_resumo)
        resumo_layout.setContentsMargins(20, 20, 20, 20)
        resumo_layout.setSpacing(6)

        resumo_layout.addWidget(QLabel("Resumo do Mês", objectName="resumo_titulo"))
        self.lbl_total_mes = QLabel("R$ 0,00")
        self.lbl_total_mes.setObjectName("resumo_valor")
        resumo_layout.addWidget(self.lbl_total_mes)
        self.lbl_qtd_mes = QLabel("0 despesas registradas")
        self.lbl_qtd_mes.setObjectName("resumo_sub")
        resumo_layout.addWidget(self.lbl_qtd_mes)

        col_esq.addWidget(self.frame_resumo)
        col_esq.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # ─── Coluna direita: lista do dia ─────────────────────────────────
        col_dir = QVBoxLayout()
        col_dir.setContentsMargins(16, 32, 32, 32)
        col_dir.setSpacing(16)

        self.header_dir = QHBoxLayout()
        self.lbl_data_sel = QLabel()
        self.lbl_data_sel.setObjectName("lbl_data_selecionada")
        self._atualizar_label_data()

        btn_nova = QPushButton("+ Nova Despesa")
        btn_nova.setObjectName("btn_primario")
        btn_nova.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_nova.clicked.connect(self._abrir_nova_despesa)

        self.header_dir.addWidget(self.lbl_data_sel)
        self.header_dir.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.header_dir.addWidget(btn_nova)
        col_dir.addLayout(self.header_dir)

        sep = QFrame()
        sep.setObjectName("separador")
        sep.setFixedHeight(1)
        col_dir.addWidget(sep)

        self.row_cats = QHBoxLayout()
        self.row_cats.setSpacing(8)
        col_dir.addLayout(self.row_cats)

        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_area")
        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scroll_content")
        self.lista_layout = QVBoxLayout(self.scroll_content)
        self.lista_layout.setContentsMargins(0, 0, 0, 0)
        self.lista_layout.setSpacing(8)
        self.lista_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setWidget(self.scroll_content)
        col_dir.addWidget(self.scroll_area, 1)

        total_dia_row = QHBoxLayout()
        lbl_t_label = QLabel("Total do dia:")
        lbl_t_label.setObjectName("total_dia_label")
        self.lbl_total_dia = QLabel("R$ 0,00")
        self.lbl_total_dia.setObjectName("total_dia_valor")
        total_dia_row.addWidget(lbl_t_label)
        total_dia_row.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        total_dia_row.addWidget(self.lbl_total_dia)
        col_dir.addLayout(total_dia_row)

        # ─── Montagem ─────────────────────────────────────────────────────
        root.addLayout(col_esq, 0)
        divisor = QFrame()
        divisor.setObjectName("divisor_vertical")
        divisor.setFixedWidth(1)
        root.addWidget(divisor)
        root.addLayout(col_dir, 1)

    # ─── Lógica ──────────────────────────────────────────────────────────────

    def _on_dia_selecionado(self, data: date):
        self._data_sel = data
        self._atualizar_label_data()
        self._carregar_despesas_dia()

    def _on_mes_alterado(self, mes: int, ano: int):
        self._carregar_tudo()

    def _atualizar_label_data(self):
        d = self._data_sel
        nome_dia = ["Segunda", "Terça", "Quarta", "Quinta", "Sexta", "Sábado", "Domingo"][d.weekday()]
        self.lbl_data_sel.setText(f"{nome_dia}, {d.strftime('%d')} de {MESES_PT[d.month]} de {d.year}")

    def _carregar_tudo(self):
        mes = self.calendario.mes_atual()
        ano = self.calendario.ano_atual()
        dias = db.dias_com_despesa_no_mes(mes, ano)
        self.calendario.atualizar_marcadores(dias)
        total = db.total_despesas_mes(mes, ano)
        despesas_mes = db.listar_despesas(mes=mes, ano=ano)
        self.lbl_total_mes.setText(
            f"R$ {total:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )
        self.lbl_qtd_mes.setText(f"{len(despesas_mes)} despesa(s) registrada(s)")
        self._carregar_despesas_dia()

    def _carregar_despesas_dia(self):
        for i in reversed(range(self.lista_layout.count())):
            w = self.lista_layout.itemAt(i).widget()
            if w:
                w.deleteLater()
        for i in reversed(range(self.row_cats.count())):
            item = self.row_cats.itemAt(i)
            if item and item.widget():
                item.widget().deleteLater()

        despesas = db.listar_despesas_por_dia(self._data_sel.isoformat())

        if not despesas:
            lbl_vazio = QLabel("Nenhuma despesa registrada neste dia.")
            lbl_vazio.setObjectName("lbl_vazio")
            lbl_vazio.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.lista_layout.addWidget(lbl_vazio)
            self.lbl_total_dia.setText("R$ 0,00")
            return

        total_dia = 0.0
        for d in despesas:
            item = DespesaItem(d, self._excluir_despesa)
            self.lista_layout.addWidget(item)
            total_dia += d.get("valor", 0)

        self.lbl_total_dia.setText(
            f"R$ {total_dia:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
        )

        cats_vistas = {}
        for d in despesas:
            cat = d.get("categoria", "Outros")
            cats_vistas[cat] = cats_vistas.get(cat, 0) + d.get("valor", 0)

        for cat, val in sorted(cats_vistas.items(), key=lambda x: -x[1]):
            badge = QLabel(f"  {cat}  ")
            badge.setFixedHeight(24)
            cor = _cor_categoria(cat)
            badge.setStyleSheet(
                f"background-color: rgba(0,0,0,0.2); color: {cor}; "
                f"border: 1px solid {cor}; border-radius: 10px; "
                f"font-size: 11px; font-weight: 600; padding: 0 4px;"
            )
            self.row_cats.addWidget(badge)
        self.row_cats.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

    def _abrir_nova_despesa(self):
        dlg = NovaDespesaWindow(data_selecionada=self._data_sel, parent=self)
        dlg.despesa_salva.connect(self._carregar_tudo)
        dlg.exec()

    def _excluir_despesa(self, despesa_id: int):
        resp = QMessageBox.question(
            self, "Confirmar exclusão",
            "Deseja excluir esta despesa?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resp == QMessageBox.StandardButton.Yes:
            db.excluir_despesa(despesa_id)
            self._carregar_tudo()

    # ─── Estilos ─────────────────────────────────────────────────────────────

    def _aplicar_estilos(self):
        self.setStyleSheet(f"""
        QWidget {{
            background-color: {COR_BG};
            font-family: 'Poppins', 'Montserrat', sans-serif;
        }}

        QLabel#title_main {{ color: {COR_TEXTO}; font-size: 24px; font-weight: 700; }}
        QLabel#subtitle   {{ color: {COR_MUTED}; font-size: 12px; font-weight: 600; }}

        QPushButton#btn_primario {{
            background-color: {COR_ACCENT}; color: {COR_TEXTO};
            font-size: 13px; font-weight: 600; border-radius: 8px;
            padding: 10px 20px; border: none;
        }}
        QPushButton#btn_primario:hover {{ background-color: #E05412; }}

        /* Calendário */
        QFrame#calendario_frame {{
            background-color: {COR_PANEL};
            border: 1px solid {COR_BORDA};
            border-radius: 14px;
        }}
        QLabel#lbl_mes_ano {{ color: {COR_TEXTO}; font-size: 15px; font-weight: 700; }}
        QLabel#lbl_dia_semana {{ color: {COR_MUTED}; font-size: 11px; font-weight: 600; }}
        QPushButton#btn_nav_cal {{
            background-color: {COR_BG}; color: {COR_TEXTO};
            border: 1px solid {COR_BORDA}; border-radius: 8px;
            font-size: 18px; font-weight: 700;
        }}
        QPushButton#btn_nav_cal:hover {{ background-color: {COR_BORDA}; }}
        QPushButton#btn_dia_normal {{
            background-color: transparent; color: {COR_TEXTO};
            border: none; border-radius: 8px; font-size: 13px;
        }}
        QPushButton#btn_dia_normal:hover {{ background-color: {COR_BORDA}; }}
        QPushButton#btn_dia_hoje {{
            background-color: rgba(242,101,34,0.15); color: {COR_ACCENT};
            border: 1px solid {COR_ACCENT}; border-radius: 8px;
            font-size: 13px; font-weight: 700;
        }}
        QPushButton#btn_dia_selecionado {{
            background-color: {COR_ACCENT}; color: {COR_TEXTO};
            border: none; border-radius: 8px; font-size: 13px; font-weight: 700;
        }}
        QPushButton#btn_dia_com_despesa {{
            background-color: rgba(239,68,68,0.15); color: {COR_VERMELHO};
            border: 1px solid rgba(239,68,68,0.3); border-radius: 8px;
            font-size: 13px; font-weight: 600;
        }}
        QPushButton#btn_dia_com_despesa:hover {{ background-color: rgba(239,68,68,0.25); }}

        /* Resumo */
        QFrame#frame_resumo {{
            background-color: {COR_PANEL};
            border: 1px solid {COR_BORDA};
            border-radius: 12px;
        }}
        QLabel#resumo_titulo {{ color: {COR_MUTED}; font-size: 12px; font-weight: 600; }}
        QLabel#resumo_valor  {{ color: {COR_VERMELHO}; font-size: 22px; font-weight: 700; }}
        QLabel#resumo_sub    {{ color: {COR_MUTED}; font-size: 11px; }}

        /* Divisores */
        QFrame#divisor_vertical {{ background-color: {COR_BORDA}; }}
        QFrame#separador        {{ background-color: {COR_BORDA}; }}

        QLabel#lbl_data_selecionada {{ color: {COR_TEXTO}; font-size: 16px; font-weight: 700; }}

        /* Scroll */
        QScrollArea#scroll_area {{ border: none; background-color: transparent; }}
        QWidget#scroll_content  {{ background-color: transparent; }}
        QScrollBar:vertical {{ border: none; background-color: {COR_PANEL}; width: 8px; border-radius: 4px; }}
        QScrollBar::handle:vertical {{ background-color: {COR_BORDA}; min-height: 20px; border-radius: 4px; }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ border: none; background: none; }}

        /* Card despesa */
        QFrame#despesa_item {{
            background-color: {COR_PANEL};
            border: 1px solid {COR_BORDA};
            border-radius: 10px;
        }}
        QFrame#despesa_item:hover {{ border: 1px solid {COR_ACCENT}; }}
        QLabel#despesa_desc  {{ color: {COR_TEXTO}; font-size: 13px; font-weight: 600; }}
        QLabel#despesa_cat   {{ color: {COR_MUTED}; font-size: 11px; }}
        QLabel#despesa_valor {{ color: {COR_VERMELHO}; font-size: 14px; font-weight: 700; }}
        QLabel#lbl_vazio     {{ color: {COR_MUTED}; font-size: 14px; font-weight: 600; }}

        /* Total dia */
        QLabel#total_dia_label {{ color: {COR_MUTED}; font-size: 13px; font-weight: 600; }}
        QLabel#total_dia_valor {{ color: {COR_VERMELHO}; font-size: 18px; font-weight: 700; }}

        /* Botão lixeira */
        QPushButton#btn_lixeira {{ background-color: transparent; border: none; color: {COR_MUTED}; }}
        QPushButton#btn_lixeira:hover {{ color: {COR_VERMELHO}; }}
        """)
