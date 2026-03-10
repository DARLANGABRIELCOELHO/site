"""
svg_utils.py — Utilitário compartilhado para renderizar SVGs coloridos como QPixmap.

Uso:
    from component.svg_utils import svg_para_pixmap
    pixmap = svg_para_pixmap("fi-sr-dashboard.svg", "#F26522", 20, 20)
"""
import os
from PyQt6.QtCore import Qt, QByteArray
from PyQt6.QtGui import QPixmap, QPainter
from PyQt6.QtSvg import QSvgRenderer

_SVG_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "svg")


def svg_para_pixmap(nome_arquivo: str, cor: str, largura: int = 20, altura: int = 20) -> QPixmap:
    """
    Lê um arquivo SVG, aplica a cor e devolve um QPixmap pronto para uso.

    - nome_arquivo : nome do arquivo dentro da pasta svg/ (ex: "fi-sr-dashboard.svg")
    - cor          : cor hexadecimal (ex: "#F26522") ou RGB CSS
    - largura/altura: dimensões do pixmap de saída em pixels
    """
    caminho = os.path.join(_SVG_DIR, nome_arquivo)
    try:
        with open(caminho, "r", encoding="utf-8") as f:
            svg = f.read()
    except FileNotFoundError:
        pixmap = QPixmap(largura, altura)
        pixmap.fill(Qt.GlobalColor.transparent)
        return pixmap

    # Troca currentColor e injeta fill no elemento raiz <svg>
    svg = svg.replace("currentColor", cor)
    if 'fill="' not in svg:
        svg = svg.replace("<svg ", f'<svg fill="{cor}" ', 1)

    renderer = QSvgRenderer(QByteArray(svg.encode("utf-8")))
    pixmap = QPixmap(largura, altura)
    pixmap.fill(Qt.GlobalColor.transparent)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.end()
    return pixmap
