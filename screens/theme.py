"""
screens/theme.py
==================
Sistema de design central do SISPE.

ESTE ARQUIVO NÃO CONTÉM NENHUMA LÓGICA DE NEGÓCIO — apenas cores e strings de
estilo (QSS) reutilizáveis. Nenhuma função aqui lê ou grava no banco, não
conhece nomes de alunos, usuários, etc. É seguro importar este módulo em
qualquer tela sem risco de efeitos colaterais.

COMO USAR
---------
1) Estilo global (aplicado uma única vez, em main.py):
       from screens.theme import GLOBAL_STYLESHEET
       app.setStyleSheet(GLOBAL_STYLESHEET)

2) Estilos pontuais para widgets criados em Python (ex: botões dinâmicos em
   listas), quando não dá para editar o .ui diretamente:
       from screens.theme import estilo_botao_primario
       meu_botao.setStyleSheet(estilo_botao_primario())

3) Constantes de cor, para usar em QPainter, QColor, etc:
       from screens.theme import CORES
       QColor(CORES["azul"])
"""

# ---------------------------------------------------------------------------
# PALETA OFICIAL — única fonte de verdade para cores no sistema.
# Troque os valores aqui se um dia quiser reajustar o tema inteiro de uma vez.
# ---------------------------------------------------------------------------
CORES = {
    "azul":         "#5B84A6",   # azul principal (botões, títulos, destaques)
    "azul_escuro":  "#2F6EA6",   # azul escuro (hover, cabeçalhos, elementos fortes)
    "azul_claro":   "#DDEEFF",   # azul claro (fundos suaves, chips, seleção)
    "branco":       "#FFFFFF",
    "cinza_claro":  "#F5F7FA",   # cinza muito claro (fundo geral)
    "cinza_medio":  "#E4E9EF",   # bordas discretas
    "texto":        "#26343F",  # texto principal (quase preto, mais suave)
    "texto_sec":    "#5B7285",  # texto secundário / labels
    "placeholder":  "#9BAFBF",

    "sucesso":      "#4FA37B",  # verde (suave, não neon)
    "sucesso_escuro": "#3D8265",
    "alerta":       "#E0A458",  # laranja (suave)
    "alerta_escuro": "#C6863A",
    "erro":         "#D9736C",  # vermelho (suave, não vibrante)
    "erro_escuro":  "#B85850",

    # NOVAS CORES EXCLUSIVAS PARA UM FUNDO ACOLHEDOR:
    "fundo_gradiente_topo": "#F9F6F0",    # Marfim/Areia ultra suave (substitui o azul frio)
    "fundo_circulo_topo": "#E5DDF2",      # Lavanda reconfortante (segurança e calma)
    "fundo_circulo_base": "#F7E5D9",      # Pêssego caloroso (acolhimento e afeto)
    "fundo_linhas": "#A199B8",            # Cinza-lavanda discreto para as curvas abstratas
}

# Atalhos usados com frequência
AZUL = CORES["azul"]
AZUL_ESCURO = CORES["azul_escuro"]
AZUL_CLARO = CORES["azul_claro"]
TEXTO = CORES["texto"]
TEXTO_SEC = CORES["texto_sec"]

FONTE = "'Segoe UI', 'Nunito Sans', -apple-system, BlinkMacSystemFont, sans-serif"


# ---------------------------------------------------------------------------
# BLOCOS REUTILIZÁVEIS — para colar dentro do styleSheet de um .ui,
# ou usar via widget.setStyleSheet(...) em widgets criados por código.
# ---------------------------------------------------------------------------

def estilo_card(radius=18, padding=28, cor_fundo=None, cor_borda=None):
    """Estilo padrão de 'card' moderno: cantos arredondados, borda discreta,
    bastante respiro interno. A sombra (elevação) é aplicada à parte, via
    screens.utils.aplicar_sombra() — QSS não faz sombra de verdade."""
    cor_fundo = cor_fundo or CORES["branco"]
    cor_borda = cor_borda or CORES["cinza_medio"]
    return f"""
        background: {cor_fundo};
        border-radius: {radius}px;
        border: 1px solid {cor_borda};
        padding: {padding}px;
    """


