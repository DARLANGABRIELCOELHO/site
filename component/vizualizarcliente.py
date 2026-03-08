# vizualizarcliente.py — Dialog de edição de Cliente
import sys
import os

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QFrame,
    QSpacerItem, QSizePolicy, QMessageBox, QButtonGroup
)
from PyQt6.QtCore import Qt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db


class InfoBox(QFrame):
    """Componente para as caixas de informação (Telefone, E-mail, etc)"""
    def __init__(self, icone, titulo, valor_texto=None, is_tag=False):
        super().__init__()
        self.setObjectName("info_box")
        self.setMinimumHeight(80)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        
        # --- Linha Superior (Ícone + Rótulo) ---
        top_layout = QHBoxLayout()
        lbl_icone = QLabel(icone)
        lbl_icone.setObjectName("info_icone")
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("info_label")
        
        top_layout.addWidget(lbl_icone)
        top_layout.addWidget(lbl_titulo)
        top_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addLayout(top_layout)
        
        # --- Linha Inferior (Valor ou Tag) ---
        if is_tag and valor_texto:
            lbl_tag = QLabel(valor_texto)
            lbl_tag.setObjectName("badge_tag")
            layout.addWidget(lbl_tag, alignment=Qt.AlignmentFlag.AlignLeft)
        elif valor_texto:
            lbl_valor = QLabel(valor_texto)
            lbl_valor.setObjectName("info_valor")
            layout.addWidget(lbl_valor)
        else:
            layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

class StatBox(QFrame):
    """Componente para as estatísticas inferiores (LTV, OS, Vendas)"""
    def __init__(self, titulo, valor, destaque=False):
        super().__init__()
        self.setObjectName("stat_box_destaque" if destaque else "stat_box")
        self.setMinimumHeight(100)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 20, 15, 20)
        layout.setSpacing(8)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("stat_label")
        
        lbl_valor = QLabel(str(valor))
        lbl_valor.setObjectName("stat_valor_destaque" if destaque else "stat_valor")
        
        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_valor)

