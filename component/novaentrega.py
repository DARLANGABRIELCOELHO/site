# novaentrega.py — Dialog de fechamento/entrega de Ordem de Serviço
import sys
import os
from datetime import datetime, date, timedelta

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QFrame,
    QSpacerItem, QSizePolicy, QMessageBox, QComboBox,
    QScrollArea, QWidget
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QDoubleValidator

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db
from component.base_dialog import ModernDialog


class NovaEntregaWindow(ModernDialog):
    """
    Dialog de entrega de OS — coleta laudo, desconto, forma de pagamento
    e garantia antes de registrar a entrega no banco.
    """

    GARANTIAS = {
        "Sem garantia":  0,
        "30 dias":      30,
        "60 dias":      60,
        "90 dias":      90,
        "6 meses":     180,
        "1 ano":       365,
    }

    FORMAS_PAGAMENTO = [
        "Dinheiro",
        "Pix",
        "Cartão Débito",
        "Cartão Crédito",
        "Transferência",
    ]

    def __init__(self, ordem: dict):
        """
        ordem: dict retornado por listar_ordens_servico()
               (precisa de: id, cliente_nome, modelo, cor,
                tecnico_nome, servicos, total_servicos)
        """
        super().__init__(f"Entregar OS #{ordem['id']}", 620, 660)
        self._ordem = ordem
        db.inicializar_estado()
        self._initUI()

    # ──────────────────────────────────────────────
    # UI
    # ──────────────────────────────────────────────

    def _initUI(self):
        root = self.content_layout

        # ─ Resumo da OS (readonly) ─
        box_resumo = QFrame()
        box_resumo.setObjectName("box_resumo")
        resumo_layout = QVBoxLayout(box_resumo)
        resumo_layout.setContentsMargins(15, 15, 15, 15)
        resumo_layout.setSpacing(8)

        cliente = self._ordem.get("cliente_nome") or "Balcão"
        modelo  = self._ordem.get("modelo", "—")
        cor     = (self._ordem.get("cor") or "").strip()
        aparelho = f"{modelo} • {cor}" if cor else modelo
        tecnico = self._ordem.get("tecnico_nome") or "—"

        for rotulo, valor in [
            ("Cliente",  cliente),
            ("Aparelho", aparelho),
            ("Técnico",  tecnico),
        ]:
            linha = QHBoxLayout()
            l = QLabel(rotulo + ":")
            l.setObjectName("lbl_rotulo")
            l.setFixedWidth(70)
            v = QLabel(valor)
            v.setObjectName("lbl_valor_resumo")
            linha.addWidget(l)
            linha.addWidget(v)
            linha.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
            resumo_layout.addLayout(linha)

        # Serviços
        servicos = self._ordem.get("servicos", [])
        if servicos:
            linha_sv = QHBoxLayout()
            l2 = QLabel("Serviços:")
            l2.setObjectName("lbl_rotulo")
            l2.setFixedWidth(70)
            nomes = ", ".join(sv.get("nome", "—") for sv in servicos)
            v2 = QLabel(nomes)
            v2.setObjectName("lbl_valor_resumo")
            v2.setWordWrap(True)
            linha_sv.addWidget(l2)
            linha_sv.addWidget(v2)
            resumo_layout.addLayout(linha_sv)

        root.addWidget(box_resumo)

        # ─ Formulário ─
        grid = QGridLayout()
        grid.setSpacing(12)

        # Desconto
        grid.addWidget(self._label("Desconto (R$)"), 0, 0)
        self.edit_desconto = QLineEdit("0,00")
        self.edit_desconto.setValidator(QDoubleValidator(0, 99999, 2, self))
        self.edit_desconto.textChanged.connect(self._atualizar_total)
        grid.addWidget(self.edit_desconto, 1, 0)

        # Forma de pagamento
        grid.addWidget(self._label("Forma de Pagamento"), 0, 1)
        self.cmb_pagamento = QComboBox()
        self.cmb_pagamento.addItems(self.FORMAS_PAGAMENTO)
        self.cmb_pagamento.currentTextChanged.connect(self._toggle_parcelamento)
        grid.addWidget(self.cmb_pagamento, 1, 1)

        # Parcelamento
        grid.addWidget(self._label("Parcelamento"), 2, 0)
        self.cmb_parcelamento = QComboBox()
        self.cmb_parcelamento.addItems([
            "À vista", "2x", "3x", "4x", "5x", "6x",
            "7x", "8x", "9x", "10x", "11x", "12x"
        ])
        self.cmb_parcelamento.setEnabled(False)
        grid.addWidget(self.cmb_parcelamento, 3, 0)

        # Garantia
        grid.addWidget(self._label("Garantia"), 2, 1)
        self.cmb_garantia = QComboBox()
        self.cmb_garantia.addItems(list(self.GARANTIAS.keys()))
        self.cmb_garantia.setCurrentText("90 dias")
        grid.addWidget(self.cmb_garantia, 3, 1)

        root.addLayout(grid)

        # Laudo técnico
        root.addWidget(self._label("Laudo Técnico"))
        self.txt_laudo = QTextEdit()
        self.txt_laudo.setPlaceholderText("Descreva o que foi feito no aparelho...")
        self.txt_laudo.setFixedHeight(80)
        root.addWidget(self.txt_laudo)

        # Observações
        root.addWidget(self._label("Observações"))
        self.txt_obs = QTextEdit()
        self.txt_obs.setPlaceholderText("Observações adicionais para o cliente...")
        self.txt_obs.setFixedHeight(60)
        root.addWidget(self.txt_obs)

        # ─ Total ─
        linha_div = QFrame()
        linha_div.setFrameShape(QFrame.Shape.HLine)
        linha_div.setObjectName("linha_laranja")
        root.addWidget(linha_div)

        total_row = QHBoxLayout()
        lbl_total_t = QLabel("Total a receber:")
        lbl_total_t.setObjectName("lbl_total_txt")
        self.lbl_total_val = QLabel("R$ 0,00")
        self.lbl_total_val.setObjectName("lbl_total_val")
        self.lbl_total_val.setAlignment(Qt.AlignmentFlag.AlignRight)
        total_row.addWidget(lbl_total_t)
        total_row.addWidget(self.lbl_total_val)
        root.addLayout(total_row)

        # ─ Botões ─
        btns = QHBoxLayout()
        btns.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("btnCancelar")
        self.btn_confirmar = QPushButton("✓ Confirmar Entrega")
        self.btn_confirmar.setObjectName("btnConfirmar")
        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_confirmar.clicked.connect(self._confirmar)
        btns.addWidget(self.btn_cancelar)
        btns.addWidget(self.btn_confirmar)
        root.addLayout(btns)

        self._atualizar_total()
        self._aplicar_estilos()

    # ──────────────────────────────────────────────
    # LÓGICA
    # ──────────────────────────────────────────────

    def _label(self, texto: str) -> QLabel:
        lbl = QLabel(texto)
        lbl.setObjectName("lbl_campo")
        return lbl

    def _toggle_parcelamento(self, forma: str):
        self.cmb_parcelamento.setEnabled(forma == "Cartão Crédito")
        if forma != "Cartão Crédito":
            self.cmb_parcelamento.setCurrentText("À vista")

    def _atualizar_total(self):
        total_bruto = float(self._ordem.get("total_servicos") or 0)
        try:
            desc_texto = self.edit_desconto.text().replace(",", ".")
            desconto = float(desc_texto) if desc_texto else 0.0
        except ValueError:
            desconto = 0.0
        total_liq = max(0.0, total_bruto - desconto)
        self.lbl_total_val.setText(f"R$ {total_liq:.2f}")

    def _confirmar(self):
        try:
            desc_texto = self.edit_desconto.text().replace(",", ".")
            desconto = float(desc_texto) if desc_texto else 0.0
        except ValueError:
            desconto = 0.0

        total_bruto = float(self._ordem.get("total_servicos") or 0)
        total_liq   = max(0.0, total_bruto - desconto)

        garantia_texto = self.cmb_garantia.currentText()
        dias = self.GARANTIAS.get(garantia_texto, 0)
        data_fim_garantia = (date.today() + timedelta(days=dias)).isoformat() if dias > 0 else None

        # Busca cliente_id e tecnico_id direto na OS
        os_raw = db.obter_ordem_servico(self._ordem["id"]) or {}

        dados = {
            "ordem_servico_id": self._ordem["id"],
            "cliente_id":       os_raw.get("cliente_id"),
            "tecnico_id":       os_raw.get("tecnico_id"),
            "laudo":            self.txt_laudo.toPlainText().strip() or None,
            "observacoes":      self.txt_obs.toPlainText().strip() or None,
            "desconto":         desconto,
            "forma_pagamento":  self.cmb_pagamento.currentText(),
            "parcelamento":     self.cmb_parcelamento.currentText(),
            "garantia":         garantia_texto,
            "data_fim_garantia": data_fim_garantia,
            "valor_total":      total_liq,
        }

        try:
            db.registrar_ordem_entrega(dados)
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao registrar entrega:\n{e}")
            return

        # Gera e imprime nota final de serviço
        try:
            from component.notas import gerar_nota_entrega
            gerar_nota_entrega(dados, self._ordem)
        except Exception as e:
            QMessageBox.warning(
                self, "Aviso",
                f"Entrega registrada, mas falha ao gerar nota:\n{e}"
            )

        QMessageBox.information(
            self, "Sucesso",
            f"OS #{self._ordem['id']} entregue!\n"
            f"Garantia: {garantia_texto}\n"
            f"Total: R$ {total_liq:.2f}\n\n"
            f"Nota de serviço enviada para impressão."
        )
        self.accept()

    # ──────────────────────────────────────────────
    # ESTILOS
    # ──────────────────────────────────────────────

    def _aplicar_estilos(self):
        self.setStyleSheet(self.styleSheet() + """
            QLabel#title {
                color: #FFFFFF;
                font-size: 18px;
                font-weight: 700;
            }

            /* Resumo da OS */
            QFrame#box_resumo {
                background-color: #0B1120;
                border: 1px solid #1E293B;
                border-radius: 10px;
            }
            QLabel#lbl_rotulo {
                color: #64748B;
                font-size: 11px;
                font-weight: 600;
            }
            QLabel#lbl_valor_resumo {
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 600;
            }

            /* Labels de campo */
            QLabel#lbl_campo {
                color: #64748B;
                font-size: 12px;
                font-weight: 600;
            }

            /* Inputs */
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
            QComboBox:disabled {
                color: #334155;
                border-color: #1E293B;
            }

            /* Linha laranja */
            QFrame#linha_laranja {
                background-color: #F26522;
                max-height: 1px;
                border: none;
            }

            /* Total */
            QLabel#lbl_total_txt {
                color: #94A3B8;
                font-size: 14px;
                font-weight: 600;
            }
            QLabel#lbl_total_val {
                color: #4ADE80;
                font-size: 22px;
                font-weight: 700;
            }

            /* Botões */
            QPushButton#btnConfirmar {
                background-color: #F26522;
                color: #FFFFFF;
                font-size: 14px;
                font-weight: 600;
                border-radius: 6px;
                padding: 10px 24px;
                border: none;
            }
            QPushButton#btnConfirmar:hover { background-color: #E05412; }

            QPushButton#btnCancelar {
                background-color: transparent;
                color: #FFFFFF;
                border: 1px solid #64748B;
                font-size: 14px;
                font-weight: 600;
                border-radius: 6px;
                padding: 10px 24px;
            }
            QPushButton#btnCancelar:hover { background-color: #1E293B; }
        """)
