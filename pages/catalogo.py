import sys
import os
from datetime import date

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFrame,
    QSpacerItem, QSizePolicy, QScrollArea,
    QButtonGroup, QMessageBox, QDialog, QComboBox, QTextEdit, QMenu
)
from PyQt6.QtGui import QAction
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
# Dialogs de Edição
# ──────────────────────────────────────────────

def _estilos_dialog():
    return """
        QDialog { background-color: #0F172A; font-family: 'Poppins', sans-serif; }
        QLabel#dlg_titulo { color: #FFFFFF; font-size: 16px; font-weight: 700; }
        QLabel { color: #64748B; font-size: 12px; font-weight: 600; }
        QLineEdit, QTextEdit, QComboBox {
            background-color: #0B1120; border: 1px solid #1E293B;
            border-radius: 6px; padding: 8px; color: #FFFFFF; font-size: 13px;
        }
        QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 1px solid #F26522; }
        QComboBox::drop-down { border: none; }
        QPushButton#btnSalvar {
            background-color: #F26522; color: #FFFFFF;
            font-size: 13px; font-weight: 600;
            border-radius: 6px; padding: 10px 20px; border: none;
        }
        QPushButton#btnSalvar:hover { background-color: #E05412; }
        QPushButton#btnCancelar {
            background-color: transparent; color: #FFFFFF;
            border: 1px solid #64748B; font-size: 13px; font-weight: 600;
            border-radius: 6px; padding: 10px 20px;
        }
        QPushButton#btnCancelar:hover { background-color: #1E293B; }
    """


