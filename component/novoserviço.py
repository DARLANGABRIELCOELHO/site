# novoserviço.py
# Interface gráfica para cadastro de novo serviço (PyQt6)

import sys
import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout, QHBoxLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton,
    QMessageBox, QListWidget, QListWidgetItem, QFrame
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QIcon

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db

try:
    from component.svg_utils import svg_para_pixmap
    _SVG_OK = True
except Exception:
    _SVG_OK = False


# ========================================================================================================================================
# JANELA DE CADASTRO DE NOVO SERVIÇO
# ========================================================================================================================================

class NovoServicoWindow(QWidget):
    def __init__(self):
        super().__init__()
        db.inicializar_estado()
        self.campo_ativo = None
        self.drag_pos = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Novo Serviço")
        self.setFixedSize(700, 750)

        # Remove a title bar nativa
        self.setWindowFlags(Qt.WindowType.Window | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, False)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Cabeçalho customizado
        header = QFrame()
        header.setObjectName("header")
        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(0, 0, 0, 0)

        self.lbl_titulo = QLabel(" NOVO SERVIÇO")
        self.lbl_titulo.setObjectName("title")

        btn_fechar = QPushButton("✕")
        btn_fechar.setObjectName("btnFechar")
        btn_fechar.setFixedSize(36, 36)
        btn_fechar.clicked.connect(self.close)

        header_layout.addWidget(self.lbl_titulo)
        header_layout.addStretch()
        header_layout.addWidget(btn_fechar)

        main_layout.addWidget(header)

        grid = QGridLayout()
        grid.setSpacing(15)

        # Linha 1: nome do serviço
        grid.addWidget(QLabel("Nome do Serviço *"), 0, 0, 1, 2)
        self.edit_nome_servico = QLineEdit()
        grid.addWidget(self.edit_nome_servico, 1, 0, 1, 2)

        # Linha 2: modelo e categoria
        grid.addWidget(QLabel("Modelo do Celular"), 2, 0)
        self.edit_modelo_celular = QLineEdit()
        grid.addWidget(self.edit_modelo_celular, 3, 0)

        grid.addWidget(QLabel("Categoria do Serviço"), 2, 1)
        self.edit_categoria = QLineEdit()
        grid.addWidget(self.edit_categoria, 3, 1)

        # Linha 3: lista de resultados da busca
        self.lista_resultados = QListWidget()
        main_layout.addLayout(grid)
        main_layout.addWidget(self.lista_resultados)

        # Definir campo ativo ao focar
        self.original_focus_modelo = self.edit_modelo_celular.focusInEvent
        self.original_focus_categoria = self.edit_categoria.focusInEvent
        self.edit_modelo_celular.focusInEvent = lambda e: self.definir_campo_ativo('modelo', e, self.original_focus_modelo)
        self.edit_categoria.focusInEvent = lambda e: self.definir_campo_ativo('categoria', e, self.original_focus_categoria)

        # Atualiza sugestões e gera nome automático ao digitar
        self.edit_modelo_celular.textChanged.connect(self.atualizar_sugestoes)
        self.edit_categoria.textChanged.connect(self.atualizar_sugestoes)
        self.edit_modelo_celular.textChanged.connect(self.gerar_nome_automatico)
        self.edit_categoria.textChanged.connect(self.gerar_nome_automatico)

        # Conecta clique na lista de sugestões
        self.lista_resultados.itemClicked.connect(self.aplicar_sugestao)

        # Linha 4: custo e preço
        grid.addWidget(QLabel("Custo *"), 4, 0)
        self.edit_custo = QLineEdit()
        grid.addWidget(self.edit_custo, 5, 0)

        grid.addWidget(QLabel("Preço *"), 4, 1)
        self.edit_preco = QLineEdit()
        grid.addWidget(self.edit_preco, 5, 1)

        # Linha 5: tempo estimado
        grid.addWidget(QLabel("Tempo Estimado"), 6, 0, 1, 2)
        self.edit_tempo_estimado = QLineEdit()
        grid.addWidget(self.edit_tempo_estimado, 7, 0, 1, 2)

        # Linha 6: observação
        grid.addWidget(QLabel("Observação"), 8, 0, 1, 2)
        self.edit_observacao = QTextEdit()
        grid.addWidget(self.edit_observacao, 9, 0, 1, 2)

        # Botão salvar
        btn_salvar = QPushButton("Salvar")
        btn_salvar.setObjectName("btnSalvar")
        btn_salvar.clicked.connect(self.salvar_servico)
        main_layout.addWidget(btn_salvar)

        self.setLayout(main_layout)
        self.apply_styles()
        self.atualizar_sugestoes()

    def definir_campo_ativo(self, campo, event, original_focus):
        self.campo_ativo = campo
        original_focus(event)
        self.atualizar_sugestoes()

    def gerar_nome_automatico(self):
        modelo = self.edit_modelo_celular.text().strip()
        categoria = self.edit_categoria.text().strip()
        if modelo and categoria:
            nome_sugerido = f"{modelo} {categoria}"
            self.edit_nome_servico.setText(nome_sugerido)

    def aplicar_sugestao(self, item):
        # Texto limpo guardado em UserRole (sem emoji nem prefixo)
        texto = item.data(Qt.ItemDataRole.UserRole) or item.text()
        if self.campo_ativo == 'modelo':
            self.edit_modelo_celular.setText(texto)
        elif self.campo_ativo == 'categoria':
            self.edit_categoria.setText(texto)
        self.gerar_nome_automatico()

    def atualizar_sugestoes(self):
        # Ícones SVG
        _ico_modelo    = QIcon(svg_para_pixmap("fi-sr-smartphone.svg",  "#F26522", 16, 16)) if _SVG_OK else None
        _ico_categoria = QIcon(svg_para_pixmap("fi-sr-folder.svg",      "#64748B", 16, 16)) if _SVG_OK else None
        _ico_servico   = QIcon(svg_para_pixmap("fi-sr-tools.svg",       "#64748B", 16, 16)) if _SVG_OK else None

        def _item(texto, icone=None):
            it = QListWidgetItem(texto)
            it.setData(Qt.ItemDataRole.UserRole, texto)  # guarda texto limpo
            if icone:
                it.setIcon(icone)
            return it

        if self.campo_ativo == 'modelo':
            termo = self.edit_modelo_celular.text().strip()
            sugestoes = db.obter_modelos_distintos(termo)
            self.lista_resultados.clear()
            if not sugestoes:
                self.lista_resultados.addItem("Nenhum modelo encontrado.")
                return
            for modelo in sugestoes:
                self.lista_resultados.addItem(_item(modelo, _ico_modelo))

        elif self.campo_ativo == 'categoria':
            termo = self.edit_categoria.text().strip()
            sugestoes = db.obter_categorias_distintas(termo)
            self.lista_resultados.clear()
            if not sugestoes:
                self.lista_resultados.addItem("Nenhuma categoria encontrada.")
                return
            for categoria in sugestoes:
                self.lista_resultados.addItem(_item(categoria, _ico_categoria))

        else:
            modelo = self.edit_modelo_celular.text().strip()
            categoria = self.edit_categoria.text().strip()
            resultados = db.pesquisar_servicos(modelo, categoria)
            self.lista_resultados.clear()
            if not resultados:
                self.lista_resultados.addItem("Nenhum serviço encontrado.")
                return
            for servico in resultados:
                texto = f"{servico['nome']}  |  {servico['modelo_celular']}  |  {servico['categoria']}  |  R$ {servico['preco']}"
                self.lista_resultados.addItem(_item(texto, _ico_servico))

    def apply_styles(self):
        estilo = """
        NovoServicoWindow {
            background-color: #0F172A;
            font-family: 'Poppins', 'Montserrat', sans-serif;
        }
        NovoServicoWindow * {
            font-family: 'Poppins', 'Montserrat', sans-serif;
            color: #FFFFFF;
        }

        QFrame#header {
            background-color: transparent;
        }

        QLabel#title {
            font-size: 20px;
            font-weight: 700;
            color: #FFFFFF;
        }

        QLabel {
            font-size: 12px;
            font-weight: 600;
            color: #64748B;
        }

        QLineEdit, QTextEdit, QListWidget {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 6px;
            padding: 10px;
            color: #FFFFFF;
            font-size: 14px;
        }

        QLineEdit:focus, QTextEdit:focus, QListWidget:focus {
            border: 1px solid #F26522;
        }

        QPushButton {
            font-size: 14px;
            font-weight: 600;
            border-radius: 6px;
            padding: 10px 24px;
            background-color: #F26522;
            color: #FFFFFF;
            border: none;
        }

        QPushButton:hover {
            background-color: #E05412;
        }

        QPushButton#btnFechar {
            background-color: transparent;
            border: 1px solid #334155;
            color: #FFFFFF;
            padding: 0;
            font-size: 16px;
            font-weight: 700;
            border-radius: 8px;
        }

        QPushButton#btnFechar:hover {
            background-color: #7F1D1D;
            border: 1px solid #EF4444;
        }

        QPushButton#btnSalvar {
            margin-top: 10px;
        }
        """
        self.setStyleSheet(estilo)

    def salvar_servico(self):
        nome = self.edit_nome_servico.text().strip()
        modelo_celular = self.edit_modelo_celular.text().strip()
        categoria = self.edit_categoria.text().strip()
        custo = self.edit_custo.text().strip()
        preco = self.edit_preco.text().strip()
        tempo_estimado = self.edit_tempo_estimado.text().strip()
        observacao = self.edit_observacao.toPlainText().strip()
        data_cadastro = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        if not nome or not custo or not preco:
            QMessageBox.warning(
                self,
                "Campos Obrigatórios",
                "Preencha: Nome do Serviço, Custo e Preço."
            )
            return

        try:
            custo_valor = float(custo)
            preco_valor = float(preco)
        except ValueError:
            QMessageBox.warning(
                self,
                "Valor Inválido",
                "Custo e Preço devem ser numéricos."
            )
            return

        db.inserir_servico(
            nome,
            modelo_celular,
            categoria,
            custo_valor,
            preco_valor,
            tempo_estimado,
            observacao,
            data_cadastro
        )

        QMessageBox.information(self, "Sucesso", "Serviço cadastrado com sucesso!")
        self.close()

    # Arrastar a janela sem title bar
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.drag_pos = event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            event.accept()

    def mouseMoveEvent(self, event):
        if self.drag_pos is not None and event.buttons() & Qt.MouseButton.LeftButton:
            self.move(event.globalPosition().toPoint() - self.drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self.drag_pos = None
        event.accept()


# MAIN
if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = NovoServicoWindow()
    janela.show()
    sys.exit(app.exec())