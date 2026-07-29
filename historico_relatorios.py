from PyQt6 import uic
from PyQt6.QtWidgets import QWidget, QTableWidgetItem, QHeaderView
from screens.utils import aplicar_sombra


class HistoricoRelatoriosScreen(QWidget):
    def __init__(self, db, main_app):
        super().__init__()
        uic.loadUi("uis/historico_relatorios.ui", self)

        # Sombra suave nos cards (profundidade calma, sem exagero)
        for card in (self.frameTabela, self.frameDetalhe):
            aplicar_sombra(card)

        self.db = db
        self.main_app = main_app
        self.aluno_id = None
        self._relatorios = []

        self.tabelaHistorico.setEditTriggers(self.tabelaHistorico.EditTrigger.NoEditTriggers)
        self.tabelaHistorico.setSelectionBehavior(self.tabelaHistorico.SelectionBehavior.SelectRows)
        header = self.tabelaHistorico.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)

        self.tabelaHistorico.cellClicked.connect(self.mostrar_relatorio)
        self.btnVoltar.clicked.connect(self.voltar)

    def carregar(self, aluno_id, nome_aluno):
        self.aluno_id = aluno_id
        self.labelTitulo.setText(f"<b>Histórico de Relatórios — {nome_aluno}</b>")

        self._relatorios = self.db.listar_relatorios_aluno(aluno_id)  # [(texto, data), ...] mais recentes primeiro
        self.tabelaHistorico.setRowCount(len(self._relatorios))

        for i, (texto, data) in enumerate(self._relatorios):
            previa = texto if len(texto) <= 80 else texto[:80].rstrip() + "..."
            self.tabelaHistorico.setItem(i, 0, QTableWidgetItem(str(data)))
            self.tabelaHistorico.setItem(i, 1, QTableWidgetItem(previa))

        self.textRelatorioCompleto.clear()

        if self._relatorios:
            self.tabelaHistorico.selectRow(0)
            self.mostrar_relatorio(0, 0)

    def mostrar_relatorio(self, row, _column=0):
        if row < 0 or row >= len(self._relatorios):
            return
        texto, data = self._relatorios[row]
        self.textRelatorioCompleto.setText(f"📅 {data}\n\n{texto}")

    def voltar(self):
        self.main_app.voltar_para_editar_aluno()
