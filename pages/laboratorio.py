# laboratorio.py — Página de gestão de Ordens de Serviço (PyQt6)
import sys
import os
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFrame,
    QSpacerItem, QSizePolicy, QMessageBox, QScrollArea,
    QComboBox, QMenu
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db
from component.ordemdeservico import NovaOrdemServicoWindow, EditarOrdemServicoWindow
from component.novaentrega import NovaEntregaWindow

try:
    from component.svg_utils import svg_para_pixmap
    _SVG_OK = True
except Exception:
    _SVG_OK = False


# ──────────────────────────────────────────────
# COMPONENTES
# ──────────────────────────────────────────────

class Badge(QLabel):
    def __init__(self, texto, cor_fundo, cor_texto):
        super().__init__(texto)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            background-color: {cor_fundo};
            color: {cor_texto};
            border-radius: 4px;
            padding: 4px 8px;
            font-size: 10px;
            font-weight: 700;
        """)


def _badge_status(status: str) -> Badge:
    mapa = {
        "aberta":       ("rgba(234,179,8,0.2)",   "#FDE047", "Pendente"),
        "pendente":     ("rgba(234,179,8,0.2)",   "#FDE047", "Pendente"),
        "em análise":   ("rgba(59,130,246,0.2)",  "#60A5FA", "Em Análise"),
        "em andamento": ("rgba(242,101,34,0.2)",  "#F26522", "Em Andamento"),
        "pronto":       ("rgba(34,197,94,0.2)",   "#4ADE80", "Pronto"),
        "entregue":     ("rgba(100,116,139,0.2)", "#94A3B8", "Entregue"),
    }
    key = (status or "").lower()
    fundo, cor, label = mapa.get(key, ("rgba(100,116,139,0.2)", "#94A3B8", status or "—"))
    return Badge(label, fundo, cor)


def _badge_prioridade(prioridade: str) -> Badge:
    key = (prioridade or "").lower()
    if key in ("urgente", "alta"):
        return Badge(prioridade.capitalize(), "rgba(239,68,68,0.2)", "#F87171")
    return Badge("Normal", "rgba(100,116,139,0.2)", "#94A3B8")


def _tempo_relativo(data_str: str) -> str:
    try:
        dt = datetime.fromisoformat(data_str)
        delta = datetime.now() - dt
        d = delta.days
        if d == 0:
            return "Hoje"
        if d == 1:
            return "Ontem"
        if d < 7:
            return f"{d} dias atrás"
        if d < 30:
            return f"{d // 7} sem. atrás"
        return f"{d // 30} mês(es) atrás"
    except Exception:
        return data_str or "—"


# ──────────────────────────────────────────────
# CARD DE OS
# ──────────────────────────────────────────────

ESTAGIOS = ["aberta", "em análise", "em andamento", "pronto"]
ESTAGIO_LABELS = {
    "aberta": "Pendente",
    "em análise": "Em Análise",
    "em andamento": "Em Andamento",
    "pronto": "Pronto",
}


class OSCard(QFrame):
    def __init__(self, ordem: dict, on_status_changed, on_checkout,
                 on_imprimir, on_whatsapp, on_editar, on_cancelar, on_apagar):
        super().__init__()
        self._ordem = ordem
        self._on_status_changed = on_status_changed
        self._on_checkout = on_checkout
        self._on_imprimir = on_imprimir
        self._on_whatsapp = on_whatsapp
        self._on_editar = on_editar
        self._on_cancelar = on_cancelar
        self._on_apagar = on_apagar

        self.setObjectName("os_card")
        self.setFixedWidth(340)

        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(20, 20, 20, 20)
        self._layout.setSpacing(12)

        self._build()

    def _build(self):
        ordem = self._ordem

        # ─ Header ─
        header = QHBoxLayout()
        lbl_icon = QLabel()
        lbl_icon.setObjectName("icone_card")
        if _SVG_OK:
            lbl_icon.setPixmap(svg_para_pixmap("fi-sr-smartphone.svg", "#F26522", 20, 20))
        else:
            lbl_icon.setText("📱")

        info = QVBoxLayout()
        info.setSpacing(2)
        lbl_nome = QLabel(ordem.get("cliente_nome") or "Balcão")
        lbl_nome.setObjectName("txt_branca_bold")
        modelo = ordem.get("modelo", "—")
        cor = (ordem.get("cor") or "").strip()
        texto_modelo = f"{modelo} • {cor}" if cor else modelo
        lbl_modelo = QLabel(texto_modelo)
        lbl_modelo.setObjectName("txt_cinza")
        info.addWidget(lbl_nome)
        info.addWidget(lbl_modelo)

        header.addWidget(lbl_icon)
        header.addLayout(info)
        header.addItem(QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        lbl_id = QLabel(f"#{ordem['id']}")
        lbl_id.setObjectName("txt_cinza")
        header.addWidget(lbl_id)

        self.btn_menu = QPushButton("⋮")
        self.btn_menu.setObjectName("btn_menu_card")
        self.btn_menu.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_menu.setFixedWidth(28)
        self.btn_menu.clicked.connect(self._abrir_menu_acoes)
        header.addWidget(self.btn_menu)

        self._layout.addLayout(header)

        # ─ Badges ─
        badges = QHBoxLayout()
        badges.setAlignment(Qt.AlignmentFlag.AlignLeft)
        badges.addWidget(_badge_status(ordem.get("status", "")))
        badges.addWidget(_badge_prioridade(ordem.get("prioridade", "")))
        self._layout.addLayout(badges)

        # ─ Meta ─
        meta = QHBoxLayout()
        lbl_data = QLabel(f"🕒 {_tempo_relativo(ordem.get('data_cadastro', ''))}")
        lbl_data.setObjectName("txt_cinza_pequeno")
        lbl_tec = QLabel(f"🔧 {ordem.get('tecnico_nome') or 'Sem técnico'}")
        lbl_tec.setObjectName("txt_cinza_pequeno")
        meta.addWidget(lbl_data)
        meta.addWidget(lbl_tec)
        meta.addItem(QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self._layout.addLayout(meta)

        # ─ Relato ─
        relato = (ordem.get("relato") or "").strip()
        if relato:
            lbl_relato_titulo = QLabel("Defeito:")
            lbl_relato_titulo.setObjectName("txt_cinza_pequeno")
            lbl_relato = QLabel(relato[:80] + ("…" if len(relato) > 80 else ""))
            lbl_relato.setObjectName("txt_branca")
            lbl_relato.setWordWrap(True)
            self._layout.addWidget(lbl_relato_titulo)
            self._layout.addWidget(lbl_relato)

        # ─ Serviços ─
        servicos = ordem.get("servicos", [])
        if servicos:
            lbl_sv_titulo = QLabel("Serviços:")
            lbl_sv_titulo.setObjectName("txt_cinza_pequeno")
            self._layout.addWidget(lbl_sv_titulo)
            for sv in servicos:
                linha_sv = QHBoxLayout()
                lbl_sv_nome = QLabel(sv.get("nome", "—"))
                lbl_sv_nome.setObjectName("txt_branca")
                lbl_sv_nome.setWordWrap(True)
                lbl_sv_preco = QLabel(f"R$ {float(sv.get('preco') or 0):.2f}")
                lbl_sv_preco.setObjectName("txt_laranja")
                linha_sv.addWidget(lbl_sv_nome)
                linha_sv.addItem(QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
                linha_sv.addWidget(lbl_sv_preco)
                self._layout.addLayout(linha_sv)

        # ─ Total ─
        total = float(ordem.get("total_servicos") or 0)
        total_row = QHBoxLayout()
        lbl_total_t = QLabel("Total")
        lbl_total_t.setObjectName("txt_branca_bold")
        lbl_total_v = QLabel(f"R$ {total:.2f}")
        lbl_total_v.setObjectName("txt_laranja_bold")
        total_row.addWidget(lbl_total_t)
        total_row.addWidget(lbl_total_v)
        total_row.addItem(QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self._layout.addLayout(total_row)

        # ─ Botões de estágio ─
        estagios_layout = QHBoxLayout()
        estagios_layout.setSpacing(4)
        status_atual = (ordem.get("status") or "").lower()
        for est in ESTAGIOS:
            label = ESTAGIO_LABELS[est]
            btn = QPushButton(label)
            btn.setObjectName("btn_estagio_ativo" if est == status_atual else "btn_estagio")
            btn.setCursor(Qt.CursorShape.PointingHandCursor)
            btn.clicked.connect(lambda _, e=est: self._on_status_changed(ordem["id"], e))
            estagios_layout.addWidget(btn)
        self._layout.addLayout(estagios_layout)

        # ─ Checkout ─
        if status_atual == "pronto":
            btn_checkout = QPushButton("✓ Entregar / Checkout")
            btn_checkout.setObjectName("btn_primario")
            btn_checkout.setCursor(Qt.CursorShape.PointingHandCursor)
            btn_checkout.clicked.connect(lambda: self._on_checkout(ordem["id"]))
            self._layout.addWidget(btn_checkout)
            self.setStyleSheet("QFrame#os_card { border: 1px solid #F26522; }")

    def _abrir_menu_acoes(self):
        menu = QMenu(self)
        menu.setObjectName("menu_card")

        acao_imprimir  = QAction("🖨  Imprimir", self)
        acao_whatsapp  = QAction("💬  Chamar no WhatsApp", self)
        acao_editar    = QAction("✏  Editar", self)
        acao_cancelar  = QAction("✕  Cancelar OS", self)
        acao_apagar    = QAction("🗑  Apagar OS", self)

        acao_imprimir.triggered.connect(lambda: self._on_imprimir(self._ordem))
        acao_whatsapp.triggered.connect(lambda: self._on_whatsapp(self._ordem))
        acao_editar.triggered.connect(lambda: self._on_editar(self._ordem))
        acao_cancelar.triggered.connect(lambda: self._on_cancelar(self._ordem))
        acao_apagar.triggered.connect(lambda: self._on_apagar(self._ordem))

        menu.addAction(acao_imprimir)
        menu.addAction(acao_whatsapp)
        menu.addSeparator()
        menu.addAction(acao_editar)
        menu.addAction(acao_cancelar)
        menu.addSeparator()
        menu.addAction(acao_apagar)

        menu.exec(self.btn_menu.mapToGlobal(self.btn_menu.rect().bottomLeft()))


# ──────────────────────────────────────────────
# TELA PRINCIPAL
# ──────────────────────────────────────────────

class LaboratorioScreen(QWidget):
    def __init__(self):
        super().__init__()
        db.inicializar_estado()
        self._janela_nova_os = None
        self.initUI()

    def initUI(self):
        self.setMinimumSize(900, 700)

        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(20)

        # ─ Cabeçalho ─
        header = QHBoxLayout()
        titulos = QVBoxLayout()
        titulos.setSpacing(0)
        lbl_titulo = QLabel("Laboratório")
        lbl_titulo.setObjectName("title_main")
        lbl_sub = QLabel("Gestão de Ordens de Serviço")
        lbl_sub.setObjectName("subtitle")
        titulos.addWidget(lbl_titulo)
        titulos.addWidget(lbl_sub)

        btn_nova_os = QPushButton("+ Nova OS")
        btn_nova_os.setObjectName("btn_primario")
        btn_nova_os.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_nova_os.clicked.connect(self._abrir_nova_os)

        header.addLayout(titulos)
        header.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        header.addWidget(btn_nova_os)
        main_layout.addLayout(header)

        # ─ Filtros ─
        filtros = QHBoxLayout()
        filtros.setSpacing(15)
        self.edit_busca = QLineEdit()
        self.edit_busca.setPlaceholderText("🔍 Buscar por cliente, modelo ou ID...")
        self.edit_busca.textChanged.connect(self._carregar_ordens)

        self.cmb_status = QComboBox()
        self.cmb_status.addItems([
            "Todos os Status", "aberta", "em análise", "em andamento", "pronto", "entregue"
        ])
        self.cmb_status.setFixedWidth(190)
        self.cmb_status.currentIndexChanged.connect(self._carregar_ordens)

        filtros.addWidget(self.edit_busca)
        filtros.addWidget(self.cmb_status)
        main_layout.addLayout(filtros)

        # ─ Scroll + grid ─
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setObjectName("scroll_area")

        self.scroll_content = QWidget()
        self.scroll_content.setObjectName("scroll_content")

        self.grid_cards = QGridLayout(self.scroll_content)
        self.grid_cards.setSpacing(20)
        self.grid_cards.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)

        self.scroll_area.setWidget(self.scroll_content)
        main_layout.addWidget(self.scroll_area)

        self.aplicar_estilos()
        self._carregar_ordens()

    # ─ Lógica ──────────────────────────────────

    def _carregar_ordens(self):
        for i in reversed(range(self.grid_cards.count())):
            w = self.grid_cards.itemAt(i).widget()
            if w:
                w.deleteLater()

        filtro = self.edit_busca.text().strip()
        status = self.cmb_status.currentText()
        if status == "Todos os Status":
            status = None

        ordens = db.listar_ordens_servico(filtro=filtro, status=status)

        if not ordens:
            lbl = QLabel("Nenhuma OS encontrada.")
            lbl.setObjectName("subtitle")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_cards.addWidget(lbl, 0, 0)
            return

        row, col = 0, 0
        for ordem in ordens:
            card = OSCard(
                ordem,
                self._mudar_status,
                self._checkout,
                self._imprimir_os,
                self._chamar_whatsapp,
                self._editar_os,
                self._cancelar_os,
                self._apagar_os,
            )
            self.grid_cards.addWidget(card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

    def _mudar_status(self, ordem_id: int, novo_status: str):
        db.atualizar_status_ordem(ordem_id, novo_status)
        self._carregar_ordens()

    def _checkout(self, ordem_id: int):
        # Busca a ordem completa (com servicos) para passar ao dialog
        ordens = db.listar_ordens_servico(filtro=str(ordem_id))
        ordem = next((o for o in ordens if o["id"] == ordem_id), None)
        if not ordem:
            QMessageBox.critical(self, "Erro", f"OS #{ordem_id} não encontrada.")
            return

        dlg = NovaEntregaWindow(ordem)
        dlg.accepted.connect(self._carregar_ordens)
        dlg.exec()

    def _abrir_nova_os(self):
        self._janela_nova_os = NovaOrdemServicoWindow()
        self._janela_nova_os.accepted.connect(self._carregar_ordens)
        self._janela_nova_os.exec()

    def _imprimir_os(self, ordem: dict):
        try:
            from component.notas import imprimir_os
            imprimir_os(ordem["id"])
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao imprimir OS:\n{e}")

    def _chamar_whatsapp(self, ordem: dict):
        try:
            from component.whatsapp import chamar_cliente_whatsapp
            chamar_cliente_whatsapp(ordem["id"])
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao abrir WhatsApp:\n{e}")

    def _editar_os(self, ordem: dict):
        try:
            janela = EditarOrdemServicoWindow(ordem["id"])
            janela.accepted.connect(self._carregar_ordens)
            janela.exec()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao abrir edição da OS:\n{e}")

    def _cancelar_os(self, ordem: dict):
        try:
            from component.novocancelamento import NovoCancelamentoWindow
            dlg = NovoCancelamentoWindow(ordem)
            dlg.accepted.connect(self._carregar_ordens)
            dlg.exec()
        except Exception as e:
            QMessageBox.critical(self, "Erro", f"Falha ao abrir cancelamento:\n{e}")

    def _apagar_os(self, ordem: dict):
        resp = QMessageBox.question(
            self,
            "Apagar OS",
            f"Deseja apagar permanentemente a OS #{ordem['id']}?\n\nEsta ação não pode ser desfeita.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )
        if resp == QMessageBox.StandardButton.Yes:
            try:
                db.excluir_ordem_servico(ordem["id"])
                self._carregar_ordens()
            except Exception as e:
                QMessageBox.critical(self, "Erro", f"Falha ao apagar OS:\n{e}")

    # ─ Estilos ─────────────────────────────────

    def aplicar_estilos(self):
        self.setStyleSheet("""
        QWidget {
            background-color: #0F172A;
            font-family: 'Poppins', 'Montserrat', sans-serif;
        }

        QLabel#title_main { color: #FFFFFF; font-size: 24px; font-weight: 700; }
        QLabel#subtitle   { color: #64748B; font-size: 12px; font-weight: 600; }

        QLabel#txt_branca        { color: #FFFFFF; font-size: 12px; }
        QLabel#txt_branca_bold   { color: #FFFFFF; font-size: 14px; font-weight: 700; }
        QLabel#txt_cinza         { color: #64748B; font-size: 12px; }
        QLabel#txt_cinza_pequeno { color: #64748B; font-size: 11px; font-weight: 600; }
        QLabel#txt_laranja       { color: #F26522; font-size: 12px; font-weight: 600; }
        QLabel#txt_laranja_bold  { color: #F26522; font-size: 14px; font-weight: 700; }

        QLineEdit, QComboBox {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 8px;
            padding: 12px;
            color: #FFFFFF;
            font-size: 13px;
        }
        QLineEdit:focus, QComboBox:focus { border: 1px solid #F26522; }
        QComboBox::drop-down { border: none; }

        QFrame#os_card {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 12px;
        }

        QLabel#icone_card {
            background-color: #1E293B;
            border-radius: 8px;
            padding: 8px;
            font-size: 20px;
        }

        QPushButton#btn_estagio {
            background-color: #1E293B;
            color: #64748B;
            border: none;
            border-radius: 4px;
            padding: 4px 6px;
            font-size: 10px;
            font-weight: 600;
        }
        QPushButton#btn_estagio:hover { background-color: #2c3b52; color: #FFFFFF; }

        QPushButton#btn_estagio_ativo {
            background-color: #0F172A;
            color: #4ADE80;
            border: 1px solid #4ADE80;
            border-radius: 4px;
            padding: 4px 6px;
            font-size: 10px;
            font-weight: 600;
        }

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

        /* Botão 3 pontinhos */
        QPushButton#btn_menu_card {
            background-color: transparent;
            color: #64748B;
            border: none;
            font-size: 18px;
            font-weight: bold;
            padding: 0px 4px;
        }
        QPushButton#btn_menu_card:hover {
            color: #FFFFFF;
            background-color: #1E293B;
            border-radius: 4px;
        }

        /* Menu contextual */
        QMenu#menu_card {
            background-color: #0B1120;
            color: #FFFFFF;
            border: 1px solid #1E293B;
            border-radius: 8px;
            padding: 6px;
        }
        QMenu#menu_card::item {
            background-color: transparent;
            padding: 8px 18px;
            border-radius: 4px;
            font-size: 13px;
        }
        QMenu#menu_card::item:selected {
            background-color: #1E293B;
            color: #F26522;
        }
        QMenu#menu_card::separator {
            height: 1px;
            background: #1E293B;
            margin: 4px 0px;
        }

        QScrollArea#scroll_area { border: none; background-color: transparent; }
        QWidget#scroll_content  { background-color: transparent; }
        QScrollBar:vertical { border: none; background-color: #0B1120; width: 8px; border-radius: 4px; }
        QScrollBar::handle:vertical { background-color: #1E293B; min-height: 20px; border-radius: 4px; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }
        """)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    w = LaboratorioScreen()
    w.show()
    import sys as _sys
    _sys.exit(app.exec())
