# 🧭 SISPE — Sistema Integrado de Saúde e Psicologia Escolar

Sistema desktop para organização e acompanhamento do atendimento psicológico
escolar, desenvolvido como projeto técnico em Guarulhos/SP. O SISPE nasceu da
insatisfação com a plataforma "Conviva" e foi moldado a partir de reuniões
com psicólogos escolares, com o objetivo de otimizar a identificação e o
encaminhamento de estudantes com necessidade de apoio psicológico na rede
pública de ensino.

![Python](https://img.shields.io/badge/Python-3.13-blue)
![PyQt6](https://img.shields.io/badge/PyQt6-Fluent%20Widgets-0078D4)
![SQLite](https://img.shields.io/badge/Banco-SQLite-003B57)
![License](https://img.shields.io/badge/status-projeto%20acad%C3%AAmico-lightgrey)

---

## 📖 Sobre o projeto

O SISPE centraliza, num único sistema, o cadastro de alunos, o histórico de
relatórios psicológicos, a agenda de atendimentos e a comunicação entre
psicólogos, administração escolar e responsáveis — substituindo controles
manuais e planilhas soltas.

### 🎯 Objetivos

**Objetivo geral:** propor um sistema facilitador que otimize a identificação
e o encaminhamento de estudantes com necessidade de apoio psicológico na rede
pública de ensino de São Paulo.

**Objetivos específicos:**
- Resolver lacunas da plataforma "Conviva"
- Aprimorar a comunicação entre psicólogos e professores
- Centralizar dados dos alunos para agilizar o atendimento
- Validar a aplicação prática com profissionais da área

### 🌍 Contribuição para os ODS (ONU)

- **ODS 3 — Saúde e Bem-Estar:** facilita o acesso ao suporte psicológico e
  promove a saúde mental dos estudantes.
- **ODS 4 — Educação de Qualidade:** cria um ambiente escolar mais propício
  ao desenvolvimento integral.
- **ODS 10 — Redução das Desigualdades:** garante acesso equitativo ao apoio
  psicológico para todos os estudantes da rede pública.

### 📚 Fundamentação teórica

Paulo Freire · Maria Helena Souza Patto · Jean Piaget · Lev Vygotsky ·
Sigmund Freud · Carl Rogers

---

## ✨ Funcionalidades

O sistema é organizado por papel de usuário (login único, telas diferentes
conforme o tipo):

| Papel | O que pode fazer |
|---|---|
| **Psicólogo** | Cadastrar/editar alunos, escrever relatórios de atendimento (com exportação em PDF), ver histórico completo por aluno, gerenciar agenda de compromissos |
| **Administrador** | Gerenciar usuários (criar/excluir), vincular responsáveis a alunos, ver estatísticas globais da escola |
| **Responsável (pai/mãe)** | Ver os alunos vinculados à sua conta e os relatórios registrados para eles |

Recursos transversais:
- Geração de PDF de relatório individual e de prontuário completo (`QPdfWriter`)
- Dashboard inicial com estatísticas específicas por papel de usuário
- Agenda com calendário e compromissos coloridos por categoria
- Autenticação com senha hasheada (`bcrypt`)
- Identidade visual própria (paleta navy / pêssego / azul-claro / teal / creme),
  com fundo orgânico renderizado em SVG

---

## 🛠️ Tecnologias

- **Linguagem:** Python 3.13
- **Interface:** PyQt6 + [PyQt6-Fluent-Widgets](https://qfluentwidgets.com/)
- **Banco de dados:** SQLite (`sqlite3`)
- **Autenticação:** `bcrypt`
- **Geração de PDF:** `QPdfWriter` (+ `reportlab` para relatórios auxiliares)
- **Empacotamento:** PyInstaller (`main.spec`)

---

## 🏗️ Arquitetura

O projeto segue uma separação estrita entre **visual** e **lógica**:

```
uis/*_ui.py      → SOMENTE construção de widgets (classes Ui_XScreen com
                    setupUi()). Nunca acessa o banco, nunca tem regra de
                    negócio, nunca conecta sinais com comportamento.

screens/*.py     → SOMENTE lógica: instancia a UI correspondente, conecta
                    sinais, valida dados e chama o database.py.

database.py      → Única fonte de acesso ao banco. Todo SQL do sistema
                    fica confinado aqui — nenhuma tela executa SQL cru.
```

Outros padrões importantes do projeto:
- Um único helper `mostrar_alerta()` (`screens/utils.py`) para todos os
  `QMessageBox` do sistema, com visual padronizado (fundo creme).
- Banco de dados armazenado na pasta de dados do usuário, não no diretório
  de execução do `.exe` (`database.py → obter_pasta_dados()`):
  - Windows: `%APPDATA%\SISPE\sispe.db`
  - macOS: `~/Library/Application Support/SISPE/sispe.db`
  - Linux: `~/.local/share/SISPE/sispe.db`
- Fundo orgânico (blobs + linhas pontilhadas) gerado como SVG e renderizado
  em `QPixmap` cacheado, reconstruído só no resize (`screens/fundo.py`).

---

## 📂 Estrutura de pastas

```
SISPE/
├── main.py                  # ponto de entrada
├── main_app_qt.py           # janela principal (navegação + stackedWidget)
├── database.py               # toda a camada de acesso ao SQLite
├── main.spec                 # build PyInstaller
├── uis/                       # camada visual (Ui_XScreen)
│   ├── main_ui.py
│   ├── home_ui.py
│   ├── login_ui.py
│   ├── psicologo_ui.py
│   ├── admin_ui.py
│   ├── pai_ui.py
│   ├── vincular_ui.py
│   ├── editar_aluno_ui.py
│   ├── historico_relatorios_ui.py
│   └── configuracoes_ui.py
└── screens/                   # camada de lógica
    ├── home.py
    ├── login_qt.py
    ├── psicologo.py
    ├── admin.py
    ├── pai.py
    ├── vincular.py
    ├── editar_aluno.py
    ├── historico_relatorios.py
    ├── configuracoes.py
    ├── fundo.py               # fundo SVG orgânico
    ├── theme.py                # paleta de cores e estilos QSS reutilizáveis
    ├── efeitos.py               # animações (hover, fade entre telas)
    └── utils.py                  # alertas, geração de PDF, helpers
```

---

## 🚀 Como rodar

### Pré-requisitos
```bash
pip install PyQt6 PyQt6-Fluent-Widgets bcrypt reportlab
```

### Executar
```bash
python main.py
```

Na primeira execução, o banco de dados é criado automaticamente com um
usuário administrador padrão:

| Usuário | Senha |
|---|---|
| `admin` | `123` |

> ⚠️ Troque a senha padrão antes de usar em produção.

### Gerar executável (Windows)
```bash
pyinstaller main.spec
```

---

## 👥 Equipe de desenvolvimento

- Andressa Alves Pereira
- Erick Lima Santos
- Iashyla Campos de Jesus
- Gustavo Cardoso Badiale
- João Vitor Lino da Cruz
- Samuel de Lima Milare

**Docente orientador:** Filipe Sara Nogueira Pann
**Guarulhos, 2025**

---

## 📄 Licença

Projeto acadêmico desenvolvido para fins educacionais. Defina uma licença
(ex: MIT) caso pretenda distribuir ou aceitar contribuições externas.
