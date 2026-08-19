"""
screens/configuracoes.py
==========================
Lógica da tela de configurações (perfil do usuário + agenda do psicólogo +
lista de filhos do responsável).

Este arquivo NÃO constrói nenhum widget diretamente — toda a interface
visual vive em uis/configuracoes_ui.py (classe Ui_ConfiguracoesScreen). Aqui
só ficam: conexões de sinal, montagem dos cards dinâmicos de compromisso e
chamadas ao banco (database.py).
"""

from PyQt6.QtWidgets import (
    QWidget, QListWidgetItem, QMessageBox, QFrame, QLabel,
    QHBoxLayout, QVBoxLayout, QPushButton, QRadioButton,
)
from PyQt6.QtCore import QDate, QLocale, QTime
from PyQt6.QtGui import QTextCharFormat, QColor

from uis.configuracoes_ui import Ui_ConfiguracoesScreen
from screens.utils import mostrar_alerta

# Paleta de cores disponíveis para marcar um compromisso
_CORES_COMPROMISSO = [
    ("#5B84A6", "Azul"),
    ("#E0A458", "Laranja"),
    ("#D9736C", "Vermelho"),
    ("#4FA37B", "Verde"),
    ("#7D74B3", "Roxo"),
]


class ConfiguracoesScreen(QWidget):
    def __init__(self, db):
        super().__init__()
        self.db = db
        self.usuario = None
        self.editando_compromisso = None
        self.cor_selecionada = _CORES_COMPROMISSO[0][0]
        self._datas_marcadas = set()

        self.ui = Ui_ConfiguracoesScreen()
        self.ui.setupUi(self)

        locale = QLocale(QLocale.Language.Portuguese, QLocale.Country.Brazil)
        QLocale.setDefault(locale)
        self.ui.calendarAgenda.setLocale(locale)

        self._construir_seletor_de_cores()

        self.ui.calendarAgenda.selectionChanged.connect(self.carregar_agenda)
        self.ui.frameNovoCompromisso.hide()
        self.ui.btnNovoCompromisso.clicked.connect(lambda: self.ui.frameNovoCompromisso.show())
        self.ui.btnSalvarCompromisso.clicked.connect(self.adicionar_compromisso)
        self.ui.btnCancelarCompromisso.clicked.connect(self.cancelar_compromisso)

    # ------------------------------------------------------------------ #
    def _construir_seletor_de_cores(self):
        """Cria os botões de seleção de cor dentro do painel de novo
        compromisso. Fica na lógica (não no _ui.py) porque a lista de cores
        disponíveis é comportamento, não layout fixo."""
        self.botoes_cor = {}
        for hex_color, nome in _CORES_COMPROMISSO:
            btn = QRadioButton()
            btn.setToolTip(nome)
            btn.setStyleSheet(f"""
                QRadioButton::indicator {{
                    width: 20px; height: 20px; border-radius: 10px;
                    background-color: {hex_color}; border: 2px solid transparent;
                }}
                QRadioButton::indicator:checked {{ border: 2px solid #26343F; }}
            """)
            btn.clicked.connect(lambda checked, c=hex_color: self._mudar_cor_ativa(c))
            self.ui.layoutCores.addWidget(btn)
            self.botoes_cor[hex_color] = btn

        self.botoes_cor[self.cor_selecionada].setChecked(True)

    def _mudar_cor_ativa(self, cor_hex):
        self.cor_selecionada = cor_hex

    def criar_card(self, id_, titulo, hora, cor, descricao):
        card = QFrame()
        card.setStyleSheet(f"QFrame {{ background: #FFFFFF; border-left: 8px solid {cor}; border-radius: 10px; }}")

        layout = QVBoxLayout(card)
        layout.setContentsMargins(16, 12, 16, 12)
        layout.setSpacing(4)

        lblHora = QLabel(hora)
        lblHora.setStyleSheet("color: #5B7285; font-size: 12px; font-weight: 600;")
        lblTitulo = QLabel(titulo)
        lblTitulo.setStyleSheet("font-size: 15px; font-weight: bold; color: #2E3A46;")
        lblDescricao = QLabel(descricao)
        lblDescricao.setStyleSheet("color: #7C93A3; font-size: 13px;")

        layout.addWidget(lblHora)
        layout.addWidget(lblTitulo)
        layout.addWidget(lblDescricao)

        botoes = QHBoxLayout()
        botoes.setContentsMargins(0, 8, 0, 0)
        editar = QPushButton("Editar")
        excluir = QPushButton("Excluir")
        estilo_bnt = "padding: 4px 12px; min-height: 28px; font-size: 12px;"
        editar.setStyleSheet(estilo_bnt)
        excluir.setStyleSheet(estilo_bnt)
        excluir.clicked.connect(lambda: self.excluir_compromisso(id_))
        editar.clicked.connect(lambda id_=id_, t=titulo, h=hora, d=descricao: self.editar_compromisso(id_, t, h, d))
        botoes.addStretch()
        botoes.addWidget(editar)
        botoes.addWidget(excluir)
        layout.addLayout(botoes)
        return card

    # ------------------------------------------------------------------ #
    # API pública — chamada por main_app_qt.py
    # ------------------------------------------------------------------ #
    def carregar(self, usuario):
        self.usuario = usuario
        self.carregar_perfil()
        self.carregar_tela()
        self.ui.frameNovoCompromisso.hide()

    # ------------------------------------------------------------------ #
    def carregar_perfil(self):
        dados = self.db.obter_usuario(self.usuario["id"])
        self.ui.labelUsername.setText(dados["username"])
        self.ui.labelTipo.setText(dados["tipo"].capitalize())
        self.ui.labelDataCriacao.setText(f"Membro desde {dados['data_criacao']}")

    def carregar_tela(self):
        tipo = self.usuario["tipo"]
        self.ui.frameAgenda.show()
        self.ui.frameFilhos.show()

        if tipo == "pai":
            self.ui.frameAgenda.hide()
            self._carregar_filhos()
        elif tipo == "psicologo":
            self.ui.frameFilhos.hide()
            self._datas_marcadas = set()
            self.carregar_agenda()
        else:
            self.ui.frameAgenda.hide()
            self.ui.frameFilhos.hide()

    def _carregar_filhos(self):
        self.ui.listaFilhos.clear()
        for _id, nome, _sala, _serie in self.db.alunos_do_pai(self.usuario["id"]):
            self.ui.listaFilhos.addItem(QListWidgetItem(nome))

    def atualizar_calendario(self):
        """Marca no calendário os dias com compromisso. Só toca nas datas
        que realmente mudaram (comparando com a última marcação), em vez de
        varrer um intervalo fixo de 100 anos a cada atualização."""
        novas_datas = set(self.db.datas_com_compromissos(self.usuario["id"]))

        formato_vazio = QTextCharFormat()
        for data_str in self._datas_marcadas - novas_datas:
            data = self._parse_data(data_str)
            if data:
                self.ui.calendarAgenda.setDateTextFormat(data, formato_vazio)

        formato = QTextCharFormat()
        formato.setBackground(QColor("#5B84A6"))
        formato.setForeground(QColor("white"))
        for data_str in novas_datas:
            data = self._parse_data(data_str)
            if data:
                self.ui.calendarAgenda.setDateTextFormat(data, formato)

        self._datas_marcadas = novas_datas

    @staticmethod
    def _parse_data(data_str):
        try:
            dia, mes, ano = map(int, data_str.split("/"))
            return QDate(ano, mes, dia)
        except Exception:
            return None

    def carregar_agenda(self):
        locale = QLocale(QLocale.Language.Portuguese, QLocale.Country.Brazil)
        data = self.ui.calendarAgenda.selectedDate().toString("dd/MM/yyyy")
        self.ui.labelDia.setText(
            locale.toString(self.ui.calendarAgenda.selectedDate(), "dddd, dd 'de' MMMM 'de' yyyy")
        )

        compromissos = self.db.compromissos_por_data(self.usuario["id"], data)

        while self.ui.layoutCompromissos.count():
            item = self.ui.layoutCompromissos.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        for id_, titulo, hora, cor, descricao in compromissos:
            self.ui.layoutCompromissos.addWidget(self.criar_card(id_, titulo, hora, cor, descricao))

        self.ui.layoutCompromissos.addStretch()
        self.atualizar_calendario()

    def adicionar_compromisso(self):
        titulo = self.ui.inputTitulo.text().strip()
        if not titulo:
            mostrar_alerta(self, QMessageBox.Icon.Warning, "Erro", "Informe um título.")
            return

        data = self.ui.calendarAgenda.selectedDate().toString("dd/MM/yyyy")
        hora = self.ui.inputHora.time().toString("HH:mm")
        descricao = self.ui.inputDescricao.text().strip()
        cor = self.cor_selecionada

        if self.editando_compromisso is not None:
            self.db.atualizar_compromisso(self.editando_compromisso, titulo, data, hora, cor, descricao)
            self.editando_compromisso = None
            self.ui.btnSalvarCompromisso.setText("Salvar")
        else:
            self.db.criar_compromisso(self.usuario["id"], titulo, data, hora, cor, descricao)

        self.ui.inputTitulo.clear()
        self.ui.inputDescricao.clear()
        self.ui.frameNovoCompromisso.hide()
        self.carregar_agenda()

    def excluir_compromisso(self, compromisso_id):
        botoes = QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        confirm = mostrar_alerta(self, QMessageBox.Icon.Question, "Confirmar", "Excluir compromisso?", botoes)
        if confirm == QMessageBox.StandardButton.Yes:
            self.db.excluir_compromisso(compromisso_id)
            self.carregar_agenda()

    def editar_compromisso(self, compromisso_id, titulo, hora, descricao):
        self.ui.inputTitulo.setText(titulo)
        t = QTime.fromString(hora, "HH:mm")
        if t.isValid():
            self.ui.inputHora.setTime(t)
        self.ui.inputDescricao.setText(descricao)
        self.editando_compromisso = compromisso_id
        self.ui.btnSalvarCompromisso.setText("Atualizar")
        self.ui.frameNovoCompromisso.show()

    def cancelar_compromisso(self):
        self.ui.inputTitulo.clear()
        self.ui.inputDescricao.clear()
        self.editando_compromisso = None
        self.ui.btnSalvarCompromisso.setText("Salvar")
        self.ui.frameNovoCompromisso.hide()
