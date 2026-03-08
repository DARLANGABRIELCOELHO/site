# laboratorio é a página onde os técnicos podem acessar informações detalhadas sobre os serviços em andamento, incluindo o status de cada serviço, as peças necessárias, os prazos estimados e as instruções de reparo. Ele também pode incluir uma seção para os técnicos registrarem notas e atualizações sobre o progresso dos serviços.
# Ele pode ser usado para melhorar a comunicação entre os técnicos e a equipe de atendimento ao cliente, garantindo que todos estejam atualizados sobre o status dos serviços e possam fornecer informações precisas aos clientes.
# ======================================================================
# IMPORTAÇÕES
# ======================================================================
import sys
import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QWidget, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QFrame, QCheckBox,
    QSpacerItem, QSizePolicy, QMessageBox, QFileDialog, QScrollArea,
    QButtonGroup, QComboBox, QTabWidget, QMainWindow, QStackedWidget
)
from PyQt6.QtCore import Qt

# Adiciona o diretório pai ao sys.path para encontrar o pacote 'data'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db

# ======================================================================
# COMPONENTES DA TELA DE LABORATÓRIO (adaptados do catalogo.py)
# ======================================================================
class Badge(QLabel):
    """Componente para as tags de status e prioridade (ex: Urgente, Pronto)"""
    def __init__(self, texto, cor_fundo, cor_texto):
        super().__init__(texto)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        estilo = f"""
            background-color: {cor_fundo};
            color: {cor_texto};
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 10px;
            font-weight: 700;
        """
        self.setStyleSheet(estilo)

class OSCard(QFrame):
    """Card de Ordem de Serviço (Expandido ou Colapsado)"""
    def __init__(self, nome, aparelho, tempo, tecnico, status, prioridade, expandido=False):
        super().__init__()
        self.setObjectName("os_card")
        self.setFixedWidth(320)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(12)

        # --- Cabeçalho do Card (Ícone, Nome, Aparelho) ---
        header_layout = QHBoxLayout()
        lbl_icone = QLabel("📱")
        lbl_icone.setObjectName("icone_card")
        
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        lbl_nome = QLabel(nome)
        lbl_nome.setObjectName("txt_branca_bold")
        lbl_aparelho = QLabel(aparelho)
        lbl_aparelho.setObjectName("txt_cinza")
        info_layout.addWidget(lbl_nome)
        info_layout.addWidget(lbl_aparelho)
        
        btn_opcoes = QPushButton("⋮")
        btn_opcoes.setObjectName("btn_transparente")
        btn_opcoes.setCursor(Qt.CursorShape.PointingHandCursor)
        
        header_layout.addWidget(lbl_icone)
        header_layout.addLayout(info_layout)
        header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        header_layout.addWidget(btn_opcoes)
        layout.addLayout(header_layout)

        # --- Badges (Status e Prioridade) ---
        badges_layout = QHBoxLayout()
        badges_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        # Cores semânticas para os badges adaptadas para tema escuro
        if status == "Pronto":
            badges_layout.addWidget(Badge("Pronto", "rgba(34, 197, 94, 0.2)", "#4ADE80")) # Verde
        elif status == "Pendente":
            badges_layout.addWidget(Badge("Pendente", "rgba(234, 179, 8, 0.2)", "#FDE047")) # Amarelo
            
        if prioridade == "Urgente":
            badges_layout.addWidget(Badge("Urgente", "rgba(239, 68, 68, 0.2)", "#F87171")) # Vermelho
        else:
            badges_layout.addWidget(Badge("Normal", "rgba(100, 116, 139, 0.2)", "#94A3B8")) # Cinza
            
        layout.addLayout(badges_layout)

        # --- Metadados (Tempo e Técnico) ---
        meta_layout = QHBoxLayout()
        meta_layout.addWidget(QLabel(f"🕒 {tempo}"))
        meta_layout.addWidget(QLabel(f"🔧 {tecnico}"))
        meta_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        # Aplica estilo aos labels de meta
        for i in range(meta_layout.count() - 1):
            meta_layout.itemAt(i).widget().setObjectName("txt_cinza_pequeno")
        layout.addLayout(meta_layout)

        # --- Conteúdo Expandido ---
        if expandido:
            # Telefone
            lbl_tel = QLabel("📞 (11) 93456-7890")
            lbl_tel.setObjectName("txt_branca")
            layout.addWidget(lbl_tel)
            
            # Defeito
            layout.addWidget(QLabel("Defeito:", objectName="txt_cinza_pequeno"))
            layout.addWidget(QLabel("Tela quebrada e bateria viciada.", objectName="txt_branca"))
            
            # Serviços
            layout.addWidget(QLabel("Serviços:", objectName="txt_cinza_pequeno"))
            serv_layout = QHBoxLayout()
            serv_layout.addWidget(QLabel("Atualização de Software", objectName="txt_branca"))
            lbl_preco = QLabel("R$ 80.00")
            lbl_preco.setObjectName("txt_laranja")
            serv_layout.addWidget(lbl_preco)
            layout.addLayout(serv_layout)
            
            # Total
            total_layout = QHBoxLayout()
            lbl_total_txt = QLabel("Total")
            lbl_total_txt.setObjectName("txt_branca_bold")
            lbl_total_val = QLabel("R$ 80.00")
            lbl_total_val.setObjectName("txt_laranja_bold")
            total_layout.addWidget(lbl_total_txt)
            total_layout.addWidget(lbl_total_val)
            layout.addLayout(total_layout)
            
            # Botões de Estágio (Pendente, Em Análise, etc)
            estagios_layout = QHBoxLayout()
            estagios = ["Pendente", "Em Análise", "Em Andamento", "Pronto"]
            for est in estagios:
                btn_est = QPushButton(est)
                btn_est.setObjectName("btn_estagio_ativo" if est == "Pronto" else "btn_estagio")
                estagios_layout.addWidget(btn_est)
            layout.addLayout(estagios_layout)
            
            # Botão de Ação Final
            btn_checkout = QPushButton("✓ Entregar / Checkout")
            btn_checkout.setObjectName("btn_primario")
            btn_checkout.setCursor(Qt.CursorShape.PointingHandCursor)
            layout.addWidget(btn_checkout)
            
            # Borda de destaque quando o card está foco/pronto
            self.setStyleSheet("QFrame#os_card { border: 1px solid #F26522; }")
        else:
            # Indicador de colapsado (setinha)
            seta = QLabel(">")
            seta.setObjectName("txt_cinza")
            seta.setAlignment(Qt.AlignmentFlag.AlignRight)
            layout.addWidget(seta)

class LaboratorioScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        # Não define window title aqui porque será gerenciado pela MainWindow
        self.setMinimumSize(900, 700)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        # --- Cabeçalho Superior ---
        header_layout = QHBoxLayout()
        
        titulos_layout = QVBoxLayout()
        titulos_layout.setSpacing(0)
        lbl_titulo = QLabel("Laboratório")
        lbl_titulo.setObjectName("title_main")
        lbl_sub = QLabel("Gestão de Ordens de Serviço")
        lbl_sub.setObjectName("subtitle")
        titulos_layout.addWidget(lbl_titulo)
        titulos_layout.addWidget(lbl_sub)
        
        btn_nova_os = QPushButton("+ Nova OS")
        btn_nova_os.setObjectName("btn_primario")
        btn_nova_os.setCursor(Qt.CursorShape.PointingHandCursor)
        
        header_layout.addLayout(titulos_layout)
        header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        header_layout.addWidget(btn_nova_os)
        main_layout.addLayout(header_layout)

        # --- Barra de Filtros ---
        filtros_layout = QHBoxLayout()
        filtros_layout.setSpacing(15)
        
        self.edit_busca = QLineEdit()
        self.edit_busca.setPlaceholderText("🔍 Buscar por cliente, modelo ou ID...")
        
        self.cmb_status = QComboBox()
        self.cmb_status.addItems(["Todos os Status", "Pendente", "Em Andamento", "Pronto"])
        self.cmb_status.setFixedWidth(180)
        
        filtros_layout.addWidget(self.edit_busca)
        filtros_layout.addWidget(self.cmb_status)
        main_layout.addLayout(filtros_layout)

        # --- Área de Scroll para os Cards ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("scroll_area")
        
        scroll_content = QWidget()
        scroll_content.setObjectName("scroll_content")
        
        # Grid para colocar os cards lado a lado
        grid_cards = QGridLayout(scroll_content)
        grid_cards.setSpacing(20)
        grid_cards.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        
        # Criando cards baseados na imagem
        card1 = OSCard("Juliana Costa", "iphone 14", "21 days ago", "Maria Santos", "Pronto", "Urgente", expandido=True)
        card2 = OSCard("Carlos Mendes", "iphone 12", "a month ago", "Pedro Oliveira", "Pendente", "Normal", expandido=False)
        
        grid_cards.addWidget(card1, 0, 0)
        grid_cards.addWidget(card2, 0, 1)
        
        scroll_area.setWidget(scroll_content)
        main_layout.addWidget(scroll_area)

        self.aplicar_estilos()

    def aplicar_estilos(self):
        estilo = """
        /* Fundo e Tipografia Global (dentro do LaboratorioScreen) */
        QWidget {
            background-color: #0F172A;
            font-family: 'Poppins', 'Montserrat', sans-serif;
        }

        /* Títulos */
        QLabel#title_main {
            color: #FFFFFF;
            font-size: 24px;
            font-weight: 700;
        }
        QLabel#subtitle {
            color: #64748B;
            font-size: 12px;
            font-weight: 600;
        }

        /* Textos Utilitários */
        QLabel#txt_branca { color: #FFFFFF; font-size: 12px; }
        QLabel#txt_branca_bold { color: #FFFFFF; font-size: 14px; font-weight: 700; }
        QLabel#txt_cinza { color: #64748B; font-size: 12px; }
        QLabel#txt_cinza_pequeno { color: #64748B; font-size: 11px; font-weight: 600; }
        QLabel#txt_laranja { color: #F26522; font-size: 12px; font-weight: 600; }
        QLabel#txt_laranja_bold { color: #F26522; font-size: 14px; font-weight: 700; }

        /* Inputs e Combobox (Barra de Filtro) */
        QLineEdit, QComboBox {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 8px;
            padding: 12px;
            color: #FFFFFF;
            font-size: 13px;
        }
        QLineEdit:focus, QComboBox:focus { border: 1px solid #F26522; }
        QComboBox::drop-down { border: none; }

        /* Card de Ordem de Serviço */
        QFrame#os_card {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 12px;
        }
        
        /* Ícone quadrado do Card */
        QLabel#icone_card {
            background-color: #1E293B;
            border-radius: 8px;
            padding: 8px;
            font-size: 20px;
        }

        /* Botões Transparentes (Três pontos) */
        QPushButton#btn_transparente {
            background-color: transparent;
            color: #64748B;
            border: none;
            font-size: 18px;
            font-weight: bold;
        }
        QPushButton#btn_transparente:hover { color: #FFFFFF; }

        /* Botões de Estágio (Mini botões dentro do card) */
        QPushButton#btn_estagio {
            background-color: #1E293B;
            color: #64748B;
            border: none;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 10px;
            font-weight: 600;
        }
        QPushButton#btn_estagio_ativo {
            background-color: #0F172A;
            color: #4ADE80;
            border: 1px solid #4ADE80;
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 10px;
            font-weight: 600;
        }

        /* Botão Primário Laranja (+ Nova OS e Checkout) */
        QPushButton#btn_primario {
            background-color: #F26522;
            color: #FFFFFF;
            font-size: 14px;
            font-weight: 600;
            border-radius: 6px;
            padding: 10px 20px;
            border: none;
        }
        QPushButton#btn_primario:hover { background-color: #E05412; }

        /* Scroll Area (Escondendo bordas) */
        QScrollArea#scroll_area { border: none; background-color: transparent; }
        QWidget#scroll_content { background-color: transparent; }
        QScrollBar:vertical { border: none; background-color: #0B1120; width: 8px; border-radius: 4px; }
        QScrollBar::handle:vertical { background-color: #1E293B; min-height: 20px; border-radius: 4px; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }
        """
        self.setStyleSheet(estilo)