class EditarServicoDialog(QDialog):
    def __init__(self, servico: dict, parent=None):
        super().__init__(parent)
        self._servico = servico
        self.setWindowTitle(f"Editar Serviço — {servico.get('nome','')}")
        self.setFixedSize(480, 400)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(12)

        lbl_t = QLabel("✏ Editar Serviço")
        lbl_t.setObjectName("dlg_titulo")
        layout.addWidget(lbl_t)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel("Nome"), 0, 0)
        self.edit_nome = QLineEdit(servico.get("nome", ""))
        grid.addWidget(self.edit_nome, 1, 0)

        grid.addWidget(QLabel("Categoria"), 0, 1)
        self.edit_cat = QLineEdit(servico.get("categoria", ""))
        grid.addWidget(self.edit_cat, 1, 1)

        grid.addWidget(QLabel("Custo (R$)"), 2, 0)
        self.edit_custo = QLineEdit(str(servico.get("custos", "") or ""))
        grid.addWidget(self.edit_custo, 3, 0)

        grid.addWidget(QLabel("Preço (R$)"), 2, 1)
        self.edit_preco = QLineEdit(str(servico.get("preco", "") or ""))
        grid.addWidget(self.edit_preco, 3, 1)

        grid.addWidget(QLabel("Tempo estimado"), 4, 0)
        self.edit_tempo = QLineEdit(servico.get("tempo_estimado", "") or "")
        grid.addWidget(self.edit_tempo, 5, 0)

        layout.addLayout(grid)
        layout.addItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        btns = QHBoxLayout()
        btns.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        btn_c = QPushButton("Cancelar")
        btn_c.setObjectName("btnCancelar")
        btn_c.clicked.connect(self.reject)
        btn_s = QPushButton("Salvar")
        btn_s.setObjectName("btnSalvar")
        btn_s.clicked.connect(self._salvar)
        btns.addWidget(btn_c)
        btns.addWidget(btn_s)
        layout.addLayout(btns)

        self.setStyleSheet(_estilos_dialog())

    def _salvar(self):
        try:
            db.atualizar_servico(
                self._servico["id"],
                self.edit_nome.text().strip(),
                self._servico.get("modelo_celular", ""),
                self.edit_cat.text().strip(),
                float(self.edit_custo.text().replace(",", ".") or 0),
                float(self.edit_preco.text().replace(",", ".") or 0),
                self.edit_tempo.text().strip() or None,
                self._servico.get("observacao", ""),
                self._servico.get("data_cadastro", date.today().isoformat()),
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar:\n{e}")


class EditarProdutoDialog(QDialog):
    def __init__(self, produto: dict, parent=None):
        super().__init__(parent)
        self._produto = produto
        self.setWindowTitle(f"Editar Produto — {produto.get('nome','')}")
        self.setFixedSize(480, 440)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(12)

        lbl_t = QLabel("✏ Editar Produto")
        lbl_t.setObjectName("dlg_titulo")
        layout.addWidget(lbl_t)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel("Nome"), 0, 0)
        self.edit_nome = QLineEdit(produto.get("nome", ""))
        grid.addWidget(self.edit_nome, 1, 0)

        grid.addWidget(QLabel("Categoria"), 0, 1)
        self.edit_cat = QLineEdit(produto.get("categoria", ""))
        grid.addWidget(self.edit_cat, 1, 1)

        grid.addWidget(QLabel("Custo (R$)"), 2, 0)
        self.edit_custo = QLineEdit(str(produto.get("custos", "") or ""))
        grid.addWidget(self.edit_custo, 3, 0)

        grid.addWidget(QLabel("Preço (R$)"), 2, 1)
        self.edit_preco = QLineEdit(str(produto.get("preco", "") or ""))
        grid.addWidget(self.edit_preco, 3, 1)

        grid.addWidget(QLabel("Estoque"), 4, 0)
        self.edit_estoque = QLineEdit(str(produto.get("estoque", "") or ""))
        grid.addWidget(self.edit_estoque, 5, 0)

        grid.addWidget(QLabel("Estoque mínimo"), 4, 1)
        self.edit_est_min = QLineEdit(str(produto.get("estoque_minimo", "") or ""))
        grid.addWidget(self.edit_est_min, 5, 1)

        layout.addLayout(grid)
        layout.addItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        btns = QHBoxLayout()
        btns.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        btn_c = QPushButton("Cancelar")
        btn_c.setObjectName("btnCancelar")
        btn_c.clicked.connect(self.reject)
        btn_s = QPushButton("Salvar")
        btn_s.setObjectName("btnSalvar")
        btn_s.clicked.connect(self._salvar)
        btns.addWidget(btn_c)
        btns.addWidget(btn_s)
        layout.addLayout(btns)

        self.setStyleSheet(_estilos_dialog())

    def _salvar(self):
        try:
            db.atualizar_produto(
                self._produto["id"],
                self.edit_nome.text().strip(),
                self.edit_cat.text().strip(),
                float(self.edit_custo.text().replace(",", ".") or 0),
                float(self.edit_preco.text().replace(",", ".") or 0),
                self._produto.get("data_cadastro", date.today().isoformat()),
                int(self.edit_estoque.text() or 0),
                int(self.edit_est_min.text() or 0),
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar:\n{e}")


class EditarCelularDialog(QDialog):
    def __init__(self, celular: dict, parent=None):
        super().__init__(parent)
        self._celular = celular
        self.setWindowTitle(f"Editar Celular — {celular.get('modelo','')}")
        self.setFixedSize(520, 500)
        self.setModal(True)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 28, 28, 28)
        layout.setSpacing(12)

        lbl_t = QLabel("✏ Editar Celular")
        lbl_t.setObjectName("dlg_titulo")
        layout.addWidget(lbl_t)

        grid = QGridLayout()
        grid.setSpacing(10)

        grid.addWidget(QLabel("Modelo"), 0, 0)
        self.edit_modelo = QLineEdit(celular.get("modelo", ""))
        grid.addWidget(self.edit_modelo, 1, 0)

        grid.addWidget(QLabel("Marca"), 0, 1)
        self.edit_marca = QLineEdit(celular.get("marca", ""))
        grid.addWidget(self.edit_marca, 1, 1)

        grid.addWidget(QLabel("Cor"), 2, 0)
        self.edit_cor = QLineEdit(celular.get("cor", ""))
        grid.addWidget(self.edit_cor, 3, 0)

        grid.addWidget(QLabel("IMEI"), 2, 1)
        self.edit_imei = QLineEdit(celular.get("imei", ""))
        grid.addWidget(self.edit_imei, 3, 1)

        grid.addWidget(QLabel("Custo Aquisição (R$)"), 4, 0)
        self.edit_custo_aq = QLineEdit(str(celular.get("custos_de_aquisicao", "") or ""))
        grid.addWidget(self.edit_custo_aq, 5, 0)

        grid.addWidget(QLabel("Custo Reparo (R$)"), 4, 1)
        self.edit_custo_rp = QLineEdit(str(celular.get("custos_de_reparo", "") or ""))
        grid.addWidget(self.edit_custo_rp, 5, 1)

        grid.addWidget(QLabel("Preço (R$)"), 6, 0)
        self.edit_preco = QLineEdit(str(celular.get("preco", "") or ""))
        grid.addWidget(self.edit_preco, 7, 0)

        grid.addWidget(QLabel("Condição"), 6, 1)
        self.edit_cond = QLineEdit(celular.get("condicao", ""))
        grid.addWidget(self.edit_cond, 7, 1)

        layout.addLayout(grid)
        layout.addItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        btns = QHBoxLayout()
        btns.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        btn_c = QPushButton("Cancelar")
        btn_c.setObjectName("btnCancelar")
        btn_c.clicked.connect(self.reject)
        btn_s = QPushButton("Salvar")
        btn_s.setObjectName("btnSalvar")
        btn_s.clicked.connect(self._salvar)
        btns.addWidget(btn_c)
        btns.addWidget(btn_s)
        layout.addLayout(btns)

        self.setStyleSheet(_estilos_dialog())

    def _salvar(self):
        try:
            fotos = (self._celular.get("fotos") or "").split(",")
            db.atualizar_celular(
                self._celular["id"],
                self.edit_modelo.text().strip(),
                self.edit_marca.text().strip(),
                self.edit_cor.text().strip(),
                self.edit_imei.text().strip(),
                self._celular.get("data_cadastro", date.today().isoformat()),
                float(self.edit_custo_aq.text().replace(",", ".") or 0),
                float(self.edit_custo_rp.text().replace(",", ".") or 0),
                float(self.edit_preco.text().replace(",", ".") or 0),
                self.edit_cond.text().strip(),
                fotos,
                self._celular.get("observacao", ""),
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar:\n{e}")


# ──────────────────────────────────────────────
# Helper: botão ⋮ com menu
# ──────────────────────────────────────────────

def _btn_menu_card(parent, on_editar, on_excluir) -> QPushButton:
    btn = QPushButton("⋮", parent)
    btn.setObjectName("btn_menu_card")
    btn.setCursor(Qt.CursorShape.PointingHandCursor)
    btn.setFixedWidth(28)

    def abrir():
        menu = QMenu(btn)
        menu.setObjectName("menu_card")
        acao_editar  = QAction("✏  Editar", btn)
        acao_excluir = QAction("🗑  Excluir", btn)
        acao_editar.triggered.connect(on_editar)
        acao_excluir.triggered.connect(on_excluir)
        menu.addAction(acao_editar)
        menu.addSeparator()
        menu.addAction(acao_excluir)
        menu.exec(btn.mapToGlobal(btn.rect().bottomLeft()))

    btn.clicked.connect(abrir)
    return btn


# ──────────────────────────────────────────────
# CARD DE SERVIÇO
# ──────────────────────────────────────────────

class ServicoCard(QFrame):
    def __init__(self, servico: dict, on_editar, on_excluir):
        super().__init__()
        self.setObjectName("card_catalogo")
        self.setFixedSize(300, 290)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)

        top = QHBoxLayout()
        lbl_titulo = QLabel(servico.get("nome", ""))
        lbl_titulo.setObjectName("card_titulo")
        lbl_titulo.setWordWrap(True)
        top.addWidget(lbl_titulo)
        top.addWidget(_btn_menu_card(self, on_editar, on_excluir))
        layout.addLayout(top)

        lbl_tag = QLabel(servico.get("categoria") or "—")
        lbl_tag.setObjectName("card_tag")
        layout.addWidget(lbl_tag)

        layout.addItem(QSpacerItem(20, 8, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        custo = servico.get("custos", 0) or 0
        preco = servico.get("preco", 0) or 0
        lucro = preco - custo

        self._linha(layout, "Custo",          brl(custo), "valor_normal")
        self._linha(layout, "Venda",          brl(preco), "valor_venda")

        linha_div = QFrame()
        linha_div.setFrameShape(QFrame.Shape.HLine)
        linha_div.setObjectName("linha_divisoria")
        layout.addWidget(linha_div)

        self._linha(layout, "Lucro",          brl(lucro),              "valor_positivo")
        self._badge(layout, "Margem",         margem_pct(custo, preco))
        self._linha(layout, "Tempo estimado", servico.get("tempo_estimado") or "—", "valor_normal")

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
    def __init__(self, produto: dict, on_editar, on_excluir):
        super().__init__()
        self.setObjectName("card_catalogo")
        self.setFixedSize(300, 290)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)

        top = QHBoxLayout()
        lbl_titulo = QLabel(produto.get("nome", ""))
        lbl_titulo.setObjectName("card_titulo")
        lbl_titulo.setWordWrap(True)
        top.addWidget(lbl_titulo)
        top.addWidget(_btn_menu_card(self, on_editar, on_excluir))
        layout.addLayout(top)

        lbl_tag = QLabel(produto.get("categoria") or "—")
        lbl_tag.setObjectName("card_tag")
        layout.addWidget(lbl_tag)

        layout.addItem(QSpacerItem(20, 8, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        custo     = produto.get("custos", 0) or 0
        preco     = produto.get("preco", 0) or 0
        estoque   = produto.get("estoque", 0) or 0
        est_min   = produto.get("estoque_minimo", 0) or 0
        lucro     = preco - custo

        self._linha(layout, "Custo",   brl(custo), "valor_normal")
        self._linha(layout, "Venda",   brl(preco), "valor_venda")

        linha_div = QFrame()
        linha_div.setFrameShape(QFrame.Shape.HLine)
        linha_div.setObjectName("linha_divisoria")
        layout.addWidget(linha_div)

        self._linha(layout, "Lucro",   brl(lucro),  "valor_positivo")
        self._badge(layout, "Margem",  margem_pct(custo, preco))
        est_obj = "valor_alerta" if estoque <= est_min else "valor_normal"
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
# CARD DE CELULAR
# ──────────────────────────────────────────────

class CelularCard(QFrame):
    def __init__(self, celular: dict, on_editar, on_excluir):
        super().__init__()
        self.setObjectName("card_catalogo")
        self.setFixedSize(300, 290)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(8)

        top = QHBoxLayout()
        lbl_titulo = QLabel(f"{celular.get('modelo', '')} • {celular.get('marca', '')}")
        lbl_titulo.setObjectName("card_titulo")
        lbl_titulo.setWordWrap(True)
        top.addWidget(lbl_titulo)
        top.addWidget(_btn_menu_card(self, on_editar, on_excluir))
        layout.addLayout(top)

        cor = celular.get("cor") or "—"
        lbl_tag = QLabel(cor)
        lbl_tag.setObjectName("card_tag")
        layout.addWidget(lbl_tag)

        layout.addItem(QSpacerItem(20, 8, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

        custo_aq = float(celular.get("custos_de_aquisicao") or 0)
        custo_rp = float(celular.get("custos_de_reparo") or 0)
        custo    = custo_aq + custo_rp
        preco    = float(celular.get("preco") or 0)
        lucro    = preco - custo

        self._linha(layout, "Custo total", brl(custo), "valor_normal")
        self._linha(layout, "Venda",       brl(preco), "valor_venda")

        linha_div = QFrame()
        linha_div.setFrameShape(QFrame.Shape.HLine)
        linha_div.setObjectName("linha_divisoria")
        layout.addWidget(linha_div)

        self._linha(layout, "Lucro",    brl(lucro),              "valor_positivo")
        self._badge(layout, "Margem",   margem_pct(custo, preco))
        self._linha(layout, "Condição", celular.get("condicao") or "—", "valor_normal")

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
        self._aba_ativa = 0   # 0=Serviços  1=Produtos  2=Celulares
        self._janela_novo = None
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
        lbl_sub = QLabel("Gestão de serviços, produtos e celulares")
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
        self.btn_servicos.setFixedWidth(160)

        self.btn_produtos = QPushButton("📦 Produtos")
        self.btn_produtos.setCheckable(True)
        self.btn_produtos.setObjectName("btn_toggle")
        self.btn_produtos.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_produtos.setFixedWidth(160)

        self.btn_celulares = QPushButton("📱 Celulares")
        self.btn_celulares.setCheckable(True)
        self.btn_celulares.setObjectName("btn_toggle")
        self.btn_celulares.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_celulares.setFixedWidth(160)

        self.grupo_toggle.addButton(self.btn_servicos, 0)
        self.grupo_toggle.addButton(self.btn_produtos,  1)
        self.grupo_toggle.addButton(self.btn_celulares, 2)
        self.grupo_toggle.idClicked.connect(self._mudar_aba)

        toggle_layout.addWidget(self.btn_servicos)
        toggle_layout.addWidget(self.btn_produtos)
        toggle_layout.addWidget(self.btn_celulares)
        controles.addWidget(toggle_frame)

        self.edit_busca = QLineEdit()
        self.edit_busca.setPlaceholderText("🔍 Buscar por nome ou categoria...")
        self.edit_busca.textChanged.connect(lambda t: self._carregar(filtro=t))
        controles.addWidget(self.edit_busca)

        self.btn_novo = QPushButton("+ Novo Serviço")
        self.btn_novo.setObjectName("btn_primario")
        self.btn_novo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_novo.clicked.connect(self._abrir_novo)
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
        labels = {0: "+ Novo Serviço", 1: "+ Novo Produto", 2: "+ Novo Celular"}
        self.btn_novo.setText(labels[index])
        self.edit_busca.clear()
        self._carregar()

    def _abrir_novo(self):
        if self._aba_ativa == 1:
            from component.novoproduto import NovoProdutoWindow
            self._janela_novo = NovoProdutoWindow()
            self._janela_novo.show()
            self._janela_novo.destroyed.connect(self._carregar)
        elif self._aba_ativa == 2:
            from component.novocelular import NovoCelularWindow
            self._janela_novo = NovoCelularWindow()
            self._janela_novo.show()
            self._janela_novo.destroyed.connect(self._carregar)

    def _carregar(self, filtro: str = ""):
        for i in reversed(range(self.grid.count())):
            w = self.grid.itemAt(i).widget()
            if w:
                w.deleteLater()

        if self._aba_ativa == 0:
            itens = db.listar_servicos(filtro)
            cards = [
                ServicoCard(
                    s,
                    on_editar=lambda _, sv=s: self._editar_servico(sv),
                    on_excluir=lambda _, sv=s: self._excluir_servico(sv["id"]),
                )
                for s in itens
            ]
        elif self._aba_ativa == 1:
            itens = db.listar_produtos(filtro)
            cards = [
                ProdutoCatCard(
                    p,
                    on_editar=lambda _, pr=p: self._editar_produto(pr),
                    on_excluir=lambda _, pr=p: self._excluir_produto(pr["id"]),
                )
                for p in itens
            ]
        else:
            itens = db.listar_celulares(filtro)
            cards = [
                CelularCard(
                    c,
                    on_editar=lambda _, cl=c: self._editar_celular(cl),
                    on_excluir=lambda _, cl=c: self._excluir_celular(cl["id"]),
                )
                for c in itens
            ]

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

    # ─ Editar ─────────────────────────────────

    def _editar_servico(self, servico: dict):
        dlg = EditarServicoDialog(servico, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._carregar(filtro=self.edit_busca.text())

    def _editar_produto(self, produto: dict):
        dlg = EditarProdutoDialog(produto, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._carregar(filtro=self.edit_busca.text())

    def _editar_celular(self, celular: dict):
        dlg = EditarCelularDialog(celular, parent=self)
        if dlg.exec() == QDialog.DialogCode.Accepted:
            self._carregar(filtro=self.edit_busca.text())

    # ─ Excluir ────────────────────────────────

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

    def _excluir_celular(self, cid: int):
        if QMessageBox.question(self, "Excluir celular", "Deseja excluir este celular?",
                                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                                ) == QMessageBox.StandardButton.Yes:
            db.excluir_celular(cid)
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
            padding: 4px 12px; border-radius: 10px; max-width: 140px;
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

        /* Botão ⋮ */
        QPushButton#btn_menu_card {
            background-color: transparent;
            color: #64748B; border: none;
            font-size: 18px; font-weight: bold; padding: 0px 4px;
        }
        QPushButton#btn_menu_card:hover {
            color: #FFFFFF; background-color: #1E293B; border-radius: 4px;
        }

        /* Menu contextual */
        QMenu#menu_card {
            background-color: #0B1120; color: #FFFFFF;
            border: 1px solid #1E293B; border-radius: 8px; padding: 6px;
        }
        QMenu#menu_card::item {
            background-color: transparent;
            padding: 8px 18px; border-radius: 4px; font-size: 13px;
        }
        QMenu#menu_card::item:selected { background-color: #1E293B; color: #F26522; }
        QMenu#menu_card::separator { height: 1px; background: #1E293B; margin: 4px 0px; }
        """)
