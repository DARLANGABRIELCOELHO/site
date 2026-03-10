# vendas.py — PDV / Balcão
import os
import sys
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QLineEdit, QPushButton, QFrame, QSpacerItem, QSizePolicy,
    QScrollArea, QComboBox, QMessageBox
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QAction

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import data.database as db
from component.novavenda import FinalizarVendaDialog

try:
    from component.svg_utils import svg_para_pixmap
    _SVG_OK = True
except Exception:
    _SVG_OK = False


# ──────────────────────────────────────────────
# CartItem — linha do carrinho
# ──────────────────────────────────────────────

class CartItem(QFrame):
    def __init__(self, item: dict, on_mais, on_menos, on_remover):
        super().__init__()
        self.setObjectName("cart_item")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 5, 0, 5)

        info = QVBoxLayout()
        info.setSpacing(2)
        lbl_nome = QLabel(item["nome"])
        lbl_nome.setObjectName("cart_item_nome")
        lbl_preco = QLabel(f"R$ {float(item['preco']):.2f} un")
        lbl_preco.setObjectName("cart_item_preco")
        info.addWidget(lbl_nome)
        info.addWidget(lbl_preco)

        ctrl = QHBoxLayout()
        ctrl.setSpacing(8)

        btn_menos = QPushButton("-")
        btn_menos.setObjectName("btn_icon_pequeno")
        btn_menos.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_menos.setFixedSize(24, 24)
        btn_menos.clicked.connect(on_menos)

        lbl_qtd = QLabel(str(item["qtd"]))
        lbl_qtd.setObjectName("cart_item_qtd")
        lbl_qtd.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_qtd.setFixedWidth(24)

        btn_mais = QPushButton("+")
        btn_mais.setObjectName("btn_icon_pequeno")
        btn_mais.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_mais.setFixedSize(24, 24)
        btn_mais.clicked.connect(on_mais)

        btn_del = QPushButton("🗑")
        btn_del.setObjectName("btn_lixeira")
        btn_del.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_del.setFixedSize(24, 24)
        btn_del.clicked.connect(on_remover)

        ctrl.addWidget(btn_menos)
        ctrl.addWidget(lbl_qtd)
        ctrl.addWidget(btn_mais)
        ctrl.addWidget(btn_del)

        layout.addLayout(info)
        layout.addItem(QSpacerItem(10, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        layout.addLayout(ctrl)


# ──────────────────────────────────────────────
# ProdutoCard — card clicável
# ──────────────────────────────────────────────

class ProdutoCard(QPushButton):
    def __init__(self, produto: dict, on_add):
        super().__init__()
        self._produto = produto
        self._on_add  = on_add

        no_carrinho = produto.get("_no_carrinho", False)
        alerta = int(produto.get("estoque") or 0) <= int(produto.get("estoque_minimo") or 0)

        self.setObjectName("card_produto_ativo" if no_carrinho else "card_produto")
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setFixedSize(220, 150)
        self.clicked.connect(self._adicionar)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(5)

        header = QHBoxLayout()
        lbl_icon = QLabel()
        lbl_icon.setObjectName("icone_box")
        cor_box = "#F26522" if no_carrinho else "#8a8f98"
        if _SVG_OK:
            lbl_icon.setPixmap(svg_para_pixmap("fi-sr-box.svg", cor_box, 16, 16))
        else:
            lbl_icon.setText("📦")
        header.addWidget(lbl_icon)
        header.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        if alerta:
            lbl_alerta = QLabel()
            lbl_alerta.setObjectName("icone_alerta")
            if _SVG_OK:
                lbl_alerta.setPixmap(svg_para_pixmap("fi-sr-triangle-warning.svg", "#EAB308", 14, 14))
            else:
                lbl_alerta.setText("⚠️")
            header.addWidget(lbl_alerta)
        layout.addLayout(header)

        lbl_nome = QLabel(produto.get("nome", "—"))
        lbl_nome.setObjectName("produto_nome")
        lbl_nome.setWordWrap(True)
        lbl_nome.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        preco = float(produto.get("preco") or 0)
        lbl_preco = QLabel(f"R$ {preco:.2f}")
        lbl_preco.setObjectName("produto_preco")
        lbl_preco.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        estoque = int(produto.get("estoque") or 0)
        lbl_estoque = QLabel(f"{estoque} un")
        lbl_estoque.setObjectName("produto_estoque_alerta" if alerta else "produto_estoque")
        lbl_estoque.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)

        layout.addWidget(lbl_nome)
        layout.addWidget(lbl_preco)
        layout.addWidget(lbl_estoque)

        if no_carrinho:
            qtd = produto.get("_qtd_carrinho", 1)
            lbl_tag = QLabel(f"{qtd}x no carrinho")
            lbl_tag.setObjectName("tag_no_carrinho")
            lbl_tag.setAlignment(Qt.AlignmentFlag.AlignCenter)
            lbl_tag.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
            layout.addWidget(lbl_tag)
        else:
            layout.addItem(QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))

    def _adicionar(self):
        self._on_add(self._produto)


