"""
screens/fundo.py
================
Sistema de fundo dinâmico do SISPE de alta performance.
Conectado diretamente à paleta centralizada de screens/theme.py.
"""

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QWidget

# Importa a paleta de cores unificada do seu sistema de design
from screens.theme import CORES

# ============================================================ #
# SVG COM CORES DINÂMICAS E MAIS VIVAS
# ============================================================ #
def _gerar_svg(largura=1600, altura=1000):
    L = largura
    A = altura
    
    # Carrega a nova identidade acolhedora do theme.py
    bg_topo = CORES["fundo_gradiente_topo"]
    cor_lavanda = CORES["fundo_circulo_topo"]
    cor_pessego = CORES["fundo_circulo_base"]
    cor_linhas = CORES["fundo_linhas"]
    
    return f"""
<svg xmlns="http://w3.org" viewBox="0 0 {L} {A}" preserveAspectRatio="none">
  <defs>
    <!-- Gradiente de fundo transita de um marfim caloroso para o branco puro -->
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="{bg_topo}"/>
      <stop offset="100%" stop-color="#FFFFFF"/>
    </linearGradient>
    <radialGradient id="g1" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0%" stop-color="{cor_lavanda}" stop-opacity="0.35"/>
      <stop offset="60%" stop-color="{cor_lavanda}" stop-opacity="0.12"/>
      <stop offset="100%" stop-color="{cor_lavanda}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="g2" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0%" stop-color="{cor_pessego}" stop-opacity="0.40"/>
      <stop offset="60%" stop-color="{cor_pessego}" stop-opacity="0.15"/>
      <stop offset="100%" stop-color="{cor_pessego}" stop-opacity="0"/>
    </radialGradient>
    <radialGradient id="g3" cx="0.5" cy="0.5" r="0.5">
      <stop offset="0%" stop-color="#FFFFFF" stop-opacity="0.60"/>
      <stop offset="100%" stop-color="#FFFFFF" stop-opacity="0"/>
    </radialGradient>
  </defs>
  <rect x="0" y="0" width="{L}" height="{A}" fill="url(#bg)" />
  <circle cx="{L*0.90}" cy="{A*0.06}" r="{min(L,A)*0.26}" fill="url(#g1)" />
  <circle cx="{L*0.03}" cy="{A*0.98}" r="{min(L,A)*0.32}" fill="url(#g2)" />
  <circle cx="{L*0.55}" cy="{A*0.42}" r="{min(L,A)*0.18}" fill="url(#g3)" />
  
  <!-- Curvas fluidas redesenhadas com o tom lavanda-cinza acolhedor -->
  <path d=" M -100,{A*0.14} C {L*0.18},{A*0.02} {L*0.34},{A*0.34} {L*0.58},{A*0.18} S {L*0.88},{A*0.02} {L+100},{A*0.16}" fill="none" stroke="{cor_linhas}" stroke-opacity="0.16" stroke-width="2.8" stroke-linecap="round" />
  <path d=" M -100,{A*0.52} C {L*0.22},{A*0.70} {L*0.40},{A*0.38} {L*0.66},{A*0.58} S {L*0.86},{A*0.86} {L+100},{A*0.60}" fill="none" stroke="{cor_linhas}" stroke-opacity="0.14" stroke-width="2.4" stroke-linecap="round" />
  <path d=" M -100,{A*0.86} C {L*0.28},{A*0.96} {L*0.48},{A*0.72} {L*0.74},{A*0.90} S {L*0.95},{A*1.06} {L+100},{A*0.94}" fill="none" stroke="{cor_linhas}" stroke-opacity="0.12" stroke-width="2.0" stroke-linecap="round" />
  <path d=" M {L*0.10},{A*1.05} C {L*0.30},{A*0.80} {L*0.45},{A*0.55} {L*0.40},{A*0.20}" fill="none" stroke="{cor_linhas}" stroke-opacity="0.10" stroke-width="2.2" stroke-linecap="round" />
</svg>
""".strip()



# ============================================================ #
# WIDGET DO FUNDO (LÓGICA CONSOLIDADA)
# ============================================================ #
class BackgroundWidget(QWidget):
    _svg_bytes = _gerar_svg().encode("utf-8")

    def __init__(self, parent=None):
        super().__init__(parent, Qt.WindowType.SubWindow | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TransparentForMouseEvents)
        self.setAttribute(Qt.WidgetAttribute.WA_NoSystemBackground, True)
        self.lower()
        self._renderer = QSvgRenderer(self._svg_bytes)
        self._cache = None

    def resizeEvent(self, event):
        super().resizeEvent(event)
        tamanho = event.size()
        if tamanho.isEmpty():
            return

        pix = QPixmap(tamanho)
        pix.fill(Qt.GlobalColor.transparent)
        
        painter = QPainter()
        if painter.begin(pix):
            painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
            self._renderer.render(painter, QRectF(pix.rect()))
            painter.end()
            self._cache = pix

    def paintEvent(self, event):
        if self._cache:
            painter = QPainter(self)
            painter.drawPixmap(0, 0, self._cache)
            painter.end()

    def eventFilter(self, watched, event):
        if watched == self.parent() and event.type() == event.Type.Resize:
            self.resize(event.size())
        return super().eventFilter(watched, event)
