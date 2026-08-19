"""
screens/fundo.py
================
Sistema de fundo dinâmico do SISPE de alta performance.
Conectado diretamente à paleta centralizada de screens/theme.py.
"""

import math

from PyQt6.QtCore import Qt, QRectF
from PyQt6.QtGui import QPainter, QPixmap
from PyQt6.QtSvg import QSvgRenderer
from PyQt6.QtWidgets import QWidget

# Importa a paleta de cores unificada do seu sistema de design
from screens.theme import CORES


# ============================================================ #
# MANCHAS ORGÂNICAS ("BLOBS") — mesmo espírito do banner Canva:
# formas irregulares e arredondadas, não círculos perfeitos.
# ============================================================ #
def _blob_path(cx, cy, r, fatores):
    """Gera um path SVG fechado e suave (Catmull-Rom -> Bézier) a partir
    de uma lista de fatores de raio por ângulo, criando uma mancha
    orgânica com "efeito de anel irregular", como no banner original."""
    n = len(fatores)
    pontos = []
    for i, fr in enumerate(fatores):
        ang = 2 * math.pi * i / n
        x = cx + r * fr * math.cos(ang)
        y = cy + r * fr * math.sin(ang)
        pontos.append((x, y))

    def _p(i):
        return pontos[i % n]

    d = f"M {pontos[0][0]:.1f},{pontos[0][1]:.1f} "
    for i in range(n):
        p0, p1, p2, p3 = _p(i - 1), _p(i), _p(i + 1), _p(i + 2)
        c1x, c1y = p1[0] + (p2[0] - p0[0]) / 6, p1[1] + (p2[1] - p0[1]) / 6
        c2x, c2y = p2[0] - (p3[0] - p1[0]) / 6, p2[1] - (p3[1] - p1[1]) / 6
        d += f"C {c1x:.1f},{c1y:.1f} {c2x:.1f},{c2y:.1f} {p2[0]:.1f},{p2[1]:.1f} "
    return d + "Z"


# Fatores de raio fixos (determinísticos) para cada mancha — dão o
# "contorno irregular" sem depender de aleatoriedade em tempo de execução.
_FATORES_A = [1.00, 0.86, 1.12, 0.90, 1.16, 0.88, 1.06, 0.94]
_FATORES_B = [0.92, 1.10, 0.88, 1.14, 0.90, 1.05, 0.86, 1.08]
_FATORES_C = [1.05, 0.90, 1.15, 0.92, 1.08, 0.86, 1.12, 0.95]


# ============================================================ #
# SVG COM A PALETA DO BANNER (navy / pêssego / azul-claro / teal / creme)
# ============================================================ #
def _gerar_svg(largura=1600, altura=1000):
    L = largura
    A = altura
    diag = min(L, A)

    # Paleta oficial extraída do banner Canva (screens/theme.py)
    cor_creme = CORES["creme"]
    cor_pessego = CORES["fundo_circulo_base"]     # topo-esquerda
    cor_teal = CORES["fundo_circulo_topo"]        # topo-direita
    cor_azul = CORES["fundo_circulo_extra"]       # base-direita
    cor_navy = CORES["navy"]

    # Manchas orgânicas: pêssego (topo-esq), teal (topo-dir), azul (base-dir)
    blob_pessego = _blob_path(L * 0.08, A * 0.06, diag * 0.30, _FATORES_A)
    blob_teal = _blob_path(L * 0.94, A * 0.10, diag * 0.24, _FATORES_B)
    blob_azul = _blob_path(L * 0.98, A * 0.95, diag * 0.32, _FATORES_C)

    # Anel irregular (eco fino da própria mancha, levemente maior) para o
    # "efeito de anel" característico do banner.
    anel_pessego = _blob_path(L * 0.08, A * 0.06, diag * 0.34, _FATORES_A)
    anel_azul = _blob_path(L * 0.98, A * 0.95, diag * 0.365, _FATORES_C)

    return f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {L} {A}" preserveAspectRatio="none">
  <rect x="0" y="0" width="{L}" height="{A}" fill="{cor_creme}" />

  <!-- Manchas orgânicas nos cantos, como no banner -->
  <path d="{blob_pessego}" fill="{cor_pessego}" fill-opacity="0.55" />
  <path d="{anel_pessego}" fill="none" stroke="{cor_pessego}" stroke-opacity="0.35" stroke-width="2" />

  <path d="{blob_teal}" fill="{cor_teal}" fill-opacity="0.16" />

  <path d="{blob_azul}" fill="{cor_azul}" fill-opacity="0.55" />
  <path d="{anel_azul}" fill="none" stroke="{cor_azul}" stroke-opacity="0.40" stroke-width="2" />

  <!-- Linhas pontilhadas curvas atravessando a tela, em 4 tons do banner -->
  <path d="M -80,{A*0.16} C {L*0.20},{A*0.04} {L*0.36},{A*0.30} {L*0.62},{A*0.14} S {L*0.90},{A*0.02} {L+80},{A*0.12}"
        fill="none" stroke="{cor_navy}" stroke-opacity="0.14" stroke-width="2.6"
        stroke-linecap="round" stroke-dasharray="1,10" />
  <path d="M -80,{A*0.46} C {L*0.24},{A*0.62} {L*0.42},{A*0.34} {L*0.68},{A*0.52} S {L*0.88},{A*0.78} {L+80},{A*0.54}"
        fill="none" stroke="{cor_teal}" stroke-opacity="0.22" stroke-width="2.4"
        stroke-linecap="round" stroke-dasharray="1,9" />
  <path d="M -80,{A*0.78} C {L*0.26},{A*0.90} {L*0.48},{A*0.66} {L*0.72},{A*0.84} S {L*0.94},{A*1.00} {L+80},{A*0.88}"
        fill="none" stroke="{cor_pessego}" stroke-opacity="0.55" stroke-width="2.2"
        stroke-linecap="round" stroke-dasharray="1,9" />
  <path d="M {L*0.06},{A*1.04} C {L*0.26},{A*0.82} {L*0.40},{A*0.58} {L*0.34},{A*0.22}"
        fill="none" stroke="{cor_azul}" stroke-opacity="0.55" stroke-width="2.2"
        stroke-linecap="round" stroke-dasharray="1,9" />
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
