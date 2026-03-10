# novocancelamento.py — Dialog de cancelamento de Ordem de Serviço
import sys
import os

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout,
    QLabel, QTextEdit, QPushButton, QFrame,
    QSpacerItem, QSizePolicy, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db
from component.base_dialog import ModernDialog


MOTIVOS = [
    "Cliente desistiu do serviço",
    "Peça indisponível no mercado",
    "Custo do reparo inviável",
    "Equipamento com dano irreparável",
    "Cliente não buscou o equipamento",
    "Problema resolvido sem reparo",
    "Outro motivo",
]


class NovoCancelamentoWindow(ModernDialog):
    """Dialog para cancelar uma Ordem de Serviço."""

    def __init__(self, ordem: dict):
        super().__init__(f"Cancelar OS #{ordem['id']}", 520, 500)
        self._ordem = ordem
        db.inicializar_estado()
        self._initUI()

    # ──────────────────────────────────────────────
    # UI
    # ──────────────────────────────────────────────

    def _initUI(self):
        layout = self.content_layout

        # ─ Resumo da OS ─
        box = QFrame()
        box.setObjectName("box_resumo")
        box_layout = QVBoxLayout(box)
        box_layout.setContentsMargins(15, 15, 15, 15)
        box_layout.setSpacing(6)

        cliente  = self._ordem.get("cliente_nome") or "Balcão"
        modelo   = self._ordem.get("modelo", "—")
        cor      = (self._ordem.get("cor") or "").strip()
        aparelho = f"{modelo} • {cor}" if cor else modelo
        status   = self._ordem.get("status", "—")

        for rotulo, valor in [
            ("Cliente",  cliente),
            ("Aparelho", aparelho),
            ("Status",   status),
        ]:
            linha = QHBoxLayout()
            lbl_r = QLabel(rotulo + ":")
            lbl_r.setObjectName("lbl_rotulo")
            lbl_r.setFixedWidth(70)
            lbl_v = QLabel(valor)
            lbl_v.setObjectName("lbl_valor")
            linha.addWidget(lbl_r)
            linha.addWidget(lbl_v)
            linha.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
            box_layout.addLayout(linha)

        layout.addWidget(box)

        # ─ Motivo ─
        layout.addWidget(self._lbl("Motivo do Cancelamento *"))
        self.cmb_motivo = QComboBox()
        self.cmb_motivo.addItems(MOTIVOS)
        layout.addWidget(self.cmb_motivo)

        # ─ Observação ─
        layout.addWidget(self._lbl("Observações adicionais"))
        self.txt_obs = QTextEdit()
        self.txt_obs.setPlaceholderText("Descreva detalhes sobre o cancelamento...")
        self.txt_obs.setFixedHeight(90)
        layout.addWidget(self.txt_obs)

        # ─ Aviso ─
        lbl_aviso = QLabel("⚠  Esta ação alterará o status da OS para 'cancelada'.")
        lbl_aviso.setObjectName("lbl_aviso")
        lbl_aviso.setWordWrap(True)
        layout.addWidget(lbl_aviso)

        layout.addItem(QSpacerItem(20, 8, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

        # ─ Linha + botões ─
        linha_div = QFrame()
        linha_div.setFrameShape(QFrame.Shape.HLine)
        linha_div.setObjectName("linha_div")
        layout.addWidget(linha_div)

        btns = QHBoxLayout()
        btns.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.btn_cancelar = QPushButton("Voltar")
        self.btn_cancelar.setObjectName("btnCancelar")
        self.btn_confirmar = QPushButton("✕ Confirmar Cancelamento")
        self.btn_confirmar.setObjectName("btnConfirmar")
        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_confirmar.clicked.connect(self._confirmar)
        btns.addWidget(self.btn_cancelar)
        btns.addWidget(self.btn_confirmar)
        layout.addLayout(btns)

        self._aplicar_estilos()

    def _lbl(self, texto: str) -> QLabel:
        lbl = QLabel(texto)
        lbl.setObjectName("lbl_campo")
        return lbl

    # ──────────────────────────────────────────────
    # Lógica
    # ──────────────────────────────────────────────

    def _confirmar(self):
        motivo = self.cmb_motivo.currentText()
        obs    = self.txt_obs.toPlainText().strip() or None

        resp = QMessageBox.question(
            self,
            "Confirmar Cancelamento",
            f"Cancelar a OS #{self._ordem['id']}?\n\nMotivo: {motivo}\n\nEsta ação não pode ser desfeita.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp != QMessageBox.StandardButton.Yes:
            return

        dados = {
            "ordem_servico_id": self._ordem["id"],
            "motivo":           motivo,
            "observacao":       obs,
        }

        try:
            db.registrar_ordem_cancelamento(dados)
            QMessageBox.information(
                self, "Cancelado",
                f"OS #{self._ordem['id']} cancelada.\nMotivo: {motivo}"
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao cancelar OS:\n{e}")

    # ──────────────────────────────────────────────
    # Estilos
    # ──────────────────────────────────────────────

    def _aplicar_estilos(self):
        self.setStyleSheet(self.styleSheet() + """
            QFrame#box_resumo {
                background-color: #0B1120;
                border: 1px solid #1E293B;
                border-radius: 10px;
            }
            QLabel#lbl_rotulo { color: #64748B; font-size: 11px; font-weight: 600; }
            QLabel#lbl_valor  { color: #FFFFFF; font-size: 13px; font-weight: 600; }
            QLabel#lbl_campo  { color: #64748B; font-size: 12px; font-weight: 600; }

            QLabel#lbl_aviso {
                color: #EAB308;
                font-size: 12px;
                font-weight: 600;
                background-color: rgba(234,179,8,0.08);
                border: 1px solid rgba(234,179,8,0.3);
                border-radius: 6px;
                padding: 8px 12px;
            }

            QComboBox, QTextEdit {
                background-color: #0B1120;
                border: 1px solid #1E293B;
                border-radius: 6px;
                padding: 10px;
                color: #FFFFFF;
                font-size: 13px;
            }
            QComboBox:focus, QTextEdit:focus { border: 1px solid #EF4444; }
            QComboBox::drop-down { border: none; }

            QFrame#linha_div { background-color: #1E293B; max-height: 1px; border: none; }

            QPushButton#btnConfirmar {
                background-color: #EF4444;
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 600;
                border-radius: 6px;
                padding: 10px 20px;
                border: none;
            }
            QPushButton#btnConfirmar:hover { background-color: #DC2626; }

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