class ClienteDadosDialog(QDialog):
    def __init__(self, cliente: dict):
        super().__init__()
        self._cliente = cliente
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Perfil do Cliente - Dados")
        self.setFixedSize(650, 500)
        self.setModal(True)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # --- Cabeçalho (Avatar + Nome) ---
        header_layout = QHBoxLayout()
        
        lbl_avatar = QLabel("👤")
        lbl_avatar.setObjectName("avatar_icon")
        lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        lbl_nome = QLabel(self._cliente.get("nome", ""))
        lbl_nome.setObjectName("title_main")
        
        header_layout.addWidget(lbl_avatar)
        header_layout.addWidget(lbl_nome)
        header_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        main_layout.addLayout(header_layout)

        # --- Toggle Abas (Dados / CRM Histórico) ---
        toggle_frame = QFrame()
        toggle_frame.setObjectName("toggle_bg")
        toggle_layout = QHBoxLayout(toggle_frame)
        toggle_layout.setContentsMargins(4, 4, 4, 4)
        toggle_layout.setSpacing(0)
        
        self.grupo_toggle = QButtonGroup(self)
        
        btn_dados = QPushButton("📄 Dados")
        btn_dados.setCheckable(True)
        btn_dados.setChecked(True) # Aba DADOS ativa
        btn_dados.setObjectName("btn_toggle")
        btn_dados.setCursor(Qt.CursorShape.PointingHandCursor)
        
        btn_historico = QPushButton("🕒 Histórico")
        btn_historico.setCheckable(True)
        btn_historico.setObjectName("btn_toggle")
        btn_historico.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.grupo_toggle.addButton(btn_dados, 0)
        self.grupo_toggle.addButton(btn_historico, 1)
        
        toggle_layout.addWidget(btn_dados)
        toggle_layout.addWidget(btn_historico)
        
        # Alinha os botões à esquerda
        toggle_container = QHBoxLayout()
        toggle_container.addWidget(toggle_frame)
        toggle_container.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        main_layout.addLayout(toggle_container)

        # --- Grid de Informações de Contato ---
        grid_info = QGridLayout()
        grid_info.setSpacing(15)
        
        telefone = self._cliente.get("telefone", "—")
        documento = self._cliente.get("documento", "—")
        # Assume email is not part of the current schema, put placeholder or empty for now
        email = "—"
        
        box_telefone = InfoBox("📞", "Telefone", telefone)
        box_email = InfoBox("✉️", "E-mail", email)
        box_doc = InfoBox("📄", "CPF/CNPJ", documento)
        
        # Check for tags/VIP status based on business logic, here placeholder
        tag = ""
        box_tags = InfoBox("🏷️", "Tags", tag, is_tag=True)
        
        grid_info.addWidget(box_telefone, 0, 0)
        grid_info.addWidget(box_email, 0, 1)
        grid_info.addWidget(box_doc, 1, 0)
        grid_info.addWidget(box_tags, 1, 1)
        
        main_layout.addLayout(grid_info)

        # --- Linha de Estatísticas Resumidas ---
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        # Fetch actual statistics if possible, otherwise placeholder 0
        ltv = self._cliente.get("LTV", 0.0) # Placeholder key
        total_os = 0 # Placeholder key
        total_vendas = 0 # Placeholder key
        
        # Attempt to get real values: We can get OS count from the client dict if it was fetched with ordens_servico count
        total_os = self._cliente.get("ordens_servico", 0)
        
        box_ltv = StatBox("LTV Total", f"R$ {ltv:.2f}", destaque=True)
        box_os = StatBox("Total de OS", str(total_os))
        box_vendas = StatBox("Total de Vendas", str(total_vendas))
        
        stats_layout.addWidget(box_ltv)
        stats_layout.addWidget(box_os)
        stats_layout.addWidget(box_vendas)
        
        main_layout.addLayout(stats_layout)
        
        # Empurra tudo para cima
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        self.aplicar_estilos()

    def aplicar_estilos(self):
        estilo = """
        /* Fundo e Tipografia Global */
        QDialog {
            background-color: #0F172A;
            font-family: 'Poppins', 'Montserrat', sans-serif;
        }

        /* Avatar Laranja */
        QLabel#avatar_icon {
            background-color: rgba(242, 101, 34, 0.1); 
            color: #F26522; 
            border-radius: 12px;
            min-width: 48px;
            max-width: 48px;
            min-height: 48px;
            max-height: 48px;
            font-size: 24px;
        }

        /* Títulos */
        QLabel#title_main {
            color: #FFFFFF;
            font-size: 22px;
            font-weight: 700;
            margin-left: 10px;
        }

        /* Toggle Button (Dados / Histórico) */
        QFrame#toggle_bg {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 8px;
        }
        QPushButton#btn_toggle {
            background-color: transparent;
            color: #64748B;
            font-size: 13px;
            font-weight: 600;
            padding: 8px 20px;
            border-radius: 6px;
            border: none;
        }
        QPushButton#btn_toggle:checked {
            background-color: #1E293B;
            color: #FFFFFF;
            border: 1px solid #1E293B;
        }

        /* Caixas de Informação (InfoBox) */
        QFrame#info_box {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 10px;
        }
        QLabel#info_icone { color: #64748B; font-size: 14px; }
        QLabel#info_label { color: #64748B; font-size: 13px; font-weight: 600; }
        QLabel#info_valor { color: #FFFFFF; font-size: 16px; font-weight: 700; }
        
        /* Estilo da Tag/Badge (Ex: VIP) */
        QLabel#badge_tag {
            background-color: #1E293B;
            color: #64748B;
            font-size: 11px;
            font-weight: 700;
            padding: 4px 12px;
            border-radius: 10px;
            text-transform: uppercase;
        }

        /* Caixas de Estatísticas (StatBox) */
        QFrame#stat_box, QFrame#stat_box_destaque {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 10px;
        }
        QFrame#stat_box_destaque {
            border: 1px solid #F26522;
            background-color: rgba(242, 101, 34, 0.03);
        }
        QLabel#stat_label { color: #64748B; font-size: 12px; font-weight: 600; }
        QLabel#stat_valor { color: #FFFFFF; font-size: 22px; font-weight: 700; }
        QLabel#stat_valor_destaque { color: #F26522; font-size: 22px; font-weight: 700; }
        """
        self.setStyleSheet(estilo)


