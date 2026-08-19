"""
screens/home_ui.py
===================
Definição PURAMENTE VISUAL da tela inicial (dashboard) do SISPE.

Este arquivo é o equivalente ao antigo home.ui — só que em Python, porque o
Qt Designer não reconhece componentes do PyQt6-Fluent-Widgets sem o plugin
pago. Segue a mesma convenção do código gerado por `pyuic`: uma classe
`Ui_HomeScreen` com um método `setupUi(tela)` que monta os widgets e guarda
referências a eles como atributos — nada além disso.

ESTE ARQUIVO NÃO CONTÉM:
    - chamadas ao banco de dados (screens/database.py)
    - lógica de negócio
    - conexões de sinal/slot com comportamento (cliques de botão, etc.)

Quem dá vida a estes widgets é screens/home.py.

Requer: pip install PyQt6-Fluent-Widgets
"""

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel

from qfluentwidgets import (
    CardWidget, SimpleCardWidget, TitleLabel, CaptionLabel,
    StrongBodyLabel, FlowLayout, ScrollArea,
)

from screens.utils import aplicar_sombra
from screens.theme import CORES, estilo_tag_secao


# --------------------------------------------------------------------------- #
# Badge circular de ícone (emoji) — mesmo espírito dos ícones do banner
# --------------------------------------------------------------------------- #
class _IconeCircular(QLabel):
    def __init__(self, emoji, cor_fundo, diametro=52, parent=None):
        super().__init__(emoji, parent)
        self.setFixedSize(diametro, diametro)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                background: {cor_fundo};
                border-radius: {diametro // 2}px;
                font-size: {int(diametro * 0.42)}px;
            }}
        """)


# --------------------------------------------------------------------------- #
# Card de estatística do dashboard (ícone + número grande + legenda).
# definir_valor() é só um setter visual — não faz consulta nenhuma.
# --------------------------------------------------------------------------- #
class _CardEstatistica(CardWidget):
    def __init__(self, emoji, cor, legenda, parent=None):
        super().__init__(parent)
        self.setBorderRadius(18)
        self.setFixedHeight(112)
        self.setMinimumWidth(220)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 16, 20, 16)
        layout.setSpacing(16)

        layout.addWidget(_IconeCircular(emoji, cor))

        textos = QVBoxLayout()
        textos.setSpacing(2)
        self.labelValor = TitleLabel("0", self)
        self.labelValor.setStyleSheet(f"color: {cor};")
        self.labelLegenda = CaptionLabel(legenda, self)
        self.labelLegenda.setStyleSheet(f"color: {CORES['texto_sec']};")
        textos.addWidget(self.labelValor)
        textos.addWidget(self.labelLegenda)

        layout.addLayout(textos)
        layout.addStretch()

    def definir_valor(self, valor):
        self.labelValor.setText(str(valor))


# --------------------------------------------------------------------------- #
# Card informativo com "tag" colorida de título, no espírito dos boxes do
# banner ("INTRODUÇÃO E PROBLEMA", "METODOLOGIA...", "CONCLUSÃO" etc.)
# --------------------------------------------------------------------------- #
class _CardInformativo(SimpleCardWidget):
    def __init__(self, titulo, parent=None):
        super().__init__(parent)
        self.setBorderRadius(18)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(28, 26, 28, 26)
        layout.setSpacing(14)

        tag = QLabel(titulo, self)
        tag.setStyleSheet(estilo_tag_secao())
        layout.addWidget(tag, alignment=Qt.AlignmentFlag.AlignLeft)

        self.corpo = QLabel(self)
        self.corpo.setWordWrap(True)
        self.corpo.setTextFormat(Qt.TextFormat.RichText)
        self.corpo.setStyleSheet(
            f"font-size: 14px; color: {CORES['texto']}; line-height: 1.6; background: transparent;"
        )
        layout.addWidget(self.corpo)

    def definir_texto(self, html):
        self.corpo.setText(html)


# --------------------------------------------------------------------------- #
# TEXTOS ESTÁTICOS DOS CARDS INFORMATIVOS
# (conteúdo institucional fixo — visual, não vem do banco)
# --------------------------------------------------------------------------- #
_TEXTOS_CARDS_INFO = [
    ("📖 SOBRE O PROJETO", (
        "O SISPE é um sistema facilitador para a organização e comunicação de "
        "informações que otimiza a identificação e o encaminhamento de estudantes "
        "com necessidades de apoio psicológico na rede pública de ensino de São "
        "Paulo. O projeto nasceu da insatisfação com a plataforma \"Conviva\" e foi "
        "moldado a partir de reuniões com psicólogos escolares, visando criar uma "
        "ferramenta mais eficiente e acolhedora."
    )),
    ("👥 EQUIPE DE DESENVOLVIMENTO", (
        "Andressa Alves Pereira<br>Byanca Santos Mello<br>Erick Lima Santos<br>Iashyla Campos de Jesus<br>"
        "Gustavo Cardoso Badiale<br>João Vitor Lino da Cruz<br>"
        "Karen Brito Gatto<br>Samuel de Lima Milare"
        "<br><br><b>Docente orientador:</b> Filipe Sara Nogueira Pann<br>"
        "<b>Guarulhos, 2025</b>"
    )),
    ("🎯 OBJETIVOS", (
        "<b>Objetivo Geral:</b> Propor um sistema facilitador que otimize a "
        "identificação e o encaminhamento de estudantes com necessidades de apoio "
        "psicológico na rede pública de ensino de São Paulo.<br><br>"
        "<b>Objetivos Específicos:</b><br>"
        "• Resolver lacunas da plataforma \"Conviva\"<br>"
        "• Aprimorar a comunicação entre psicólogos e professores<br>"
        "• Centralizar dados dos alunos para agilizar o atendimento<br>"
        "• Validar a aplicação prática com profissionais da área"
    )),
    ("📚 FUNDAMENTAÇÃO TEÓRICA", (
        "<b>Paulo Freire:</b> Educação como espaço de diálogo e transformação.<br>"
        "<b>Maria Helena Souza Patto:</b> Olhar crítico sobre a psicologia escolar "
        "e as condições sociais dos alunos.<br>"
        "<b>Jean Piaget:</b> Desenvolvimento cognitivo e fases da aprendizagem.<br>"
        "<b>Lev Vygotsky:</b> Mediação social e zona de desenvolvimento proximal.<br>"
        "<b>Sigmund Freud:</b> Complexidades emocionais e raízes do comportamento.<br>"
        "<b>Carl Rogers:</b> Psicologia humanista, empatia e aceitação no ambiente "
        "escolar."
    )),
    ("🌍 OBJETIVOS DE DESENVOLVIMENTO SUSTENTÁVEL", (
        "Este projeto contribui para os ODS da ONU:<br><br>"
        "<b>ODS 3 – Saúde e Bem-Estar:</b> Facilitando o acesso ao suporte "
        "psicológico e promovendo a saúde mental dos estudantes.<br><br>"
        "<b>ODS 4 – Educação de Qualidade:</b> Criando um ambiente escolar mais "
        "propício ao desenvolvimento integral.<br><br>"
        "<b>ODS 10 – Redução das Desigualdades:</b> Garantindo que todos os "
        "estudantes da rede pública tenham acesso equitativo ao apoio psicológico."
    )),
]


# --------------------------------------------------------------------------- #
# Ui_HomeScreen — equivalente ao Ui_Form gerado por pyuic
# --------------------------------------------------------------------------- #
class Ui_HomeScreen:
    """Monta a interface visual da tela inicial e expõe os widgets como
    atributos de instância. Não faz nada além disso.

    Uso (em screens/home.py):
        self.ui = Ui_HomeScreen()
        self.ui.setupUi(self)
        # depois: self.ui.cardAlunos, self.ui.labelMensagem, etc.
    """

    def setupUi(self, tela: QWidget):
        tela.setStyleSheet("background: transparent;")

        raiz = QVBoxLayout(tela)
        raiz.setContentsMargins(0, 0, 0, 0)

        self.scrollArea = ScrollArea(tela)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet("background: transparent; border: none;")
        self.scrollArea.viewport().setStyleSheet("background: transparent;")
        raiz.addWidget(self.scrollArea)

        self.conteudo = QWidget(tela)
        self.conteudo.setStyleSheet("background: transparent;")
        self.scrollArea.setWidget(self.conteudo)

        corpo = QVBoxLayout(self.conteudo)
        corpo.setSpacing(28)
        corpo.setContentsMargins(48, 40, 48, 48)

        corpo.addWidget(self._montar_cabecalho())
        corpo.addWidget(self._montar_saudacao())
        corpo.addWidget(self._montar_estatisticas())
        corpo.addWidget(self._montar_cartoes_info())
        corpo.addStretch()

    # ------------------------------------------------------------------ #
    def _montar_cabecalho(self):
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        v = QVBoxLayout(container)
        v.setContentsMargins(0, 0, 0, 0)
        v.setSpacing(2)

        titulo = TitleLabel("SISPE", container)
        titulo.setStyleSheet(f"color: {CORES['navy']}; font-size: 42px; font-weight: 800; background: transparent;")
        v.addWidget(titulo)

        subtitulo = StrongBodyLabel("Sistema Integrado de Saúde e Psicologia Escolar", container)
        subtitulo.setStyleSheet(f"color: {CORES['teal']}; font-size: 16px; background: transparent;")
        v.addWidget(subtitulo)

        escola = CaptionLabel("E.E. Professora Maria Aparecida Felix Porto", container)
        escola.setStyleSheet(f"color: {CORES['texto_sec']}; background: transparent;")
        v.addWidget(escola)

        return container

    def _montar_saudacao(self):
        card = SimpleCardWidget()
        card.setBorderRadius(18)
        card.setStyleSheet(f"""
            SimpleCardWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {CORES['navy']}, stop:1 {CORES['teal']});
            }}
        """)
        layout = QHBoxLayout(card)
        layout.setContentsMargins(28, 22, 28, 22)

        # labelMensagem é atualizado pela lógica (home.py) ao logar o usuário
        self.labelMensagem = QLabel("Bem-vindo(a) ao SISPE", card)
        self.labelMensagem.setStyleSheet("color: white; font-size: 20px; font-weight: 600; background: transparent;")
        layout.addWidget(self.labelMensagem)

        aplicar_sombra(card, blur=30, y_offset=8, alpha=30)
        return card

    def _montar_estatisticas(self):
        """Container vazio para os cards de estatística. Quais cards entram
        aqui (e com quais valores) depende do tipo de usuário logado — isso
        é decisão de negócio, então fica a cargo de screens/home.py, que usa
        criar_card_estatistica() e limpar_estatisticas() abaixo."""
        self.containerEstatisticas = QWidget()
        self.containerEstatisticas.setStyleSheet("background: transparent;")
        self.layoutEstatisticas = FlowLayout(self.containerEstatisticas, needAni=False)
        self.layoutEstatisticas.setContentsMargins(0, 0, 0, 0)
        self.layoutEstatisticas.setHorizontalSpacing(16)
        self.layoutEstatisticas.setVerticalSpacing(16)
        return self.containerEstatisticas

    def criar_card_estatistica(self, emoji, cor, legenda):
        """Cria um card de estatística, já com sombra, e o adiciona ao
        layout de estatísticas. Retorna o card (chame .definir_valor(n)
        nele para preencher o número)."""
        card = _CardEstatistica(emoji, cor, legenda)
        aplicar_sombra(card, blur=20, y_offset=5, alpha=16)
        self.layoutEstatisticas.addWidget(card)
        return card

    def limpar_estatisticas(self):
        """Remove todos os cards de estatística montados até agora, para
        remontar do zero (ex: usuário trocou, ou trocou de tipo).

        IMPORTANTE: ao contrário dos layouts nativos do Qt, o FlowLayout do
        PyQt6-Fluent-Widgets retorna o próprio QWidget em takeAt(), não um
        QLayoutItem que precisa de .widget() para extrair o widget. Tratamos
        os dois formatos aqui para não quebrar se a lib mudar de versão."""
        while self.layoutEstatisticas.count():
            item = self.layoutEstatisticas.takeAt(0)
            widget = item.widget() if hasattr(item, "widget") else item
            if widget:
                widget.deleteLater()

    def _montar_cartoes_info(self):
        container = QWidget()
        container.setStyleSheet("background: transparent;")
        flow = FlowLayout(container, needAni=False)
        flow.setContentsMargins(0, 0, 0, 0)
        flow.setHorizontalSpacing(20)
        flow.setVerticalSpacing(20)

        for titulo, texto in _TEXTOS_CARDS_INFO:
            card = _CardInformativo(titulo)
            card.definir_texto(texto)
            card.setFixedWidth(460)
            aplicar_sombra(card, blur=22, y_offset=6, alpha=18)
            flow.addWidget(card)

        return container