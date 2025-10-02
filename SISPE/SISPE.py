import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import hashlib
import sqlite3
import os

# essa é uma classe colocada em algum momento das versões, ela é usada na parte de registro para guardar e printar as informações do aluno
class Aluno:
    def __init__(self, nome, sala, serie, gravidade, id=None, observacoes=''):
        self.nome = nome
        self.sala = sala
        self.serie = serie
        self.gravidade = gravidade
        self.id = id
        self.observacoes = observacoes

    def __str__(self):
        return f"Nome: {self.nome}, Sala: {self.sala}, Série: {self.serie}, Gravidade: {self.gravidade}"
      
    def to_dict(self):
        return {"nome": self.nome, "sala": self.sala, "serie": self.serie, "gravidade": self.gravidade}
    # eu preciso explicar isso, o staticmethod cria uma def que não depende da classe
    @staticmethod
    def from_dict(data):
        return Aluno(data['nome'], data['sala'], data['serie'], data['gravidade'])

# isso é muito chat tá? tipo acho que eu n escrevi nem uma linha
# bom agora eu escrevi algumas linhas, pq deu erro do nada ai eu precisei mexer em tudo
class DatabaseManager:
    def __init__(self, db_name="sispe.db"):
        base_dir = os.path.dirname(os.path.abspath(__file__))  # Pega a pasta do script
        db_path = os.path.join(base_dir, db_name) 
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_tables()

    def _hash_senha(self, senha):
        """Método privado para gerar o hash da senha."""
        return hashlib.sha256(senha.encode()).hexdigest()

    def add_user(self, username, password, user_type): # Modificado para receber a senha sem hash
        password_hash = self._hash_senha(password) # Gera o hash aqui
        try:
            self.cursor.execute("INSERT INTO usuarios (username, password_hash, user_type) VALUES (?, ?, ?)", (username, password_hash, user_type))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        
    def create_tables(self):
        """Cria as tabelas do banco de dados se elas não existirem."""
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                username TEXT PRIMARY KEY,
                password_hash TEXT NOT NULL,
                user_type TEXT NOT NULL
            );
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS alunos (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                sala INTEGER NOT NULL,
                serie INTEGER NOT NULL,
                gravidade TEXT NOT NULL,
                observacoes TEXT,
                user_id TEXT,
                FOREIGN KEY (user_id) REFERENCES usuarios(username) ON DELETE CASCADE
            );
        ''')
        # nova tabela para relacionar pais e alunos
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS alunos_pais (
                aluno_id INTEGER,
                pai_id TEXT,
                PRIMARY KEY (aluno_id, pai_id),
                FOREIGN KEY (aluno_id) REFERENCES alunos(id) ON DELETE CASCADE,
                FOREIGN KEY (pai_id) REFERENCES usuarios(username) ON DELETE CASCADE
            );
        ''')
        self.conn.commit()

    def get_user(self, username):
        self.cursor.execute("SELECT password_hash, user_type FROM usuarios WHERE username = ?", (username,))
        result = self.cursor.fetchone()
        return result if result else None

    def add_aluno(self, nome, sala, serie, gravidade, user_id):
        self.cursor.execute(
            "INSERT INTO alunos (nome, sala, serie, gravidade, observacoes, user_id) VALUES (?, ?, ?, ?, ?, ?)",
            (nome, sala, serie, gravidade, "", user_id)
        )
        self.conn.commit()

    def get_alunos_by_user(self, user_id):
        self.cursor.execute("SELECT id, nome, sala, serie, gravidade, observacoes FROM alunos WHERE user_id = ?", (user_id,))
        alunos_data = self.cursor.fetchall()
        return [Aluno(nome=data[1], sala=data[2], serie=data[3], gravidade=data[4], observacoes=data[5], id=data[0]) for data in alunos_data]

    def get_aluno_by_id(self, aluno_id):
        self.cursor.execute('SELECT id, nome, sala, serie, gravidade, observacoes FROM alunos WHERE id = ?', (aluno_id,))
        data = self.cursor.fetchone()
        if data:
            return Aluno(nome=data[1], sala=data[2], serie=data[3], gravidade=data[4], observacoes=data[5], id=data[0])
        return None
    
    # eu criei uma parte pra salvar registor sobre os alunos
    def aluno_observação(self, aluno_id, observacao):
        self.cursor.execute(
            'UPDATE alunos SET observacoes = ? WHERE id = ?',
            (observacao, aluno_id)
        )
        self.conn.commit()

    def update_aluno(self, aluno_id, nome, sala, serie, gravidade):
        self.cursor.execute(
            "UPDATE alunos SET nome = ?, sala = ?, serie = ?, gravidade = ? WHERE id = ?",
            (nome, sala, serie, gravidade, aluno_id)
        )
        self.conn.commit()
    # acaba aqui

    def delete_aluno(self, aluno_id):
        self.cursor.execute("DELETE FROM alunos WHERE id = ?", (aluno_id,))
        self.conn.commit()

    def close(self):
        # Fecha a conexão com o banco de dados
        self.conn.close()

    def delete_user(self, username):
        # Exclui a conta do usuário
        self.cursor.execute("DELETE FROM usuarios WHERE username = ?", (username,))
        self.conn.commit()

    def vincular_pai_aluno(self, aluno_id, pai_username):
        try:
            self.cursor.execute(
                "INSERT INTO alunos_pais (aluno_id, pai_id) VALUES (?, ?)",
                (aluno_id, pai_username)
            )
            self.conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Erro", "Esse vínculo já existe.")


    def get_alunos_by_pai(self, pai_username):
        self.cursor.execute('''
            SELECT a.id, a.nome, a.sala, a.serie, a.gravidade, a.observacoes
            FROM alunos a
            JOIN alunos_pais ap ON a.id = ap.aluno_id
            WHERE ap.pai_id = ?
        ''', (pai_username,))
        alunos_data = self.cursor.fetchall()
        return [Aluno(nome=d[1], sala=d[2], serie=d[3], gravidade=d[4], observacoes=d[5], id=d[0]) for d in alunos_data]

    def get_pais(self):
        self.cursor.execute("SELECT username FROM usuarios WHERE user_type = 'pai'")
        return [row[0] for row in self.cursor.fetchall()]

    def get_psicologas(self):
        self.cursor.execute("SELECT username FROM usuarios WHERE user_type = 'psicologa'")
        return [row[0] for row in self.cursor.fetchall()]

