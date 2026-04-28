from PyQt6 import uic
from PyQt6.QtWidgets import QDialog


class RelatorioScreen(QDialog):
    def __init__(self, db, app, aluno_id, nome):
        super().__init__()
        # Carrega a interface da pasta uis
        uic.loadUi("uis/relatorio.ui", self)

        self.db = db
        self.app = app
        self.aluno_id = aluno_id

        # Atualiza o título com o nome do aluno
        self.labelAluno.setText(f"Aluno: {nome}")

        # Carrega os relatórios existentes na lista
        self.carregar_relatorios()

        # Conecta o botão de salvar
        self.btnSalvarRelatorio.clicked.connect(self.salvar)

    def carregar_relatorios(self):
        """Limpa e recarrega a lista de relatórios do aluno."""
        self.listaRelatorios.clear()  # nome corrigido: listaRelatorios
        dados = self.db.listar_relatorios_aluno(self.aluno_id)
        for texto, data in dados:
            self.listaRelatorios.addItem(f"{data} - {texto[:30]}")

    def salvar(self):
        """Salva um novo relatório e atualiza a lista."""
        texto = self.textNovoRelatorio.toPlainText().strip()  # nome corrigido: textNovoRelatorio
        if texto:
            self.db.criar_relatorio(
                self.aluno_id,
                self.app.usuario_logado["id"],
                texto
            )
            self.textNovoRelatorio.clear()
            self.carregar_relatorios()