# ======================================================================
# MENU LATERAL E JANELA PRINCIPAL (comprimido)
# ======================================================================
class SidebarMenu(QWidget):
    """Componente do Menu Lateral"""
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
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
        self.botoes = []
        itens_menu = [
            ("⊞", "Dashboard"),
            ("🔧", "Laboratório"),
            ("🛒", "Vendas"),
            ("👥", "Clientes"),
            ("🛡️", "Garantias & RMA"),
            ("🧮", "Orçamentos"),
            ("📦", "Catálogo"),
            ("🧑‍🔧", "Técnicos")
        ]

        for i, (icone, texto) in enumerate(itens_menu):
            btn = QPushButton(f"{icone}   {texto}")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.setObjectName("menu_item")
            
            # Conecta o clique do botão à troca de tela
            btn.clicked.connect(lambda checked, index=i: self.mudar_tela(index))
            
            layout.addWidget(btn)
            self.botoes.append(btn)

        # Define a primeira aba (Laboratório) como ativa
        self.mudar_tela(1)

        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # --- Rodapé ---
        box_versao = QFrame()
        box_versao.setObjectName("box_versao")
        box_layout = QVBoxLayout(box_versao)
        box_layout.addWidget(QLabel("Versão", objectName="lbl_versao_cinza"))
        box_layout.addWidget(QLabel("IFIX Pro v2.0", objectName="lbl_versao_branca"))
        layout.addWidget(box_versao)

    def mudar_tela(self, index):
        """Muda a tela no QStackedWidget e atualiza a cor do botão ativo"""
        self.stacked_widget.setCurrentIndex(index)
        
        for i, btn in enumerate(self.botoes):
            if i == index:
                btn.setObjectName("menu_item_ativo")
            else:
                btn.setObjectName("menu_item")
                
        # Força a re-renderização do estilo (QSS)
        self.setStyleSheet(self.styleSheet())


