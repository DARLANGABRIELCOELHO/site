import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFrame,
    QSpacerItem, QSizePolicy, QMessageBox
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db


class NovoTecnicoWindow(QWidget):
    def __init__(self):
        super().__init__()
        db.inicializar_estado()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Novo Técnico")
        self.setFixedSize(500, 500)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15)

        lbl_titulo = QLabel("👤 NOVO TÉCNICO")
        lbl_titulo.setObjectName("title")
        main_layout.addWidget(lbl_titulo)
        main_layout.addSpacing(10)

        grid = QGridLayout()
        grid.setSpacing(15)

        grid.addWidget(QLabel("Nome *"), 0, 0)
        self.edit_nome = QLineEdit()
        grid.addWidget(self.edit_nome, 1, 0)

        grid.addWidget(QLabel("Telefone *"), 0, 1)
        self.edit_telefone = QLineEdit()
        grid.addWidget(self.edit_telefone, 1, 1)

        grid.addWidget(QLabel("Especialidade *"), 2, 0, 1, 2)
        self.edit_especialidade = QLineEdit()
        grid.addWidget(self.edit_especialidade, 3, 0, 1, 2)

        main_layout.addLayout(grid)
        main_layout.addSpacing(15)

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

        self.btn_cadastrar.clicked.connect(self.salvar_tecnico)
        self.btn_cancelar.clicked.connect(self.close)

        main_layout.addLayout(botoes_layout)
        self.setLayout(main_layout)

        self.aplicar_estilos()

    def aplicar_estilos(self):
        estilo = """
        QWidget {
            background-color: #0F172A;
            font-family: 'Poppins', 'Montserrat', sans-serif;
            color: #FFFFFF;
        }

        QLabel#title {
            font-size: 20px;
            font-weight: 700;
        }

        QLabel {
            font-size: 12px;
            font-weight: 600;
            color: #64748B;
        }

        QLineEdit {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 6px;
            padding: 10px;
            color: #FFFFFF;
            font-size: 14px;
            selection-background-color: #F26522;
        }

        QLineEdit:focus {
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
        }
        """
        self.setStyleSheet(estilo)
#========================================================================================================================================
    # Exemplo de implementação do método salvar_tecnico
#========================================================================================================================================

    def salvar_tecnico(self):
        nome = self.edit_nome.text().strip()
        telefone = self.edit_telefone.text().strip()
        especialidade = self.edit_especialidade.text().strip()

        if not nome or not telefone or not especialidade:
            QMessageBox.warning(
                self,
                "Atenção",
                "Nome, Telefone e Especialidade são obrigatórios."
            )
            return

        try:
            tecnico = db.inserir_tecnico(nome, telefone, especialidade)
            QMessageBox.information(
                self,
                "Sucesso",
                f"Técnico cadastrado com sucesso!\nID: {tecnico['id']}"
            )
            self.close()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Erro ao salvar",
                f"Não foi possível salvar o técnico.\n\n{str(e)}"
            )
#========================================================================================================================================
# MAIN
#========================================================================================================================================
if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = NovoTecnicoWindow()
    janela.show()
    sys.exit(app.exec())