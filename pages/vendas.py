# vendas é a página onde os usuários podem visualizar e gerenciar as vendas realizadas. Ele exibe uma lista de vendas, incluindo detalhes como o cliente, os produtos vendidos, o valor total e a data da venda. Os usuários também podem adicionar novas vendas, editar informações existentes e visualizar o histórico de vendas.
# Ele pode ser usado para acompanhar o desempenho de vendas, identificar os produtos mais vendidos e analisar as tendências de compra dos clientes.
# vendas.py

import os
import sys
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QSpacerItem, QSizePolicy,
    QScrollArea, QComboBox
)
from PyQt6.QtCore import Qt

# Adiciona o diretório pai ao sys.path para encontrar o pacote 'data' (se necessário)
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


class CartItem(QFrame):
    """Componente para um item adicionado ao Carrinho lateral"""
    def __init__(self, nome, preco, qtd):
        super().__init__()
        self.setObjectName("cart_item")
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)

        # Informações do Produto (Nome e Preço)
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        lbl_nome = QLabel(nome)
        lbl_nome.setObjectName("cart_item_nome")
        lbl_preco = QLabel(preco)
        lbl_preco.setObjectName("cart_item_preco")
        info_layout.addWidget(lbl_nome)
        info_layout.addWidget(lbl_preco)

        # Controles de Quantidade
        ctrl_layout = QHBoxLayout()
        ctrl_layout.setSpacing(10)
        
        btn_menos = QPushButton("-")
        btn_menos.setObjectName("btn_icon_pequeno")
        btn_menos.setCursor(Qt.CursorShape.PointingHandCursor)
        
        lbl_qtd = QLabel(str(qtd))
        lbl_qtd.setObjectName("cart_item_qtd")
        
        btn_mais = QPushButton("+")
        btn_mais.setObjectName("btn_icon_pequeno")
        btn_mais.setCursor(Qt.CursorShape.PointingHandCursor)
        
        btn_lixeira = QPushButton("🗑️")
        btn_lixeira.setObjectName("btn_lixeira")
        btn_lixeira.setCursor(Qt.CursorShape.PointingHandCursor)

        ctrl_layout.addWidget(btn_menos)
        ctrl_layout.addWidget(lbl_qtd)
        ctrl_layout.addWidget(btn_mais)
        ctrl_layout.addWidget(btn_lixeira)

        layout.addLayout(info_layout)
        layout.addItem(QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addLayout(ctrl_layout)


class ProdutoCard(QPushButton):
    """Componente customizado para os cards de Produtos no PDV"""
    def __init__(self, nome, preco, estoque, alerta=False, no_carrinho=False):
        super().__init__()
        self.setObjectName("card_produto_ativo" if no_carrinho else "card_produto")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(220, 150)  # Tamanho fixo para manter a grade uniforme

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)

        # --- Cabeçalho do Card (Ícone e Alerta) ---
        header_layout = QHBoxLayout()
        lbl_icone = QLabel("📦")
        lbl_icone.setObjectName("icone_box")
        header_layout.addWidget(lbl_icone)
        
        header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        if alerta:
            lbl_alerta = QLabel("⚠️")
            lbl_alerta.setObjectName("icone_alerta")
            header_layout.addWidget(lbl_alerta)
            
        layout.addLayout(header_layout)

        # --- Informações do Produto ---
        lbl_nome = QLabel(nome)
        lbl_nome.setObjectName("produto_nome")
        lbl_nome.setWordWrap(True)
        lbl_nome.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        lbl_preco = QLabel(preco)
        lbl_preco.setObjectName("produto_preco")
        lbl_preco.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        lbl_estoque = QLabel(estoque)
        lbl_estoque.setObjectName("produto_estoque_alerta" if alerta else "produto_estoque")
        lbl_estoque.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        layout.addWidget(lbl_nome)
        layout.addWidget(lbl_preco)
        layout.addWidget(lbl_estoque)

        # --- Indicador de Item no Carrinho ---
        if no_carrinho:
            lbl_tag_carrinho = QLabel("1x no carrinho")
            lbl_tag_carrinho.setObjectName("tag_no_carrinho")
            lbl_tag_carrinho.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_tag_carrinho.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            layout.addWidget(lbl_tag_carrinho)
        else:
            # Espaçador para manter o tamanho dos cards igual
            layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))


class VendasScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.carrinho_itens = []  # Lista para controlar itens (simulação)
        self.initUI()

    def initUI(self):
        # Não define window title para não conflitar com a janela principal
        self.setMinimumSize(1000, 700)
        
        # Layout Principal divide a tela em Esquerda (Produtos) e Direita (Carrinho)
        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # ==========================================
        # PAINEL ESQUERDO (Produtos e Busca)
        # ==========================================
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)

        # --- Cabeçalho (com Botão Finalizar Topo) ---
        header_layout = QHBoxLayout()
        
        titulos_layout = QVBoxLayout()
        titulos_layout.setSpacing(0)
        lbl_titulo = QLabel("VENDAS")
        lbl_titulo.setObjectName("title_main")
        lbl_sub = QLabel("PDV / Balcão")
        lbl_sub.setObjectName("subtitle")
        titulos_layout.addWidget(lbl_titulo)
        titulos_layout.addWidget(lbl_sub)
        
        self.btn_finalizar_topo = QPushButton("🛒 Finalizar (0)")
        self.btn_finalizar_topo.setObjectName("btn_primario")
        self.btn_finalizar_topo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_finalizar_topo.clicked.connect(self._finalizar_venda)
        
        header_layout.addLayout(titulos_layout)
        header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        header_layout.addWidget(self.btn_finalizar_topo)
        
        left_layout.addLayout(header_layout)

        # --- Barra de Busca ---
        self.edit_busca = QLineEdit()
        self.edit_busca.setPlaceholderText("🔍 Buscar produto...")
        left_layout.addWidget(self.edit_busca)

        # --- Área de Scroll e Grid de Produtos ---
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("scroll_area")
        
        scroll_content = QWidget()
        scroll_content.setObjectName("scroll_content")
        
        self.grid_produtos = QGridLayout(scroll_content)
        self.grid_produtos.setSpacing(15)
        self.grid_produtos.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        # Dados Mockados (exemplo com um item já no carrinho)
        produtos_mock = [
            ("vvv", "R$ 1000.00", "1 un", True, False),
            ("Tela iPhone 13 (peça)", "R$ 300.00", "4 un", False, False),
            ("Bateria iPhone (peça)", "R$ 90.00", "8 un", False, True),   # Já no carrinho
            ("Carregador USB-C 20W", "R$ 60.00", "14 un", False, False),
            ("Película de Vidro", "R$ 30.00", "50 un", False, False),
            ("Capinha Silicone", "R$ 35.00", "30 un", False, False)
        ]

        self.carregar_produtos(produtos_mock)

        scroll_area.setWidget(scroll_content)
        left_layout.addWidget(scroll_area)
        main_layout.addWidget(left_panel, stretch=7)

        # ==========================================
        # PAINEL DIREITO (Carrinho)
        # ==========================================
        self.cart_frame = QFrame()
        self.cart_frame.setObjectName("cart_frame")
        self.cart_frame.setFixedWidth(340)
        
        self.cart_layout = QVBoxLayout(self.cart_frame)
        self.cart_layout.setContentsMargins(20, 20, 20, 20)
        
        # Título do Carrinho
        lbl_carrinho_titulo = QLabel("🛒 Carrinho")
        lbl_carrinho_titulo.setObjectName("txt_branca_bold")
        self.cart_layout.addWidget(lbl_carrinho_titulo)
        self.cart_layout.addSpacing(15)

        # Área para os itens do carrinho (será preenchida dinamicamente)
        self.cart_items_area = QVBoxLayout()
        self.cart_items_area.setSpacing(10)
        self.cart_layout.addLayout(self.cart_items_area)

        # Espaçador flexível
        self.cart_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.cart_layout.addItem(self.cart_spacer)

        # Linha divisória e total (inicialmente ocultos)
        self.linha_divisoria = QFrame()
        self.linha_divisoria.setFrameShape(QFrame.Shape.HLine)
        self.linha_divisoria.setObjectName("linha_divisoria")
        self.linha_divisoria.setVisible(False)
        self.cart_layout.addWidget(self.linha_divisoria)

        self.total_layout = QHBoxLayout()
        self.lbl_total_txt = QLabel("Total")
        self.lbl_total_txt.setObjectName("txt_branca_16")
        self.lbl_total_val = QLabel("R$ 0,00")
        self.lbl_total_val.setObjectName("txt_laranja_20")
        self.lbl_total_val.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.total_layout.addWidget(self.lbl_total_txt)
        self.total_layout.addWidget(self.lbl_total_val)
        self.cart_layout.addLayout(self.total_layout)
        self.total_layout_parent = self.total_layout  # referência
        # Inicialmente oculto
        self.lbl_total_txt.setVisible(False)
        self.lbl_total_val.setVisible(False)

        # Botão Finalizar Grande
        self.btn_finalizar = QPushButton("✓ Finalizar Venda")
        self.btn_finalizar.setObjectName("btn_primario")
        self.btn_finalizar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_finalizar.setFixedHeight(45)
        self.btn_finalizar.setVisible(False)
        self.btn_finalizar.clicked.connect(self._finalizar_venda)
        self.cart_layout.addWidget(self.btn_finalizar)

        main_layout.addWidget(self.cart_frame, stretch=3)

        # Inicia o PDV limpo
        self.atualizar_carrinho(com_itens=False)

        self.aplicar_estilos()

    def carregar_produtos(self, produtos):
        """Popula o grid com os cards de produtos."""
        # Limpa o grid existente
        for i in reversed(range(self.grid_produtos.count())):
            self.grid_produtos.itemAt(i).widget().deleteLater()
        
        row, col = 0, 0
        for nome, preco, estoque, alerta, no_carrinho in produtos:
            card = ProdutoCard(nome, preco, estoque, alerta, no_carrinho)
            self.grid_produtos.addWidget(card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

    def atualizar_carrinho(self, com_itens=False):
        """Atualiza a exibição do carrinho: vazio ou com itens."""
        # Limpa a área de itens
        for i in reversed(range(self.cart_items_area.count())):
            item = self.cart_items_area.itemAt(i)
            if item.widget():
                item.widget().deleteLater()
            else:
                self.cart_items_area.removeItem(item)

        if com_itens:
            # Adiciona um item de exemplo (poderia ser gerado a partir de self.carrinho_itens)
            item = CartItem("Bateria iPhone...", "R$ 90.00", 1)
            self.cart_items_area.addWidget(item)

            # Mostra linha divisória, totais e botão finalizar
            self.linha_divisoria.setVisible(True)
            self.lbl_total_txt.setVisible(True)
            self.lbl_total_val.setVisible(True)
            self.lbl_total_val.setText("R$ 90.00")
            self.btn_finalizar.setVisible(True)
            self.btn_finalizar_topo.setText("🛒 Finalizar (1)")
        else:
            # Exibe mensagem de carrinho vazio
            lbl_vazio = QLabel("Carrinho vazio")
            lbl_vazio.setObjectName("txt_cinza_centro")
            lbl_vazio.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cart_items_area.addWidget(lbl_vazio)

            self.linha_divisoria.setVisible(False)
            self.lbl_total_txt.setVisible(False)
            self.lbl_total_val.setVisible(False)
            self.btn_finalizar.setVisible(False)
            self.btn_finalizar_topo.setText("🛒 Finalizar (0)")

    def _finalizar_venda(self):
        from PyQt6.QtWidgets import QMessageBox
        if not self.carrinho_itens:
            QMessageBox.warning(self, "Carrinho vazio", "Adicione produtos antes de finalizar.")
            return
        resp = QMessageBox.question(
            self, "Finalizar Venda",
            f"Confirmar venda de {len(self.carrinho_itens)} item(ns)?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resp == QMessageBox.StandardButton.Yes:
            # Aqui entraria o registro no banco; por ora reinicia o PDV
            self.carrinho_itens.clear()
            self.edit_busca.clear()
            self.atualizar_carrinho(com_itens=False)

    def aplicar_estilos(self):
        estilo = """
        /* Fundo Geral e Tipografia */
        QWidget {
            background-color: #0F172A;
            font-family: 'Poppins', 'Montserrat', sans-serif;
        }

        /* Títulos */
        QLabel#title_main {
            color: #FFFFFF;
            font-size: 24px;
            font-weight: 700;
            text-transform: uppercase;
        }
        QLabel#subtitle {
            color: #64748B;
            font-size: 12px;
            font-weight: 600;
            margin-top: -5px;
        }

        /* Input de Busca */
        QLineEdit {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 8px;
            padding: 12px;
            color: #FFFFFF;
            font-size: 13px;
        }
        QLineEdit:focus { border: 1px solid #F26522; }

        /* Botão Primário Laranja */
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

        /* Scroll Area */
        QScrollArea#scroll_area { border: none; background-color: transparent; }
        QWidget#scroll_content { background-color: transparent; }
        QScrollBar:vertical { border: none; background-color: #0B1120; width: 8px; border-radius: 4px; }
        QScrollBar::handle:vertical { background-color: #1E293B; min-height: 20px; border-radius: 4px; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }

        /* Cards de Produto (Normal e Ativo) */
        QPushButton#card_produto, QPushButton#card_produto_ativo {
            background-color: #0B1120;
            border-radius: 10px;
            text-align: left;
        }
        QPushButton#card_produto { border: 1px solid #1E293B; }
        QPushButton#card_produto:hover { background-color: #1E293B; border: 1px solid #64748B; }
        
        QPushButton#card_produto_ativo {
            border: 1px solid #F26522;
            background-color: rgba(242, 101, 34, 0.05);
        }

        /* Elementos do Card */
        QLabel#icone_box {
            background-color: #1E293B;
            border-radius: 6px;
            padding: 6px;
            font-size: 16px;
        }
        QLabel#icone_alerta { font-size: 14px; }
        QLabel#produto_nome {
            color: #FFFFFF;
            font-size: 13px;
            font-weight: 700;
        }
        QLabel#produto_preco {
            color: #F26522;
            font-size: 14px;
            font-weight: 700;
        }
        QLabel#produto_estoque {
            color: #64748B;
            font-size: 11px;
        }
        QLabel#produto_estoque_alerta {
            color: #EAB308;
            font-size: 11px;
            font-weight: 600;
        }
        QLabel#tag_no_carrinho {
            background-color: rgba(242, 101, 34, 0.15);
            color: #F26522;
            font-size: 10px;
            font-weight: 700;
            border-radius: 4px;
            padding: 4px;
            margin-top: 5px;
        }

        /* Painel do Carrinho (Direita) */
        QFrame#cart_frame {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 12px;
        }
        
        /* Itens do Carrinho */
        QLabel#txt_branca_bold {
            color: #FFFFFF;
            font-size: 16px;
            font-weight: 700;
        }
        QLabel#cart_item_nome {
            color: #FFFFFF;
            font-size: 13px;
            font-weight: 600;
        }
        QLabel#cart_item_preco {
            color: #64748B;
            font-size: 12px;
        }
        QLabel#cart_item_qtd {
            color: #FFFFFF;
            font-size: 14px;
            font-weight: 700;
        }
        
        /* Botões + e - do Carrinho */
        QPushButton#btn_icon_pequeno {
            background-color: transparent;
            color: #FFFFFF;
            font-size: 16px;
            font-weight: bold;
            border: none;
        }
        QPushButton#btn_icon_pequeno:hover { color: #F26522; }
        
        /* Botão Lixeira */
        QPushButton#btn_lixeira {
            background-color: transparent;
            color: #EF4444;
            font-size: 14px;
            border: none;
            margin-left: 5px;
        }
        QPushButton#btn_lixeira:hover { color: #B91C1C; }

        /* Linha divisória */
        QFrame#linha_divisoria {
            background-color: #1E293B;
            max-height: 1px;
            border: none;
        }
        QLabel#txt_branca_16 {
            color: #FFFFFF;
            font-size: 16px;
            font-weight: 600;
        }
        QLabel#txt_laranja_20 {
            color: #F26522;
            font-size: 20px;
            font-weight: 700;
        }
        QLabel#txt_cinza_centro {
            color: #64748B;
            font-size: 14px;
            font-weight: 600;
        }
        """
        self.setStyleSheet(estilo)


# Exemplo de uso standalone (para teste)
if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VendasScreen()
    window.show()
    sys.exit(app.exec())