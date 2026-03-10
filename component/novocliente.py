# novocliente.py
# Interface gráfica para cadastro de novo cliente (PyQt6)
import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QFrame,
    QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import QSize
from PyQt6.QtGui import QIcon

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db
from component.base_dialog import ModernWindow

try:
    from component.svg_utils import svg_para_pixmap
    _SVG_OK = True
except Exception:
    _SVG_OK = False
#========================================================================================================================================
# JANELA DE CADASTRO DE NOVO CLIENTE
#========================================================================================================================================
class NovoClienteWindow(ModernWindow):
    def __init__(self):
        super().__init__("Novo Cliente", 620, 580)
        db.inicializar_estado()
        self.initUI()

    def initUI(self):
        main_layout = self.content_layout

        # Grid Layout
        grid = QGridLayout()
        grid.setSpacing(15)

        # Linha 1: Nome e Telefone
        grid.addWidget(QLabel("Nome *"), 0, 0)
        self.edit_nome = QLineEdit()
        grid.addWidget(self.edit_nome, 1, 0)

        grid.addWidget(QLabel("Telefone *"), 0, 1)
        self.edit_telefone = QLineEdit()
        grid.addWidget(self.edit_telefone, 1, 1)

        # Linha 2: Documento
        grid.addWidget(QLabel("CPF/CNPJ"), 2, 0, 1, 2)
        self.edit_documento = QLineEdit()
        grid.addWidget(self.edit_documento, 3, 0, 1, 2)

        # Linha 3: Endereço
        grid.addWidget(QLabel("Endereço"), 4, 0, 1, 2)
        self.edit_endereco = QLineEdit()
        grid.addWidget(self.edit_endereco, 5, 0, 1, 2)

        # Linha 4: Observações
        grid.addWidget(QLabel("Observações"), 6, 0, 1, 2)
        self.edit_observacoes = QTextEdit()
        self.edit_observacoes.setMaximumHeight(120)
        grid.addWidget(self.edit_observacoes, 7, 0, 1, 2)

        main_layout.addLayout(grid)
        main_layout.addSpacing(15)

        # Linha separadora laranja
        linha = QFrame()
        linha.setFrameShape(QFrame.Shape.HLine)
        linha.setObjectName("linha_laranja")
        main_layout.addWidget(linha)

        main_layout.addSpacing(15)

        # Botões
        botoes_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        botoes_layout.addItem(spacer)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("btnCancelar")

        self.btn_cadastrar = QPushButton("Cadastrar")
        self.btn_cadastrar.setObjectName("btnCadastrar")
        if _SVG_OK:
            self.btn_cadastrar.setIcon(QIcon(svg_para_pixmap("fi-sr-check.svg", "#FFFFFF", 16, 16)))
            self.btn_cadastrar.setIconSize(QSize(16, 16))

        botoes_layout.addWidget(self.btn_cancelar)
        botoes_layout.addWidget(self.btn_cadastrar)

        # Conexões (descomente e implemente o método salvar_cliente quando necessário)
        self.btn_cadastrar.clicked.connect(self.salvar_cliente)
        self.btn_cancelar.clicked.connect(self.close)

        main_layout.addLayout(botoes_layout)

        self.aplicar_estilos()
#========================================================================================================================================
# ESTILOS
#========================================================================================================================================
    def aplicar_estilos(self):
        estilo = """
        QLabel#title {
            font-size: 20px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        /* Estilo das Labels descritivas */
        QLabel {
            font-size: 12px;
            font-weight: 600;
            color: #64748B;
            letter-spacing: 0.5px;
        }

        /* Campos de Entrada (Inputs) */
        QLineEdit, QTextEdit {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 6px;
            padding: 10px;
            color: #FFFFFF;
            font-size: 14px;
            selection-background-color: #F26522;
        }

        /* Destaque ao clicar/focar no input */
        QLineEdit:focus, QTextEdit:focus {
            border: 1px solid #F26522;
        }

        /* Linha laranja acima dos botões */
        QFrame#linha_laranja {
            background-color: #F26522;
            max-height: 1px;
            border: none;
        }

        /* Base para os botões */
        QPushButton {
            font-size: 14px;
            font-weight: 600;
            border-radius: 6px;
            padding: 10px 24px;
        }

        /* Botão Cadastrar (Laranja) */
        QPushButton#btnCadastrar {
            background-color: #F26522;
            color: #FFFFFF;
            border: none;
        }
        QPushButton#btnCadastrar:hover {
            background-color: #E05412;
        }

        /* Botão Cancelar (Outline) */
        QPushButton#btnCancelar {
            background-color: transparent;
            color: #FFFFFF;
            border: 1px solid #64748B;
        }
        QPushButton#btnCancelar:hover {
            background-color: #1E293B;
            border: 1px solid #FFFFFF;
        }
        """
        self._card.setStyleSheet(self._card.styleSheet() + estilo)
#========================================================================================================================================
    # Exemplo de implementação do método salvar_cliente
#========================================================================================================================================
    def salvar_cliente(self):
        nome = self.edit_nome.text()
        telefone = self.edit_telefone.text()
        documento = self.edit_documento.text()
        endereco = self.edit_endereco.text()
        observacoes = self.edit_observacoes.toPlainText()
        # Aqui você pode chamar funções do módulo database para inserir no banco
        db.inserir_cliente(nome, telefone, documento, endereco, observacoes)
        self.close()

#========================================================================================================================================
# MAIN
#========================================================================================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = NovoClienteWindow()
    janela.show()
    sys.exit(app.exec())
