import sys
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame,
    QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QPixmap

from component.svg_utils import svg_para_pixmap


COR_INATIVO = "#64748B"
COR_ATIVO   = "#F26522"


class SidebarMenu(QWidget):
    """
    Barra lateral de navegação do IFIX Pro.
    Emite o sinal `pagina_mudou` com o índice da tela sempre que um item é clicado.
    Também aceita um QStackedWidget opcional para controle direto.
    """
    pagina_mudou = pyqtSignal(int)

    # (arquivo SVG, texto do menu)
    ITENS_MENU = [
        ("fi-sr-dashboard.svg",          " Dashboard"),
        ("fi-sr-tools.svg",              " Laboratório"),
        ("fi-sr-shopping-cart.svg",      " Vendas"),
        ("fi-sr-users.svg",              " Clientes"),
        ("fi-sr-shield-check.svg",       " Garantias & RMA"),
        ("fi-sr-catalog.svg",            " Catálogo"),
        ("fi-sr-user-helmet-safety.svg", " Técnicos"),
        ("fi-sr-calculator.svg",         " Despesas"),
    ]

    def __init__(self, stacked_widget=None, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.botoes = []
        self._svgs   = []
        self._indice_ativo = 0
        self._initUI()
        self._aplicar_estilos()

    def _initUI(self):
        self.setFixedWidth(260)
        self.setObjectName("sidebar")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(16, 30, 16, 30)
        layout.setSpacing(6)

        # --- Logo ---
        _logo_path = os.path.join(os.path.dirname(__file__), '..', 'logo.png')
        lbl_logo = QLabel()
        lbl_logo.setObjectName("logo_img")
        lbl_logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if os.path.exists(_logo_path):
            pix = QPixmap(_logo_path).scaledToWidth(140, Qt.TransformationMode.SmoothTransformation)
            lbl_logo.setPixmap(pix)
        else:
            lbl_logo.setText("IFIX Pro")
            lbl_logo.setObjectName("logo_title")

        layout.addWidget(lbl_logo)
        layout.addSpacing(24)

        # --- Itens do Menu ---
        for i, (svg_file, texto) in enumerate(self.ITENS_MENU):
            btn = QPushButton(texto)
            btn.setIconSize(QSize(20, 20))
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setObjectName("menu_item")
            btn.clicked.connect(lambda checked, idx=i: self.mudar_tela(idx))
            layout.addWidget(btn)
            self.botoes.append(btn)
            self._svgs.append(svg_file)

        # Marca o primeiro item como ativo por padrão
        self._marcar_ativo(0)

        # --- Espaçador ---
        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # --- Rodapé (Versão) ---
        box_versao = QFrame()
        box_versao.setObjectName("box_versao")
        box_layout = QVBoxLayout(box_versao)
        box_layout.setContentsMargins(15, 15, 15, 15)
        box_layout.addWidget(QLabel("Versão", objectName="lbl_versao_cinza"))
        box_layout.addWidget(QLabel("IFIX Pro v2.0", objectName="lbl_versao_branca"))
        layout.addWidget(box_versao)

    def mudar_tela(self, index: int):
        """Muda a tela ativa e atualiza o estado visual dos botões."""
        self._indice_ativo = index
        self._marcar_ativo(index)

        if self.stacked_widget is not None:
            self.stacked_widget.setCurrentIndex(index)

        self.pagina_mudou.emit(index)

    def _marcar_ativo(self, index: int):
        for i, btn in enumerate(self.botoes):
            ativo = i == index
            btn.setObjectName("menu_item_ativo" if ativo else "menu_item")
            cor = COR_ATIVO if ativo else COR_INATIVO
            btn.setIcon(QIcon(svg_para_pixmap(self._svgs[i], cor)))

        # Força o Qt a reaplicar o QSS após a mudança de objectName
        self.style().unpolish(self)
        self.style().polish(self)
        for btn in self.botoes:
            btn.style().unpolish(btn)
            btn.style().polish(btn)

    def _aplicar_estilos(self):
        self.setStyleSheet("""
        /* Fundo da Sidebar */
        QWidget#sidebar {
            background-color: #0B1120;
            border-right: 1px solid #1E293B;
            font-family: 'Poppins', 'Montserrat', sans-serif;
        }

        /* Logo imagem */
        QLabel#logo_img {
            padding: 8px 0px;
        }

        /* Botão inativo */
        QPushButton#menu_item {
            background-color: transparent;
            color: #64748B;
            font-size: 13px;
            font-weight: 600;
            text-align: left;
            padding: 11px 18px;
            border-radius: 8px;
            border: none;
        }
        QPushButton#menu_item:hover {
            background-color: #1E293B;
            color: #FFFFFF;
        }

        /* Botão ativo */
        QPushButton#menu_item_ativo {
            background-color: #0F172A;
            color: #F26522;
            font-size: 13px;
            font-weight: 700;
            text-align: left;
            padding: 11px 18px;
            border-radius: 8px;
            border: 1px solid #1E293B;
        }

        /* Rodapé */
        QFrame#box_versao {
            background-color: #0F172A;
            border-radius: 10px;
        }
        QLabel#lbl_versao_cinza {
            color: #64748B;
            font-size: 11px;
        }
        QLabel#lbl_versao_branca {
            color: #FFFFFF;
            font-size: 13px;
            font-weight: 700;
        }
        """)


def create_sidebar():
    """Retorna o mapeamento de rotas do menu (legado)."""
    return {
        "dashboard":   "/pages/dashboard.py",
        "laboratorio": "/pages/laboratorio.py",
        "vendas":      "/pages/vendas.py",
        "clientes":    "/pages/clientes.py",
        "garantia":    "/pages/garantia.py",
        "catalogo":    "/pages/catalogo.py",
        "tecnicos":    "/pages/tecnicos.py",
    }
