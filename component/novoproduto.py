# Novo Produto
# interface para cadastro de novos produtos (PyQt6)
import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QFrame,
    QSpacerItem, QSizePolicy, QMessageBox
)
# Adiciona o diretório pai ao sys.path para encontrar o pacote 'data'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db
from component.base_dialog import ModernWindow
#========================================================================================================================================
# JANELA DE CADASTRO DE NOVO PRODUTO
#========================================================================================================================================
class NovoProdutoWindow(ModernWindow):
    def __init__(self):
        super().__init__("Novo Produto", 580, 460)
        db.inicializar_estado()
        self.initUI()

    def initUI(self):
        main_layout = self.content_layout

        # Grid Layout
        grid = QGridLayout()
        grid.setSpacing(15)

        # Linha 1: nome e categoria
        grid.addWidget(QLabel("nome *"), 0, 0)
        self.edit_nome = QLineEdit()
        grid.addWidget(self.edit_nome, 1, 0)

        grid.addWidget(QLabel("categoria *"), 0, 1)
        self.edit_categoria = QLineEdit()
        grid.addWidget(self.edit_categoria, 1, 1)

        # Linha 2: custo e preço
        grid.addWidget(QLabel("Custo"), 2, 0)
        self.edit_custo = QLineEdit()
        grid.addWidget(self.edit_custo, 3, 0)

        grid.addWidget(QLabel("Preço"), 2, 1)
        self.edit_preco = QLineEdit()
        grid.addWidget(self.edit_preco, 3, 1)

        # Linha 3: Data de Cadastro (autopreenchida)
        self.edit_data_cadastro = QLineEdit(datetime.now().strftime("%Y-%m-%d"))

        # Linha 4: estoque e estoque mínimo
        grid.addWidget(QLabel("estoque"), 6, 0)
        self.edit_estoque = QLineEdit()
        grid.addWidget(self.edit_estoque, 7, 0)
        grid.addWidget(QLabel("estoque mínimo"), 6, 1)
        self.edit_estoque_minimo = QLineEdit()   
        grid.addWidget(self.edit_estoque_minimo, 7, 1)
        main_layout.addLayout(grid)
        main_layout.addSpacing(20)  
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
        botoes_layout.addWidget(self.btn_cancelar)
        botoes_layout.addWidget(self.btn_cadastrar)
        main_layout.addLayout(botoes_layout)
        self.btn_cadastrar.clicked.connect(self.salvar_produto)
        self.btn_cancelar.clicked.connect(self.close)
        self.aplicar_estilos()

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
    # Exemplo de implementação do método salvar_produto 
#========================================================================================================================================
    def salvar_produto(self):
        nome = self.edit_nome.text().strip()
        categoria = self.edit_categoria.text().strip()
        data_cadastro = self.edit_data_cadastro.text().strip()

        if not nome or not categoria:
            QMessageBox.warning(self, "Erro", "Por favor, preencha os campos obrigatórios.")
            return

        try:
            custo = float(self.edit_custo.text().strip() or 0)
            preco = float(self.edit_preco.text().strip() or 0)
            estoque = int(self.edit_estoque.text().strip() or 0)
            estoque_minimo = int(self.edit_estoque_minimo.text().strip() or 0)

            db.inserir_produto(
                nome,
                categoria,
                custo,
                preco,
                data_cadastro,
                estoque,
                estoque_minimo
            )

            QMessageBox.information(self, "Sucesso", "Produto cadastrado com sucesso!")
            self.close()

        except ValueError:
            QMessageBox.warning(
                self,
                "Erro de preenchimento",
                "Custo e preço devem ser números.\nEstoque e estoque mínimo devem ser inteiros."
            )
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar produto:\n{e}")
#========================================================================================================================================
# main
#========================================================================================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = NovoProdutoWindow()
    janela.show()
    sys.exit(app.exec())