def estilo_botao_primario(radius=12):
    """Botão de ação principal: fundo azul em degradê, hover mais escuro.
    Combine com efeitos.instalar_hover_crescimento() para o botão também
    'crescer' levemente ao passar o mouse (isso QSS sozinho não faz)."""
    return f"""
        QPushButton {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {CORES['azul']}, stop:1 {CORES['azul_escuro']});
            color: white;
            border: none;
            border-radius: {radius}px;
            padding: 12px 24px;
            font-weight: 600;
            font-size: 14px;
            min-height: 42px;
        }}
        QPushButton:hover {{
            background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                stop:0 {CORES['azul_escuro']}, stop:1 #244F73);
        }}
        QPushButton:pressed {{
            background: #244F73;
        }}
        QPushButton:disabled {{
            background: {CORES['cinza_medio']};
            color: {CORES['placeholder']};
        }}
    """


def estilo_botao_secundario(radius=12):
    """Botão neutro (ex: 'Cancelar', 'Voltar')."""
    return f"""
        QPushButton {{
            background: {CORES['cinza_claro']};
            color: {CORES['texto']};
            border: 1px solid {CORES['cinza_medio']};
            border-radius: {radius}px;
            padding: 11px 22px;
            font-weight: 600;
            font-size: 14px;
            min-height: 40px;
        }}
        QPushButton:hover {{
            background: {CORES['azul_claro']};
            border: 1px solid {CORES['azul']};
            color: {CORES['azul_escuro']};
        }}
        QPushButton:pressed {{
            background: #C9DFF0;
        }}
    """


def estilo_botao_perigo(radius=12):
    """Botão de ação destrutiva (excluir, desvincular)."""
    return f"""
        QPushButton {{
            background: {CORES['erro']};
            color: white;
            border: none;
            border-radius: {radius}px;
            padding: 10px 18px;
            font-weight: 600;
            font-size: 13px;
            min-height: 36px;
        }}
        QPushButton:hover {{ background: {CORES['erro_escuro']}; }}
        QPushButton:pressed {{ background: #9C453F; }}
    """


def estilo_input(radius=10):
    return f"""
        border: 2px solid {CORES['cinza_medio']};
        border-radius: {radius}px;
        padding: 11px 15px;
        background-color: {CORES['branco']};
        color: {CORES['texto']};
        font-size: 14px;
    """


def estilo_tabela():
    """Tabela moderna: cabeçalho em degradê, linhas alternadas, hover e seleção suaves."""
    return f"""
QTableWidget {{
    background: transparent;
    gridline-color: #EEF3F7;
    font-size: 14px;
    border: none;
    selection-background-color: {CORES['azul_claro']};
    selection-color: {CORES['texto']};
    alternate-background-color: #FAFCFE;
}}
QTableWidget::item {{
    padding: 12px 10px;
    border-bottom: 1px solid #EEF3F7;
}}
QTableWidget::item:hover {{
    background: #F1F7FB;
}}
QTableWidget::item:selected {{
    background: {CORES['azul_claro']};
    color: {CORES['texto']};
}}
QHeaderView::section {{
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 {CORES['azul']}, stop:1 {CORES['azul_escuro']});
    padding: 14px 12px;
    border: none;
    font-weight: 600;
    font-size: 13px;
    color: white;
}}
QTableCornerButton::section {{
    background: {CORES['azul_escuro']};
    border: none;
}}
"""

