# ordemdeserviço.py
# cria uma ordem de serviço para o cliente de serviço
import os
from datetime import datetime
# 4 ABAS 
# 1 - entrada: dados do cliente
# 2 - APARELHO: dados do aparelho
# 3 - CHECKLIST: checklist de entrada
# 4 - SERVIÇO: dados do serviço
import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QDialog, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QFrame, QCheckBox,
    QSpacerItem, QSizePolicy, QMessageBox, QFileDialog, QScrollArea,
    QButtonGroup, QComboBox, QTabWidget, QCompleter
)
from PyQt6.QtCore import Qt

# Adiciona o diretório pai ao sys.path para encontrar o pacote 'data'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db

# ============================================================================
# COMPONENTES REUTILIZÁVEIS
# ============================================================================

class ClienteCard(QPushButton):
    """Widget customizado para simular o card de cliente selecionável"""
    def __init__(self, cliente_id, nome, telefone, tag=None):
        super().__init__()
        self.cliente_id = cliente_id
        self.setCheckable(True)
        self.setObjectName("card_cliente")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(70)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)

        # Info do Cliente
        info_layout = QVBoxLayout()
        lbl_nome = QLabel(nome)
        lbl_nome.setObjectName("cliente_nome")
        lbl_tel = QLabel(telefone)
        lbl_tel.setObjectName("cliente_tel")
        
        info_layout.addWidget(lbl_nome)
        info_layout.addWidget(lbl_tel)
        layout.addLayout(info_layout)

        # Tag (VIP, Atacado, etc.)
        if tag:
            spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
            layout.addItem(spacer)
            
            lbl_tag = QLabel(tag)
            lbl_tag.setObjectName("cliente_tag")
            lbl_tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(lbl_tag)


class ToggleBox(QFrame):
    """Componente customizado para as Condições de Entrada (Caixa + Label + Switch)"""
    def __init__(self, texto):
        super().__init__()
        self.setObjectName("toggle_box")
        self.setFixedHeight(50)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 0, 15, 0)
        
        self.lbl_texto = QLabel(texto)
        self.lbl_texto.setObjectName("toggle_label")
        
        self.chk_switch = QCheckBox()
        self.chk_switch.setCursor(Qt.CursorShape.PointingHandCursor)
        
        layout.addWidget(self.lbl_texto)
        layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addWidget(self.chk_switch)


class ChecklistItem(QFrame):
    """Componente customizado para cada item do checklist (Card com 3 opções)"""
    def __init__(self, chave, titulo):
        super().__init__()
        self.chave = chave
        self.setObjectName("checklist_box")
        self.setFixedHeight(80)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        layout.setSpacing(8)
        
        # Título do Item (Ex: Wi-Fi, Bluetooth)
        self.lbl_titulo = QLabel(titulo)
        self.lbl_titulo.setObjectName("item_titulo")
        layout.addWidget(self.lbl_titulo)
        
        # Layout e Botões (OK, NOK, NA)
        layout_botoes = QHBoxLayout()
        layout_botoes.setSpacing(5)
        
        self.grupo_botoes = QButtonGroup(self)
        self.grupo_botoes.setExclusive(True)
        
        self.mapa_estado = {}
        
        opcoes = ["OK", "NOK", "NA"]
        for i, texto in enumerate(opcoes):
            btn = QPushButton(texto)
            btn.setObjectName("btn_estado")
            btn.setCheckable(True)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            
            self.grupo_botoes.addButton(btn, i)
            self.mapa_estado[i] = texto
            layout_botoes.addWidget(btn)
            
            if texto == "NA":
                btn.setChecked(True)
                
        layout.addLayout(layout_botoes)

    def obter_estado(self):
        btn = self.grupo_botoes.checkedButton()
        if not btn:
            return "NA"
        return btn.text()