class SISPE:
    def __init__(self, principal):
        self.principal = principal
        principal.title("SISPE")
        principal.geometry("900x600")
        principal.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.frames = {}
        self.usuario_logado = None
        self.db = DatabaseManager()
        self.aluno_id_edicao = None
        self.aluno_id_observacoes = None

        # 🔹 cria só login e principal aqui
        self.criar_tela_login()
        self.criar_tela_principal()
        self.criar_tela_registro()

        # 🔹 as outras telas só serão criadas quando o usuário logar
        # (porque precisam do conteudo_frame já existente)

        self.mostrar_frame("login")

    def fazer_login(self):
        usuario = self.campo_usuario_login.get()
        senha = self.campo_senha_login.get()

        senha_hash = self.db._hash_senha(senha)
        result = self.db.get_user(usuario)

        if result and senha_hash == result[0]:
            self.usuario_logado = usuario
            self.user_type = result[1]

            self.campo_usuario_login.delete(0, tk.END)
            self.campo_senha_login.delete(0, tk.END)

            self.configurar_interface_por_tipo()

            if "gestao" not in self.frames:
                self.criar_tela_gestao()
                self.criar_tela_registro()
                self.criar_tela_perfil()
                self.criar_tela_observacoes()
                self.criar_tela_vinculo()
                self.criar_tela_ver_alunos()

            self.mostrar_frame("principal")
        else:
            messagebox.showerror("Login", "Usuário ou senha incorretos.")

    
    def on_closing(self):
        """Fecha a conexão com o banco de dados ao fechar a janela."""
        if messagebox.askokcancel("Sair", "Tem certeza que deseja sair?"):
            self.db.close()
            self.principal.destroy()

    def _hash_senha(self, senha):
        return hashlib.sha256(senha.encode()).hexdigest()

    def criar_tela_login(self):
        frame_login = ttk.Frame(self.principal, padding="30 20 30 20", relief="groove")
        self.frames["login"] = frame_login
        # eu mudei essa parte pra deixar redimensionavel os elementos na tela, isso vai se repetir em cada frame
        frame_login.grid_rowconfigure(0, weight=1)
        frame_login.grid_rowconfigure(9, weight=1)
        frame_login.grid_columnconfigure(0, weight=1)
        frame_login.grid_columnconfigure(2, weight=1)

        ttk.Label(frame_login, text="Login", font=("Arial", 16, "bold")).grid(row=1, column=1, pady=2)
        ttk.Label(frame_login, text="Bem-Vindo ao SISPE", font=("Arial", 16, "bold")).grid(row=2, column=1, pady=2)

        ttk.Label(frame_login, text="Usuário:").grid(row=3, column=1, pady=5, sticky="W")
        self.campo_usuario_login = ttk.Entry(frame_login)
        self.campo_usuario_login.grid(row=4, column=1, pady=5, sticky="EW")

        ttk.Label(frame_login, text="Senha:").grid(row=5, column=1, pady=5, sticky="W")
        self.campo_senha_login = ttk.Entry(frame_login, show="*")
        self.campo_senha_login.grid(row=6, column=1, pady=5, sticky="EW")

        botao_login = ttk.Button(frame_login, text="Entrar", command=self.fazer_login)
        botao_login.grid(row=7, column=1, pady=23)


    def criar_usuario_admin(self):
        novo_usuario = self.campo_admin_novo_usuario.get()
        nova_senha = self.campo_admin_nova_senha.get()
        user_type = self.combo_admin_user_type.get()

        if not all([novo_usuario, nova_senha, user_type]):
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        if self.db.add_user(novo_usuario, nova_senha, user_type):
            messagebox.showinfo("Sucesso", f"Usuário '{novo_usuario}' ({user_type}) criado com sucesso!")
            self.campo_admin_novo_usuario.delete(0, tk.END)
            self.campo_admin_nova_senha.delete(0, tk.END)
        else:
            messagebox.showerror("Erro", "Nome de usuário já existe.")

    def configurar_interface_por_tipo(self):
        # Esconde todos os botões que dependem do tipo de usuário
        self.botao_registrar.pack_forget()
        self.botao_vinculo.pack_forget()
        self.botao_gerenciar_usuarios.pack_forget()
        self.botao_ver_alunos.pack_forget()

        # Mostra os botões com base no tipo de usuário
        if self.user_type in ('secretaria'):
           self.botao_gerenciar_usuarios.pack(padx=10, side=tk.LEFT)
           self.botao_vinculo.pack(padx=10, side=tk.LEFT)
        
        elif self.user_type in ('psicologa'):
            self.botao_registrar.pack(padx=20, side=tk.LEFT)

        elif self.user_type == 'pai':
            self.botao_ver_alunos.pack(padx=20, side=tk.LEFT)

    def criar_tela_principal(self):
        frame_principal = ttk.Frame(self.principal)
        self.frames["principal"] = frame_principal

        self.menu_frame = tk.Frame(frame_principal,bg="#e3c097")
        self.menu_frame.pack(side="top", fill="x")

        ttk.Label(self.menu_frame, text="SISPE", font=("Arial", 20, "bold"), style="azul.TLabel").pack(side="left", padx=40)

        self.botao_inicio = ttk.Button(
            self.menu_frame, text= "início",
            command=lambda: self.mostrar_frame("principal")
        ).pack(padx = 20,side=tk.LEFT)

        self.botao_gerenciar_usuarios = ttk.Button(
            self.menu_frame, text='Gerenciar Usuários',
            command=lambda: self.mostrar_frame("gestao")
        )
        self.botao_registrar = ttk.Button(
            self.menu_frame, text='Registrar aluno',
            command=self.ir_registro
        )
        self.botao_vinculo = ttk.Button(
            self.menu_frame, text="Vincular Pai ↔ Aluno",
            command=lambda: self.mostrar_frame("vinculo")
        )
        self.botao_ver_alunos = ttk.Button(
            self.menu_frame, text="Meus Filhos",
            command=lambda: [self.atualizar_alunos_pai(), self.mostrar_frame("ver_alunos")]
        )

        ttk.Button(self.menu_frame, text="Perfil", command=self.ir_perfil).pack(padx = 20,side=tk.LEFT)
        ttk.Button(self.menu_frame, text="Sair", command=self.fazer_logout).pack(padx=20,side=tk.RIGHT)

        self.conteudo_frame = tk.Frame(frame_principal, bg="white")
        self.conteudo_frame.pack(side="right", expand=True, fill="both")

        self.label_bem_vindo = ttk.Label(self.conteudo_frame, text="", font=("Arial", 14))
        self.label_bem_vindo.pack(pady=10)

    def criar_tela_gestao(self):
        frame_gestao = ttk.Frame(self.conteudo_frame, padding ='50 30 50 30', relief='groove' )
        self.frames['gestao'] = frame_gestao

        frame_gestao.grid_rowconfigure(0, weight=1)
        frame_gestao.grid_rowconfigure(9, weight=1)
        frame_gestao.grid_columnconfigure(0, weight=1)
        frame_gestao.grid_columnconfigure(2, weight=1)

        central_frame = ttk.Frame(frame_gestao)
        central_frame.grid(row=1, column=1, rowspan=8, sticky="nsew")

        central_frame.grid_columnconfigure(0, weight=1)
        central_frame.grid_columnconfigure(1, weight=1)

        ttk.Label(central_frame, text='cadastro de usuários',font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=10)

        ttk.Label(central_frame, text ='Nome do Usuário:').grid(row=1, column=0, padx=10, pady=5, sticky="W")
        self.campo_admin_novo_usuario = ttk.Entry(central_frame)
        self.campo_admin_novo_usuario.grid(row=1, column=1, padx=10, pady=5, sticky="EW")

        ttk.Label(central_frame, text="Senha:").grid(row=2, column=0, padx=10, pady=5, sticky="W")
        self.campo_admin_nova_senha = ttk.Entry(central_frame, show="*")
        self.campo_admin_nova_senha.grid(row=2, column=1, padx=10, pady=5, sticky="EW")

        ttk.Label(central_frame, text="Tipo de Usuário:").grid(row=3, column=0, padx=10, pady=5, sticky="W")
        self.combo_admin_user_type = ttk.Combobox(
            central_frame,
            values=['psicologa', 'secretaria', 'pai'],
            state='readonly'
        )
        self.combo_admin_user_type.grid(row=3, column=1, padx=10, pady=5, sticky="EW")
        self.combo_admin_user_type.set('pai') # Valor padrão

        # Botões de ação
        ttk.Button(central_frame, text="Criar Usuário", command=self.criar_usuario_admin).grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(central_frame, text="Voltar", command=lambda: self.mostrar_frame("principal")).grid(row=5, column=0, columnspan=2, pady=5)



    def criar_tela_registro(self):
        frame_registro = ttk.Frame(self.conteudo_frame, padding="50 30 50 30", relief="groove")
        self.frames["registro"] = frame_registro

        frame_registro.grid_rowconfigure(0, weight=1)
        frame_registro.grid_rowconfigure(9, weight=1)
        frame_registro.grid_columnconfigure(0, weight=1)
        frame_registro.grid_columnconfigure(2, weight=1)

        # Isso garante que tudo se mova junto
        central_frame = ttk.Frame(frame_registro)
        central_frame.grid(row=1, column=1, rowspan=8, sticky="nsew")

        # Configura as colunas do central_frame para que os widgets se centralizem nele
        central_frame.grid_columnconfigure(0, weight=1)
        central_frame.grid_columnconfigure(1, weight=1)
        
        # todos os widgets são colocados dentro do central_frame
        ttk.Label(central_frame, text='Registro de Aluno', font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=5)

        ttk.Label(central_frame, text="Nome:").grid(row=1, column=0, padx=10, pady=5, sticky="W")
        self.entry_nome = ttk.Entry(central_frame)
        self.entry_nome.grid(row=1, column=1, padx=10, pady=5, sticky="EW")

        ttk.Label(central_frame, text="Sala:").grid(row=2, column=0, padx=10, pady=5, sticky="W")
        self.entry_sala = ttk.Entry(central_frame)
        self.entry_sala.grid(row=2, column=1, padx=10, pady=5, sticky="EW")

        ttk.Label(central_frame, text="Série:").grid(row=3, column=0, padx=10, pady=5, sticky="W")
        self.entry_serie = ttk.Entry(central_frame)
        self.entry_serie.grid(row=3, column=1, padx=10, pady=5, sticky="EW")

        ttk.Label(central_frame, text="Nível de Gravidade:").grid(row=4, column=0,padx=10, pady=5, sticky="W")
        self.gravidade_combo = ttk.Combobox(central_frame, values=["Baixo", "Médio", "Alto"], state='readonly')
        self.gravidade_combo.grid(row=4, column=1, padx=10, pady=5, sticky="EW")

        ttk.Button(central_frame, text="Salvar", command=self.salvar_aluno).grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(central_frame, text="Voltar para a tela principal", command=lambda: self.mostrar_frame("principal")).grid(row=6, column=0, columnspan=2, pady=5)

        list_frame = ttk.Frame(central_frame)
        list_frame.grid(row=7, column=0, columnspan=2, padx=10, pady=5, sticky="nsew")

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Substituindo o Listbox pelo Treeview
        self.tree_alunos = ttk.Treeview(list_frame, columns=("Nome", "Sala", "Série", "Gravidade"), show="headings")
        self.tree_alunos.heading("Nome", text="Nome")
        self.tree_alunos.heading("Sala", text="Sala")
        self.tree_alunos.heading("Série", text="Série")
        self.tree_alunos.heading("Gravidade", text="Gravidade")
        
        self.tree_alunos.column("Nome", width=150)
        self.tree_alunos.column("Sala", width=50, anchor=tk.CENTER)
        self.tree_alunos.column("Série", width=50, anchor=tk.CENTER)
        self.tree_alunos.column("Gravidade", width=100)
        self.tree_alunos.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.tree_alunos.bind("<Double-1>", self.abrir_tela_observacoes)
        
        scrollbar.config(command=self.tree_alunos.yview)

        # Criei um novo frame para os botões de ação para melhor organização
        botoes_acao_frame = ttk.Frame(central_frame)
        botoes_acao_frame.grid(row=8, column=0, columnspan=2, pady=5)
        
        ttk.Button(botoes_acao_frame, text='editar', command=self.editar_aluno).pack(side='left', padx=5)
        ttk.Button(botoes_acao_frame, text='excluir', command=self.excluir_aluno).pack(side='left', padx=5)

    def criar_tela_perfil(self):
        frame_perfil = ttk.Frame(self.conteudo_frame, padding="50 30 50 30", relief="groove")
        self.frames["perfil"] = frame_perfil

        frame_perfil.grid_rowconfigure(0, weight=1)
        frame_perfil.grid_rowconfigure(9, weight=1)
        frame_perfil.grid_columnconfigure(0, weight=1)
        frame_perfil.grid_columnconfigure(2, weight=1)

        central_frame2 = ttk.Frame(frame_perfil)
        central_frame2.grid(row=1, column=1, rowspan=8, sticky="nsew")

        # Configura as colunas do central_frame para que os widgets se centralizem nele
        central_frame2.grid_columnconfigure(0, weight=1)
        central_frame2.grid_columnconfigure(1, weight=1)

        ttk.Label(central_frame2, text= 'perfil', font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=5)

        ttk.Button(central_frame2, text="Voltar", command=lambda: self.mostrar_frame("principal")).grid(row=6, column=0, columnspan=2, pady=5)

        ttk.Button(central_frame2, text="Excluir Conta", command=self.excluir_conta, style='Danger.TButton').grid(row=4, column=0, columnspan=2, pady=20)

        ttk.Button(central_frame2, text="Voltar", command=lambda: self.mostrar_frame("principal")).grid(row=6, column=0, columnspan=2, pady=5)
 
    # isso é pra criar uma tela dentro das informações de cada aluno
    def criar_tela_observacoes(self):
        frame_obs = ttk.Frame(self.conteudo_frame, padding='30 20 30 20', relief='groove')
        self.frames['observacoes'] = frame_obs 

        frame_obs.grid_rowconfigure(0, weight=1)
        frame_obs.grid_rowconfigure(5, weight=1)
        frame_obs.grid_columnconfigure(0, weight=1)

        self.label_obs_nome = ttk.Label(frame_obs, text='Nome do Aluno', font=('Arial', 16, 'bold'))
        self.label_obs_nome.grid(row=1, column=0, pady=(0, 10))

        self.label_obs_info = ttk.Label(frame_obs, text='Série: X | Sala: Y | Gravidade: Z')
        self.label_obs_info.grid(row=2, column=0, pady=(0, 20))

        ttk.Label(frame_obs, text="Relatório:").grid(row=3, column=0, sticky="W")

        text_frame = ttk.Frame(frame_obs)
        text_frame.grid(row=4, column=0, sticky="nsew")
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        frame_obs.grid_rowconfigure(4, weight=3)

        self.texto_observacoes = tk.Text(text_frame, height=10, width=50, wrap="word", font=("Arial", 11))
        self.texto_observacoes.grid(row=0, column=0, sticky="nsew")

        scrollbar_obs = ttk.Scrollbar(text_frame, orient="vertical", command=self.texto_observacoes.yview)
        scrollbar_obs.grid(row=0, column=1, sticky="ns")
        self.texto_observacoes.config(yscrollcommand=scrollbar_obs.set)

        botoes_frame = ttk.Frame(frame_obs)
        botoes_frame.grid(row=5, column=0, pady=(20, 0))

        ttk.Button(botoes_frame, text="Salvar Observações", command=self.salvar_observacoes).pack(side="left", padx=10)
        ttk.Button(botoes_frame, text="Voltar", command=lambda: self.mostrar_frame("registro")).pack(side="left", padx=10)

    def criar_tela_vinculo(self):
        frame_vinculo = ttk.Frame(self.conteudo_frame, padding="20 20 20 20", relief="groove")
        self.frames["vinculo"] = frame_vinculo

        ttk.Label(frame_vinculo, text="Vincular Pai a Aluno", font=("Arial", 16, "bold")).pack(pady=10)

        # Seletor de psicóloga
        ttk.Label(frame_vinculo, text="Selecione um Psicólogo:").pack(pady=5)
        self.combo_psicologas = ttk.Combobox(frame_vinculo, values=self.db.get_psicologas(), state="readonly")
        self.combo_psicologas.pack(pady=5)

        ttk.Button(frame_vinculo, text="Carregar Alunos", command=self.carregar_alunos_psicologa).pack(pady=5)

        # Lista de alunos
        self.tree_alunos_vinculo = ttk.Treeview(frame_vinculo, columns=("ID", "Nome", "Sala", "Série"), show="headings")
        self.tree_alunos_vinculo.heading("ID", text="ID")
        self.tree_alunos_vinculo.heading("Nome", text="Nome")
        self.tree_alunos_vinculo.heading("Sala", text="Sala")
        self.tree_alunos_vinculo.heading("Série", text="Série")
        self.tree_alunos_vinculo.pack(fill="both", expand=True, pady=10)

        # Seletor de pai
        ttk.Label(frame_vinculo, text="Selecione o Pai:").pack(pady=5)
        self.combo_pais = ttk.Combobox(frame_vinculo, values=self.db.get_pais(), state="readonly")
        self.combo_pais.pack(pady=5)

        # Botão de vínculo e saída
        ttk.Button(frame_vinculo, text="Vincular", command=self.vincular_pai_aluno).pack(pady=10)

        ttk.Button(frame_vinculo, text="Voltar", command=lambda:self.mostrar_frame('principal')).pack(pady=10, padx=10)

    def criar_tela_ver_alunos(self):
        frame_ver_alunos = ttk.Frame(self.conteudo_frame, padding="20 20 20 20", relief="groove")
        self.frames["ver_alunos"] = frame_ver_alunos

        ttk.Label(frame_ver_alunos, text="Meus Filhos", font=("Arial", 16, "bold")).pack(pady=10)

        self.tree_alunos_pai = ttk.Treeview(
            frame_ver_alunos,
            columns=("ID", "Nome", "Sala", "Série", "Gravidade"),
            show="headings"
        )
        self.tree_alunos_pai.heading("ID", text="ID")
        self.tree_alunos_pai.heading("Nome", text="Nome")
        self.tree_alunos_pai.heading("Sala", text="Sala")
        self.tree_alunos_pai.heading("Série", text="Série")
        self.tree_alunos_pai.heading("Gravidade", text="Gravidade")

        self.tree_alunos_pai.pack(fill="both", expand=True, pady=10)

        ttk.Button(frame_ver_alunos, text="Ver Detalhes", command=self.ver_detalhes_aluno).pack(pady=10)

        ttk.Button(frame_ver_alunos, text="Voltar", command=lambda: self.mostrar_frame("principal")).pack(pady=10)

    def mostrar_frame(self, nome_do_frame):
        if nome_do_frame == "registro":
            self.atualizar_exibicao()
    
        if nome_do_frame == "login":
            for frame in self.frames.values():
                frame.pack_forget()
            self.frames["login"].pack(fill="both", expand=True)
            return

        if nome_do_frame == "principal":
            for frame in self.frames.values():
                frame.pack_forget()
            self.frames["principal"].pack(fill="both", expand=True)
            return

        for frame in self.conteudo_frame.winfo_children():
            frame.pack_forget()

        frame = self.frames[nome_do_frame]
        frame.pack(fill="both", expand=True)

    def ir_perfil(self):
        self.mostrar_frame('perfil')

    def ir_registro(self):
        self.mostrar_frame("registro")


    def fazer_logout(self):
        # Limpa o usuário logado ao sair para garantir que a próxima sessão comece do zero
        self.usuario_logado = None
        self.mostrar_frame("login")

    def abrir_tela_observacoes(self, event):
        item_selecionado_id = self.tree_alunos.focus() 
        if not item_selecionado_id:
            return 

        self.aluno_id_observacao = item_selecionado_id
        aluno = self.db.get_aluno_by_id(self.aluno_id_observacao)

        if aluno:
            self.label_obs_nome.config(text=aluno.nome)
            self.label_obs_info.config(text=f"Série: {aluno.serie} | Sala: {aluno.sala} | Gravidade: {aluno.gravidade}")
            
            self.texto_observacoes.delete("1.0", tk.END)
            self.texto_observacoes.insert("1.0", aluno.observacoes or "")

            self.mostrar_frame("observacoes")

    # isso é pra funcionar quando clicar duas vezes :)
    def salvar_observacoes(self):
        if self.aluno_id_observacao is None:
            messagebox.showerror("Erro", "Nenhum aluno selecionado.")
            return

        novas_observacoes = self.texto_observacoes.get("1.0", tk.END).strip()

        self.db.aluno_observação(self.aluno_id_observacao, novas_observacoes)

        messagebox.showinfo("Sucesso", "Observações salvas com sucesso!")
        
        self.aluno_id_observacao = None
        self.mostrar_frame("registro")

    def vincular_pai_aluno(self):
        selecionado = self.tree_alunos_vinculo.selection()
        pai_username = self.combo_pais.get()

        if not selecionado:
            messagebox.showerror("Erro", "Selecione um aluno na lista.")
            return
        if not pai_username:
            messagebox.showerror("Erro", "Selecione um pai.")
            return

        aluno_id = self.tree_alunos_vinculo.item(selecionado, "values")[0]
        self.db.vincular_pai_aluno(aluno_id, pai_username)
        messagebox.showinfo("Sucesso", f"Aluno vinculado ao pai '{pai_username}' com sucesso!")

    def atualizar_exibicao(self):
        self.tree_alunos.delete(*self.tree_alunos.get_children())
        if self.usuario_logado:
            alunos_do_usuario = self.db.get_alunos_by_user(self.usuario_logado)
            for aluno in alunos_do_usuario:
                self.tree_alunos.insert("", "end", iid=aluno.id, values=(aluno.nome, aluno.sala, aluno.serie, aluno.gravidade))

    def salvar_aluno(self):
    # Verifica se o usuário logado tem permissão para salvar
        if self.user_type != 'psicologa':
            messagebox.showerror("Acesso Negado", "Apenas psicólogas podem registrar alunos.")
            return
    
        nome = self.entry_nome.get()
        sala = self.entry_sala.get()
        serie = self.entry_serie.get()
        gravidade = self.gravidade_combo.get()

        if not all([nome, sala, serie, gravidade]):
            messagebox.showerror("Registro", "Preencha todos os campos.")
            return
    
        try:
            sala = int(sala)
            serie = int(serie)
        except ValueError:
            messagebox.showerror("Registro", "Sala e Série devem ser números.")
            return
    
        if self.aluno_id_edicao is not None:
            self.db.update_aluno(self.aluno_id_edicao, nome, sala, serie, gravidade)
            messagebox.showinfo("Registro", "Aluno atualizado com sucesso!")
            self.aluno_id_edicao = None
        else:
            self.db.add_aluno(nome, sala, serie, gravidade, self.usuario_logado)
            messagebox.showinfo("Registro", "Aluno registrado com sucesso!")

        self.entry_nome.delete(0, tk.END)
        self.entry_sala.delete(0, tk.END)
        self.entry_serie.delete(0, tk.END)
        self.gravidade_combo.set('')

        self.atualizar_exibicao()
    
    def excluir_aluno(self):
        item_selecionado = self.tree_alunos.focus()
        
        if not item_selecionado:
            messagebox.showerror("Exclusão", "Selecione um aluno para excluir.")
            return

        aluno_id = item_selecionado
        aluno_nome = self.tree_alunos.item(item_selecionado, "values")[0]
    
        # Confirma a exclusão
        confirmar = messagebox.askyesno(
            "Confirmar Exclusão", 
            f"Tem certeza que deseja excluir o aluno '{aluno_nome}'?"
        )
    
        if confirmar:
            # Chama a função do banco de dados com o ID do aluno
            self.db.delete_aluno(aluno_id)
            self.atualizar_exibicao()
            messagebox.showinfo("Exclusão", f"Aluno '{aluno_nome}' excluído com sucesso.")

    def editar_aluno(self):
        item_selecionado = self.tree_alunos.focus()
        
        if not item_selecionado:
            messagebox.showerror("Edição", "Selecione um aluno para editar.")
            return
        
        # Pega os dados do aluno no Treeview para pré-preencher o formulário
        aluno_id_para_editar = item_selecionado
        valores = self.tree_alunos.item(item_selecionado, "values")

        self.entry_nome.delete(0, tk.END)
        self.entry_sala.delete(0, tk.END)
        self.entry_serie.delete(0, tk.END)
        self.gravidade_combo.set('')

        self.entry_nome.insert(0, valores[0])
        self.entry_sala.insert(0, valores[1])
        self.entry_serie.insert(0, valores[2])
        self.gravidade_combo.set(valores[3])

        # Armazena o ID do aluno a ser editado para o método salvar_aluno
        self.aluno_id_edicao = aluno_id_para_editar

    def atualizar_exibicao(self):
        self.tree_alunos.delete(*self.tree_alunos.get_children())

        # Atualiza o Treeview com os dados mais recentes do banco de dados
        if self.usuario_logado:
            alunos_do_usuario = self.db.get_alunos_by_user(self.usuario_logado)
            for aluno in alunos_do_usuario:
                self.tree_alunos.insert("", "end", iid=aluno.id, values=(aluno.nome, aluno.sala, aluno.serie, aluno.gravidade))

    def carregar_alunos_psicologa(self):
        psicologa = self.combo_psicologas.get()
        if not psicologa:
            messagebox.showerror("Erro", "Selecione uma psicóloga.")
            return

        self.tree_alunos_vinculo.delete(*self.tree_alunos_vinculo.get_children())
        alunos = self.db.get_alunos_by_user(psicologa)
        for aluno in alunos:
            self.tree_alunos_vinculo.insert(
                "", 
                "end", 
                values=(aluno.id, aluno.nome, aluno.sala, aluno.serie)
            )

    def ver_detalhes_aluno(self):
        selecionado = self.tree_alunos_pai.selection()
        if not selecionado:
            messagebox.showerror('Erro', 'Selecione um aluno')
            return
        
        aluno_id = selecionado[0]
        aluno = self.db.get_aluno_by_id(aluno_id)

        
        if aluno:
            detalhe_win = tk.Toplevel(self.principal)
            detalhe_win.title(f"Detalhes de {aluno.nome}")
            detalhe_win.geometry("400x300")

            ttk.Label(detalhe_win, text=f"Nome: {aluno.nome}", font=("Arial", 12, "bold")).pack(pady=5)
            ttk.Label(detalhe_win, text=f"Sala: {aluno.sala} | Série: {aluno.serie} | Gravidade: {aluno.gravidade}").pack(pady=5)

            ttk.Label(detalhe_win, text="Observações:").pack(pady=5)
            text_obs = tk.Text(detalhe_win, height=10, wrap="word")
            text_obs.insert("1.0", aluno.observacoes or "")
            text_obs.config(state="disabled")  # só leitura
            text_obs.pack(fill="both", expand=True, padx=10, pady=10)

    def atualizar_alunos_pai(self):
        if self.user_type != "pai":
            return

        self.tree_alunos_pai.delete(*self.tree_alunos_pai.get_children())
        alunos = self.db.get_alunos_by_pai(self.usuario_logado)
        for aluno in alunos:
            self.tree_alunos_pai.insert(
                "", "end", iid=aluno.id,
                values=(aluno.id, aluno.nome, aluno.sala, aluno.serie, aluno.gravidade)
            )

    def excluir_conta(self):
        resposta = messagebox.askyesno(
            "Confirmação de Exclusão",
            "Tem certeza que deseja excluir sua conta? Esta ação é definitiva e removerá todos os seus dados."
        )

        if resposta:
            username = self.usuario_logado
            self.db.delete_user(username) # ON DELETE CASCADE cuida dos alunos
            self.fazer_logout()
            messagebox.showinfo("Exclusão de Conta", "Sua conta foi excluída com sucesso.")

if __name__ == "__main__":
    teste = tk.Tk()
    style = ttk.Style()
    # tema
    style.theme_use('vista')
    # estilo do botão
    style.configure("Accent.TButton", font=("Arial", 12, "bold"), 
                    foreground="White", background="#0d3057", 
                    padding=10, borderwidth=0, relief="flat")
    style.map("Accent.TButton", background=[('active', '#0056b3')])
    
    style.configure("Danger.TButton", font=("Arial", 12, "bold"), 
                    foreground="red", background="#0d3057", 
                    padding=5, borderwidth=0, relief="solid", fieldbackground='white', bordercolor="#0d3057",
                    focuscolor="#0d3057")
    style.map("Danger.TButton", background=[('active', '#a30000')], foreground=[('active', '#ff3333')])
    # estilo de entrada (a parte onde escreve)
    style.configure("TEntry", padding=5, font=("Arial", 12), fieldbackground="white", 
                    foreground="#333333", borderwidth=1, relief="solid")

    style.configure("TLabel", foreground= "#3A0D0D")
    style.configure("azul.TLabel", foreground="#2c3e50", background="#e3c097")

    app = SISPE(teste)
    teste.mainloop()
