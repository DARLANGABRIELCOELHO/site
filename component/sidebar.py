# O arquivo sidebar.py é responsável por criar a barra lateral do sistema, que contém as rotas para as diferentes páginas do sistema. Ele define uma função create_sidebar() que retorna um dicionário com as rotas das páginas, permitindo que os usuários naveguem facilmente entre as diferentes seções do sistema.
import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QFrame,
    QSpacerItem, QSizePolicy, QMessageBox, QFileDialog
)
import pages
def create_sidebar():
    menu_routes = {
        "dashboard": "/pages/dashboard.py",
        "laboratorio": "/pages/laboratorio.py",
        "vendas": "/pages/vendas.py",
        "clientes": "/pages/clientes.py",
        "garantia": "/pages/garantia.py",
        "catalogo": "/pages/catalogo.py",
        "tecnicos": "/pages/tecnicos.py",
    }
    return menu_routes
class SidebarMenu(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setFixedWidth(260)
        
        # Layout Principal
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 30, 20, 30)
        main_layout.setSpacing(10)

        # --- LOGO & TÍTULO ---
        lbl_logo = QLabel("📱 IFIX Pro")
        lbl_logo.setObjectName("logo_title")
        
        lbl_subtitle = QLabel("Manager")
        lbl_subtitle.setObjectName("logo_subtitle")
        
        main_layout.addWidget(lbl_logo)
        main_layout.addWidget(lbl_subtitle)
        main_layout.addSpacing(30) # Espaço após o logo

        # --- ITENS DO MENU ---
        itens_menu = [
            ("⊞", "Dashboard", False),
            ("🔧", "Laboratório", False),
            ("🛒", "Vendas", False),
            ("👥", "Clientes", False),
            ("🛡️", "Garantias & RMA", False),
            ("📦", "Catálogo", True),  
            ("🧑‍🔧", "Técnicos", False)
        ]

        self.botoes_menu = []
        for icone, texto, selecionado in itens_menu:
            btn = QPushButton(f"{icone}   {texto}")
            btn.setCursor(Qt.PointingHandCursor)
            
            # Se for o selecionado, aplica a classe especial no QSS
            if selecionado:
                btn.setObjectName("menu_item_ativo")
            else:
                btn.setObjectName("menu_item")
                
            main_layout.addWidget(btn)
            self.botoes_menu.append(btn)

        # --- ESPAÇADOR (Empurra o rodapé para baixo) ---
        spacer = QSpacerItem(20, 40, QSizePolicy.Minimum, QSizePolicy.Expanding)
        main_layout.addItem(spacer)

        # --- CAIXA DE VERSÃO (Rodapé) ---
        box_versao = QFrame()
        box_versao.setObjectName("box_versao")
        box_layout = QVBoxLayout(box_versao)
        box_layout.setContentsMargins(15, 15, 15, 15)
        
        lbl_versao_label = QLabel("Versão")
        lbl_versao_label.setObjectName("lbl_versao_cinza")
        
        lbl_versao_valor = QLabel("IFIX Pro v2.0")
        lbl_versao_valor.setObjectName("lbl_versao_branca")
        
        box_layout.addWidget(lbl_versao_label)
        box_layout.addWidget(lbl_versao_valor)
        
        main_layout.addWidget(box_versao)

        self.setLayout(main_layout)
        self.aplicar_estilos()

    def aplicar_estilos(self):
        """Aplica a paleta hexadecimal e tipografia usando Qt StyleSheet (QSS)"""
        estilo = """
        /* Fundo da Sidebar e Tipografia Global */
        SidebarMenu {
            background-color: #0F172A;
            font-family: 'Poppins', 'Montserrat', sans-serif;
        }

        /* Estilos do Logo */
        QLabel#logo_title {
            font-size: 22px;
            font-weight: 700;
            color: #FFFFFF;
        }
        QLabel#logo_subtitle {
            font-size: 12px;
            font-weight: 600;
            color: #64748B;
            margin-top: -5px;
            margin-left: 32px; /* Alinhar com o texto pulando o ícone */
        }

        /* Botões do Menu (Não Selecionados) */
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
            background-color: #1E293B; /* Leve destaque ao passar o mouse */
            color: #FFFFFF;
        }

        /* Botão do Menu (Selecionado / Ativo) */
        QPushButton#menu_item_ativo {
            background-color: #0B1120;
            color: #F26522; /* Destaque Laranja */
            font-size: 14px;
            font-weight: 700;
            text-align: left;
            padding: 12px 15px;
            border-radius: 8px;
            border: 1px solid #1E293B; /* Opcional: bordinha discreta */
        }

        /* Caixa de Versão no Rodapé */
        QFrame#box_versao {
            background-color: #0B1120;
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
        """
        self.setStyleSheet(estilo)     