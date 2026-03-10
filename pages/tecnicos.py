import sys
import os

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QPushButton, QFrame, QSpacerItem,
    QSizePolicy, QScrollArea, QCheckBox, QMessageBox
)
from PyQt6.QtCore import Qt

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db
from component.novotecnico import NovoTecnicoWindow

try:
    from component.svg_utils import svg_para_pixmap
    _SVG_OK = True
except Exception:
    _SVG_OK = False


# ──────────────────────────────────────────────
# COMPONENTES
# ──────────────────────────────────────────────

class TopStatBox(QFrame):
    def __init__(self, titulo: str, valor, cor_valor: str = "#FFFFFF"):
        super().__init__()
        self.setObjectName("top_stat_box")
        self.setFixedHeight(100)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)

        lbl_titulo = QLabel(titulo)
        lbl_titulo.setObjectName("stat_label")

        self.lbl_valor = QLabel(str(valor))
        self.lbl_valor.setObjectName("stat_valor")
        self.lbl_valor.setStyleSheet(f"color: {cor_valor};")

        layout.addWidget(lbl_titulo)
        layout.addWidget(self.lbl_valor)
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))


class TecnicoCard(QFrame):
    def __init__(self, tecnico: dict, on_excluir):
        super().__init__()
        self.setObjectName("card_tecnico")
        self.setFixedSize(340, 280)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # ─ Cabeçalho: avatar, nome, especialidade, toggle, excluir ─
        header = QHBoxLayout()

        lbl_avatar = QLabel()
        lbl_avatar.setObjectName("avatar_icon")
        lbl_avatar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        if _SVG_OK:
            lbl_avatar.setPixmap(svg_para_pixmap("fi-sr-user.svg", "#F26522", 20, 20))
        else:
            lbl_avatar.setText("👤")
        header.addWidget(lbl_avatar)

        info = QVBoxLayout()
        info.setSpacing(2)
        lbl_nome = QLabel(tecnico.get("nome", ""))
        lbl_nome.setObjectName("tecnico_nome")
        lbl_tag = QLabel(tecnico.get("especialidade", ""))
        lbl_tag.setObjectName("tecnico_tag")
        info.addWidget(lbl_nome)
        info.addWidget(lbl_tag)
        header.addLayout(info)

        header.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))

        chk_ativo = QCheckBox()
        chk_ativo.setObjectName("toggle_switch")
        chk_ativo.setChecked(True)
        chk_ativo.setCursor(Qt.CursorShape.PointingHandCursor)
        header.addWidget(chk_ativo)

        btn_excluir = QPushButton("🗑️")
        btn_excluir.setObjectName("btn_lixeira")
        btn_excluir.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_excluir.clicked.connect(lambda: on_excluir(tecnico["id"]))
        header.addWidget(btn_excluir)

        layout.addLayout(header)

        # ─ Grid de mini-estatísticas ─
        grid_stats = QGridLayout()
        grid_stats.setSpacing(10)

        concluidas = tecnico.get("os_concluidas", 0) or 0
        andamento  = tecnico.get("os_andamento",  0) or 0
        pendentes  = tecnico.get("os_pendentes",  0) or 0
        total      = tecnico.get("os_total",      0) or 0

        self._mini_stat(grid_stats, "✓ Concluídas",   concluidas, "#4ADE80", 0, 0)
        self._mini_stat(grid_stats, "🔧 Em Andamento", andamento,  "#F26522", 0, 1)
        self._mini_stat(grid_stats, "⏱ Pendentes",    pendentes,  "#EAB308", 1, 0)
        self._mini_stat(grid_stats, "👤 Total",        total,      "#FFFFFF", 1, 1)
        layout.addLayout(grid_stats)

        # ─ OS em andamento ─
        lbl_os_titulo = QLabel("OS em andamento")
        lbl_os_titulo.setObjectName("stat_label")
        layout.addWidget(lbl_os_titulo)

        if andamento > 0:
            box_os = QFrame()
            box_os.setObjectName("os_atual_box")
            box_layout = QVBoxLayout(box_os)
            box_layout.setContentsMargins(10, 10, 10, 10)
            lbl_os_val = QLabel(f"{andamento} OS ativa(s)")
            lbl_os_val.setObjectName("os_atual_texto")
            box_layout.addWidget(lbl_os_val)
            layout.addWidget(box_os)
        else:
            layout.addItem(QSpacerItem(20, 36, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Fixed))

    def _mini_stat(self, grid, titulo, valor, cor, row, col):
        box = QFrame()
        box.setObjectName("mini_stat_box")
        bl = QVBoxLayout(box)
        bl.setContentsMargins(10, 10, 10, 10)
        bl.setSpacing(2)
        lbl_t = QLabel(titulo)
        lbl_t.setObjectName("mini_stat_label")
        lbl_v = QLabel(str(valor))
        lbl_v.setObjectName("mini_stat_valor")
        lbl_v.setStyleSheet(f"color: {cor};")
        bl.addWidget(lbl_t)
        bl.addWidget(lbl_v)
        grid.addWidget(box, row, col)


