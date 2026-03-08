import sys
import os
from datetime import date

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFrame,
    QSpacerItem, QSizePolicy, QScrollArea,
    QButtonGroup, QMessageBox
)
from PyQt6.QtCore import Qt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db


# ──────────────────────────────────────────────
# Utilitários
# ──────────────────────────────────────────────

def brl(v) -> str:
    try:
        return f"R$ {float(v):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except Exception:
        return "R$ 0,00"


def margem_pct(custo, preco) -> str:
    try:
        c, p = float(custo), float(preco)
        if p > 0:
            return f"{((p - c) / p * 100):.1f}%"
    except Exception:
        pass
    return "—"


# ──────────────────────────────────────────────
# CARD DE SERVIÇO
# ──────────────────────────────────────────────

class ServicoCard(QFrame):
    def __init__(self, servico: dict, on_excluir):
        super().__init__()
        self.setObjectName("card_catalogo")
        self.setFixedSize(300, 290)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)

        # ─ Título + botão excluir ─
        top = QHBoxLayout()
        lbl_titulo = QLabel(servico.get("nome", ""))
        lbl_titulo.setObjectName("card_titulo")
        lbl_titulo.setWordWrap(True)
        top.addWidget(lbl_titulo)
        btn_del = QPushButton("🗑️")
        btn_del.setObjectName("btn_lixeira")
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.clicked.connect(lambda: on_excluir(servico["id"]))
        top.addWidget(btn_del)
        layout.addLayout(top)

        # ─ Tag categoria ─
        lbl_tag = QLabel(servico.get("categoria") or "—")
        lbl_tag.setObjectName("card_tag")
        layout.addWidget(lbl_tag)

        layout.addItem(QSpacerItem(20, 8, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        # ─ Linhas de valores ─
        custo = servico.get("custos", 0) or 0
        preco = servico.get("preco", 0) or 0
        lucro = preco - custo

        self._linha(layout, "Custo",           brl(custo), "valor_normal")
        self._linha(layout, "Venda",           brl(preco), "valor_venda")

        linha_div = QFrame()
        linha_div.setFrameShape(QFrame.Shape.HLine)
        linha_div.setObjectName("linha_divisoria")
        layout.addWidget(linha_div)

        self._linha(layout, "Lucro",           brl(lucro),                  "valor_positivo")
        self._badge(layout, "Margem",          margem_pct(custo, preco))
        self._linha(layout, "Tempo estimado",  servico.get("tempo_estimado") or "—", "valor_normal")

    def _linha(self, parent, label, valor, obj_name):
        row = QHBoxLayout()
        lbl_l = QLabel(label)
        lbl_l.setObjectName("card_label")
        lbl_r = QLabel(valor)
        lbl_r.setObjectName(obj_name)
        lbl_r.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(lbl_l)
        row.addWidget(lbl_r)
        parent.addLayout(row)

    def _badge(self, parent, label, valor):
        row = QHBoxLayout()
        lbl_l = QLabel(label)
        lbl_l.setObjectName("card_label")
        lbl_r = QLabel(valor)
        lbl_r.setObjectName("badge_positivo")
        lbl_r.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(lbl_l)
        row.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        row.addWidget(lbl_r)
        parent.addLayout(row)


# ──────────────────────────────────────────────
# CARD DE PRODUTO
# ──────────────────────────────────────────────

class ProdutoCatCard(QFrame):
    def __init__(self, produto: dict, on_excluir):
        super().__init__()
        self.setObjectName("card_catalogo")
        self.setFixedSize(300, 290)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)

        # ─ Título + excluir ─
        top = QHBoxLayout()
        lbl_titulo = QLabel(produto.get("nome", ""))
        lbl_titulo.setObjectName("card_titulo")
        lbl_titulo.setWordWrap(True)
        top.addWidget(lbl_titulo)
        btn_del = QPushButton("🗑️")
        btn_del.setObjectName("btn_lixeira")
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.clicked.connect(lambda: on_excluir(produto["id"]))
        top.addWidget(btn_del)
        layout.addLayout(top)

        # ─ Tag categoria ─
        lbl_tag = QLabel(produto.get("categoria") or "—")
        lbl_tag.setObjectName("card_tag")
        layout.addWidget(lbl_tag)

        layout.addItem(QSpacerItem(20, 8, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        custo = produto.get("custos", 0) or 0
        preco = produto.get("preco", 0) or 0
        estoque = produto.get("estoque", 0) or 0
        estoque_min = produto.get("estoque_minimo", 0) or 0
        lucro = preco - custo

        self._linha(layout, "Custo",    brl(custo),  "valor_normal")
        self._linha(layout, "Venda",    brl(preco),  "valor_venda")

        linha_div = QFrame()
        linha_div.setFrameShape(QFrame.Shape.HLine)
        linha_div.setObjectName("linha_divisoria")
        layout.addWidget(linha_div)

        self._linha(layout, "Lucro",   brl(lucro),  "valor_positivo")
        self._badge(layout, "Margem",  margem_pct(custo, preco))

        # Estoque com alerta visual se abaixo do mínimo
        est_obj = "valor_alerta" if estoque <= estoque_min else "valor_normal"
        self._linha(layout, "Estoque", f"{estoque} un", est_obj)

    def _linha(self, parent, label, valor, obj_name):
        row = QHBoxLayout()
        lbl_l = QLabel(label)
        lbl_l.setObjectName("card_label")
        lbl_r = QLabel(valor)
        lbl_r.setObjectName(obj_name)
        lbl_r.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        row.addWidget(lbl_l)
        row.addWidget(lbl_r)
        parent.addLayout(row)

    def _badge(self, parent, label, valor):
        row = QHBoxLayout()
        lbl_l = QLabel(label)
        lbl_l.setObjectName("card_label")
        lbl_r = QLabel(valor)
        lbl_r.setObjectName("badge_positivo")
        lbl_r.setAlignment(Qt.AlignmentFlag.AlignCenter)
        row.addWidget(lbl_l)
        row.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        row.addWidget(lbl_r)
        parent.addLayout(row)


# ──────────────────────────────────────────────
# TELA PRINCIPAL
# ──────────────────────────────────────────────

class CatalogoScreen(QWidget):
    def __init__(self):
        super().__init__()
        db.inicializar_estado()
        self._aba_ativa = 0   # 0 = Serviços, 1 = Produtos
        self.initUI()

    def initUI(self):
        self.setMinimumSize(1000, 700)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(25)

        # ─ Cabeçalho ─
        titulos = QVBoxLayout()
        titulos.setSpacing(0)
        lbl_titulo = QLabel("CATÁLOGO & PREÇOS")
        lbl_titulo.setObjectName("title_main")
        lbl_sub = QLabel("Gestão de serviços e produtos")
        lbl_sub.setObjectName("subtitle")
        titulos.addWidget(lbl_titulo)
        titulos.addWidget(lbl_sub)
        self.main_layout.addLayout(titulos)

        # ─ Toggle + busca + botão novo ─
        controles = QHBoxLayout()

        toggle_frame = QFrame()
        toggle_frame.setObjectName("toggle_bg")
        toggle_layout = QHBoxLayout(toggle_frame)
        toggle_layout.setContentsMargins(4, 4, 4, 4)
        toggle_layout.setSpacing(0)

        self.grupo_toggle = QButtonGroup(self)
        self.btn_servicos = QPushButton("🔧 Serviços")
        self.btn_servicos.setCheckable(True)
        self.btn_servicos.setChecked(True)
        self.btn_servicos.setObjectName("btn_toggle")
        self.btn_servicos.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_servicos.setFixedWidth(200)

        self.btn_produtos = QPushButton("📦 Produtos")
        self.btn_produtos.setCheckable(True)
        self.btn_produtos.setObjectName("btn_toggle")
        self.btn_produtos.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_produtos.setFixedWidth(200)

        self.grupo_toggle.addButton(self.btn_servicos, 0)
        self.grupo_toggle.addButton(self.btn_produtos, 1)
        self.grupo_toggle.idClicked.connect(self._mudar_aba)

        toggle_layout.addWidget(self.btn_servicos)
        toggle_layout.addWidget(self.btn_produtos)
        controles.addWidget(toggle_frame)

        self.edit_busca = QLineEdit()
        self.edit_busca.setPlaceholderText("🔍 Buscar por nome ou categoria...")
        self.edit_busca.textChanged.connect(lambda t: self._carregar(filtro=t))
        controles.addWidget(self.edit_busca)

        self.btn_novo = QPushButton("+ Novo Serviço")
        self.btn_novo.setObjectName("btn_primario")
        self.btn_novo.setCursor(Qt.CursorShape.PointingHandCursor)
        controles.addWidget(self.btn_novo)

        self.main_layout.addLayout(controles)

        # ─ Scroll + grid ─
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
        self._carregar()

    # ─ Lógica ─────────────────────────────────

    def _mudar_aba(self, index: int):
        self._aba_ativa = index
        self.btn_novo.setText("+ Novo Serviço" if index == 0 else "+ Novo Produto")
        self.edit_busca.clear()
        self._carregar()

    def _carregar(self, filtro: str = ""):
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.deleteLater()

        if self._aba_ativa == 0:
            itens = db.listar_servicos(filtro)
            cards = [ServicoCard(s, self._excluir_servico) for s in itens]
        else:
            itens = db.listar_produtos(filtro)
            cards = [ProdutoCatCard(p, self._excluir_produto) for p in itens]

        if not cards:
            lbl = QLabel("Nenhum item encontrado.")
            lbl.setObjectName("subtitle")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid.addWidget(lbl, 0, 0)
            return

        row, col = 0, 0
        for card in cards:
            self.grid.addWidget(card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

    def _excluir_servico(self, sid: int):
        if QMessageBox.question(self, "Excluir serviço", "Deseja excluir este serviço?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                                ) == QMessageBox.StandardButton.Yes:
            db.excluir_servico(sid)
            self._carregar(filtro=self.edit_busca.text())

    def _excluir_produto(self, pid: int):
        if QMessageBox.question(self, "Excluir produto", "Deseja excluir este produto?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                                ) == QMessageBox.StandardButton.Yes:
            db.excluir_produto(pid)
            self._carregar(filtro=self.edit_busca.text())

    # ─ Estilos ────────────────────────────────

    def aplicar_estilos(self):
        self.setStyleSheet("""
        QWidget {
            background-color: #0F172A;
            font-family: 'Poppins', 'Montserrat', sans-serif;
        }

        QLabel#title_main { color: #FFFFFF; font-size: 24px; font-weight: 700; }
        QLabel#subtitle   { color: #64748B; font-size: 12px; font-weight: 600; }

        QPushButton#btn_primario {
            background-color: #F26522; color: #FFFFFF;
            font-size: 14px; font-weight: 600;
            border-radius: 6px; padding: 10px 20px; border: none;
        }
        QPushButton#btn_primario:hover { background-color: #E05412; }

        /* Toggle */
        QFrame#toggle_bg {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 8px;
        }
        QPushButton#btn_toggle {
            background-color: transparent; color: #64748B;
            font-size: 13px; font-weight: 600;
            padding: 8px 16px; border-radius: 6px; border: none;
        }
        QPushButton#btn_toggle:checked { background-color: #1E293B; color: #FFFFFF; }

        /* Busca */
        QLineEdit {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 8px; padding: 10px;
            color: #FFFFFF; font-size: 13px;
        }
        QLineEdit:focus { border: 1px solid #F26522; }

        /* Scroll */
        QScrollArea#scroll_area { border: none; background-color: transparent; }
        QWidget#scroll_content  { background-color: transparent; }
        QScrollBar:vertical { border: none; background-color: #0B1120; width: 8px; border-radius: 4px; }
        QScrollBar::handle:vertical { background-color: #1E293B; min-height: 20px; border-radius: 4px; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }

        /* Card */
        QFrame#card_catalogo {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 12px;
        }
        QFrame#card_catalogo:hover { border: 1px solid #64748B; }

        QLabel#card_titulo { color: #FFFFFF; font-size: 15px; font-weight: 700; }
        QLabel#card_tag {
            border: 1px solid #F26522; color: #F26522;
            font-size: 10px; font-weight: 600;
            padding: 4px 12px; border-radius: 10px; max-width: 100px;
        }

        QLabel#card_label    { color: #64748B; font-size: 12px; }
        QLabel#valor_normal  { color: #FFFFFF; font-size: 12px; font-weight: 600; }
        QLabel#valor_venda   { color: #FFFFFF; font-size: 16px; font-weight: 700; }
        QLabel#valor_positivo{ color: #4ADE80; font-size: 12px; font-weight: 700; }
        QLabel#valor_alerta  { color: #EAB308; font-size: 12px; font-weight: 700; }

        QFrame#linha_divisoria {
            background-color: #1E293B;
            max-height: 1px; border: none; margin: 4px 0;
        }

        QLabel#badge_positivo {
            background-color: rgba(74,222,128,0.15);
            color: #4ADE80; font-size: 11px; font-weight: 700;
            padding: 2px 6px; border-radius: 4px;
        }

        /* Lixeira */
        QPushButton#btn_lixeira {
            background-color: transparent;
            color: #64748B; border: none; font-size: 14px;
        }
        QPushButton#btn_lixeira:hover { color: #EF4444; }
        """)
