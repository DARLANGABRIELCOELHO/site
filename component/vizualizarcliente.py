# vizualizarcliente.py — Dialog de edição de Cliente
import sys
import os

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QFrame,
    QSpacerItem, QSizePolicy, QMessageBox, QButtonGroup
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db
from component.base_dialog import ModernDialog

try:
    from component.svg_utils import svg_para_pixmap
    _SVG_OK = True
except Exception:
    _SVG_OK = False


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
        lbl_icone = QLabel()
        lbl_icone.setObjectName("info_icone")
        # icone pode ser uma chave de SVG (str sem emoji) ou emoji fallback
        _SVG_MAP = {
            "phone":   "fi-sr-phone-call.svg",
            "email":   "fi-sr-envelope.svg",
            "doc":     "fi-sr-document.svg",
            "tag":     "fi-sr-tag.svg",
        }
        svg_file = _SVG_MAP.get(icone, "")
        if _SVG_OK and svg_file:
            lbl_icone.setPixmap(svg_para_pixmap(svg_file, "#64748B", 14, 14))
        else:
            lbl_icone.setText(icone)
        
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

class HistoricoItem(QFrame):
    """Componente para cada item da lista de histórico (OS ou Venda)"""
    def __init__(self, icone, titulo, data, status, preco, cor_status="#EAB308", bg_status="rgba(234, 179, 8, 0.1)"):
        super().__init__()
        self.setObjectName("item_historico")
        self.setMinimumHeight(80)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)

        # --- Ícone da Esquerda ---
        lbl_icone = QLabel()
        lbl_icone.setObjectName("icone_servico")
        lbl_icone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # icone é um arquivo SVG (ex: "fi-sr-tools.svg") ou emoji
        if _SVG_OK and icone.endswith(".svg"):
            lbl_icone.setPixmap(svg_para_pixmap(icone, "#F26522", 20, 20))
        else:
            lbl_icone.setText(icone)
        layout.addWidget(lbl_icone)

        # --- Informações Centrais (Título e Data) ---
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("historico_titulo")
        
        lbl_data = QLabel(data)
        lbl_data.setObjectName("historico_data")
        
        info_layout.addWidget(lbl_titulo)
        info_layout.addWidget(lbl_data)
        layout.addLayout(info_layout)

        layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        # --- Valores e Status da Direita ---
        right_layout = QVBoxLayout()
        right_layout.setSpacing(4)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        lbl_status = QLabel(status)
        lbl_status.setObjectName("badge_status")
        lbl_status.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_status.setStyleSheet(f"color: {cor_status}; background-color: {bg_status}; border: 1px solid {cor_status};")
        
        lbl_preco = QLabel(preco)
        lbl_preco.setObjectName("historico_preco")
        lbl_preco.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        
        right_layout.addWidget(lbl_status)
        right_layout.addWidget(lbl_preco)
        
        layout.addLayout(right_layout)