# ──────────────────────────────────────────────
# TELA PRINCIPAL
# ──────────────────────────────────────────────

class TecnicosScreen(QWidget):
    def __init__(self):
        super().__init__()
        db.inicializar_estado()
        self._janela_novo = None
        self.initUI()

    def initUI(self):
        self.setMinimumSize(1000, 700)

        self.main_layout = QVBoxLayout(self)
        self.main_layout.setContentsMargins(40, 40, 40, 40)
        self.main_layout.setSpacing(25)

        # ─ Cabeçalho ─
        header = QHBoxLayout()
        titulos = QVBoxLayout()
        titulos.setSpacing(0)
        lbl_titulo = QLabel("TÉCNICOS")
        lbl_titulo.setObjectName("title_main")
        lbl_sub = QLabel("Gestão da equipe técnica")
        lbl_sub.setObjectName("subtitle")
        titulos.addWidget(lbl_titulo)
        titulos.addWidget(lbl_sub)

        btn_novo = QPushButton("+ Novo Técnico")
        btn_novo.setObjectName("btn_primario")
        btn_novo.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_novo.clicked.connect(self._abrir_novo_tecnico)

        header.addLayout(titulos)
        header.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        header.addWidget(btn_novo)
        self.main_layout.addLayout(header)

        # ─ Stat boxes do topo ─
        stats_row = QHBoxLayout()
        stats_row.setSpacing(15)
        self.box_total     = TopStatBox("Total de Técnicos", 0)
        self.box_ativos    = TopStatBox("Ativos",            0, "#4ADE80")
        self.box_andamento = TopStatBox("OS em Andamento",   0, "#F26522")
        self.box_concl     = TopStatBox("Concluídas (total)",0)
        for b in (self.box_total, self.box_ativos, self.box_andamento, self.box_concl):
            stats_row.addWidget(b)
        self.main_layout.addLayout(stats_row)

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
        self.main_layout.addWidget(self.scroll_area)

        self.aplicar_estilos()
        self._carregar_tecnicos()

    # ─ Lógica ─────────────────────────────────

    def _carregar_tecnicos(self):
        for i in reversed(range(self.grid_cards.count())):
            w = self.grid_cards.itemAt(i).widget()
            if w:
                w.deleteLater()

        tecnicos = db.listar_tecnicos()

        # Atualiza stat boxes
        total     = len(tecnicos)
        andamento = sum(t.get("os_andamento", 0) or 0 for t in tecnicos)
        concl     = sum(t.get("os_concluidas", 0) or 0 for t in tecnicos)

        self.box_total.lbl_valor.setText(str(total))
        self.box_ativos.lbl_valor.setText(str(total))   # todos ativos por enquanto
        self.box_andamento.lbl_valor.setText(str(andamento))
        self.box_concl.lbl_valor.setText(str(concl))

        if not tecnicos:
            lbl = QLabel("Nenhum técnico cadastrado.")
            lbl.setObjectName("subtitle")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_cards.addWidget(lbl, 0, 0)
            return

        row, col = 0, 0
        for t in tecnicos:
            card = TecnicoCard(t, self._excluir_tecnico)
            self.grid_cards.addWidget(card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

    def _abrir_novo_tecnico(self):
        self._janela_novo = NovoTecnicoWindow()
        original_salvar = self._janela_novo.salvar_tecnico
        def salvar_e_atualizar():
            original_salvar()
            self._carregar_tecnicos()
        self._janela_novo.btn_cadastrar.clicked.disconnect()
        self._janela_novo.btn_cadastrar.clicked.connect(salvar_e_atualizar)
        self._janela_novo.show()

    def _excluir_tecnico(self, tecnico_id: int):
        resp = QMessageBox.question(
            self, "Confirmar exclusão",
            "Deseja excluir este técnico?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if resp == QMessageBox.StandardButton.Yes:
            sucesso = db.excluir_tecnico(tecnico_id)
            if not sucesso:
                QMessageBox.warning(
                    self,
                    "Atenção",
                    "Não é possível excluir este técnico pois ele possui Ordens de Serviço vinculadas."
                )
            self._carregar_tecnicos()

    # ─ Estilos ────────────────────────────────

    def aplicar_estilos(self):
        self.setStyleSheet("""
        QWidget {
            background-color: #0F172A;
            font-family: 'Poppins', 'Montserrat', sans-serif;
        }

        QLabel#title_main { color: #FFFFFF; font-size: 24px; font-weight: 700; }
        QLabel#subtitle   { color: #64748B; font-size: 12px; font-weight: 600; }

        QPushButton#btn_primario {
            background-color: #F26522; color: #FFFFFF;
            font-size: 14px; font-weight: 600;
            border-radius: 6px; padding: 10px 20px; border: none;
        }
        QPushButton#btn_primario:hover { background-color: #E05412; }

        /* Stat boxes topo */
        QFrame#top_stat_box {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 10px;
        }
        QLabel#stat_label { color: #64748B; font-size: 12px; font-weight: 600; }
        QLabel#stat_valor { font-size: 24px; font-weight: 700; }

        /* Scroll */
        QScrollArea#scroll_area { border: none; background-color: transparent; }
        QWidget#scroll_content  { background-color: transparent; }
        QScrollBar:vertical { border: none; background-color: #0B1120; width: 8px; border-radius: 4px; }
        QScrollBar::handle:vertical { background-color: #1E293B; min-height: 20px; border-radius: 4px; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }

        /* Card */
        QFrame#card_tecnico {
            background-color: #0B1120;
            border: 1px solid #1E293B;
            border-radius: 12px;
        }

        QLabel#avatar_icon {
            background-color: rgba(242,101,34,0.1);
            color: #F26522;
            border-radius: 20px;
            min-width: 40px; min-height: 40px;
            max-width: 40px; max-height: 40px;
            font-size: 18px;
        }

        QLabel#tecnico_nome { color: #FFFFFF; font-size: 15px; font-weight: 700; }
        QLabel#tecnico_tag {
            border: 1px solid #F26522; color: #F26522;
            font-size: 10px; font-weight: 600;
            padding: 2px 8px; border-radius: 8px;
        }

        /* Mini stats */
        QFrame#mini_stat_box {
            background-color: #0F172A;
            border-radius: 8px;
        }
        QLabel#mini_stat_label { color: #64748B; font-size: 10px; font-weight: 600; }
        QLabel#mini_stat_valor { font-size: 16px; font-weight: 700; }

        /* OS em andamento */
        QFrame#os_atual_box {
            background-color: #0F172A;
            border: 1px solid #1E293B;
            border-radius: 6px;
        }
        QLabel#os_atual_texto { color: #FFFFFF; font-size: 12px; font-weight: 600; }

        /* Botão lixeira */
        QPushButton#btn_lixeira {
            background-color: transparent;
            color: #64748B; border: none; font-size: 14px;
        }
        QPushButton#btn_lixeira:hover { color: #EF4444; }

        /* Toggle switch */
        QCheckBox#toggle_switch::indicator {
            width: 36px; height: 20px;
            border-radius: 10px;
            background-color: #0F172A;
            border: 2px solid #1E293B;
        }
        QCheckBox#toggle_switch::indicator:checked {
            background-color: #F26522;
            border: 2px solid #F26522;
        }
        """)
