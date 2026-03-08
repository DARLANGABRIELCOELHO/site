import sys
import os
import ctypes

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QHBoxLayout, QVBoxLayout, QLabel, QStackedWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# ID único do app para o Windows agrupar e exibir o ícone corretamente na barra de tarefas
ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("ifix.sistema.desktop")

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
        self.setWindowIcon(QIcon(resource_path("logo.ico")))
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
    try:
        app = QApplication(sys.argv)
        app.setWindowIcon(QIcon(resource_path("logo.ico")))
        window = MainWindow()
        window.show()
        sys.exit(app.exec())
    except Exception as e:
        import traceback
        import pathlib
        crash_file = pathlib.Path(os.getenv("LOCALAPPDATA", str(pathlib.Path.home()))) / "iFix" / "crash.txt"
        crash_file.parent.mkdir(parents=True, exist_ok=True)
        with open(crash_file, "w") as f:
            f.write(traceback.format_exc())
            f.write(f"\n{e}")
        from PyQt6.QtWidgets import QMessageBox
        # Fallback raw message box 
        # Needs active application or QApplication.instance()
        if not QApplication.instance():
            _app = QApplication(sys.argv)
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Critical)
        msg.setText("Erro fatal:")
        msg.setDetailedText(traceback.format_exc())
        msg.exec()
