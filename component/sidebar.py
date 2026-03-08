import sys
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame,
    QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal


class SidebarMenu(QWidget):
    """
    Barra lateral de navegação do IFIX Pro.
    Emite o sinal `pagina_mudou` com o índice da tela sempre que um item é clicado.
    Também aceita um QStackedWidget opcional para controle direto.
    """
    pagina_mudou = pyqtSignal(int)

    ITENS_MENU = [
        ("⊞", "Dashboard"),
        ("🔧", "Laboratório"),
        ("🛒", "Vendas"),
        ("👥", "Clientes"),
        ("🛡️", "Garantias & RMA"),
        ("📦", "Catálogo"),
        ("🧑‍🔧", "Técnicos"),
    ]

    def __init__(self, stacked_widget=None, parent=None):
        super().__init__(parent)
        self.stacked_widget = stacked_widget
        self.botoes = []
        self._indice_ativo = 0
        self._initUI()
        self._aplicar_estilos()

    def _initUI(self):
        self.setFixedWidth(260)
        self.setObjectName("sidebar")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 30, 20, 30)
        layout.setSpacing(10)

        # --- Logo ---
        lbl_logo = QLabel("📱 IFIX Pro")
        lbl_logo.setObjectName("logo_title")

        lbl_subtitle = QLabel("Manager")
        lbl_subtitle.setObjectName("logo_subtitle")

        layout.addWidget(lbl_logo)
        layout.addWidget(lbl_subtitle)
        layout.addSpacing(30)

        # --- Itens do Menu ---
        for i, (icone, texto) in enumerate(self.ITENS_MENU):
            btn = QPushButton(f"{icone}   {texto}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setObjectName("menu_item")
            btn.clicked.connect(lambda checked, idx=i: self.mudar_tela(idx))
            layout.addWidget(btn)
            self.botoes.append(btn)

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
            btn.setObjectName("menu_item_ativo" if i == index else "menu_item")

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

        /* Logo */
        QLabel#logo_title {
            color: #FFFFFF;
            font-size: 22px;
            font-weight: 700;
        }
        QLabel#logo_subtitle {
            color: #64748B;
            font-size: 12px;
            font-weight: 600;
            margin-top: -5px;
            margin-left: 32px;
        }

        /* Botão inativo */
        QPushButton#menu_item {
            background-color: transparent;
            color: #64748B;
            font-size: 14px;
            font-weight: 600;
            text-align: left;
            padding: 12px 15px;
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
            font-size: 14px;
            font-weight: 700;
            text-align: left;
            padding: 12px 15px;
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
