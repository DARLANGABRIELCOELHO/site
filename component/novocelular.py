# novo celular 
#modulo para cadastrar um novo celular
import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QFrame,
    QSpacerItem, QSizePolicy, QMessageBox, QFileDialog
)

# Adiciona o diretório pai ao sys.path para encontrar o pacote 'data'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db
from component.base_dialog import ModernWindow

#========================================================================================================================================
# JANELA DE CADASTRO DE NOVO CELULAR
#========================================================================================================================================
class NovoCelularWindow(ModernWindow):
    def __init__(self):
        super().__init__("Novo Celular", 760, 640)
        db.inicializar_estado()
        self.fotos_selecionadas = []
        self.initUI()

    def initUI(self):
        main_layout = self.content_layout

        grid = QGridLayout()
        grid.setSpacing(15)

        # Linha 1: modelo e marca
        grid.addWidget(QLabel("Modelo *"), 0, 0)
        self.edit_modelo = QLineEdit()
        grid.addWidget(self.edit_modelo, 1, 0)

        grid.addWidget(QLabel("Marca *"), 0, 1)
        self.edit_marca = QLineEdit()
        grid.addWidget(self.edit_marca, 1, 1)

        # Linha 2: cor e imei
        grid.addWidget(QLabel("Cor"), 2, 0)
        self.edit_cor = QLineEdit()
        grid.addWidget(self.edit_cor, 3, 0)

        grid.addWidget(QLabel("IMEI"), 2, 1)
        self.edit_imei = QLineEdit()
        grid.addWidget(self.edit_imei, 3, 1)

        # Linha 3: Data de Cadastro
        self.edit_data_cadastro = QLineEdit(datetime.now().strftime("%Y-%m-%d"))
        self.edit_data_cadastro.setReadOnly(True)

        # Linha 4: custos de aquisição e reparo
        grid.addWidget(QLabel("Custos de Aquisição"), 4, 0) 
        self.edit_custos_aquisicao = QLineEdit()
        grid.addWidget(self.edit_custos_aquisicao, 5, 0)

        grid.addWidget(QLabel("Custos de Reparo"), 4, 1)
        self.edit_custos_reparo = QLineEdit()
        grid.addWidget(self.edit_custos_reparo, 5, 1)

        # Linha 5: preço e condição
        grid.addWidget(QLabel("Preço"), 6, 0)
        self.edit_preco = QLineEdit()
        grid.addWidget(self.edit_preco, 7, 0)

        grid.addWidget(QLabel("Condição"), 6, 1)
        self.edit_condicao = QLineEdit()
        grid.addWidget(self.edit_condicao, 7, 1)

        # Linha 6: fotos
        grid.addWidget(QLabel("Fotos"), 8, 0, 1, 2)

        self.edit_fotos = QLineEdit()
        self.edit_fotos.setReadOnly(True)
        grid.addWidget(self.edit_fotos, 9, 0)

        self.btn_fotos = QPushButton("Selecionar Fotos")
        self.btn_fotos.setObjectName("btnFotos")
        grid.addWidget(self.btn_fotos, 9, 1)
        # Linha 7: observação
        grid.addWidget(QLabel("Observação"), 10, 0, 1, 2)
        self.edit_observacao = QTextEdit()
        grid.addWidget(self.edit_observacao, 11, 0, 1, 2)

        main_layout.addLayout(grid)

        linha = QFrame()
        linha.setFrameShape(QFrame.Shape.HLine)
        linha.setObjectName("linha_laranja")
        main_layout.addWidget(linha)
        main_layout.addSpacing(15)

        botoes_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        botoes_layout.addItem(spacer)

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("btnCancelar")

        self.btn_cadastrar = QPushButton("Cadastrar")
        self.btn_cadastrar.setObjectName("btnCadastrar")

        botoes_layout.addWidget(self.btn_cancelar)
        botoes_layout.addWidget(self.btn_cadastrar)

        self.btn_cadastrar.clicked.connect(self.salvar_celular)
        self.btn_cancelar.clicked.connect(self.close)
        self.btn_fotos.clicked.connect(self.selecionar_fotos)

        main_layout.addLayout(botoes_layout)
        self.aplicar_estilos()

    def aplicar_estilos(self):
        estilo = """
        QLabel#title {
            font-size: 20px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }

        QLabel {
            font-size: 12px;
            font-weight: 600;
            color: #64748B;
            letter-spacing: 0.5px;
        }

        QLineEdit, QTextEdit {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 6px;
            padding: 10px;
            color: #FFFFFF;
            font-size: 14px;
            selection-background-color: #F26522;
        }

        QLineEdit:focus, QTextEdit:focus {
            border: 1px solid #F26522;
        }

        QFrame#linha_laranja {
            background-color: #F26522;
            max-height: 1px;
            border: none;
        }

        QPushButton {
            font-size: 14px;
            font-weight: 600;
            border-radius: 6px;
            padding: 10px 24px;
        }

        QPushButton#btnCadastrar {
            background-color: #F26522;
            color: #FFFFFF;
            border: none;
        }

        QPushButton#btnCadastrar:hover {
            background-color: #E05412;
        }

        QPushButton#btnCancelar {
            background-color: transparent;
            color: #FFFFFF;
            border: 1px solid #64748B;
        }

        QPushButton#btnCancelar:hover {
            background-color: #1E293B;
            border: 1px solid #FFFFFF;
        }

        QPushButton#btnFotos {
            background-color: #1E293B;
            color: #FFFFFF;
            border: 1px solid #64748B;
        }

        QPushButton#btnFotos:hover {
            border: 1px solid #F26522;
        }
        """
        self._card.setStyleSheet(self._card.styleSheet() + estilo)

    def selecionar_fotos(self):
        arquivos, _ = QFileDialog.getOpenFileNames(
            self,
            "Selecionar Fotos",
            "",
            "Imagens (*.png *.jpg *.jpeg *.bmp *.webp)"
        )

        if arquivos:
            self.fotos_selecionadas = arquivos
            self.edit_fotos.setText(" | ".join(arquivos))

    def salvar_celular(self):
        modelo = self.edit_modelo.text().strip()
        marca = self.edit_marca.text().strip()
        cor = self.edit_cor.text().strip()
        imei = self.edit_imei.text().strip()
        data_cadastro = self.edit_data_cadastro.text().strip()
        condicao = self.edit_condicao.text().strip()
        observacao = self.edit_observacao.toPlainText().strip()

        if not modelo or not marca:
            QMessageBox.warning(self, "Erro", "Modelo e Marca são campos obrigatórios.")
            return

        try:
            custos_aquisicao = float(self.edit_custos_aquisicao.text().strip() or 0)
            custos_reparo = float(self.edit_custos_reparo.text().strip() or 0)
            preco = float(self.edit_preco.text().strip() or 0)

            fotos = self.fotos_selecionadas

            db.inserir_celular(
                modelo,
                marca,
                cor,
                imei,
                data_cadastro,
                custos_aquisicao,
                custos_reparo,
                preco,
                condicao,
                fotos,
                observacao
            )

            QMessageBox.information(self, "Sucesso", "Celular cadastrado com sucesso!")
            self.close()

        except ValueError:
            QMessageBox.warning(
                self,
                "Erro de preenchimento",
                "Custos e preço devem ser números válidos."
            )
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao salvar celular:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = NovoCelularWindow()
    window.show()
    sys.exit(app.exec())