class EditarClienteDialog(QDialog):
    """Dialog para editar as informações de um Cliente."""

    def __init__(self, cliente: dict):
        super().__init__()
        self._cliente = cliente
        self.setWindowTitle(f"Editar Cliente — {cliente.get('nome', '')}")
        self.setFixedSize(580, 560)
        self.setModal(True)
        self._initUI()

    # ──────────────────────────────────────────────
    # UI
    # ──────────────────────────────────────────────

    def _initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        # ─ Título ─
        lbl_titulo = QLabel(f"👤 EDITAR CLIENTE #{self._cliente['id']}")
        lbl_titulo.setObjectName("title")
        layout.addWidget(lbl_titulo)
        layout.addSpacing(5)

        # ─ Grid de campos ─
        grid = QGridLayout()
        grid.setSpacing(12)

        # Nome
        grid.addWidget(self._lbl("Nome *"), 0, 0)
        self.edit_nome = QLineEdit(self._cliente.get("nome", ""))
        grid.addWidget(self.edit_nome, 1, 0)

        # Telefone
        grid.addWidget(self._lbl("Telefone"), 0, 1)
        self.edit_telefone = QLineEdit(self._cliente.get("telefone", "") or "")
        grid.addWidget(self.edit_telefone, 1, 1)

        # Documento
        grid.addWidget(self._lbl("CPF/CNPJ"), 2, 0, 1, 2)
        self.edit_documento = QLineEdit(self._cliente.get("documento", "") or "")
        grid.addWidget(self.edit_documento, 3, 0, 1, 2)

        # Endereço
        grid.addWidget(self._lbl("Endereço"), 4, 0, 1, 2)
        self.edit_endereco = QLineEdit(self._cliente.get("endereco", "") or "")
        grid.addWidget(self.edit_endereco, 5, 0, 1, 2)

        # Observações
        grid.addWidget(self._lbl("Observações"), 6, 0, 1, 2)
        self.edit_observacoes = QTextEdit()
        self.edit_observacoes.setMaximumHeight(100)
        self.edit_observacoes.setPlainText(self._cliente.get("observacoes", "") or "")
        grid.addWidget(self.edit_observacoes, 7, 0, 1, 2)

        layout.addLayout(grid)
        layout.addItem(QSpacerItem(20, 10, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # ─ Linha separadora ─
        linha = QFrame()
        linha.setFrameShape(QFrame.Shape.HLine)
        linha.setObjectName("linha_laranja")
        layout.addWidget(linha)

        # ─ Botões ─
        btns = QHBoxLayout()
        btns.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("btnCancelar")
        self.btn_cancelar.clicked.connect(self.reject)

        self.btn_salvar = QPushButton("✓ Salvar Alterações")
        self.btn_salvar.setObjectName("btnSalvar")
        self.btn_salvar.clicked.connect(self._salvar)

        btns.addWidget(self.btn_cancelar)
        btns.addWidget(self.btn_salvar)
        layout.addLayout(btns)

        self._aplicar_estilos()

    def _lbl(self, texto: str) -> QLabel:
        lbl = QLabel(texto)
        lbl.setObjectName("lbl_campo")
        return lbl

    # ──────────────────────────────────────────────
    # Lógica
    # ──────────────────────────────────────────────

    def _salvar(self):
        nome = self.edit_nome.text().strip()
        if not nome:
            QMessageBox.warning(self, "Campo obrigatório", "O campo Nome é obrigatório.")
            return

        telefone = self.edit_telefone.text().strip()
        documento = self.edit_documento.text().strip()
        endereco = self.edit_endereco.text().strip()
        observacoes = self.edit_observacoes.toPlainText().strip()

        try:
            db.atualizar_cliente(
                self._cliente["id"],
                nome,
                telefone or None,
                documento or None,
                endereco or None,
                observacoes or None,
            )
            QMessageBox.information(self, "Salvo", "Cliente atualizado com sucesso.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar cliente:\n{e}")

    # ──────────────────────────────────────────────
    # Estilos
    # ──────────────────────────────────────────────

    def _aplicar_estilos(self):
        self.setStyleSheet("""
            QDialog {
                background-color: #0F172A;
                font-family: 'Poppins', 'Montserrat', sans-serif;
            }

            QLabel#title {
                color: #FFFFFF;
                font-size: 18px;
                font-weight: 700;
            }

            QLabel#lbl_campo {
                color: #64748B;
                font-size: 12px;
                font-weight: 600;
            }

            QLineEdit, QTextEdit {
                background-color: #0B1120;
                border: 1px solid #1E293B;
                border-radius: 6px;
                padding: 10px;
                color: #FFFFFF;
                font-size: 13px;
            }
            QLineEdit:focus, QTextEdit:focus { border: 1px solid #F26522; }

            QFrame#linha_laranja {
                background-color: #F26522;
                max-height: 1px;
                border: none;
            }

            QPushButton#btnSalvar {
                background-color: #F26522;
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 600;
                border-radius: 6px;
                padding: 10px 20px;
                border: none;
            }
            QPushButton#btnSalvar:hover { background-color: #E05412; }

            QPushButton#btnCancelar {
                background-color: transparent;
                color: #FFFFFF;
                border: 1px solid #64748B;
                font-size: 13px;
                font-weight: 600;
                border-radius: 6px;
                padding: 10px 20px;
            }
            QPushButton#btnCancelar:hover { background-color: #1E293B; }
        """)
