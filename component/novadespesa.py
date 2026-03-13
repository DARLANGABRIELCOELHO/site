# Nova Despesa
# Interface para cadastro de despesas (PyQt6)
import sys
import os
from datetime import date

from PyQt6.QtWidgets import (
    QApplication, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFrame,
    QComboBox, QCheckBox, QTextEdit,
    QSpacerItem, QSizePolicy, QMessageBox
)
from PyQt6.QtCore import QSize, pyqtSignal
from PyQt6.QtGui import QIcon, QDoubleValidator

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db
from component.base_dialog import ModernDialog

try:
    from component.svg_utils import svg_para_pixmap
    _SVG_OK = True
except Exception:
    _SVG_OK = False


class NovaDespesaWindow(ModernDialog):
    despesa_salva = pyqtSignal()

    def __init__(self, data_selecionada: date = None, parent=None):
        super().__init__("Nova Despesa", 600, 700, parent)
        db.inicializar_estado()
        self.data_sel = data_selecionada or date.today()
        self.initUI()

    def initUI(self):
        layout = self.content_layout

        # ─ Data ─
        lbl_data = QLabel(f"Data: {self.data_sel.strftime('%d/%m/%Y')}")
        lbl_data.setObjectName("lbl_data_info")
        layout.addWidget(lbl_data)

        # ─ Descrição ─
        layout.addWidget(QLabel("Descrição *"))
        self.edit_descricao = QLineEdit()
        self.edit_descricao.setPlaceholderText("Ex: Conta de luz, aluguel...")
        layout.addWidget(self.edit_descricao)

        # ─ Valor + Categoria ─
        grid = QGridLayout()
        grid.setSpacing(12)

        grid.addWidget(QLabel("Valor (R$) *"), 0, 0)
        self.edit_valor = QLineEdit()
        self.edit_valor.setPlaceholderText("0,00")
        self.edit_valor.setValidator(QDoubleValidator(0, 999999, 2))
        grid.addWidget(self.edit_valor, 1, 0)

        grid.addWidget(QLabel("Categoria *"), 0, 1)
        self.cmb_categoria = QComboBox()
        for c in db.CATEGORIAS_DESPESA:
            self.cmb_categoria.addItem(c)
        grid.addWidget(self.cmb_categoria, 1, 1)

        layout.addLayout(grid)

        # ─ Forma de Pagamento ─
        layout.addWidget(QLabel("Forma de Pagamento"))
        self.cmb_pagamento = QComboBox()
        for p in ["Dinheiro", "Pix", "Cartão de Débito", "Cartão de Crédito", "Boleto", "Transferência"]:
            self.cmb_pagamento.addItem(p)
        layout.addWidget(self.cmb_pagamento)

        # ─ Observações ─
        layout.addWidget(QLabel("Observações (opcional)"))
        self.edit_obs = QTextEdit()
        self.edit_obs.setFixedHeight(64)
        self.edit_obs.setPlaceholderText("Detalhes adicionais...")
        layout.addWidget(self.edit_obs)

        # ─ Recorrente ─
        recorrente_row = QHBoxLayout()
        recorrente_row.setSpacing(10)

        self.chk_recorrente = QCheckBox("Despesa recorrente")
        self.chk_recorrente.setObjectName("chk_recorrente")
        self.chk_recorrente.toggled.connect(self._toggle_recorrencia)
        recorrente_row.addWidget(self.chk_recorrente)

        self.cmb_recorrencia = QComboBox()
        self.cmb_recorrencia.setObjectName("cmb_recorrencia")
        self.cmb_recorrencia.addItems(["Semanal", "Quinzenal", "Mensal"])
        self.cmb_recorrencia.setFixedWidth(120)
        self.cmb_recorrencia.setEnabled(False)
        recorrente_row.addWidget(self.cmb_recorrencia)
        recorrente_row.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        layout.addLayout(recorrente_row)

        layout.addItem(QSpacerItem(20, 8, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # ─ Separador ─
        linha = QFrame()
        linha.setFrameShape(QFrame.Shape.HLine)
        linha.setObjectName("linha_laranja")
        layout.addWidget(linha)

        # ─ Botões ─
        btns = QHBoxLayout()
        btns.setSpacing(10)
        btns.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("btnCancelar")
        self.btn_cancelar.clicked.connect(self.reject)

        self.btn_salvar = QPushButton("Salvar Despesa")
        self.btn_salvar.setObjectName("btnCadastrar")
        if _SVG_OK:
            self.btn_salvar.setIcon(QIcon(svg_para_pixmap("fi-sr-check.svg", "#FFFFFF", 16, 16)))
            self.btn_salvar.setIconSize(QSize(16, 16))
        self.btn_salvar.clicked.connect(self.salvar_despesa)

        btns.addWidget(self.btn_cancelar)
        btns.addWidget(self.btn_salvar)
        layout.addLayout(btns)

        self._aplicar_estilos()

    def _toggle_recorrencia(self, checked: bool):
        self.cmb_recorrencia.setEnabled(checked)

    def salvar_despesa(self):
        descricao = self.edit_descricao.text().strip()
        valor_txt = self.edit_valor.text().replace(",", ".").strip()
        categoria = self.cmb_categoria.currentText()
        forma = self.cmb_pagamento.currentText()
        obs = self.edit_obs.toPlainText().strip()
        recorrente = self.chk_recorrente.isChecked()
        recorrencia = self.cmb_recorrencia.currentText().lower() if recorrente else ""

        if not descricao:
            QMessageBox.warning(self, "Atenção", "Preencha a descrição da despesa.")
            return
        try:
            valor = float(valor_txt)
            if valor <= 0:
                raise ValueError
        except ValueError:
            QMessageBox.warning(self, "Atenção", "Informe um valor válido maior que zero.")
            return

        try:
            db.registrar_despesa(
                descricao=descricao,
                valor=valor,
                categoria=categoria,
                data=self.data_sel.isoformat(),
                forma_pagamento=forma,
                observacoes=obs,
                recorrente=recorrente,
                recorrencia=recorrencia
            )
            self.despesa_salva.emit()
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro ao salvar", f"Não foi possível salvar a despesa.\n\n{str(e)}")

    def _aplicar_estilos(self):
        estilo = """
        QLabel#lbl_data_info {
            color: #F26522;
            font-size: 12px;
            font-weight: 600;
        }

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
            font-size: 13px;
            selection-background-color: #F26522;
        }

        QLineEdit:focus, QTextEdit:focus {
            border: 1px solid #F26522;
        }

        QComboBox {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 6px;
            padding: 10px;
            color: #FFFFFF;
            font-size: 13px;
        }

        QComboBox::drop-down { border: none; }

        QComboBox QAbstractItemView {
            background-color: #0B1120;
            color: #FFFFFF;
            border: 1px solid #1E293B;
            selection-background-color: #F26522;
        }

        QCheckBox#chk_recorrente {
            color: #64748B;
            font-size: 12px;
        }

        QCheckBox#chk_recorrente::indicator {
            width: 16px;
            height: 16px;
            border-radius: 4px;
            background-color: #0F172A;
            border: 1px solid #1E293B;
        }

        QCheckBox#chk_recorrente::indicator:checked {
            background-color: #F26522;
            border: 1px solid #F26522;
        }

        QComboBox#cmb_recorrencia {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 6px;
            padding: 6px 10px;
            color: #FFFFFF;
            font-size: 12px;
        }

        QComboBox#cmb_recorrencia:disabled {
            color: #64748B;
            border: 1px solid #1E293B;
        }

        QComboBox#cmb_recorrencia::drop-down { border: none; }

        QComboBox#cmb_recorrencia QAbstractItemView {
            background-color: #0B1120;
            color: #FFFFFF;
            border: 1px solid #1E293B;
            selection-background-color: #F26522;
        }

        QFrame#linha_laranja {
            background-color: #F26522;
            max-height: 1px;
            border: none;
        }

        QPushButton {
            font-size: 13px;
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
        self._card.setStyleSheet(self._card.styleSheet() + estilo)


# ════════════════════════════════════════════════════════════════════
# MAIN
# ════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    app = QApplication(sys.argv)
    janela = NovaDespesaWindow()
    janela.show()
    sys.exit(app.exec())
