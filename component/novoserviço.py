# novoserviço.py
# Interface gráfica para cadastro de novo serviço (PyQt6)
import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton,
    QMessageBox, QListWidget
)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db
from component.base_dialog import ModernWindow
#========================================================================================================================================
# JANELA DE CADASTRO DE NOVO SERVIÇO
#========================================================================================================================================

class NovoServicoWindow(ModernWindow):
    def __init__(self):
        super().__init__("Novo Serviço", 660, 680)
        db.inicializar_estado()
        self.campo_ativo = None
        self.initUI()

    def initUI(self):
        main_layout = self.content_layout

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
        btn_salvar.clicked.connect(self.salvar_servico)
        main_layout.addWidget(btn_salvar)

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
        texto = item.text()
        if self.campo_ativo == 'modelo' and texto.startswith("📱"):
            modelo = texto[2:].strip()
            self.edit_modelo_celular.setText(modelo)
        elif self.campo_ativo == 'categoria' and texto.startswith("📂"):
            categoria = texto[2:].strip()
            self.edit_categoria.setText(categoria)
        self.gerar_nome_automatico()

# Atualiza a lista de resultados com base nos filtros de modelo e categoria
    def atualizar_sugestoes(self):
        if self.campo_ativo == 'modelo':
            termo = self.edit_modelo_celular.text().strip()
            sugestoes = db.obter_modelos_distintos(termo)
            self.lista_resultados.clear()
            if not sugestoes:
                self.lista_resultados.addItem("Nenhum modelo encontrado.")
                return
            for modelo in sugestoes:
                self.lista_resultados.addItem(f"📱 {modelo}")
        elif self.campo_ativo == 'categoria':
            termo = self.edit_categoria.text().strip()
            sugestoes = db.obter_categorias_distintas(termo)
            self.lista_resultados.clear()
            if not sugestoes:
                self.lista_resultados.addItem("Nenhuma categoria encontrada.")
                return
            for categoria in sugestoes:
                self.lista_resultados.addItem(f"📂 {categoria}")
        else:
            # Comportamento original
            modelo = self.edit_modelo_celular.text().strip()
            categoria = self.edit_categoria.text().strip()
            resultados = db.pesquisar_servicos(modelo, categoria)
            self.lista_resultados.clear()
            if not resultados:
                self.lista_resultados.addItem("Nenhum serviço encontrado.")
                return
            for servico in resultados:
                texto = f"ID: {servico['id']} | {servico['nome']} | {servico['modelo_celular']} | {servico['categoria']} | R$ {servico['preco']}"
                self.lista_resultados.addItem(texto)
# Aplica estilos 
    def apply_styles(self):
        estilo = """
        QLabel {
            font-size: 12px;
            font-weight: 600;
            color: #64748B;
        }

        QLineEdit, QTextEdit {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 6px;
            padding: 10px;
            color: #FFFFFF;
            font-size: 14px;
        }

        QLineEdit:focus, QTextEdit:focus {
            border: 1px solid #F26522;
        }

        QListWidget {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 6px;
            color: #FFFFFF;
            font-size: 13px;
        }

        QListWidget::item:selected {
            background-color: #F26522;
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
        """
        self.setStyleSheet(self.styleSheet() + estilo)
# Exemplo de implementação do método salvar_servico
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

# MAIN
if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = NovoServicoWindow()
    janela.show()
    sys.exit(app.exec())