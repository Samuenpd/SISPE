from PyQt6 import uic
from PyQt6.QtWidgets import (
    QWidget,
    QMessageBox,
    QTableWidgetItem,
    QPushButton,
    QHeaderView,
    QScrollArea,
    QVBoxLayout,
    QHBoxLayout,
    QFrame,
    QLabel
)
from PyQt6.QtCore import (Qt, QDate, QLocale, QTime)
from screens.utils import aplicar_sombra
from PyQt6.QtGui import QTextCharFormat, QColor

class ConfiguracoesScreen(QWidget):
    def __init__(self, db):
        super().__init__()

        uic.loadUi("uis/configuracoes.ui", self)

        self.calendarAgenda.setLocale(
            QLocale(
                QLocale.Language.Portuguese,
                QLocale.Country.Brazil
            )
        )
        locale = QLocale(QLocale.Language.Portuguese, QLocale.Country.Brazil)
        QLocale.setDefault(locale)
        self.calendarAgenda.setLocale(locale)

        self.db = db
        self.usuario = None
        self.editando_compromisso = None

        # sombra
        for card in (
            self.framePerfil,
            self.frameFilhos,
            self.frameAgenda
        ):
            aplicar_sombra(card)

        QLocale.setDefault(
            QLocale(
                QLocale.Language.Portuguese,
                QLocale.Country.Brazil
            )
        )

        # Scroll
        self.conteudo = QWidget()
        self.conteudo.setLayout(self.verticalLayout)

        self.scrollArea = QScrollArea()
        self.scrollArea.setWidget(self.conteudo)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setFrameShape(QScrollArea.Shape.NoFrame)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.scrollArea)

        # tabela
        self.calendarAgenda.selectionChanged.connect(
            self.carregar_agenda
        )

        self.frameNovoCompromisso.hide()

        self.btnNovoCompromisso.clicked.connect(
            lambda: self.frameNovoCompromisso.show()
        )

        self.btnSalvarCompromisso.clicked.connect(
            self.adicionar_compromisso
        )

        self.btnCancelarCompromisso.clicked.connect(
            self.cancelar_compromisso
        )

    def criar_card(self, id_, titulo, hora, cor, descricao):

        card = QFrame()

        card.setStyleSheet(f"""
        QFrame {{
            background:white;
            border-left:8px solid {cor};
            border-radius:10px;
        }}
        """)

        layout = QVBoxLayout(card)

        lblHora = QLabel(hora)
        lblTitulo = QLabel(titulo)
        lblDescricao = QLabel(descricao)

        lblTitulo.setStyleSheet(
            "font-size:15px;font-weight:bold;"
        )

        layout.addWidget(lblHora)
        layout.addWidget(lblTitulo)
        layout.addWidget(lblDescricao)

        botoes = QHBoxLayout()

        editar = QPushButton("Editar")
        excluir = QPushButton("Excluir")

        excluir.clicked.connect(
            lambda: self.excluir_compromisso(id_)
        )

        # conecta o botão Editar para abrir o formulário preenchido
        editar.clicked.connect(
            lambda id_=id_, titulo=titulo, hora=hora, descricao=descricao: self.editar_compromisso(id_, titulo, hora, descricao)
        )

        botoes.addStretch()
        botoes.addWidget(editar)
        botoes.addWidget(excluir)

        layout.addLayout(botoes)

        return card

    def carregar(self, usuario):
        self.usuario = usuario

        self.carregar_perfil()
        self.carregar_tela()
        self.frameNovoCompromisso.hide()

    def carregar_perfil(self):
        dados = self.db.obter_usuario(self.usuario["id"])

        self.labelUsername.setText(dados["username"])
        self.labelTipo.setText(dados["tipo"].capitalize())
        self.labelDataCriacao.setText(
            f"Membro desde {dados['data_criacao']}"
        )

    def carregar_tela(self):
        tipo = self.usuario["tipo"]

        # Sempre restaura os dois frames
        self.frameAgenda.show()
        self.frameFilhos.show()

        if tipo == "pai":
            self.frameAgenda.hide()
            self.carregar_filhos()

        elif tipo == "psicologo":
            self.frameFilhos.hide()
            self.carregar_agenda()

        else:
            self.frameAgenda.hide()
            self.frameFilhos.hide()


    def atualizar_calendario(self):

        formato = QTextCharFormat()

        # limpa todas as marcações
        inicio = QDate(2000, 1, 1)
        fim = QDate(2100, 12, 31)

        data = inicio
        while data <= fim:
            self.calendarAgenda.setDateTextFormat(data, formato)
            data = data.addDays(1)

        cursor = self.db.conn.cursor()

        cursor.execute("""
            SELECT DISTINCT data
            FROM compromissos
            WHERE psicologo_id=?
        """, (self.usuario["id"],))

        formato = QTextCharFormat()
        formato.setBackground(QColor("#5B84A6"))
        formato.setForeground(QColor("white"))

        for (data,) in cursor.fetchall():

            dia, mes, ano = map(int, data.split("/"))

            self.calendarAgenda.setDateTextFormat(
                QDate(ano, mes, dia),
                formato
            )

    def carregar_agenda(self):

        locale = QLocale(
            QLocale.Language.Portuguese,
            QLocale.Country.Brazil
        )

        data = self.calendarAgenda.selectedDate().toString("dd/MM/yyyy")

        self.labelDia.setText(
            locale.toString(
                self.calendarAgenda.selectedDate(),
                "dddd, dd 'de' MMMM 'de' yyyy"
            )
        )

        compromissos = self.db.compromissos_por_data(
            self.usuario["id"],
            data
        )

        # Limpa os cards antigos
        while self.layoutCompromissos.count():

            item = self.layoutCompromissos.takeAt(0)

            if item.widget():
                item.widget().deleteLater()

        # Cria um card para cada compromisso
        for id_, titulo, hora, cor, descricao in compromissos:

            card = self.criar_card(
                id_,
                titulo,
                hora,
                cor,
                descricao
            )

            self.layoutCompromissos.addWidget(card)

        self.layoutCompromissos.addStretch()
        self.atualizar_calendario()

    def adicionar_compromisso(self):

        titulo = self.inputTitulo.text().strip()
        if not titulo:
            QMessageBox.warning(
                self,
                "Erro",
                "Informe um título."
            )
            return

        data = self.calendarAgenda.selectedDate().toString("dd/MM/yyyy")
        hora = self.inputHora.time().toString("HH:mm")
        descricao = self.inputDescricao.text().strip()

        cor = "#5B84A6"

        # se estiver em edição, atualiza o compromisso existente
        if self.editando_compromisso is not None:
            self.db.atualizar_compromisso(
                self.editando_compromisso,
                titulo,
                data,
                hora,
                cor,
                descricao
            )
            # limpa estado de edição
            self.editando_compromisso = None
            try:
                self.btnSalvarCompromisso.setText("Salvar")
            except Exception:
                pass

        else:
            self.db.criar_compromisso(
                self.usuario["id"],
                titulo,
                data,
                hora,
                cor,
                descricao
            )

        self.inputTitulo.clear()
        self.inputDescricao.clear()

        self.frameNovoCompromisso.hide()

        self.carregar_agenda()
        self.atualizar_calendario()

    def excluir_compromisso(self, compromisso_id):

        if QMessageBox.question(
            self,
            "Confirmar",
            "Excluir compromisso?"
        ) == QMessageBox.StandardButton.Yes:

            self.db.excluir_compromisso(compromisso_id)

            self.carregar_agenda()
            self.atualizar_calendario()

    def editar_compromisso(self, compromisso_id, titulo, hora, descricao):
        """Abre o formulário de compromisso preenchido para edição."""
        # preenche campos
        try:
            self.inputTitulo.setText(titulo)
        except Exception:
            pass

        # hora é string 'HH:mm' — converte para QTime
        t = QTime.fromString(hora, "HH:mm")
        if t.isValid():
            try:
                self.inputHora.setTime(t)
            except Exception:
                pass

        try:
            self.inputDescricao.setText(descricao)
        except Exception:
            pass

        self.editando_compromisso = compromisso_id
        try:
            self.btnSalvarCompromisso.setText("Atualizar")
        except Exception:
            pass

        self.frameNovoCompromisso.show()

    def cancelar_compromisso(self):
        """Cancela a criação/edição e limpa o estado."""
        try:
            self.inputTitulo.clear()
            self.inputDescricao.clear()
        except Exception:
            pass

        self.editando_compromisso = None
        try:
            self.btnSalvarCompromisso.setText("Salvar")
        except Exception:
            pass

        self.frameNovoCompromisso.hide()