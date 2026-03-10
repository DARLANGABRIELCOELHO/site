# base_dialog.py — Base classes para janelas modernas sem barra nativa
#
# ModernDialog  → herda de QDialog  (usar com .exec())
# ModernWindow  → herda de QWidget  (usar com .show())
#
# Ambas oferecem:
#   • Frameless + fundo translúcido
#   • QFrame interno arredondado com sombra visual
#   • Header customizado (título + botão ✕) arrastável
#   • self.content_layout  — adicione seus widgets aqui
# ─────────────────────────────────────────────────────────────
import sys
import os

from PyQt6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QFrame, QSpacerItem, QSizePolicy,
    QGraphicsDropShadowEffect,
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QColor

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


# ────────────────────────────────────────────────────────────
# CSS compartilhado para o chrome (frame + header)
# ────────────────────────────────────────────────────────────
_CHROME_CSS = """
    QWidget {
        font-family: 'Poppins', 'Montserrat', sans-serif;
        color: #FFFFFF;
    }
    QFrame#modal_card {
        background-color: #0F172A;
        border: 1px solid #1E293B;
        border-radius: 16px;
    }
    QFrame#modal_header {
        background-color: transparent;
        border-bottom: 1px solid #1E293B;
        border-top-left-radius: 16px;
        border-top-right-radius: 16px;
    }
    QLabel#modal_titulo {
        color: #FFFFFF;
        font-size: 15px;
        font-weight: 700;
    }
    QPushButton#modal_btn_fechar {
        background-color: transparent;
        color: #64748B;
        border: none;
        border-radius: 6px;
        font-size: 14px;
        font-weight: 700;
        padding: 0px;
    }
    QPushButton#modal_btn_fechar:hover {
        background-color: rgba(239,68,68,0.15);
        color: #EF4444;
    }
"""


# ────────────────────────────────────────────────────────────
# Mixin com drag + estrutura interna
# ────────────────────────────────────────────────────────────
class _FramelessMixin:
    """
    Mixin que injeta o comportamento frameless em QDialog ou QWidget.
    Deve ser o primeiro pai na herança MRO.
    """

    def _setup_frameless(self, titulo: str, largura: int, altura: int, close_fn):
        """
        Configura a estrutura visual. Chame no __init__ do filho ANTES de
        construir o conteúdo.
        """
        SHADOW = 16   # espaço extra em cada lado para a sombra

        # ── flags do sistema ────────────────────────────────
        self.setWindowFlags(
            Qt.WindowType.Dialog
            | Qt.WindowType.FramelessWindowHint
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground, True)
        self.setFixedSize(largura + SHADOW * 2, altura + SHADOW * 2)

        self._drag_pos: QPoint | None = None

        # ── layout externo (transparente — espaço para sombra) ──
        outer = QVBoxLayout(self)
        outer.setContentsMargins(SHADOW, SHADOW, SHADOW, SHADOW)
        outer.setSpacing(0)

        # ── card interno ────────────────────────────────────
        self._card = QFrame()
        self._card.setObjectName("modal_card")
        outer.addWidget(self._card)

        # sombra suave
        shadow = QGraphicsDropShadowEffect(self._card)
        shadow.setBlurRadius(30)
        shadow.setOffset(0, 4)
        shadow.setColor(QColor(0, 0, 0, 160))
        self._card.setGraphicsEffect(shadow)

        card_layout = QVBoxLayout(self._card)
        card_layout.setContentsMargins(0, 0, 0, 0)
        card_layout.setSpacing(0)

        # ── header arrastável ────────────────────────────────
        self._header = QFrame()
        self._header.setObjectName("modal_header")
        self._header.setFixedHeight(52)
        self._header.setCursor(Qt.CursorShape.SizeAllCursor)

        header_h = QHBoxLayout(self._header)
        header_h.setContentsMargins(22, 0, 12, 0)
        header_h.setSpacing(8)

        self._lbl_titulo = QLabel(titulo)
        self._lbl_titulo.setObjectName("modal_titulo")
        header_h.addWidget(self._lbl_titulo)
        header_h.addItem(
            QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        )

        btn_x = QPushButton("✕")
        btn_x.setObjectName("modal_btn_fechar")
        btn_x.setFixedSize(30, 30)
        btn_x.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_x.clicked.connect(close_fn)
        header_h.addWidget(btn_x)

        card_layout.addWidget(self._header)

        # ── área de conteúdo ─────────────────────────────────
        self.content_layout = QVBoxLayout()
        self.content_layout.setContentsMargins(24, 18, 24, 22)
        self.content_layout.setSpacing(12)
        card_layout.addLayout(self.content_layout)

        # ── estilos chrome ───────────────────────────────────
        self.setStyleSheet(_CHROME_CSS)

    # ── drag handling ────────────────────────────────────────
    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._drag_pos = (
                event.globalPosition().toPoint() - self.frameGeometry().topLeft()
            )
            event.accept()

    def mouseMoveEvent(self, event):
        if self._drag_pos is not None and (
            event.buttons() & Qt.MouseButton.LeftButton
        ):
            self.move(event.globalPosition().toPoint() - self._drag_pos)
            event.accept()

    def mouseReleaseEvent(self, event):
        self._drag_pos = None
        event.accept()


# ────────────────────────────────────────────────────────────
# ModernDialog  (QDialog — modal, use .exec())
# ────────────────────────────────────────────────────────────
class ModernDialog(_FramelessMixin, QDialog):
    """
    Base para janelas modais.

    Exemplo de uso:
        class MeuDialog(ModernDialog):
            def __init__(self):
                super().__init__("Título", 520, 480)
                # adicione widgets em self.content_layout
    """

    def __init__(self, titulo: str, largura: int, altura: int, parent=None):
        QDialog.__init__(self, parent)
        self._setup_frameless(titulo, largura, altura, close_fn=self.reject)


# ────────────────────────────────────────────────────────────
# ModernWindow  (QWidget — não-modal, use .show())
# ────────────────────────────────────────────────────────────
class ModernWindow(_FramelessMixin, QWidget):
    """
    Base para janelas não-modais (cadastros abertos com .show()).

    Exemplo de uso:
        class NovoClienteWindow(ModernWindow):
            def __init__(self):
                super().__init__("Novo Cliente", 650, 680)
    """

    def __init__(self, titulo: str, largura: int, altura: int, parent=None):
        QWidget.__init__(self, parent)
        self._setup_frameless(titulo, largura, altura, close_fn=self.close)