# ──────────────────────────────────────────────
# Tela principal
# ──────────────────────────────────────────────

class VendasScreen(QWidget):
    def __init__(self):
        super().__init__()
        db.inicializar_estado()
        self.carrinho_itens: list[dict] = []
        self.initUI()

    def initUI(self):
        self.setMinimumSize(1000, 700)

        main_layout = QHBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # ── Painel esquerdo ───────────────────────
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(0, 0, 0, 0)
        left_layout.setSpacing(15)

        header = QHBoxLayout()
        titulos = QVBoxLayout()
        titulos.setSpacing(0)
        lbl_titulo = QLabel("VENDAS")
        lbl_titulo.setObjectName("title_main")
        lbl_sub = QLabel("PDV / Balcão")
        lbl_sub.setObjectName("subtitle")
        titulos.addWidget(lbl_titulo)
        titulos.addWidget(lbl_sub)

        self.btn_finalizar_topo = QPushButton("Finalizar (0)")
        if _SVG_OK:
            self.btn_finalizar_topo.setIcon(QIcon(svg_para_pixmap("fi-sr-shopping-cart.svg", "#FFFFFF", 16, 16)))
            self.btn_finalizar_topo.setIconSize(QSize(16, 16))
        else:
            self.btn_finalizar_topo.setText("🛒 Finalizar (0)")
        self.btn_finalizar_topo.setObjectName("btn_primario")
        self.btn_finalizar_topo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_finalizar_topo.clicked.connect(self._finalizar_venda)

        header.addLayout(titulos)
        header.addItem(QSpacerItem(40, 20, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        header.addWidget(self.btn_finalizar_topo)
        left_layout.addLayout(header)

        self.edit_busca = QLineEdit()
        self.edit_busca.setPlaceholderText("Buscar produto...")
        if _SVG_OK:
            search_action = QAction(
                QIcon(svg_para_pixmap("fi-sr-search.svg", "#64748B", 16, 16)), "",
                self.edit_busca
            )
            self.edit_busca.addAction(search_action, QLineEdit.ActionPosition.LeadingPosition)
        self.edit_busca.textChanged.connect(self._carregar_produtos)
        left_layout.addWidget(self.edit_busca)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setObjectName("scroll_area")
        scroll_content = QWidget()
        scroll_content.setObjectName("scroll_content")
        self.grid_produtos = QGridLayout(scroll_content)
        self.grid_produtos.setSpacing(15)
        self.grid_produtos.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft)
        scroll_area.setWidget(scroll_content)
        left_layout.addWidget(scroll_area)
        main_layout.addWidget(left_panel, stretch=7)

        # ── Painel direito (carrinho) ─────────────
        self.cart_frame = QFrame()
        self.cart_frame.setObjectName("cart_frame")
        self.cart_frame.setFixedWidth(340)
        self.cart_layout = QVBoxLayout(self.cart_frame)
        self.cart_layout.setContentsMargins(20, 20, 20, 20)

        # Título do carrinho com SVG
        cart_titulo_row = QHBoxLayout()
        cart_titulo_row.setSpacing(8)
        cart_titulo_row.setContentsMargins(0, 0, 0, 0)
        if _SVG_OK:
            ico_cart = QLabel()
            ico_cart.setPixmap(svg_para_pixmap("fi-sr-shopping-cart.svg", "#F26522", 18, 18))
            cart_titulo_row.addWidget(ico_cart)
        lbl_carrinho_titulo = QLabel("Carrinho")
        lbl_carrinho_titulo.setObjectName("txt_branca_bold")
        cart_titulo_row.addWidget(lbl_carrinho_titulo)
        cart_titulo_row.addItem(QSpacerItem(10, 10, QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum))
        self.cart_layout.addLayout(cart_titulo_row)
        self.cart_layout.addSpacing(10)

        self.cart_items_area = QVBoxLayout()
        self.cart_items_area.setSpacing(10)
        self.cart_layout.addLayout(self.cart_items_area)

        self.cart_spacer = QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.cart_layout.addItem(self.cart_spacer)

        self.linha_divisoria = QFrame()
        self.linha_divisoria.setFrameShape(QFrame.Shape.HLine)
        self.linha_divisoria.setObjectName("linha_divisoria")
        self.linha_divisoria.setVisible(False)
        self.cart_layout.addWidget(self.linha_divisoria)

        total_row = QHBoxLayout()
        self.lbl_total_txt = QLabel("Total")
        self.lbl_total_txt.setObjectName("txt_branca_16")
        self.lbl_total_val = QLabel("R$ 0,00")
        self.lbl_total_val.setObjectName("txt_laranja_20")
        self.lbl_total_val.setAlignment(Qt.AlignmentFlag.AlignRight)
        total_row.addWidget(self.lbl_total_txt)
        total_row.addWidget(self.lbl_total_val)
        self.cart_layout.addLayout(total_row)
        self.lbl_total_txt.setVisible(False)
        self.lbl_total_val.setVisible(False)

        self.btn_finalizar = QPushButton("Finalizar Venda")
        if _SVG_OK:
            self.btn_finalizar.setIcon(QIcon(svg_para_pixmap("fi-sr-check.svg", "#FFFFFF", 16, 16)))
            self.btn_finalizar.setIconSize(QSize(16, 16))
        else:
            self.btn_finalizar.setText("✓ Finalizar Venda")
        self.btn_finalizar.setObjectName("btn_primario")
        self.btn_finalizar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_finalizar.setFixedHeight(45)
        self.btn_finalizar.setVisible(False)
        self.btn_finalizar.clicked.connect(self._finalizar_venda)
        self.cart_layout.addWidget(self.btn_finalizar)

        main_layout.addWidget(self.cart_frame, stretch=3)

        self.aplicar_estilos()
        self._carregar_produtos()

    # ── Produtos ────────────────────────────────

    def _carregar_produtos(self):
        filtro = self.edit_busca.text().strip()
        try:
            produtos = db.listar_produtos(filtro)
        except Exception:
            produtos = []

        # Marca quais estão no carrinho
        ids_carrinho = {i["id"]: i["qtd"] for i in self.carrinho_itens}
        for p in produtos:
            p["_no_carrinho"] = p["id"] in ids_carrinho
            p["_qtd_carrinho"] = ids_carrinho.get(p["id"], 0)

        # Limpa grid
        for i in reversed(range(self.grid_produtos.count())):
            w = self.grid_produtos.itemAt(i).widget()
            if w:
                w.deleteLater()

        if not produtos:
            lbl = QLabel("Nenhum produto encontrado.")
            lbl.setObjectName("subtitle")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.grid_produtos.addWidget(lbl, 0, 0)
            return

        row, col = 0, 0
        for produto in produtos:
            card = ProdutoCard(produto, self._add_produto_carrinho)
            self.grid_produtos.addWidget(card, row, col)
            col += 1
            if col > 2:
                col = 0
                row += 1

    # ── Carrinho ────────────────────────────────

    def _add_produto_carrinho(self, produto: dict):
        estoque = int(produto.get("estoque") or 0)
        for item in self.carrinho_itens:
            if item["id"] == produto["id"]:
                if item["qtd"] >= estoque:
                    QMessageBox.warning(self, "Estoque insuficiente",
                                        f"Apenas {estoque} un em estoque.")
                    return
                item["qtd"] += 1
                self._render_carrinho()
                self._carregar_produtos()
                return

        if estoque <= 0:
            QMessageBox.warning(self, "Sem estoque", "Produto sem estoque disponível.")
            return

        self.carrinho_itens.append({
            "id":    produto["id"],
            "nome":  produto["nome"],
            "preco": float(produto.get("preco") or 0),
            "qtd":   1,
        })
        self._render_carrinho()
        self._carregar_produtos()

    def _render_carrinho(self):
        # Limpa itens anteriores
        for i in reversed(range(self.cart_items_area.count())):
            item = self.cart_items_area.itemAt(i)
            if item.widget():
                item.widget().deleteLater()

        if not self.carrinho_itens:
            lbl = QLabel("Carrinho vazio")
            lbl.setObjectName("txt_cinza_centro")
            lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.cart_items_area.addWidget(lbl)
            self.linha_divisoria.setVisible(False)
            self.lbl_total_txt.setVisible(False)
            self.lbl_total_val.setVisible(False)
            self.btn_finalizar.setVisible(False)
            self.btn_finalizar_topo.setText("Finalizar (0)")
            return

        total = 0.0
        for idx, item in enumerate(self.carrinho_itens):
            widget = CartItem(
                item,
                on_mais=lambda _, i=idx: self._alterar_qtd(i, +1),
                on_menos=lambda _, i=idx: self._alterar_qtd(i, -1),
                on_remover=lambda _, i=idx: self._remover_item(i),
            )
            self.cart_items_area.addWidget(widget)
            total += item["preco"] * item["qtd"]

        self.linha_divisoria.setVisible(True)
        self.lbl_total_txt.setVisible(True)
        self.lbl_total_val.setVisible(True)
        self.lbl_total_val.setText(f"R$ {total:.2f}")
        self.btn_finalizar.setVisible(True)
        self.btn_finalizar_topo.setText(f"Finalizar ({len(self.carrinho_itens)})")

    def _alterar_qtd(self, idx: int, delta: int):
        if not (0 <= idx < len(self.carrinho_itens)):
            return
        item = self.carrinho_itens[idx]
        nova_qtd = item["qtd"] + delta
        if nova_qtd <= 0:
            self._remover_item(idx)
            return
        item["qtd"] = nova_qtd
        self._render_carrinho()
        self._carregar_produtos()

    def _remover_item(self, idx: int):
        if 0 <= idx < len(self.carrinho_itens):
            self.carrinho_itens.pop(idx)
            self._render_carrinho()
            self._carregar_produtos()

    # ── Finalizar ───────────────────────────────

    def _finalizar_venda(self):
        if not self.carrinho_itens:
            QMessageBox.warning(self, "Carrinho vazio", "Adicione produtos antes de finalizar.")
            return

        total = sum(i["preco"] * i["qtd"] for i in self.carrinho_itens)
        descricao = f"{len(self.carrinho_itens)} produto(s) no carrinho"

        dlg = FinalizarVendaDialog(
            item_tipo="produto",
            item_id=0,
            descricao=descricao,
            valor_base=total,
        )

        # Desconecta o confirmar original e usa o PDV multi-item
        dlg.btn_confirmar.clicked.disconnect()
        dlg.btn_confirmar.clicked.connect(lambda: self._confirmar_venda_pdv(dlg))

        dlg.exec()

    def _confirmar_venda_pdv(self, dlg: FinalizarVendaDialog):
        try:
            desconto = float(dlg.edit_desconto.text().strip().replace(",", ".") or 0)
        except ValueError:
            QMessageBox.warning(dlg, "Erro", "Desconto inválido.")
            return

        forma_pagamento = dlg.obter_forma_pagamento()
        parcelamento    = dlg.cmb_parcelas.currentText()
        cliente_id      = dlg.cmb_cliente.currentData()
        cliente_nome    = dlg.cmb_cliente.currentText() if cliente_id else "Balcão"
        total_bruto     = sum(i["preco"] * i["qtd"] for i in self.carrinho_itens)
        total_liq       = max(0.0, total_bruto - desconto)

        try:
            venda_id = db.registrar_venda_pdv(
                itens=self.carrinho_itens,
                forma_pagamento=forma_pagamento,
                parcelamento=parcelamento,
                cliente_id=cliente_id,
            )
        except Exception as e:
            QMessageBox.critical(dlg, "Erro", f"Falha ao registrar venda:\n{e}")
            return

        # Imprime cupom
        try:
            from component.notas import imprimir_venda
            imprimir_venda(
                venda_id=venda_id,
                itens=self.carrinho_itens,
                cliente_nome=cliente_nome,
                forma_pagamento=forma_pagamento,
                parcelamento=parcelamento,
                total=total_liq,
            )
        except Exception as e:
            QMessageBox.warning(dlg, "Aviso", f"Venda registrada, mas falha ao imprimir:\n{e}")

        QMessageBox.information(
            dlg, "Sucesso",
            f"Venda #{venda_id} finalizada!\n"
            f"Total: R$ {total_liq:.2f}  •  {forma_pagamento}\n"
            f"Cupom enviado para impressão."
        )
        dlg.accept()

        # Reseta PDV
        self.carrinho_itens.clear()
        self.edit_busca.clear()
        self._render_carrinho()
        self._carregar_produtos()

    # ── Estilos ─────────────────────────────────

    def aplicar_estilos(self):
        self.setStyleSheet("""
        QWidget {
            background-color: #0F172A;
            font-family: 'Poppins', 'Montserrat', sans-serif;
        }
        QLabel#title_main {
            color: #FFFFFF; font-size: 24px; font-weight: 700; text-transform: uppercase;
        }
        QLabel#subtitle { color: #64748B; font-size: 12px; font-weight: 600; margin-top: -5px; }
        QLineEdit {
            background-color: #0B1120; border: 1px solid #1E293B;
            border-radius: 8px; padding: 12px; color: #FFFFFF; font-size: 13px;
        }
        QLineEdit:focus { border: 1px solid #F26522; }
        QPushButton#btn_primario {
            background-color: #F26522; color: #FFFFFF;
            font-size: 14px; font-weight: 600;
            border-radius: 6px; padding: 10px 20px; border: none;
        }
        QPushButton#btn_primario:hover { background-color: #E05412; }
        QScrollArea#scroll_area { border: none; background-color: transparent; }
        QWidget#scroll_content  { background-color: transparent; }
        QScrollBar:vertical { border: none; background-color: #0B1120; width: 8px; border-radius: 4px; }
        QScrollBar::handle:vertical { background-color: #1E293B; min-height: 20px; border-radius: 4px; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { border: none; background: none; }
        QPushButton#card_produto, QPushButton#card_produto_ativo {
            background-color: #0B1120; border-radius: 10px; text-align: left;
        }
        QPushButton#card_produto { border: 1px solid #1E293B; }
        QPushButton#card_produto:hover { background-color: #1E293B; border: 1px solid #64748B; }
        QPushButton#card_produto_ativo {
            border: 1px solid #F26522; background-color: rgba(242,101,34,0.05);
        }
        QLabel#icone_box {
            background-color: #1E293B; border-radius: 6px; padding: 6px; font-size: 16px;
        }
        QLabel#icone_alerta { font-size: 14px; }
        QLabel#produto_nome  { color: #FFFFFF; font-size: 13px; font-weight: 700; }
        QLabel#produto_preco { color: #F26522; font-size: 14px; font-weight: 700; }
        QLabel#produto_estoque       { color: #64748B; font-size: 11px; }
        QLabel#produto_estoque_alerta { color: #EAB308; font-size: 11px; font-weight: 600; }
        QLabel#tag_no_carrinho {
            background-color: rgba(242,101,34,0.15); color: #F26522;
            font-size: 10px; font-weight: 700; border-radius: 4px; padding: 4px; margin-top: 5px;
        }
        QFrame#cart_frame {
            background-color: #0B1120; border: 1px solid #1E293B; border-radius: 12px;
        }
        QLabel#txt_branca_bold { color: #FFFFFF; font-size: 16px; font-weight: 700; }
        QLabel#cart_item_nome  { color: #FFFFFF; font-size: 13px; font-weight: 600; }
        QLabel#cart_item_preco { color: #64748B; font-size: 12px; }
        QLabel#cart_item_qtd   { color: #FFFFFF; font-size: 14px; font-weight: 700; }
        QPushButton#btn_icon_pequeno {
            background-color: #1E293B; color: #FFFFFF;
            font-size: 14px; font-weight: bold; border: none; border-radius: 4px;
        }
        QPushButton#btn_icon_pequeno:hover { color: #F26522; }
        QPushButton#btn_lixeira {
            background-color: transparent; color: #64748B;
            font-size: 14px; border: none;
        }
        QPushButton#btn_lixeira:hover { color: #EF4444; }
        QFrame#linha_divisoria { background-color: #1E293B; max-height: 1px; border: none; }
        QLabel#txt_branca_16 { color: #FFFFFF; font-size: 16px; font-weight: 600; }
        QLabel#txt_laranja_20 { color: #F26522; font-size: 20px; font-weight: 700; }
        QLabel#txt_cinza_centro { color: #64748B; font-size: 14px; font-weight: 600; }
        """)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = VendasScreen()
    window.show()
    sys.exit(app.exec())