def estilo_lista():
    """Estilo limpo e exclusivo para QListWidget para evitar erros de parse do Qt."""
    return f"""
QListWidget {{
    border: none;
    font-size: 15px;
    color: #2E3A46;
    background: transparent;
}}
QListWidget::item {{
    padding: 12px 14px;
    border-bottom: 1px solid #EAF1F6;
}}
QListWidget::item:hover {{
    background: #F1F7FB;
}}
QListWidget::item:selected {{
    background-color: {CORES['azul_claro']};
    color: {CORES['texto']};
}}
"""


# ---------------------------------------------------------------------------
# ESTILO GLOBAL — aplicado uma única vez em toda a QApplication (main.py).
# Cobre elementos que hoje NÃO têm styleSheet próprio nos arquivos .ui
# (ex: botões "Editar"/"Excluir" criados dinamicamente em Python), além de
# padronizar scrollbars, inputs e o "look" básico de qualquer widget novo.
#
# IMPORTANTE: um styleSheet definido diretamente num widget (via .ui ou via
# widget.setStyleSheet) tem prioridade sobre este estilo global para aquele
# widget específico — então isto aqui não quebra nada do que já existe, só
# preenche o que ainda está com a aparência padrão feia do Qt.
# ---------------------------------------------------------------------------
# Dentro de screens/theme.py

GLOBAL_STYLESHEET = f"""
* {{
    font-family: {FONTE};
}}

# CORREÇÃO CRÍTICA: Aplicar o fundo cinza_claro especificamente nas janelas principais 
# e telas comuns do sistema, impedindo que afete caixas nativas como QMessageBox.
QMainWindow, QStackedWidget, QWidget#centralwidget, QWidget.HomeScreen, QWidget.LoginScreen {{
    background-color: {CORES['cinza_claro']};
    color: {CORES['texto']};
}}

# Garante que os diálogos tenham texto escuro e fundo limpo padrão
# Dentro do screens/theme.py, localize o bloco do QMessageBox e substitua por este:

# ===========================================================================
# BLINDAGEM COMPLETA DO QMESSAGEBOX
# Impede que telas com stylesheets escuras (ex: tela do psicólogo) corrompam os alertas
# ===========================================================================
QMessageBox, QDialog, QMessageBox QLabel, QMessageBox QPushButton {{
    background-color: #FFFFFF !important;
    color: #26343F !important;
}}

QMessageBox QPushButton {{
    background-color: {CORES['azul']} !important;
    color: white !important;
    border: none;
    border-radius: 6px;
    padding: 6px 18px;
    min-width: 75px;
    min-height: 28px;
}}

QMessageBox QPushButton:hover {{
    background-color: {CORES['azul_escuro']} !important;
}}

QMessageBox QLabel {{
    color: {CORES['texto']};
}}

QPushButton {{
    background: {CORES['azul']};
    color: white;
    border: none;
    border-radius: 10px;
    padding: 8px 16px;
    font-weight: 600;
}}

QPushButton:hover {{
    background: {CORES['azul_escuro']};
}}

QPushButton:pressed {{
    background: #244F73;
}}

QLineEdit, QTextEdit, QComboBox, QDateEdit, QTimeEdit {{
    {estilo_input()}
}}

QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QDateEdit:focus, QTimeEdit:focus {{
    border: 2px solid {CORES['azul']};
}}

QTableWidget {{
    {estilo_tabela()}
}}

QListWidget {{
    {estilo_lista()}
}}

QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 2px;
}}

QScrollBar::handle:vertical {{
    background: {CORES['cinza_medio']};
    border-radius: 5px;
    min-height: 24px;
}}

QScrollBar::handle:vertical:hover {{
    background: {CORES['azul']};
}}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
    height: 0px;
}}

QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    margin: 2px;
}}

QScrollBar::handle:horizontal {{
    background: {CORES['cinza_medio']};
    border-radius: 5px;
    min-width: 24px;
}}

QScrollBar::handle:horizontal:hover {{
    background: {CORES['azul']};
}}

QToolTip {{
    background: {CORES['texto']};
    color: white;
    border: none;
    border-radius: 6px;
    padding: 6px 10px;
}}
"""
