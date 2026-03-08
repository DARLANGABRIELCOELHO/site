import sys
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFrame,
    QSpacerItem, QSizePolicy, QScrollArea, QMessageBox, QMenu
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QAction

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db
from component.novocliente import NovoClienteWindow


class ClienteCRMCard(QFrame):
    """Card individual de um cliente."""
    def __init__(self, cliente: dict, on_vizualizar, on_editar, on_excluir):
        super().__init__()
        self.cliente = cliente
        self.setObjectName("card_cliente")
        self.setFixedSize(320, 180)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)

        # --- Linha 1: Avatar, Info e Ações ---
        top_layout = QHBoxLayout()

        lbl_avatar = QLabel("👤")
        lbl_avatar.setObjectName("avatar_icon")
        lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        top_layout.addWidget(lbl_avatar)

        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        lbl_nome = QLabel(cliente.get("nome", ""))
        lbl_nome.setObjectName("cliente_nome")
        lbl_tel = QLabel(cliente.get("telefone", "") or "—")
        lbl_tel.setObjectName("cliente_tel")
        info_layout.addWidget(lbl_nome)
        info_layout.addWidget(lbl_tel)
        top_layout.addLayout(info_layout)

        top_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        btn_menu = QPushButton("⋮")
        btn_menu.setObjectName("btn_acao_pequeno")
        btn_menu.setCursor(Qt.CursorShape.PointingHandCursor)

        def _abrir_menu():
            menu = QMenu(btn_menu)
            menu.setStyleSheet("""
                QMenu { background-color: #1E293B; border: 1px solid #334155; border-radius: 6px; padding: 4px; }
                QMenu::item { color: #FFFFFF; padding: 8px 20px; font-size: 13px; }
                QMenu::item:selected { background-color: #334155; border-radius: 4px; }
                QMenu::separator { height: 1px; background: #334155; margin: 4px 8px; }
            """)
            acao_visualizar = QAction("👁  Visualizar dados", menu)
            acao_visualizar.triggered.connect(lambda: on_vizualizar(cliente))
            menu.addAction(acao_visualizar)
            menu.addSeparator()
            acao_editar = QAction("✏  Editar cliente", menu)
            acao_editar.triggered.connect(lambda: on_editar(cliente))
            menu.addAction(acao_editar)
            menu.addSeparator()
            acao_excluir = QAction("🗑  Excluir", menu)
            acao_excluir.triggered.connect(lambda: on_excluir(cliente["id"]))
            menu.addAction(acao_excluir)
            menu.exec(btn_menu.mapToGlobal(btn_menu.rect().bottomLeft()))

        btn_menu.clicked.connect(_abrir_menu)
        top_layout.addWidget(btn_menu)

        layout.addLayout(top_layout)

        # --- Linha 2: Documento (como "tag") ---
        doc = cliente.get("documento", "")
        if doc:
            tag_layout = QHBoxLayout()
            lbl_doc = QLabel(doc)
            lbl_doc.setObjectName("cliente_tag")
            tag_layout.addWidget(lbl_doc)
            tag_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
            layout.addLayout(tag_layout)

        layout.addItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # --- Linha 3: Data de cadastro ---
        rodape_layout = QHBoxLayout()
        lbl_data_label = QLabel("Cadastro:")
        lbl_data_label.setObjectName("stat_label")
        lbl_data_val = QLabel(cliente.get("data_cadastro", "") or "—")
        lbl_data_val.setObjectName("stat_valor")
        rodape_layout.addWidget(lbl_data_label)
        rodape_layout.addWidget(lbl_data_val)
        rodape_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addLayout(rodape_layout)


