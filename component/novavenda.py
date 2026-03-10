# NOVA VENDA
# Página para registrar uma nova venda de um celular ou produto relacionando a um cliente cadastrado, com detalhes do produto, preço, forma de pagamento e observações.
# capaz de editar o estoque automaticamente ao finalizar a venda, reduzindo a quantidade do produto vendido e registrando a data da venda.
import sys
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QFrame,
    QSpacerItem, QSizePolicy, QMessageBox, QFileDialog, QComboBox, QButtonGroup, QCompleter
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon
# Adiciona o diretório pai ao sys.path para encontrar o pacote 'data'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db
from component.base_dialog import ModernDialog

try:
    from component.svg_utils import svg_para_pixmap
    _SVG_OK = True
except Exception:
    _SVG_OK = False

class FinalizarVendaDialog(ModernDialog):
    def __init__(self, item_tipo="servico", item_id=0, descricao="Serviço ou Produto", valor_base=0.0):
        super().__init__("Finalizar Venda", 500, 920)
        self.item_tipo = item_tipo
        self.item_id = item_id
        self.descricao = descricao
        self.valor_base = valor_base
        self.total_final = valor_base
        self.initUI()

    def initUI(self):
        main_layout = self.content_layout

        # --- Cliente (Opcional) ---
        lbl_cliente = QLabel("Cliente (opcional)")
        lbl_cliente.setObjectName("form_label")
        main_layout.addWidget(lbl_cliente)
        
        self.cmb_cliente = QComboBox()
        self.cmb_cliente.setEditable(True)
        self.cmb_cliente.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.cmb_cliente.completer().setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        self.cmb_cliente.completer().setFilterMode(Qt.MatchFlag.MatchContains)
        
        self.cmb_cliente.addItem("Selecione um cliente...", None)
        try:
            with db.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome FROM clientes")
                for row in cursor.fetchall():
                    self.cmb_cliente.addItem(row["nome"], row["id"])
        except Exception as e:
            pass
        main_layout.addWidget(self.cmb_cliente)

        # --- Resumo do Item (Box Escuro) ---
        box_item = QFrame()
        box_item.setObjectName("box_padrao")
        layout_item = QHBoxLayout(box_item)
        
        self.lbl_item = QLabel(f"1x {self.descricao}")
        layout_item.addWidget(self.lbl_item)
        
        self.lbl_valor_item = QLabel(f"R$ {self.valor_base:.2f}")
        self.lbl_valor_item.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
        layout_item.addWidget(self.lbl_valor_item)
        main_layout.addWidget(box_item)

        # --- Desconto ---
        lbl_desconto = QLabel("Desconto (R$)")
        lbl_desconto.setObjectName("form_label")
        main_layout.addWidget(lbl_desconto)
        
        self.edit_desconto = QLineEdit()
        self.edit_desconto.setText("0")
        self.edit_desconto.textChanged.connect(self.atualizar_total)
        main_layout.addWidget(self.edit_desconto)

        # --- Forma de Pagamento ---
        lbl_pagamento = QLabel("Forma de Pagamento")
        lbl_pagamento.setObjectName("form_label")
        main_layout.addWidget(lbl_pagamento)
        layout_pagamento = QHBoxLayout()
        layout_pagamento.setSpacing(10)
        
        self.grupo_pagamento = QButtonGroup(self)
        
        opcoes_pagamento = [
            {"texto": "PIX",     "svg": "fi-sr-qrcode.svg",       "id": 1},
            {"texto": "Dinheiro","svg": "fi-sr-money-bills.svg",   "id": 2},
            {"texto": "Crédito", "svg": "fi-sr-credit-card.svg",   "id": 3},
            {"texto": "Débito",  "svg": "fi-sr-credit-card.svg",   "id": 4},
        ]
        
        for op in opcoes_pagamento:
            btn = QPushButton(op["texto"])
            btn.setObjectName("btn_pagamento")
            btn.setCheckable(True)
            btn.setFixedHeight(70)
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            if _SVG_OK:
                btn.setIcon(QIcon(svg_para_pixmap(op["svg"], "#64748B", 20, 20)))
                btn.setIconSize(QSize(20, 20))
            self.grupo_pagamento.addButton(btn, op["id"])
            layout_pagamento.addWidget(btn)
            
            # Deixa o Crédito selecionado por padrão
            if op["id"] == 3:
                btn.setChecked(True)
                
        main_layout.addLayout(layout_pagamento)

        # --- Parcelas ---
        lbl_parcelas = QLabel("Parcelas")
        lbl_parcelas.setObjectName("form_label")
        main_layout.addWidget(lbl_parcelas)
        self.cmb_parcelas = QComboBox()
        self.cmb_parcelas.addItem("1x")
        self.cmb_parcelas.addItem("2x")
        self.cmb_parcelas.addItem("3x")
        self.cmb_parcelas.addItem("4x")
        self.cmb_parcelas.addItem("5x")
        self.cmb_parcelas.addItem("6x")
        self.cmb_parcelas.addItem("7x")
        self.cmb_parcelas.addItem("8x")
        self.cmb_parcelas.addItem("9x")
        self.cmb_parcelas.addItem("10x")
        self.cmb_parcelas.addItem("11x")
        self.cmb_parcelas.addItem("12x")
        main_layout.addWidget(self.cmb_parcelas)

        # --- Garantia ---
        lbl_garantia = QLabel("Garantia")
        lbl_garantia.setObjectName("form_label")
        main_layout.addWidget(lbl_garantia)
        
        self.edit_garantia = QLineEdit()
        self.edit_garantia.setText("90 dias")
        main_layout.addWidget(self.edit_garantia)

        # --- Observação ---
        lbl_observacao = QLabel("Observação")
        lbl_observacao.setObjectName("form_label")
        main_layout.addWidget(lbl_observacao)
        
        self.edit_observacao = QTextEdit()
        self.edit_observacao.setFixedHeight(60)
        self.edit_observacao.setPlaceholderText("Alguma observação importante sobre a venda?")
        main_layout.addWidget(self.edit_observacao)

        # --- Box de Totais ---
        box_totais = QFrame()
        box_totais.setObjectName("box_padrao")
        layout_totais = QVBoxLayout(box_totais)
        
        # Subtotal
        layout_subtotal = QHBoxLayout()
        lbl_subtotal_txt = QLabel("Subtotal")
        lbl_subtotal_txt.setObjectName("txt_cinza")
        self.lbl_subtotal_val = QLabel(f"R$ {self.valor_base:.2f}")
        self.lbl_subtotal_val.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout_subtotal.addWidget(lbl_subtotal_txt)
        layout_subtotal.addWidget(self.lbl_subtotal_val)
        layout_totais.addLayout(layout_subtotal)
        
        # Linha divisória interna
        linha_interna = QFrame()
        linha_interna.setFrameShape(QFrame.Shape.HLine)
        linha_interna.setObjectName("linha_escura")
        layout_totais.addWidget(linha_interna)
        
        # Total
        layout_total = QHBoxLayout()
        lbl_total_txt = QLabel("Total")
        lbl_total_txt.setObjectName("txt_total")
        self.lbl_total_val = QLabel(f"R$ {self.total_final:.2f}")
        self.lbl_total_val.setObjectName("valor_total_destaque")
        self.lbl_total_val.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout_total.addWidget(lbl_total_txt)
        layout_total.addWidget(self.lbl_total_val)
        layout_totais.addLayout(layout_total)

        main_layout.addWidget(box_totais)
        
        # Empurra o resto para baixo
        main_layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # --- Linha de Destaque Laranja ---
        linha = QFrame()
        linha.setFrameShape(QFrame.Shape.HLine)
        linha.setObjectName("linha_laranja")
        main_layout.addWidget(linha)

        main_layout.addSpacing(10)

        # --- Botões de Ação ---
        botoes_layout = QHBoxLayout()
        spacer = QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        botoes_layout.addItem(spacer)
        
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("btnCancelar")
        
        self.btn_confirmar = QPushButton("Confirmar Venda")
        if _SVG_OK:
            self.btn_confirmar.setIcon(QIcon(svg_para_pixmap("fi-sr-check.svg", "#FFFFFF", 16, 16)))
            self.btn_confirmar.setIconSize(QSize(16, 16))
        else:
            self.btn_confirmar.setText("✓ Confirmar Venda")
        self.btn_confirmar.setObjectName("btnConfirmar")
        
        botoes_layout.addWidget(self.btn_cancelar)
        botoes_layout.addWidget(self.btn_confirmar)
        
        self.btn_cancelar.clicked.connect(self.close)
        self.btn_confirmar.clicked.connect(self.confirmar_venda)

        main_layout.addLayout(botoes_layout)

        self.aplicar_estilos()

    def atualizar_total(self):
        try:
            desconto = float(self.edit_desconto.text().strip().replace(",", ".") or 0)
        except ValueError:
            desconto = 0

        total = self.valor_base - desconto
        if total < 0:
            total = 0

        self.total_final = total
        self.lbl_subtotal_val.setText(f"R$ {self.valor_base:.2f}")
        self.lbl_total_val.setText(f"R$ {total:.2f}")

    def obter_forma_pagamento(self):
        btn = self.grupo_pagamento.checkedButton()
        if not btn:
            return "não informado"

        texto = btn.text()
        if "PIX" in texto:
            return "pix"
        if "Dinheiro" in texto:
            return "dinheiro"
        if "Crédito" in texto:
            return "credito"
        if "Débito" in texto:
            return "debito"

        return "não informado"

    def confirmar_venda(self):
        try:
            desconto = float(self.edit_desconto.text().strip().replace(",", ".") or 0)
        except ValueError:
            QMessageBox.warning(self, "Erro", "Desconto inválido.")
            return

        forma_pagamento = self.obter_forma_pagamento()
        parcelamento = self.cmb_parcelas.currentText()
        observacao = self.edit_observacao.toPlainText().strip()
        if not observacao:
            observacao = "Venda finalizada pelo sistema"
        
        garantia = self.edit_garantia.text().strip()
        if not garantia:
            garantia = "90 dias"

        cliente_id = self.cmb_cliente.currentData()
        produto_id = None
        celular_id = None
        servico_id = None

        if self.item_tipo == "produto":
            produto_id = self.item_id
        elif self.item_tipo == "celular":
            celular_id = self.item_id
        elif self.item_tipo == "servico":
            servico_id = self.item_id

        try:
            db.registrar_venda(
                cliente_id,
                produto_id,
                celular_id,
                servico_id,
                desconto,
                forma_pagamento,
                parcelamento,
                observacao,
                garantia,
                self.total_final
            )
            QMessageBox.information(self, "Sucesso", "Venda registrada com sucesso.")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Erro ao registrar venda:\n{e}")

    def aplicar_estilos(self):
        estilo = """
        QLabel {
            color: #FFFFFF;
            font-size: 13px;
        }
        QLabel#title {
            font-size: 18px;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
        }
        QLabel#form_label {
            font-size: 12px;
            font-weight: 600;
            color: #64748B;
            letter-spacing: 0.5px;
        }
        QLabel#txt_cinza { color: #64748B; }

        /* Inputs e Combobox */
        QLineEdit, QComboBox {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 6px;
            padding: 10px;
            color: #FFFFFF;
            font-size: 14px;
        }
        QLineEdit:focus, QComboBox:focus {
            border: 1px solid #F26522;
        }
        QComboBox::drop-down { border: none; }
        
        /* Caixas Escuras (Item e Totais) */
        QFrame#box_padrao {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 8px;
        }
        
        /* Textos do Box de Totais */
        QLabel#txt_total {
            font-size: 16px;
            font-weight: 700;
        }
        QLabel#valor_total_destaque {
            font-size: 20px;
            font-weight: 700;
            color: #F26522; /* Laranja no Total */
        }
        QFrame#linha_escura {
            background-color: #1E293B;
            max-height: 1px;
            border: none;
            margin: 5px 0px;
        }

        /* Botões de Forma de Pagamento */
        QPushButton#btn_pagamento {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 8px;
            color: #64748B;
            font-size: 12px;
            font-weight: 600;
        }
        QPushButton#btn_pagamento:hover {
            background-color: #1E293B;
            color: #FFFFFF;
        }
        QPushButton#btn_pagamento:checked {
            border: 2px solid #F26522; /* Borda laranja quando selecionado */
            color: #FFFFFF;
            background-color: #0F172A;
        }

        /* Linha laranja de rodapé */
        QFrame#linha_laranja {
            background-color: #F26522;
            max-height: 1px;
            border: none;
        }

        /* Botões Base */
        QPushButton {
            font-size: 14px;
            font-weight: 600;
            border-radius: 6px;
            padding: 10px 20px;
        }

        /* Botão Confirmar Venda */
        QPushButton#btnConfirmar {
            background-color: #F26522;
            color: #FFFFFF;
            border: none;
        }
        QPushButton#btnConfirmar:hover { background-color: #E05412; }

        /* Botão Cancelar */
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
        self.setStyleSheet(self.styleSheet() + estilo)

# main para teste
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dialog = FinalizarVendaDialog()
    dialog.exec()