class ServicoCard(QPushButton):
    """Componente customizado para os cards de Serviço (Selecionáveis)"""
    def __init__(self, servico_id, titulo, preco):
        super().__init__()
        self.servico_id = servico_id
        self.setCheckable(True)
        self.setObjectName("card_servico")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedHeight(80)

        # Layout interno do botão
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)

        # Título do Serviço
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("servico_titulo")
        # Ignora o clique na label para que o botão pai receba a ação
        lbl_titulo.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        # Preço do Serviço (em Laranja)
        lbl_preco = QLabel(preco)
        lbl_preco.setObjectName("servico_preco")
        lbl_preco.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        layout.addWidget(lbl_titulo)
        layout.addWidget(lbl_preco)


# ============================================================================
# ABAS (Cada uma é um QWidget)
# ============================================================================

class AbaCliente(QWidget):
    def __init__(self):
        super().__init__()
        self.cards_clientes = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        layout_balcao = QHBoxLayout()
        lbl_balcao = QLabel("Modo Balcão Rápido")
        lbl_balcao.setObjectName("lbl_destaque")
        self.chk_balcao = QCheckBox()
        self.chk_balcao.setCursor(Qt.CursorShape.PointingHandCursor)
        layout_balcao.addWidget(lbl_balcao)
        layout_balcao.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout_balcao.addWidget(self.chk_balcao)
        layout.addLayout(layout_balcao)

        self.edit_busca = QLineEdit()
        self.edit_busca.setPlaceholderText("🔍 Buscar por nome ou telefone...")
        layout.addWidget(self.edit_busca)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("scroll_area")

        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scroll_content")
        self.layout_clientes = QVBoxLayout(self.scroll_content)
        self.layout_clientes.setSpacing(10)
        self.layout_clientes.setContentsMargins(0, 0, 10, 0)

        self.grupo_clientes = QButtonGroup(self)
        self.grupo_clientes.setExclusive(True)

        scroll_area.setWidget(self.scroll_content)
        layout.addWidget(scroll_area)

        self.edit_busca.textChanged.connect(self.filtrar_clientes)

        self.carregar_clientes()

    def carregar_clientes(self):
        while self.layout_clientes.count():
            item = self.layout_clientes.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.cards_clientes.clear()

        try:
            with db.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome, telefone FROM clientes ORDER BY nome")
                for i, row in enumerate(cursor.fetchall()):
                    card = ClienteCard(
                        row["id"],
                        row["nome"],
                        row["telefone"] or "",
                        None
                    )
                    self.grupo_clientes.addButton(card, i)
                    self.layout_clientes.addWidget(card)
                    self.cards_clientes.append(card)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar clientes:\n{e}")

        self.layout_clientes.addItem(
            QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

    def filtrar_clientes(self):
        texto = self.edit_busca.text().strip().lower()
        for card in self.cards_clientes:
            nome = card.findChild(QLabel, "cliente_nome").text().lower()
            tel = card.findChild(QLabel, "cliente_tel").text().lower()
            mostrar = texto in nome or texto in tel
            card.setVisible(mostrar)


class AbaAparelho(QWidget):
    """Aba Aparelho (antiga AbaAparelhoDialog)"""
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        # --- Formulário: Aparelho e Identificação ---
        grid = QGridLayout()
        grid.setSpacing(15)

        grid.addWidget(QLabel("Modelo do Aparelho *"), 0, 0)
        self.edit_modelo = QComboBox()
        self.edit_modelo.setEditable(True)
        self.edit_modelo.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.edit_modelo.lineEdit().setPlaceholderText("Ex: iPhone 13 Pro Max")
        self._carregar_modelos()
        grid.addWidget(self.edit_modelo, 1, 0)

        grid.addWidget(QLabel("Cor"), 0, 1)
        self.edit_cor = QLineEdit()
        self.edit_cor.setPlaceholderText("Ex: Preto")
        grid.addWidget(self.edit_cor, 1, 1)

        grid.addWidget(QLabel("Senha do Aparelho"), 2, 0)
        self.edit_senha = QLineEdit()
        self.edit_senha.setPlaceholderText("Senha para desbloqueio")
        grid.addWidget(self.edit_senha, 3, 0)

        grid.addWidget(QLabel("IMEI / Número de Série"), 2, 1)
        self.edit_imei = QLineEdit()
        self.edit_imei.setPlaceholderText("IMEI ou Serial")
        grid.addWidget(self.edit_imei, 3, 1)

        layout.addLayout(grid)

        # --- Condições de Entrada (Toggles) ---
        layout.addWidget(QLabel("Condições de Entrada"))
        layout_toggles = QHBoxLayout()
        layout_toggles.setSpacing(10)
        
        self.tgl_liga = ToggleBox("Liga?")
        self.tgl_acessorios = ToggleBox("Acessórios?")
        self.tgl_aberto = ToggleBox("Já aberto?")
        self.tgl_molhado = ToggleBox("Molhado?")
        
        # Simulando o botão "Liga?" ativado como na imagem
        self.tgl_liga.chk_switch.setChecked(True)

        layout_toggles.addWidget(self.tgl_liga)
        layout_toggles.addWidget(self.tgl_acessorios)
        layout_toggles.addWidget(self.tgl_aberto)
        layout_toggles.addWidget(self.tgl_molhado)
        layout.addLayout(layout_toggles)

        # --- Dropdowns (Técnico e Prioridade) ---
        grid_combos = QGridLayout()
        grid_combos.setSpacing(15)

        grid_combos.addWidget(QLabel("Técnico Responsável"), 0, 0)
        self.cmb_tecnico = QComboBox()
        self.cmb_tecnico.addItem("Selecione...", None)
        
        try:
            with db.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome FROM tecnicos ORDER BY nome")
                for row in cursor.fetchall():
                    self.cmb_tecnico.addItem(row["nome"], row["id"])
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar técnicos:\n{e}")
        grid_combos.addWidget(self.cmb_tecnico, 1, 0)

        grid_combos.addWidget(QLabel("Prioridade"), 0, 1)
        self.cmb_prioridade = QComboBox()
        self.cmb_prioridade.addItems(["Baixa", "Normal", "Alta", "Urgente"])
        self.cmb_prioridade.setCurrentText("Normal")
        grid_combos.addWidget(self.cmb_prioridade, 1, 1)

        layout.addLayout(grid_combos)

        # --- Relato do Cliente (Defeito) ---
        layout.addWidget(QLabel("Relato do Cliente (Defeito)"))
        self.txt_relato = QTextEdit()
        self.txt_relato.setPlaceholderText("Descreva o problema relatado pelo cliente...")
        layout.addWidget(self.txt_relato)

    def _carregar_modelos(self):
        modelos = []
        try:
            with db.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT DISTINCT modelo || ' (' || marca || ')' AS label, modelo "
                    "FROM celulares ORDER BY modelo"
                )
                for row in cursor.fetchall():
                    self.edit_modelo.addItem(row["label"], row["modelo"])
                    modelos.append(row["label"])
        except Exception:
            pass

        # Também inclui modelos já usados em ordens de serviço (histórico)
        try:
            with db.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT DISTINCT modelo FROM ordem_servico ORDER BY modelo"
                )
                for row in cursor.fetchall():
                    m = row["modelo"]
                    if m and m not in modelos:
                        self.edit_modelo.addItem(m)
                        modelos.append(m)
        except Exception:
            pass

        # Autocomplete
        completer = QCompleter(modelos, self.edit_modelo)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        self.edit_modelo.setCompleter(completer)

        # Começa vazio
        self.edit_modelo.setCurrentIndex(-1)
        self.edit_modelo.lineEdit().clear()


