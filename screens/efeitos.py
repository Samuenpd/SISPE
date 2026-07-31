"""
screens/efeitos.py
===================
Efeitos visuais reutilizáveis: animações de hover estáveis e transições de página.
Versão corrigida utilizando animação de tamanho mínimo (minimumSize) para layouts estáveis.
"""

from PyQt6.QtCore import Qt, QObject, QEvent, QPropertyAnimation, QEasingCurve, QSize
from PyQt6.QtWidgets import QGraphicsOpacityEffect

# --------------------------------------------------------------------------- #
# 1) HOVER COM CRESCIMENTO SUAVE EM LAYOUTS (CORRIGIDO)
# --------------------------------------------------------------------------- #
class _HoverCrescimento(QObject):
    """
    Filtro de eventos que expande o tamanho mínimo do widget.
    Garante crescimento centrado e livre de erros de herança do C++.
    """
    def __init__(self, widget, escala, duracao):
        super().__init__(widget)
        self.widget = widget
        self.escala = escala
        self.duracao = duracao
        
        # Armazena o tamanho original do botão
        self._tamanho_original = None
        self._animacao = None

    def eventFilter(self, obj, event):
        if obj is self.widget:
            if event.type() == QEvent.Type.Enter:
                self._animar(crescer=True)
            elif event.type() == QEvent.Type.Leave:
                self._animar(crescer=False)
        return False

    def _animar(self, crescer):
        # Captura o tamanho inicial na primeira interação
        if self._tamanho_original is None:
            self._tamanho_original = self.widget.size()
            # Garante que o botão use tamanho fixado no layout para não colapsar
            self.widget.setMinimumSize(self._tamanho_original)

        if crescer:
            largura_destino = int(self._tamanho_original.width() * self.escala)
            altura_destino = int(self._tamanho_original.height() * self.escala)
            destino = QSize(largura_destino, altura_destino)
        else:
            destino = self._tamanho_original

        # Anima a propriedade QSize nativa do componente
        self._animacao = QPropertyAnimation(self.widget, b"minimumSize")
        self._animacao.setDuration(self.duracao)
        self._animacao.setStartValue(self.widget.minimumSize())
        self._animacao.setEndValue(destino)
        self._animacao.setEasingCurve(QEasingCurve.Type.OutCubic)
        self._animacao.start()


def instalar_hover_crescimento(botao, escala=1.05, duracao=120):
    """Aplica o efeito de crescimento visual seguro via propriedades de tamanho nativas."""
    if not botao:
        return
    filtro = _HoverCrescimento(botao, escala, duracao)
    botao.installEventFilter(filtro)
    botao._filtro_hover_crescimento = filtro


# --------------------------------------------------------------------------- #
# 2) FADE-IN DE TRANSIÇÃO ENTRE TELAS
# --------------------------------------------------------------------------- #
def trocar_tela_com_fade(stacked_widget, novo_widget, duracao=250):
    if not novo_widget:
        return

    efeito = QGraphicsOpacityEffect(novo_widget)
    efeito.setOpacity(0.0)
    novo_widget.setGraphicsEffect(efeito)

    stacked_widget.setCurrentWidget(novo_widget)

    animacao = QPropertyAnimation(efeito, b"opacity", novo_widget)
    animacao.setDuration(duracao)
    animacao.setStartValue(0.0)
    animacao.setEndValue(1.0)
    animacao.setEasingCurve(QEasingCurve.Type.OutCubic)

    def limpar_efeito():
        try:
            if novo_widget:
                novo_widget.setGraphicsEffect(None)
        except RuntimeError:
            pass

    animacao.finished.connect(limpar_efeito)
    stacked_widget._animacao_fade = animacao
    animacao.start()