class ClientesScreen(QWidget):
    def __init__(self):
        super().__init__()
        db.inicializar_estado()
        self._janela_novo_cliente = None
        self.initUI()

    def initUI(self):
        self.setMinimumSize(1000, 700)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(20)

        # --- Cabeçalho ---
        header_layout = QHBoxLayout()

        titulos_layout = QVBoxLayout()
        titulos_layout.setSpacing(0)
        lbl_titulo = QLabel("Clientes")
        lbl_titulo.setObjectName("title_main")
        lbl_sub = QLabel("Cadastro e CRM")
        lbl_sub.setObjectName("subtitle")
        titulos_layout.addWidget(lbl_titulo)
        titulos_layout.addWidget(lbl_sub)

        btn_novo = QPushButton("+ Novo Cliente")
        btn_novo.setObjectName("btn_primario")
        btn_novo.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_novo.clicked.connect(self._abrir_novo_cliente)

        header_layout.addLayout(titulos_layout)
        header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        header_layout.addWidget(btn_novo)
        self.main_layout.addLayout(header_layout)

        # --- Barra de Busca ---
        self.edit_busca = QLineEdit()
        self.edit_busca.setPlaceholderText("🔍 Buscar por nome, telefone ou documento...")
        self.edit_busca.textChanged.connect(self._filtrar)
        self.main_layout.addWidget(self.edit_busca)

        # --- Scroll Area ---
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_area")

        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scroll_content")

        self.grid_cards = QGridLayout(self.scroll_content)
        self.grid_cards.setSpacing(20)
        self.grid_cards.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.scroll_area.setWidget(self.scroll_content)
        self.main_layout.addWidget(self.scroll_area)

        self.aplicar_estilos()
        self._carregar_clientes()

    def _carregar_clientes(self, filtro: str = ""):
        # Limpa o grid
        for i in reversed(range(self.grid_cards.count())):
            widget = self.grid_cards.itemAt(i).widget()
            if widget:
                widget.deleteLater()

        clientes = db.listar_clientes()

        if filtro:
            f = filtro.lower()
            clientes = [
                c for c in clientes
                if f in (c.get("nome") or "").lower()
                or f in (c.get("telefone") or "").lower()
                or f in (c.get("documento") or "").lower()
            ]

        if not clientes:
            lbl = QLabel("Nenhum cliente encontrado.")
            lbl.setObjectName("subtitle")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_cards.addWidget(lbl, 0, 0)
            return

        row, col = 0, 0
        for cliente in clientes:
            card = ClienteCRMCard(cliente, self._vizualizar_cliente, self._editar_cliente, self._excluir_cliente)
            self.grid_cards.addWidget(card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

    def _filtrar(self, texto: str):
        self._carregar_clientes(filtro=texto)

    def _abrir_novo_cliente(self):
        self._janela_novo_cliente = NovoClienteWindow()
        # Sobrescreve o salvar para atualizar a lista após cadastro
        original_salvar = self._janela_novo_cliente.salvar_cliente
        def salvar_e_atualizar():
            original_salvar()
            self._carregar_clientes(filtro=self.edit_busca.text())
        self._janela_novo_cliente.btn_cadastrar.clicked.disconnect()
        self._janela_novo_cliente.btn_cadastrar.clicked.connect(salvar_e_atualizar)
        self._janela_novo_cliente.show()

    def _vizualizar_cliente(self, cliente: dict):
        from component.vizualizarcliente import ClienteDadosDialog
        dlg = ClienteDadosDialog(cliente)
        dlg.exec()

    def _editar_cliente(self, cliente: dict):
        from component.vizualizarcliente import EditarClienteDialog
        dlg = EditarClienteDialog(cliente)
        if dlg.exec() == EditarClienteDialog.DialogCode.Accepted:
            self._carregar_clientes(filtro=self.edit_busca.text())

    def _excluir_cliente(self, cliente_id: int):
        resposta = QMessageBox.question(
            self,
            "Confirmar exclusão",
            "Deseja excluir este cliente?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resposta == QMessageBox.StandardButton.Yes:
            sucesso = db.excluir_cliente(cliente_id)
            if not sucesso:
                QMessageBox.warning(
                    self,
                    "Atenção",
                    "Não é possível excluir este cliente pois ele possui Ordens de Serviço vinculadas."
                )
            self._carregar_clientes(filtro=self.edit_busca.text())

    def aplicar_estilos(self):
        self.setStyleSheet("""
        QWidget {
            background-color: #0F172A;
            font-family: 'Poppins', 'Montserrat', sans-serif;
        }

        QLabel#title_main { color: #FFFFFF; font-size: 24px; font-weight: 700; }
        QLabel#subtitle   { color: #64748B; font-size: 12px; font-weight: 600; }

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

        QLineEdit {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 8px;
            padding: 12px;
            color: #FFFFFF;
            font-size: 13px;
        }
        QLineEdit:focus { border: 1px solid #F26522; }

        QScrollArea#scroll_area { border: none; background-color: transparent; }
        QWidget#scroll_content  { background-color: transparent; }
        QScrollBar:vertical { border: none; background-color: #0B1120; width: 8px; border-radius: 4px; }
        QScrollBar::handle:vertical { background-color: #1E293B; min-height: 20px; border-radius: 4px; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }

        QFrame#card_cliente {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 12px;
        }
        QFrame#card_cliente:hover { border: 1px solid #64748B; }

        QLabel#avatar_icon {
            background-color: rgba(242, 101, 34, 0.1);
            color: #F26522;
            border-radius: 20px;
            min-width: 40px; min-height: 40px;
            max-width: 40px; max-height: 40px;
            font-size: 20px;
        }

        QLabel#cliente_nome { color: #FFFFFF; font-size: 14px; font-weight: 700; }
        QLabel#cliente_tel  { color: #64748B; font-size: 12px; }

        QLabel#cliente_tag {
            background-color: #1E293B;
            color: #64748B;
            font-size: 10px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 10px;
        }

        QPushButton#btn_acao_pequeno {
            background-color: transparent;
            color: #64748B;
            border: none;
            font-size: 14px;
        }
        QPushButton#btn_acao_pequeno:hover { color: #EF4444; }

        QLabel#stat_label { color: #64748B; font-size: 10px; font-weight: 600; }
        QLabel#stat_valor { color: #FFFFFF; font-size: 12px; font-weight: 600; }
        """)
