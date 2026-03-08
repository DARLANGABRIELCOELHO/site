import sys
import os

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QLabel, QStackedWidget
)
from PyQt6.QtCore import Qt

# Garante que o diretório raiz está no path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from component.sidebar import SidebarMenu
from pages.laboratorio import LaboratorioScreen
from pages.vendas import VendasScreen
from pages.clientes import ClientesScreen
from pages.garantia import GarantiasRMAScreen
from pages.tecnicos import TecnicosScreen
from pages.dashboard import DashboardScreen
from pages.catalogo import CatalogoScreen


class PlaceholderScreen(QWidget):
    """Tela provisória para páginas ainda não implementadas."""
    def __init__(self, titulo: str):
        super().__init__()
        layout = QVBoxLayout(self)
        lbl = QLabel(titulo)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setStyleSheet("color: #FFFFFF; font-size: 24px; font-weight: 700;")
        layout.addWidget(lbl)
        self.setStyleSheet("background-color: #0F172A;")


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IFIX Pro Manager")
        self.setMinimumSize(1280, 800)

        central = QWidget()
        self.setCentralWidget(central)

        root_layout = QHBoxLayout(central)
        root_layout.setContentsMargins(0, 0, 0, 0)
        root_layout.setSpacing(0)

        # --- Área de conteúdo (ordem deve bater com SidebarMenu.ITENS_MENU) ---
        self.stack = QStackedWidget()
        self.stack.setObjectName("content_area")
        self.stack.addWidget(DashboardScreen())                    # 0
        self.stack.addWidget(LaboratorioScreen())                  # 1
        self.stack.addWidget(VendasScreen())                       # 2
        self.stack.addWidget(ClientesScreen())                     # 3
        self.stack.addWidget(GarantiasRMAScreen())                 # 4
        self.stack.addWidget(CatalogoScreen())                     # 5
        self.stack.addWidget(TecnicosScreen())                     # 6

        # --- Sidebar ---
        self.sidebar = SidebarMenu(stacked_widget=self.stack)

        root_layout.addWidget(self.sidebar)
        root_layout.addWidget(self.stack)

        # Abre no Dashboard por padrão
        self.sidebar.mudar_tela(0)

        self.setStyleSheet("""
            QMainWindow { background-color: #0F172A; }
            QWidget#content_area { background-color: #0F172A; }
        """)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