class AbaChecklist(QWidget):
    def __init__(self):
        super().__init__()
        self.itens_checklist = {}
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        lbl_instrucao = QLabel("Marque o estado de cada item: OK, NOK ou N/A")
        lbl_instrucao.setObjectName("lbl_instrucao")
        layout.addWidget(lbl_instrucao)

        grid_checklist = QGridLayout()
        grid_checklist.setSpacing(15)

        itens = [
            ("wifi", "Wi-Fi"),
            ("bluetooth", "Bluetooth"),
            ("sinal", "Sinal"),
            ("biometria", "Biometria"),
            ("chip_sim", "Chip SIM"),
            ("tela", "Tela"),
            ("touch", "Touch"),
            ("camera_frontal", "Câm. Frontal"),
            ("camera_traseira", "Câm. Traseira"),
            ("flash", "Flash"),
            ("sensor_prox", "Sensor Prox."),
            ("carregamento", "Carregamento"),
            ("microfone", "Microfone"),
            ("alto_falante", "Alto-falante"),
            ("auricular", "Auricular"),
            ("vibracao", "Vibração"),
            ("botoes", "Botões"),
        ]

        row, col = 0, 0
        for chave, titulo in itens:
            card = ChecklistItem(chave, titulo)
            self.itens_checklist[chave] = card
            grid_checklist.addWidget(card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

        layout.addLayout(grid_checklist)

    def obter_dados_checklist(self):
        return {
            chave: item.obter_estado()
            for chave, item in self.itens_checklist.items()
        }


class AbaServicos(QWidget):
    def __init__(self):
        super().__init__()
        self.cards_servicos = []
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(15)

        self.edit_busca = QLineEdit()
        self.edit_busca.setPlaceholderText("🔍 Buscar serviço...")
        layout.addWidget(self.edit_busca)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("scroll_area")

        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scroll_content")
        self.grid_servicos = QGridLayout(self.scroll_content)
        self.grid_servicos.setSpacing(15)
        self.grid_servicos.setContentsMargins(0, 0, 10, 0)

        scroll_area.setWidget(self.scroll_content)
        layout.addWidget(scroll_area)

        self.edit_busca.textChanged.connect(self.filtrar_servicos)

        self.carregar_servicos()

    def carregar_servicos(self, modelo=None):
        while self.grid_servicos.count():
            item = self.grid_servicos.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        self.cards_servicos.clear()

        try:
            if modelo:
                servicos = db.pesquisar_servicos_por_modelo(modelo)
            else:
                with db.get_db_connection() as conn:
                    cursor = conn.cursor()
                    cursor.execute("SELECT id, nome, preco FROM servicos ORDER BY nome")
                    servicos = [dict(row) for row in cursor.fetchall()]

            row, col = 0, 0
            for servico in servicos:
                card = ServicoCard(
                    servico["id"],
                    servico["nome"],
                    f"R$ {float(servico['preco'] or 0):.2f}"
                )
                self.grid_servicos.addWidget(card, row, col)
                self.cards_servicos.append(card)

                col += 1
                if col > 1:
                    col = 0
                    row += 1

            spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
            self.grid_servicos.addItem(spacer, row + 1, 0, 1, 2)

        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao carregar serviços:\n{e}")

    def filtrar_servicos(self):
        texto = self.edit_busca.text().strip().lower()
        for card in self.cards_servicos:
            titulo = card.findChild(QLabel, "servico_titulo").text().lower()
            card.setVisible(texto in titulo)

    def obter_servicos_selecionados(self):
        return [card.servico_id for card in self.cards_servicos if card.isChecked()]


# ============================================================================
# JANELA PRINCIPAL COM ABAS
# ============================================================================

class NovaOrdemServicoWindow(QDialog):
    def __init__(self):
        super().__init__()
        db.inicializar_estado()
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Nova Ordem de Serviço")
        self.setFixedSize(900, 800)  # Tamanho ajustado para acomodar todas as abas
        self.setModal(True)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(15)

        # --- Cabeçalho ---
        lbl_titulo = QLabel("+ NOVA ORDEM DE SERVIÇO")
        lbl_titulo.setObjectName("title")
        main_layout.addWidget(lbl_titulo)

        # --- Tab Widget ---
        self.tab_widget = QTabWidget()
        self.tab_widget.setObjectName("tab_widget")

        # Adiciona as abas
        self.aba_cliente = AbaCliente()
        self.aba_aparelho = AbaAparelho()
        self.aba_checklist = AbaChecklist()
        self.aba_servicos = AbaServicos()
        
        self.tab_widget.addTab(self.aba_cliente, "👤 Cliente")
        self.tab_widget.addTab(self.aba_aparelho, "📱 Aparelho")
        self.tab_widget.addTab(self.aba_checklist, "📋 Checklist")
        self.tab_widget.addTab(self.aba_servicos, "🔧 Serviços")

        self.aba_aparelho.edit_modelo.currentTextChanged.connect(self.atualizar_servicos_por_modelo)

        main_layout.addWidget(self.tab_widget)

        # --- Linha de Destaque Laranja ---
        linha = QFrame()
        linha.setFrameShape(QFrame.Shape.HLine)
        linha.setObjectName("linha_laranja")
        main_layout.addWidget(linha)

        # --- Botões de Ação ---
        botoes_layout = QHBoxLayout()
        botoes_layout.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("btnCancelar")
        
        self.btn_criar_os = QPushButton("+ Criar OS")
        self.btn_criar_os.setObjectName("btnConfirmar")
        
        botoes_layout.addWidget(self.btn_cancelar)
        botoes_layout.addWidget(self.btn_criar_os)
        
        self.btn_cancelar.clicked.connect(self.close)
        self.btn_criar_os.clicked.connect(self.criar_os)

        main_layout.addLayout(botoes_layout)

        self.apply_styles()

    def atualizar_servicos_por_modelo(self):
        modelo = self.aba_aparelho.edit_modelo.currentText().strip()
        self.aba_servicos.carregar_servicos(modelo if modelo else None)

    def criar_os(self):
        try:
            # -------------------------
            # CLIENTE
            # -------------------------
            cliente_card = self.aba_cliente.grupo_clientes.checkedButton()
            if not cliente_card and not self.aba_cliente.chk_balcao.isChecked():
                QMessageBox.warning(self, "Atenção", "Selecione um cliente ou ative Modo Balcão Rápido.")
                return
    
            cliente_id = cliente_card.cliente_id if cliente_card else None
    
            # -------------------------
            # APARELHO
            # -------------------------
            modelo = self.aba_aparelho.edit_modelo.currentText().strip()
            cor = self.aba_aparelho.edit_cor.text().strip()
            senha = self.aba_aparelho.edit_senha.text().strip()
            imei = self.aba_aparelho.edit_imei.text().strip()
            tecnico_id = self.aba_aparelho.cmb_tecnico.currentData()
            prioridade = self.aba_aparelho.cmb_prioridade.currentText().lower()
            relato = self.aba_aparelho.txt_relato.toPlainText().strip()
    
            if not modelo:
                QMessageBox.warning(self, "Atenção", "Informe o modelo do aparelho.")
                return
    
            # -------------------------
            # CONDIÇÕES DE ENTRADA
            # -------------------------
            condicao_id = db.inserir_condicoes_entrada(
                liga=self.aba_aparelho.tgl_liga.chk_switch.isChecked(),
                acessorios=self.aba_aparelho.tgl_acessorios.chk_switch.isChecked(),
                ja_aberto=self.aba_aparelho.tgl_aberto.chk_switch.isChecked(),
                molhado=self.aba_aparelho.tgl_molhado.chk_switch.isChecked()
            )
    
            # -------------------------
            # CHECKLIST
            # -------------------------
            checklist = self.aba_checklist.obter_dados_checklist()
    
            checklist_id = db.inserir_checklist_entrada(
                ordem_servico_id=None,  # atualiza depois
                wifi=checklist.get("wifi"),
                bluetooth=checklist.get("bluetooth"),
                sinal=checklist.get("sinal"),
                biometria=checklist.get("biometria"),
                chip_sim=checklist.get("chip_sim"),
                tela=checklist.get("tela"),
                touch=checklist.get("touch"),
                camera_frontal=checklist.get("camera_frontal"),
                camera_traseira=checklist.get("camera_traseira"),
                flash=checklist.get("flash"),
                sensor_prox=checklist.get("sensor_prox"),
                carregamento=checklist.get("carregamento"),
                microfone=checklist.get("microfone"),
                alto_falante=checklist.get("alto_falante"),
                auricular=checklist.get("auricular"),
                vibracao=checklist.get("vibracao"),
                botoes=checklist.get("botoes")
            )
    
            # -------------------------
            # SERVIÇOS
            # -------------------------
            servico_ids = self.aba_servicos.obter_servicos_selecionados()
            if not servico_ids:
                QMessageBox.warning(self, "Atenção", "Selecione pelo menos um serviço.")
                return
    
            # -------------------------
            # DADOS DA OS
            # -------------------------
            dados_os = {
                "cliente_id": cliente_id,
                "modelo": modelo,
                "tecnico_id": tecnico_id,
                "condicao_id": condicao_id,
                "checklist_id": checklist_id,
                "prioridade": prioridade,
                "relato": relato,
                "senha": senha,
                "cor": cor,
                "imei": imei,
                "status": "aberta",
                "data_cadastro": datetime.now().isoformat(),
                "observacoes": None,
                "laudo": None
            }
    
            ordem_id = db.registrar_ordem_servico(dados_os, servico_ids)
            db.vincular_checklist_na_ordem(checklist_id, ordem_id)
    
            QMessageBox.information(self, "Sucesso", f"Ordem de Serviço criada com sucesso!\nOS #{ordem_id}")
            self.accept()
    
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao criar OS:\n{e}")
    def apply_styles(self):
        estilo = """
            /* Fundo da Janela e Tipografia Global */
            QDialog, QTabWidget::pane {
                background-color: #0F172A;
                font-family: 'Poppins', 'Montserrat', sans-serif;
            }
            /* Títulos e Labels */
            QLabel {
                color: #64748B;
                font-size: 12px;
                font-weight: 600;
            }
            QLabel#title {
                color: #FFFFFF;
                font-size: 18px;
                font-weight: 700;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            QLabel#lbl_destaque {
                font-size: 12px;
                font-weight: 700;
                color: #FFFFFF;
            }
            QLabel#lbl_instrucao {
                color: #64748B;
                font-size: 12px;
                font-weight: 600;
            }
            /* Abas (QTabWidget) */
            QTabWidget::pane {
                border: 1px solid #1E293B;
                border-radius: 8px;
                background-color: #0F172A;
                padding: 15px;
            }
            QTabBar::tab {
                background-color: #0B1120;
                color: #64748B;
                border: 1px solid #1E293B;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 12px;
                font-weight: 600;
                margin-right: 5px;
            }
            QTabBar::tab:selected {
                background-color: rgba(242, 101, 34, 0.1);
                color: #F26522;
                border: 1px solid #F26522;
            }
            QTabBar::tab:hover {
                background-color: #1E293B;
            }
            /* Inputs de Texto e Dropdowns */
            QLineEdit, QTextEdit, QComboBox {
                background-color: #0B1120;
                border: 1px solid #1E293B;
                border-radius: 6px;
                padding: 10px;
                color: #FFFFFF;
                font-size: 13px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus {
                border: 1px solid #F26522;
            }
            QComboBox::drop-down { border: none; }
            /* Checkbox Modo Balcão (Estilo simplificado) */
            QCheckBox::indicator {
                width: 40px;
                height: 20px;
                border-radius: 10px;
                border: 1px solid #1E293B;
                background-color: #0B1120;
            }
            QCheckBox::indicator:checked {
                background-color: #F26522;
                border: 1px solid #F26522;
            }
            /* Scroll Area e Content (Removendo bordas nativas) */
            QScrollArea#scroll_area {
                border: none;
                background-color: transparent;
            }
            QWidget#scroll_content {
                background-color: transparent;
            }
            /* Estilização da Scrollbar */
            QScrollBar:vertical {
                border: none;
                background-color: #0B1120;
                width: 8px;
                border-radius: 4px;
            }
            QScrollBar::handle:vertical {
                background-color: #1E293B;
                min-height: 20px;
                border-radius: 4px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }
            /* Cards de Clientes */
            QPushButton#card_cliente {
                background-color: #0B1120;
                border: 1px solid #1E293B;
                border-radius: 8px;
                text-align: left;
            }
            QPushButton#card_cliente:hover {
                background-color: #1E293B;
            }
            QPushButton#card_cliente:checked {
                border: 1px solid #F26522;
                background-color: #0F172A;
            }
            /* Textos dentro do Card de Cliente */
            QLabel#cliente_nome {
                font-size: 14px;
                font-weight: 700;
                color: #FFFFFF;
            }
            QLabel#cliente_tel {
                font-size: 12px;
                color: #64748B;
            }
            QLabel#cliente_tag {
                background-color: #1E293B;
                color: #64748B;
                font-size: 10px;
                font-weight: 600;
                padding: 4px 10px;
                border-radius: 10px;
                text-transform: uppercase;
            }
            /* Toggles (Condições de Entrada) */
            QFrame#toggle_box {
                background-color: #0B1120;
                border: 1px solid #1E293B;
                border-radius: 8px;
            }
            QLabel#toggle_label {
                color: #FFFFFF;
                font-size: 12px;
            }
            /* Cards do Checklist */
            QFrame#checklist_box {
                background-color: #0B1120;
                border: 1px solid #1E293B;
                border-radius: 8px;
            }
            QLabel#item_titulo {
                font-size: 12px;
                font-weight: 700;
                color: #FFFFFF;
            }
            /* Botões de Estado (OK, NOK, NA) */
            QPushButton#btn_estado {
                background-color: #1E293B;
                color: #64748B;
                border: none;
                border-radius: 6px;
                padding: 6px 0px;
                font-size: 11px;
                font-weight: 700;
            }
            QPushButton#btn_estado:hover {
                background-color: #2c3b52;
                color: #FFFFFF;
            }
            QPushButton#btn_estado:checked {
                background-color: #F26522;
                color: #FFFFFF;
            }
            /* Cards de Serviços */
            QPushButton#card_servico {
                background-color: #0B1120;
                border: 1px solid #1E293B;
                border-radius: 8px;
                text-align: left;
            }
            QPushButton#card_servico:hover {
                background-color: #1E293B;
            }
            QPushButton#card_servico:checked {
                border: 1px solid #F26522;
                background-color: #0F172A;
            }
            /* Textos do Card de Serviço */
            QLabel#servico_titulo {
                color: #FFFFFF;
                font-size: 14px;
                font-weight: 700;
            }
            QLabel#servico_preco {
                color: #F26522;
                font-size: 13px;
                font-weight: 600;
            }
            /* Linha laranja de rodapé */
            QFrame#linha_laranja {
                background-color: #F26522;
                max-height: 1px;
                border: none;
                margin-top: 10px;
            }
            /* Botões de Rodapé */
            QPushButton#btnConfirmar, QPushButton#btnCancelar {
                font-size: 14px;
                font-weight: 600;
                border-radius: 6px;
                padding: 10px 24px;
            }
            QPushButton#btnConfirmar {
                background-color: #F26522;
                color: #FFFFFF;
                border: none;
            }
            QPushButton#btnConfirmar:hover { background-color: #E05412; }
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
        self.setStyleSheet(estilo)
# ============================================================================
# EXECUÇÃO PRINCIPAL
# ============================================================================

if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = NovaOrdemServicoWindow()
    janela.show()
    sys.exit(app.exec())