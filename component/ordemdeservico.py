# ordemdeservico.py — sem acento no nome, para import seguro em qualquer SO
# Re-exporta tudo de ordemdeserviço.py e adiciona EditarOrdemServicoWindow
import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from component.ordemdeserviço import (   # noqa: F401
    NovaOrdemServicoWindow,
    AbaCliente,
    AbaAparelho,
    AbaChecklist,
    AbaServicos,
    ClienteCard,
    ToggleBox,
    ChecklistItem,
    ServicoCard,
)

from PyQt6.QtWidgets import (
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QTextEdit, QPushButton, QFrame,
    QSpacerItem, QSizePolicy, QMessageBox, QComboBox,
    QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtWidgets import QCompleter

import data.database as db
from component.base_dialog import ModernDialog

try:
    from component.svg_utils import svg_para_pixmap
    _SVG_OK = True
except Exception:
    _SVG_OK = False


class EditarOrdemServicoWindow(ModernDialog):
    def __init__(self, ordem_id: int):
        super().__init__(f"Editar OS #{ordem_id}", 640, 750)
        self.ordem_id = ordem_id
        db.inicializar_estado()
        self._dados = db.obter_ordem_servico(ordem_id) or {}
        # Lista de trabalho: cada item é {"id": servico_id, "nome": str, "preco": float}
        self._servicos: list[dict] = []
        self._carregar_servicos_atuais()
        self._todos_servicos: list[dict] = self._obter_todos_servicos()
        self._initUI()

    # ──────────────────────────────────────────────
    # Dados
    # ──────────────────────────────────────────────

    def _carregar_servicos_atuais(self):
        for s in db.obter_servicos_da_ordem(self.ordem_id):
            self._servicos.append({
                "id":    s["servico_id"],
                "nome":  s["nome_servico_snapshot"],
                "preco": float(s.get("preco_servico_snapshot") or 0),
            })

    def _obter_todos_servicos(self) -> list[dict]:
        try:
            with db.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome, preco FROM servicos ORDER BY nome")
                return [dict(r) for r in cursor.fetchall()]
        except Exception:
            return []

    # ──────────────────────────────────────────────
    # UI
    # ──────────────────────────────────────────────

    def _initUI(self):
        layout = self.content_layout
        layout.setSpacing(14)

        # ─ Grid principal ─
        grid = QGridLayout()
        grid.setSpacing(12)

        # Modelo
        grid.addWidget(self._lbl("Modelo do Aparelho"), 0, 0)
        self.edit_modelo = QLineEdit(self._dados.get("modelo", ""))
        grid.addWidget(self.edit_modelo, 1, 0)

        # Técnico
        grid.addWidget(self._lbl("Técnico Responsável"), 0, 1)
        self.cmb_tecnico = QComboBox()
        self.cmb_tecnico.addItem("Sem técnico", None)
        try:
            with db.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT id, nome FROM tecnicos ORDER BY nome")
                for row in cursor.fetchall():
                    self.cmb_tecnico.addItem(row["nome"], row["id"])
                    if row["id"] == self._dados.get("tecnico_id"):
                        self.cmb_tecnico.setCurrentIndex(self.cmb_tecnico.count() - 1)
        except Exception:
            pass
        grid.addWidget(self.cmb_tecnico, 1, 1)

        # Prioridade
        grid.addWidget(self._lbl("Prioridade"), 2, 0)
        self.cmb_prioridade = QComboBox()
        self.cmb_prioridade.addItems(["baixa", "normal", "alta", "urgente"])
        self.cmb_prioridade.setCurrentText(self._dados.get("prioridade") or "normal")
        grid.addWidget(self.cmb_prioridade, 3, 0)

        # Status
        grid.addWidget(self._lbl("Status"), 2, 1)
        self.cmb_status = QComboBox()
        self.cmb_status.addItems(["aberta", "em análise", "em andamento", "pronto", "entregue"])
        self.cmb_status.setCurrentText(self._dados.get("status") or "aberta")
        grid.addWidget(self.cmb_status, 3, 1)

        layout.addLayout(grid)

        # ─ Relato ─
        layout.addWidget(self._lbl("Relato do Cliente"))
        self.txt_relato = QTextEdit(self._dados.get("relato") or "")
        self.txt_relato.setFixedHeight(70)
        layout.addWidget(self.txt_relato)

        # ─ Observações ─
        layout.addWidget(self._lbl("Observações / Laudo"))
        self.txt_obs = QTextEdit(self._dados.get("observacoes") or "")
        self.txt_obs.setFixedHeight(60)
        layout.addWidget(self.txt_obs)

        # ─ Serviços ─
        layout.addWidget(self._separador())
        layout.addWidget(self._lbl("Serviços vinculados"))

        # Área de serviços atuais (scroll)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_sv")
        self.scroll_area.setFixedHeight(140)

        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scroll_sv_content")
        self.lista_layout = QVBoxLayout(self.scroll_content)
        self.lista_layout.setSpacing(6)
        self.lista_layout.setContentsMargins(0, 0, 0, 0)
        self.lista_layout.addItem(
            QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        )

        self.scroll_area.setWidget(self.scroll_content)
        layout.addWidget(self.scroll_area)

        self._renderizar_servicos()

        # Adicionar serviço
        add_row = QHBoxLayout()
        add_row.setSpacing(10)

        self.cmb_add_servico = QComboBox()
        self.cmb_add_servico.setEditable(True)
        self.cmb_add_servico.setInsertPolicy(QComboBox.InsertPolicy.NoInsert)
        self.cmb_add_servico.lineEdit().setPlaceholderText("Pesquisar serviço...")
        if _SVG_OK:
            _act = QAction(QIcon(svg_para_pixmap("fi-sr-search.svg", "#64748B", 14, 14)), "", self.cmb_add_servico.lineEdit())
            self.cmb_add_servico.lineEdit().addAction(_act, QLineEdit.ActionPosition.LeadingPosition)
        self._popular_cmb_servicos()
        add_row.addWidget(self.cmb_add_servico)

        btn_add = QPushButton("Adicionar")
        btn_add.setObjectName("btnAdd")
        btn_add.setCursor(Qt.CursorShape.PointingHandCursor)
        if _SVG_OK:
            btn_add.setIcon(QIcon(svg_para_pixmap("fi-sr-plus.svg", "#FFFFFF", 14, 14)))
            btn_add.setIconSize(QSize(14, 14))
        btn_add.clicked.connect(self._adicionar_servico)
        btn_add.setFixedWidth(130)
        add_row.addWidget(btn_add)
        layout.addLayout(add_row)

        # ─ Linha + botões ─
        layout.addWidget(self._separador())

        btns = QHBoxLayout()
        btns.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.btn_cancelar = QPushButton("Cancelar")
        self.btn_cancelar.setObjectName("btnCancelar")
        self.btn_salvar = QPushButton("Salvar Alterações")
        self.btn_salvar.setObjectName("btnConfirmar")
        if _SVG_OK:
            self.btn_salvar.setIcon(QIcon(svg_para_pixmap("fi-sr-check.svg", "#FFFFFF", 16, 16)))
            self.btn_salvar.setIconSize(QSize(16, 16))
        self.btn_cancelar.clicked.connect(self.reject)
        self.btn_salvar.clicked.connect(self._salvar)
        btns.addWidget(self.btn_cancelar)
        btns.addWidget(self.btn_salvar)
        layout.addLayout(btns)

        self._aplicar_estilos()

    def _lbl(self, texto: str) -> QLabel:
        l = QLabel(texto)
        l.setObjectName("lbl_campo")
        return l

    def _separador(self) -> QFrame:
        f = QFrame()
        f.setFrameShape(QFrame.Shape.HLine)
        f.setObjectName("linha_laranja")
        return f

    # ──────────────────────────────────────────────
    # Gestão de serviços
    # ──────────────────────────────────────────────

    def _popular_cmb_servicos(self):
        self.cmb_add_servico.blockSignals(True)
        self.cmb_add_servico.clear()
        ids_atuais = {s["id"] for s in self._servicos}
        nomes = []
        for sv in self._todos_servicos:
            if sv["id"] not in ids_atuais:
                label = f"{sv['nome']}  —  R$ {float(sv.get('preco') or 0):.2f}"
                self.cmb_add_servico.addItem(label, sv)
                nomes.append(label)
        self.cmb_add_servico.blockSignals(False)
        self.cmb_add_servico.setCurrentIndex(-1)
        self.cmb_add_servico.lineEdit().clear()

        completer = QCompleter(nomes, self.cmb_add_servico)
        completer.setFilterMode(Qt.MatchFlag.MatchContains)
        completer.setCaseSensitivity(Qt.CaseSensitivity.CaseInsensitive)
        completer.setCompletionMode(QCompleter.CompletionMode.PopupCompletion)
        completer.activated.connect(self._selecionar_por_completer)
        self.cmb_add_servico.setCompleter(completer)

    def _selecionar_por_completer(self, texto: str):
        idx = self.cmb_add_servico.findText(texto, Qt.MatchFlag.MatchExactly)
        if idx >= 0:
            self.cmb_add_servico.setCurrentIndex(idx)

    def _renderizar_servicos(self):
        # Limpa todos exceto o spacer final
        while self.lista_layout.count() > 1:
            item = self.lista_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._servicos:
            lbl = QLabel("Nenhum serviço vinculado.")
            lbl.setObjectName("lbl_campo")
            self.lista_layout.insertWidget(0, lbl)
            return

        for i, sv in enumerate(self._servicos):
            row = QFrame()
            row.setObjectName("sv_row")
            rl = QHBoxLayout(row)
            rl.setContentsMargins(10, 6, 10, 6)

            lbl_nome = QLabel(sv["nome"])
            lbl_nome.setObjectName("sv_nome")
            lbl_preco = QLabel(f"R$ {sv['preco']:.2f}")
            lbl_preco.setObjectName("sv_preco")

            btn_del = QPushButton()
            btn_del.setObjectName("btn_lixeira")
            btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_del.setFixedSize(28, 28)
            if _SVG_OK:
                btn_del.setIcon(QIcon(svg_para_pixmap("fi-sr-trash.svg", "#64748B", 14, 14)))
                btn_del.setIconSize(QSize(14, 14))
            else:
                btn_del.setText("🗑")
            btn_del.clicked.connect(lambda _, idx=i: self._remover_servico(idx))

            rl.addWidget(lbl_nome)
            rl.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
            rl.addWidget(lbl_preco)
            rl.addWidget(btn_del)

            self.lista_layout.insertWidget(i, row)

    def _adicionar_servico(self):
        sv = self.cmb_add_servico.currentData()
        if not sv:
            return
        self._servicos.append({
            "id":    sv["id"],
            "nome":  sv["nome"],
            "preco": float(sv.get("preco") or 0),
        })
        self._renderizar_servicos()
        self._popular_cmb_servicos()

    def _remover_servico(self, index: int):
        if 0 <= index < len(self._servicos):
            self._servicos.pop(index)
            self._renderizar_servicos()
            self._popular_cmb_servicos()

    # ──────────────────────────────────────────────
    # Salvar
    # ──────────────────────────────────────────────

    def _salvar(self):
        modelo = self.edit_modelo.text().strip()
        if not modelo:
            QMessageBox.warning(self, "Atenção", "Informe o modelo do aparelho.")
            return
        if not self._servicos:
            QMessageBox.warning(self, "Atenção", "Adicione pelo menos um serviço.")
            return
        try:
            with db.get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE ordem_servico
                    SET modelo = ?, tecnico_id = ?, prioridade = ?,
                        status = ?, relato = ?, observacoes = ?
                    WHERE id = ?
                """, (
                    modelo,
                    self.cmb_tecnico.currentData(),
                    self.cmb_prioridade.currentText(),
                    self.cmb_status.currentText(),
                    self.txt_relato.toPlainText().strip(),
                    self.txt_obs.toPlainText().strip(),
                    self.ordem_id,
                ))
                conn.commit()

            # Re-sincroniza serviços: apaga e re-insere
            db.remover_servicos_da_ordem(self.ordem_id)
            db.vincular_servicos_na_ordem(self.ordem_id, [s["id"] for s in self._servicos])

            QMessageBox.information(self, "Sucesso", "OS atualizada com sucesso!")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao salvar:\n{e}")

    # ──────────────────────────────────────────────
    # Estilos
    # ──────────────────────────────────────────────

    def _aplicar_estilos(self):
        self._card.setStyleSheet(self._card.styleSheet() + """
            QLabel { color: #64748B; font-size: 12px; }
            QLabel#title { color: #FFFFFF; font-size: 18px; font-weight: 700; }
            QLabel#lbl_campo { color: #64748B; font-size: 12px; font-weight: 600; }

            QLineEdit, QTextEdit, QComboBox {
                background-color: #0B1120;
                border: 1px solid #1E293B;
                border-radius: 6px;
                padding: 10px;
                color: #FFFFFF;
                font-size: 13px;
            }
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus { border: 1px solid #F26522; }
            QComboBox::drop-down { border: none; }

            QFrame#linha_laranja { background-color: #F26522; max-height: 1px; border: none; }

            /* Scroll de serviços */
            QScrollArea#scroll_sv { border: 1px solid #1E293B; border-radius: 8px; background: transparent; }
            QWidget#scroll_sv_content { background-color: #0B1120; }

            /* Linha de serviço */
            QFrame#sv_row {
                background-color: #0F172A;
                border: 1px solid #1E293B;
                border-radius: 6px;
            }
            QLabel#sv_nome  { color: #FFFFFF; font-size: 13px; font-weight: 600; }
            QLabel#sv_preco { color: #F26522; font-size: 13px; font-weight: 600; }

            QPushButton#btn_lixeira {
                background-color: transparent;
                color: #64748B;
                border: none;
                font-size: 14px;
            }
            QPushButton#btn_lixeira:hover { color: #EF4444; }

            /* Botão Adicionar */
            QPushButton#btnAdd {
                background-color: #1E293B;
                color: #FFFFFF;
                font-size: 13px;
                font-weight: 600;
                border-radius: 6px;
                padding: 8px 12px;
                border: none;
            }
            QPushButton#btnAdd:hover { background-color: #F26522; }

            /* Botões principais */
            QPushButton#btnConfirmar {
                background-color: #F26522; color: #FFFFFF;
                font-size: 14px; font-weight: 600;
                border-radius: 6px; padding: 10px 24px; border: none;
            }
            QPushButton#btnConfirmar:hover { background-color: #E05412; }
            QPushButton#btnCancelar {
                background-color: transparent; color: #FFFFFF;
                border: 1px solid #64748B;
                font-size: 14px; font-weight: 600;
                border-radius: 6px; padding: 10px 24px;
            }
            QPushButton#btnCancelar:hover { background-color: #1E293B; }
        """)