class ClienteDadosDialog(ModernDialog):
    def __init__(self, cliente: dict):
        super().__init__(f"Perfil — {cliente.get('nome', '')}", 630, 520)
        self._cliente = cliente
        self.initUI()

    def initUI(self):
        main_layout = self.content_layout
        main_layout.setSpacing(16)

        # --- Cabeçalho (Avatar + Nome) ---
        header_layout = QHBoxLayout()
        
        lbl_avatar = QLabel()
        lbl_avatar.setObjectName("avatar_icon")
        lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if _SVG_OK:
            lbl_avatar.setPixmap(svg_para_pixmap("fi-sr-user.svg", "#F26522", 24, 24))
        else:
            lbl_avatar.setText("👤")
        
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
        
        btn_dados = QPushButton("  Dados")
        if _SVG_OK:
            btn_dados.setIcon(QIcon(svg_para_pixmap("fi-sr-document.svg", "#64748B", 14, 14)))
            btn_dados.setIconSize(QSize(14, 14))
        btn_dados.setCheckable(True)
        btn_dados.setChecked(True)
        btn_dados.setObjectName("btn_toggle")
        btn_dados.setCursor(Qt.CursorShape.PointingHandCursor)
        
        btn_historico = QPushButton("  Histórico")
        if _SVG_OK:
            btn_historico.setIcon(QIcon(svg_para_pixmap("fi-sr-clock.svg", "#64748B", 14, 14)))
            btn_historico.setIconSize(QSize(14, 14))
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
        # Remove old grid info initialization to use inside a QStackedWidget
        
        # --- Páginas (Stacked Widget) ---
        from PyQt6.QtWidgets import QWidget, QStackedWidget, QTableWidget, QTableWidgetItem, QHeaderView, QScrollArea
        self.stacked_widget = QStackedWidget()
        main_layout.addWidget(self.stacked_widget)
        
        # Página 1: DADOS
        page_dados = QWidget()
        layout_dados = QVBoxLayout(page_dados)
        layout_dados.setContentsMargins(0, 0, 0, 0)
        
        grid_info = QGridLayout()
        grid_info.setSpacing(15)
        
        telefone = self._cliente.get("telefone", "—")
        documento = self._cliente.get("documento", "—")
        email = "—" # placeholder
        
        # Busca o histórico real do cliente
        self.historico = db.obter_historico_cliente(self._cliente["id"])
        
        # Definição de badge VIP (LTV > 500 por exemplo)
        is_vip = self.historico["ltv"] > 500
        tag = "VIP" if is_vip else "REGULAR"
        
        box_telefone = InfoBox("phone", "Telefone", telefone)
        box_email    = InfoBox("email", "E-mail",   email)
        box_doc      = InfoBox("doc",   "CPF/CNPJ", documento)
        box_tags     = InfoBox("tag",   "Tags",     tag, is_tag=True)
        
        grid_info.addWidget(box_telefone, 0, 0)
        grid_info.addWidget(box_email, 0, 1)
        grid_info.addWidget(box_doc, 1, 0)
        grid_info.addWidget(box_tags, 1, 1)
        layout_dados.addLayout(grid_info)
        
        stats_layout = QHBoxLayout()
        stats_layout.setSpacing(15)
        
        box_ltv = StatBox("LTV Total", f"R$ {self.historico['ltv']:.2f}", destaque=True)
        box_os = StatBox("Total de OS", str(self.historico["total_os"]))
        box_vendas = StatBox("Total de Vendas", str(self.historico["total_vendas"]))
        
        stats_layout.addWidget(box_ltv)
        stats_layout.addWidget(box_os)
        stats_layout.addWidget(box_vendas)
        layout_dados.addLayout(stats_layout)
        layout_dados.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        
        self.stacked_widget.addWidget(page_dados)
        
        # Página 2: HISTÓRICO
        page_historico = QWidget()
        layout_hist = QVBoxLayout(page_historico)
        layout_hist.setContentsMargins(0, 0, 0, 0)
        
        # Área de Scroll para a Lista de Histórico
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("scroll_area")
        
        scroll_content = QWidget()
        scroll_content.setObjectName("scroll_content")
        
        self.lista_layout = QVBoxLayout(scroll_content)
        self.lista_layout.setSpacing(10)
        self.lista_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.lista_layout.setContentsMargins(0, 0, 10, 0)

        self._preencher_lista_historico()
        
        scroll_area.setWidget(scroll_content)
        layout_hist.addWidget(scroll_area)
        self.stacked_widget.addWidget(page_historico)
        
        # Conexões do Toggle
        self.grupo_toggle.buttonClicked.connect(self._mudar_aba)

        self.aplicar_estilos()

    def _mudar_aba(self, btn):
        index = self.grupo_toggle.id(btn)
        self.stacked_widget.setCurrentIndex(index)

    def _preencher_lista_historico(self):
        # Une OS e Vendas em uma única lista para exibir ordenado por data
        itens = []
        for os_data in self.historico["ordens"]:
            data_str = os_data.get("data_cadastro", "")
            data_formatada = data_str[:16].replace("T", " ") if "T" in data_str else data_str[:16]
            if "-" in data_formatada:
                partes = data_formatada.split(" ")[0].split("-")
                hora = data_formatada.split(" ")[1] if " " in data_formatada else ""
                if len(partes) == 3:
                    data_formatada = f"{partes[2]}/{partes[1]}/{partes[0]} {hora}"
                    
            status_os = os_data.get('status', 'Pendente')
            
            # Definir cores por status (pode ajustar conforme a necessidade)
            cor_status = "#EAB308" # Amarelo (Pendente, etc)
            bg_status = "rgba(234, 179, 8, 0.1)"
            icone = "fi-sr-tools.svg"
            
            if status_os.lower() in ["entregue", "concluído", "pronto"]:
                cor_status = "#4ADE80"
                bg_status = "rgba(74, 222, 128, 0.1)"
            elif status_os.lower() in ["cancelado", "cancelada"]:
                cor_status = "#EF4444"
                bg_status = "rgba(239, 68, 68, 0.1)"
                icone = "fi-sr-ban.svg"
                
            itens.append({
                "data_raw": data_str,
                "data_formatada": data_formatada,
                "icone": icone,
                "titulo": os_data.get("modelo", f"OS #{os_data['id']}"),
                "status": status_os,
                "preco": f"R$ {float(os_data.get('total_servicos', 0)):.2f}",
                "cor_status": cor_status,
                "bg_status": bg_status
            })
            
        for venda in self.historico["vendas"]:
            data_str = venda.get("data_venda", "")
            data_formatada = data_str[:16].replace("T", " ") if "T" in data_str else data_str[:16]
            if "-" in data_formatada:
                partes = data_formatada.split(" ")[0].split("-")
                hora = data_formatada.split(" ")[1] if " " in data_formatada else ""
                if len(partes) == 3:
                    data_formatada = f"{partes[2]}/{partes[1]}/{partes[0]} {hora}"
                    
            itens.append({
                "data_raw": data_str,
                "data_formatada": data_formatada,
                "icone": "fi-sr-box.svg",
                "titulo": f"Venda Balcão #{venda['id']}",
                "status": "Concluído",
                "preco": f"R$ {float(venda.get('valor_total', 0) or 0):.2f}",
                "cor_status": "#4ADE80",
                "bg_status": "rgba(74, 222, 128, 0.1)"
            })
            
        # Ordena do mais recente para o mais antigo
        itens.sort(key=lambda x: x["data_raw"], reverse=True)
        
        for item in itens:
            widget_item = HistoricoItem(
                icone=item["icone"], 
                titulo=item["titulo"], 
                data=item["data_formatada"], 
                status=item["status"], 
                preco=item["preco"],
                cor_status=item["cor_status"],
                bg_status=item["bg_status"]
            )
            self.lista_layout.addWidget(widget_item)

    def aplicar_estilos(self):
        estilo = """
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
        
        /* Scroll Area */
        QScrollArea#scroll_area { border: none; background-color: transparent; }
        QWidget#scroll_content { background-color: transparent; }
        QScrollBar:vertical { border: none; background-color: #0B1120; width: 6px; border-radius: 3px; }
        QScrollBar::handle:vertical { background-color: #1E293B; min-height: 20px; border-radius: 3px; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }

        /* Item da Lista de Histórico */
        QFrame#item_historico {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 12px;
        }
        
        /* Ícone de Serviço (ex: 🔧) */
        QLabel#icone_servico {
            background-color: #1E293B;
            border-radius: 8px;
            min-width: 40px;
            max-width: 40px;
            min-height: 40px;
            max-height: 40px;
            font-size: 20px;
        }

        /* Textos do Item */
        QLabel#historico_titulo { color: #FFFFFF; font-size: 15px; font-weight: 700; }
        QLabel#historico_data { color: #64748B; font-size: 12px; }
        
        QLabel#historico_preco {
            color: #F26522; /* Preço Laranja substituindo o verde original */
            font-size: 16px;
            font-weight: 700;
        }
        
        /* Status Badge (Pendente, Concluído, etc) */
        QLabel#badge_status {
            font-size: 11px;
            font-weight: 700;
            padding: 2px 8px;
            border-radius: 6px;
        }
        """
        self.setStyleSheet(self.styleSheet() + estilo)


class EditarClienteDialog(ModernDialog):
    """Dialog para editar as informações de um Cliente."""

    def __init__(self, cliente: dict):
        super().__init__(f"Editar Cliente — {cliente.get('nome', '')}", 560, 500)
        self._cliente = cliente
        self._initUI()

    # ──────────────────────────────────────────────
    # UI
    # ──────────────────────────────────────────────

    def _initUI(self):
        layout = self.content_layout

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

        self.btn_salvar = QPushButton("Salvar Alterações")
        if _SVG_OK:
            self.btn_salvar.setIcon(QIcon(svg_para_pixmap("fi-sr-check.svg", "#FFFFFF", 16, 16)))
            self.btn_salvar.setIconSize(QSize(16, 16))
        else:
            self.btn_salvar.setText("✓ Salvar Alterações")
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
        self.setStyleSheet(self.styleSheet() + """
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