class PlaceholderScreen(QWidget):
    """Tela genérica para preencher os menus que ainda não codamos"""
    def __init__(self, titulo):
        super().__init__()
        layout = QVBoxLayout(self)
        lbl = QLabel(titulo)
        lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl.setObjectName("title_main")
        layout.addWidget(lbl)


class MainWindow(QMainWindow):
    """Janela Principal que une Sidebar e o Conteúdo"""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("IFIX Pro Manager")
        self.setMinimumSize(1200, 800)
        
        # Widget Central que segura o Layout Principal (Sidebar + Conteúdo)
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # 1. Área de Conteúdo (Stacked Widget)
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.setObjectName("content_area")
        
        # Adiciona as telas ao StackedWidget (A ordem importa!)
        self.stacked_widget.addWidget(PlaceholderScreen("Dashboard"))          # Index 0
        self.stacked_widget.addWidget(LaboratorioScreen())                    # Index 1 (Laboratório real)
        self.stacked_widget.addWidget(PlaceholderScreen("Vendas"))            # Index 2
        self.stacked_widget.addWidget(PlaceholderScreen("Clientes"))          # Index 3
        self.stacked_widget.addWidget(PlaceholderScreen("Garantias & RMA"))   # Index 4
        self.stacked_widget.addWidget(PlaceholderScreen("Orçamentos"))        # Index 5
        self.stacked_widget.addWidget(PlaceholderScreen("Catálogo"))          # Index 6
        self.stacked_widget.addWidget(PlaceholderScreen("Técnicos"))          # Index 7

        # 2. Sidebar Lateral
        self.sidebar = SidebarMenu(self.stacked_widget)

        # Monta a estrutura final
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.stacked_widget)

        self.aplicar_estilos_globais()

    def aplicar_estilos_globais(self):
        estilo = """
        /* Fundo da Janela Principal */
        QMainWindow, QWidget#content_area {
            background-color: #0F172A;
            font-family: 'Poppins', 'Montserrat', sans-serif;
        }

        /* Fundo da Sidebar (Tom mais escuro) */
        QWidget#sidebar {
            background-color: #0B1120;
            border-right: 1px solid #1E293B;
        }

        /* Títulos Globais */
        QLabel#title_main {
            color: #FFFFFF;
            font-size: 24px;
            font-weight: 700;
        }
        QLabel#logo_title { color: #FFFFFF; font-size: 22px; font-weight: 700; }
        QLabel#logo_subtitle { color: #64748B; font-size: 12px; font-weight: 600; margin-left: 32px; margin-top: -5px;}

        /* Botões do Menu Lateral */
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
        QPushButton#menu_item_ativo {
            background-color: #0F172A; /* Mesma cor do conteúdo principal */
            color: #F26522; /* Laranja */
            font-size: 14px;
            font-weight: 700;
            text-align: left;
            padding: 12px 15px;
            border-radius: 8px;
            border: 1px solid #1E293B;
        }

        /* Rodapé da Versão */
        QFrame#box_versao { background-color: #0F172A; border-radius: 10px; }
        QLabel#lbl_versao_cinza { color: #64748B; font-size: 11px; }
        QLabel#lbl_versao_branca { color: #FFFFFF; font-size: 13px; font-weight: 700; }
        """
        self.setStyleSheet(estilo)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())