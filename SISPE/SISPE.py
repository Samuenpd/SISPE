import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
import hashlib
import sqlite3
import os

# --- CLASSES DE DADOS (Sem alteração na lógica) ---
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
        
    @staticmethod
    def from_dict(data):
        return Aluno(data['nome'], data['sala'], data['serie'], data['gravidade'])

class DatabaseManager:
    def __init__(self, db_name="sispe.db"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        db_path = os.path.join(base_dir, db_name) 
        self.conn = sqlite3.connect(db_path) # Alterado para usar o caminho completo
        self.cursor = self.conn.cursor()
        self.create_tables()

    def _hash_senha(self, senha):
        return hashlib.sha256(senha.encode()).hexdigest()

    def add_user(self, username, password, user_type):
        password_hash = self._hash_senha(password)
        try:
            self.cursor.execute("INSERT INTO usuarios (username, password_hash, user_type) VALUES (?, ?, ?)", (username, password_hash, user_type))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False
        
    def create_tables(self):
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
        return self.cursor.fetchone()

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
    
    def aluno_observação(self, aluno_id, observacao):
        self.cursor.execute('UPDATE alunos SET observacoes = ? WHERE id = ?', (observacao, aluno_id))
        self.conn.commit()

    def update_aluno(self, aluno_id, nome, sala, serie, gravidade):
        self.cursor.execute("UPDATE alunos SET nome = ?, sala = ?, serie = ?, gravidade = ? WHERE id = ?", (nome, sala, serie, gravidade, aluno_id))
        self.conn.commit()

    def delete_aluno(self, aluno_id):
        self.cursor.execute("DELETE FROM alunos WHERE id = ?", (aluno_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()

    def delete_user(self, username):
        self.cursor.execute("DELETE FROM usuarios WHERE username = ?", (username,))
        self.conn.commit()

    def vincular_pai_aluno(self, aluno_id, pai_username):
        try:
            self.cursor.execute("INSERT INTO alunos_pais (aluno_id, pai_id) VALUES (?, ?)", (aluno_id, pai_username))
            self.conn.commit()
            messagebox.showinfo("Sucesso", f"Aluno vinculado ao pai '{pai_username}' com sucesso!")
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

# --- CLASSE PRINCIPAL DA APLICAÇÃO ---
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
        self.aluno_id_observacao = None

        self.criar_tela_login()
        self.criar_tela_principal()

        self.mostrar_frame("login")

    def fazer_login(self):
        usuario = self.campo_usuario_login.get()
        senha = self.campo_senha_login.get()

        senha_hash = self.db._hash_senha(senha)
        result = self.db.get_user(usuario)

        if result and senha_hash == result[0]:
            self.usuario_logado = usuario
            self.user_type = result[1]

            self.campo_usuario_login.delete(0, ctk.END)
            self.campo_senha_login.delete(0, ctk.END)
            self.label_bem_vindo.configure(text=f"Bem-vindo, {self.usuario_logado}!")

            self.configurar_interface_por_tipo()
            
            # Cria as telas internas agora que o conteudo_frame já existe
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
        if messagebox.askokcancel("Sair", "Tem certeza que deseja sair?"):
            self.db.close()
            self.principal.destroy()

    def _hash_senha(self, senha):
        return hashlib.sha256(senha.encode()).hexdigest()

    def criar_tela_login(self):
        # Configurações gerais do CTk
        ctk.set_appearance_mode("light")  # Tema claro
        ctk.set_default_color_theme("blue")  # Tema base

        # Frame principal com fundo azul marinho
        self.frame_login = ctk.CTkFrame(self.principal, fg_color="#1E3A8A") 
        self.frames["login"] = self.frame_login
        self.frame_login.pack(fill="both", expand=True)

    # Container central para os campos (fundo bege claro)
        self.card_login = ctk.CTkFrame(self.frame_login, fg_color="#F5F5DC", corner_radius=15)
        self.card_login.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.4, relheight=0.5)

    # Título
        self.label_titulo = ctk.CTkLabel(self.card_login, text="SISPE", font=("Arial", 26, "bold"), text_color="#1E3A8A")
        self.label_titulo.pack(pady=(20, 10))

    # Campo Usuário
        self.campo_usuario_login = ctk.CTkEntry(self.card_login, placeholder_text="Usuário", fg_color="white", text_color="black")
        self.campo_usuario_login.pack(pady=10, padx=40, fill="x")

    # Campo Senha
        self.campo_senha_login = ctk.CTkEntry(self.card_login, placeholder_text="Senha", fg_color="white", text_color="black", show="*")
        self.campo_senha_login.pack(pady=10, padx=40, fill="x")

    # Botão Login (verde escuro)
        self.botao_login = ctk.CTkButton(
            self.card_login,
            text="Entrar",
            fg_color="#047857",  # Verde escuro
            hover_color="#065F46",
            corner_radius=20,
            command= self.fazer_login
        )
        self.botao_login.pack(pady=25)

    def criar_usuario_admin(self):
        novo_usuario = self.campo_admin_novo_usuario.get()
        nova_senha = self.campo_admin_nova_senha.get()
        user_type = self.combo_admin_user_type.get()

        if not all([novo_usuario, nova_senha, user_type]):
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        if self.db.add_user(novo_usuario, nova_senha, user_type):
            messagebox.showinfo("Sucesso", f"Usuário '{novo_usuario}' ({user_type}) criado com sucesso!")
            self.campo_admin_novo_usuario.delete(0, ctk.END)
            self.campo_admin_nova_senha.delete(0, ctk.END)
        else:
            messagebox.showerror("Erro", "Nome de usuário já existe.")

    def configurar_interface_por_tipo(self):
        # Esconde todos os botões que dependem do tipo de usuário
        self.botao_registrar.pack_forget()
        self.botao_vinculo.pack_forget()
        self.botao_gerenciar_usuarios.pack_forget()
        self.botao_ver_alunos.pack_forget()

        if self.user_type == 'secretaria':
            self.botao_gerenciar_usuarios.pack(padx=10, side=ctk.LEFT)
            self.botao_vinculo.pack(padx=10, side=ctk.LEFT)
        
        elif self.user_type == 'psicologa':
            self.botao_registrar.pack(padx=10, side=ctk.LEFT)

        elif self.user_type == 'pai':
            self.botao_ver_alunos.pack(padx=10, side=ctk.LEFT)

    def criar_tela_principal(self):
        frame_principal = ctk.CTkFrame(self.principal)
        self.frames["principal"] = frame_principal
        frame_principal.pack(fill="both", expand=True) # Adicionado para garantir visibilidade

        # O menu agora é um CTkFrame
        self.menu_frame = ctk.CTkFrame(frame_principal, fg_color="#2c3e50", corner_radius=0)
        self.menu_frame.pack(side="top", fill="x")

        self.botao_gerenciar_usuarios = ctk.CTkButton(self.menu_frame, text='Gerenciar Usuários', fg_color= "transparent", hover=False, command=lambda: self.mostrar_frame("gestao"))
        self.botao_registrar = ctk.CTkButton(self.menu_frame, text='Registrar Aluno', fg_color= "transparent", hover=False, command=self.ir_registro)
        self.botao_vinculo = ctk.CTkButton(self.menu_frame, text="Vincular Pai ↔ Aluno", fg_color= "transparent", hover=False, command=lambda: self.mostrar_frame("vinculo"))
        self.botao_ver_alunos = ctk.CTkButton(self.menu_frame, text="Meus Filhos", fg_color= "transparent", hover=False, command=lambda: [self.atualizar_alunos_pai(), self.mostrar_frame("ver_alunos")])

        ctk.CTkButton(self.menu_frame, text="Perfil", command=self.ir_perfil, fg_color= "transparent", hover=False, width=100).pack(padx=10, pady=10, side=ctk.LEFT)
        ctk.CTkButton(self.menu_frame, text="Sair", command=self.fazer_logout, fg_color= "transparent", hover=False, width=100).pack(padx=10, pady=10, side=ctk.RIGHT)

        self.conteudo_frame = ctk.CTkFrame(frame_principal, fg_color="transparent")
        self.conteudo_frame.pack(side="bottom", expand=True, fill="both", padx=10, pady=10)

        self.label_bem_vindo = ctk.CTkLabel(self.conteudo_frame, text="", font=("Arial", 20))
        self.label_bem_vindo.pack(pady=20)
    
    def _configurar_estilo_treeview(self):
        style = ttk.Style()
        
        # Use o tema 'clam', que oferece melhor suporte para personalização de cores
        style.theme_use("clam")
        
        # Cores que combinam com o tema "blue" (light) do CustomTkinter
        # Fundo do Treeview e Fieldbackground
        bg_color = "#ebebeb" 
        # Cor de seleção (o mesmo azul do botão padrão)
        selected_color = "#3b8ed8" 
        # Cor do texto
        text_color = "#363636"
        # Fundo do cabeçalho
        header_bg_color = "#e5e5e5" 

        # Configura o estilo para o corpo do Treeview
        style.configure("Treeview", 
                        background=bg_color, 
                        foreground=text_color, 
                        fieldbackground=bg_color, 
                        borderwidth=0)
        
        # Mapeia a cor de seleção
        style.map('Treeview', 
                  background=[('selected', selected_color)],
                  foreground=[('selected', 'white')])
        
        # Configura o estilo para o cabeçalho
        style.configure("Treeview.Heading", 
                        background=header_bg_color, 
                        foreground=text_color, 
                        relief="flat", 
                        font=('Arial', 10, 'bold'))
        
        # Efeito de hover para o cabeçalho
        style.map("Treeview.Heading", background=[('active', selected_color)])

    def criar_tela_gestao(self):
        frame_gestao = ctk.CTkFrame(self.conteudo_frame)
        self.frames['gestao'] = frame_gestao
        frame_gestao.pack(expand=True)

        ctk.CTkLabel(frame_gestao, text='Cadastro de Usuários', font=("Arial", 18, "bold")).grid(row=0, column=0, columnspan=2, padx=20, pady=20)

        ctk.CTkLabel(frame_gestao, text='Nome do Usuário:').grid(row=1, column=0, padx=10, pady=10, sticky="w")
        self.campo_admin_novo_usuario = ctk.CTkEntry(frame_gestao)
        self.campo_admin_novo_usuario.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkLabel(frame_gestao, text="Senha:").grid(row=2, column=0, padx=10, pady=10, sticky="w")
        self.campo_admin_nova_senha = ctk.CTkEntry(frame_gestao, show="*")
        self.campo_admin_nova_senha.grid(row=2, column=1, padx=10, pady=10)

        ctk.CTkLabel(frame_gestao, text="Tipo de Usuário:").grid(row=3, column=0, padx=10, pady=10, sticky="w")
        self.combo_admin_user_type = ctk.CTkComboBox(frame_gestao, values=['psicologa', 'secretaria', 'pai'], state='readonly')
        self.combo_admin_user_type.grid(row=3, column=1, padx=10, pady=10)
        self.combo_admin_user_type.set('pai')

        ctk.CTkButton(frame_gestao, text="Criar Usuário", command=self.criar_usuario_admin).grid(row=4, column=0, columnspan=2, padx=20, pady=20)

    def criar_tela_registro(self):
        self._configurar_estilo_treeview()
        frame_registro = ctk.CTkFrame(self.conteudo_frame, fg_color="transparent")
        self.frames["registro"] = frame_registro
        
        # Frame do formulário
        form_frame = ctk.CTkFrame(frame_registro)
        form_frame.pack(pady=10, padx=10, fill="x")

        ctk.CTkLabel(form_frame, text='Registro de Aluno', font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=4, pady=10)

        ctk.CTkLabel(form_frame, text="Nome:").grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_nome = ctk.CTkEntry(form_frame)
        self.entry_nome.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(form_frame, text="Sala:").grid(row=1, column=2, padx=10, pady=5, sticky="w")
        self.entry_sala = ctk.CTkEntry(form_frame, width=80)
        self.entry_sala.grid(row=1, column=3, padx=10, pady=5)

        ctk.CTkLabel(form_frame, text="Série:").grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.entry_serie = ctk.CTkEntry(form_frame, width=80)
        self.entry_serie.grid(row=2, column=1, padx=10, pady=5, sticky="w")

        ctk.CTkLabel(form_frame, text="Nível de Gravidade:").grid(row=2, column=2, padx=10, pady=5, sticky="w")
        self.gravidade_combo = ctk.CTkComboBox(form_frame, values=["Baixo", "Médio", "Alto"], state='readonly')
        self.gravidade_combo.grid(row=2, column=3, padx=10, pady=5, sticky="ew")
        
        form_frame.grid_columnconfigure(1, weight=1)

        # Botões do formulário
        botoes_form_frame = ctk.CTkFrame(frame_registro, fg_color="transparent")
        botoes_form_frame.pack(pady=5)
        ctk.CTkButton(botoes_form_frame, text="Salvar", command=self.salvar_aluno).pack(side="left", padx=10)

        # Frame da lista (Treeview)
        list_frame = ctk.CTkFrame(frame_registro)
        list_frame.pack(pady=10, padx=10, fill="both", expand=True)

        self.tree_alunos = ttk.Treeview(list_frame, columns=("Nome", "Sala", "Série", "Gravidade"), show="headings")
        self.tree_alunos.heading("Nome", text="Nome")
        self.tree_alunos.heading("Sala", text="Sala")
        self.tree_alunos.heading("Série", text="Série")
        self.tree_alunos.heading("Gravidade", text="Gravidade")
        
        self.tree_alunos.column("Nome", width=250)
        self.tree_alunos.column("Sala", width=50, anchor=ctk.CENTER)
        self.tree_alunos.column("Série", width=50, anchor=ctk.CENTER)
        self.tree_alunos.column("Gravidade", width=100)
        
        scrollbar = ttk.Scrollbar(list_frame, orient=ctk.VERTICAL, command=self.tree_alunos.yview)
        self.tree_alunos.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=ctk.RIGHT, fill=ctk.Y)
        self.tree_alunos.pack(side=ctk.LEFT, fill=ctk.BOTH, expand=True)
        self.tree_alunos.bind("<Double-1>", self.abrir_tela_observacoes)
        
        botoes_acao_frame = ctk.CTkFrame(frame_registro, fg_color="transparent")
        botoes_acao_frame.pack(pady=5)
        ctk.CTkButton(botoes_acao_frame, text='Editar', command=self.editar_aluno).pack(side='left', padx=5)
        ctk.CTkButton(botoes_acao_frame, text='Excluir', command=self.excluir_aluno).pack(side='left', padx=5)

    def criar_tela_perfil(self):
        frame_perfil = ctk.CTkFrame(self.conteudo_frame)
        self.frames["perfil"] = frame_perfil
        frame_perfil.pack(expand=True)
        
        ctk.CTkLabel(frame_perfil, text='Perfil do Usuário', font=("Arial", 18, "bold")).pack(pady=20, padx=40)
        ctk.CTkButton(frame_perfil, text="Excluir Conta", command=self.excluir_conta, fg_color="#D32F2F", hover_color="#B71C1C").pack(pady=10)
 
    def criar_tela_observacoes(self):
        frame_obs = ctk.CTkFrame(self.conteudo_frame)
        self.frames['observacoes'] = frame_obs 
        frame_obs.pack(fill="both", expand=True, padx=20, pady=20)
        
        frame_obs.grid_rowconfigure(2, weight=1)
        frame_obs.grid_columnconfigure(0, weight=1)

        self.label_obs_nome = ctk.CTkLabel(frame_obs, text='Nome do Aluno', font=('Arial', 18, 'bold'))
        self.label_obs_nome.grid(row=0, column=0, pady=(0, 10))

        self.label_obs_info = ctk.CTkLabel(frame_obs, text='Série: X | Sala: Y | Gravidade: Z')
        self.label_obs_info.grid(row=1, column=0, pady=(0, 20))
        
        # CTkTextbox substitui o tk.Text e já vem com scrollbar
        self.texto_observacoes = ctk.CTkTextbox(frame_obs, wrap="word", font=("Arial", 12))
        self.texto_observacoes.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        botoes_frame = ctk.CTkFrame(frame_obs, fg_color="transparent")
        botoes_frame.grid(row=3, column=0, pady=10)
        ctk.CTkButton(botoes_frame, text="Salvar Observações", command=self.salvar_observacoes).pack(side="left", padx=10)

    def criar_tela_vinculo(self):
        self._configurar_estilo_treeview()
        frame_vinculo = ctk.CTkFrame(self.conteudo_frame)
        self.frames["vinculo"] = frame_vinculo
        frame_vinculo.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame_vinculo, text="Vincular Pai a Aluno", font=("Arial", 16, "bold")).pack(pady=10)
        
        ctk.CTkLabel(frame_vinculo, text="Selecione um Psicólogo:").pack(pady=(10,0))
        self.combo_psicologas = ctk.CTkComboBox(frame_vinculo, values=self.db.get_psicologas(), state="readonly", width=250)
        self.combo_psicologas.pack(pady=5)
        ctk.CTkButton(frame_vinculo, text="Carregar Alunos", command=self.carregar_alunos_psicologa).pack(pady=5)

        tree_frame = ctk.CTkFrame(frame_vinculo)
        tree_frame.pack(fill="both", expand=True, pady=10)
        self.tree_alunos_vinculo = ttk.Treeview(tree_frame, columns=("ID", "Nome", "Sala", "Série"), show="headings")
        self.tree_alunos_vinculo.heading("ID", text="ID")
        self.tree_alunos_vinculo.heading("Nome", text="Nome")
        self.tree_alunos_vinculo.heading("Sala", text="Sala")
        self.tree_alunos_vinculo.heading("Série", text="Série")
        self.tree_alunos_vinculo.pack(fill="both", expand=True)

        ctk.CTkLabel(frame_vinculo, text="Selecione o Pai:").pack(pady=(10,0))
        self.combo_pais = ctk.CTkComboBox(frame_vinculo, values=self.db.get_pais(), state="readonly", width=250)
        self.combo_pais.pack(pady=5)

        ctk.CTkButton(frame_vinculo, text="Vincular", command=self.vincular_pai_aluno).pack(pady=10)

    def criar_tela_ver_alunos(self):
        self._configurar_estilo_treeview()
        frame_ver_alunos = ctk.CTkFrame(self.conteudo_frame)
        self.frames["ver_alunos"] = frame_ver_alunos
        frame_ver_alunos.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(frame_ver_alunos, text="Meus Filhos", font=("Arial", 16, "bold")).pack(pady=10)
        
        tree_frame = ctk.CTkFrame(frame_ver_alunos)
        tree_frame.pack(fill="both", expand=True, pady=10)
        self.tree_alunos_pai = ttk.Treeview(tree_frame, columns=("ID", "Nome", "Sala", "Série", "Gravidade"), show="headings")
        self.tree_alunos_pai.heading("ID", text="ID")
        self.tree_alunos_pai.heading("Nome", text="Nome")
        self.tree_alunos_pai.heading("Sala", text="Sala")
        self.tree_alunos_pai.heading("Série", text="Série")
        self.tree_alunos_pai.heading("Gravidade", text="Gravidade")
        self.tree_alunos_pai.pack(fill="both", expand=True)

        ctk.CTkButton(frame_ver_alunos, text="Ver Detalhes", command=self.ver_detalhes_aluno).pack(pady=10)

    def mostrar_frame(self, nome_do_frame):
        # Esconde todos os frames de conteúdo e o frame de login
        for frame in self.frames.values():
            if frame.master in [self.principal, self.conteudo_frame]:
                frame.pack_forget()

        if nome_do_frame == "login":
            self.menu_frame.pack_forget() # Esconde o menu principal
            self.conteudo_frame.pack_forget()
            self.frames["login"].pack(fill="both", expand=True)
        elif nome_do_frame == "principal":
            self.frames["principal"].pack(fill="both", expand=True)
            self.menu_frame.pack(side="top", fill="x") # Mostra o menu
            self.conteudo_frame.pack(side="bottom", expand=True, fill="both", padx=10, pady=10)
            # Limpa o frame de conteúdo para mostrar a msg de bem-vindo
            for widget in self.conteudo_frame.winfo_children():
                if widget != self.label_bem_vindo:
                    widget.pack_forget()
            self.label_bem_vindo.pack(pady=20)
        else:
            # Garante que a estrutura principal está visível
            self.frames["principal"].pack(fill="both", expand=True)
            self.menu_frame.pack(side="top", fill="x")
            self.conteudo_frame.pack(side="bottom", expand=True, fill="both", padx=10, pady=10)

            # Limpa o frame de conteúdo antes de mostrar o novo frame
            for widget in self.conteudo_frame.winfo_children():
                widget.pack_forget()
            
            # Mostra o frame solicitado dentro do frame de conteúdo
            frame = self.frames[nome_do_frame]
            frame.pack(fill="both", expand=True)
        
        # Atualiza as listas quando as telas são exibidas
        if nome_do_frame == "registro":
            self.atualizar_exibicao_alunos()
        if nome_do_frame == "vinculo":
            # Atualiza as listas de psicólogas e pais
            self.combo_psicologas.configure(values=self.db.get_psicologas())
            self.combo_pais.configure(values=self.db.get_pais())
            
    def ir_perfil(self):
        self.mostrar_frame('perfil')

    def ir_registro(self):
        self.mostrar_frame("registro")

    def fazer_logout(self):
        self.usuario_logado = None
        self.user_type = None
        self.mostrar_frame("login")

    def abrir_tela_observacoes(self, event):
        item_selecionado_id = self.tree_alunos.focus() 
        if not item_selecionado_id:
            return 
        self.aluno_id_observacao = item_selecionado_id
        aluno = self.db.get_aluno_by_id(self.aluno_id_observacao)
        if aluno:
            self.label_obs_nome.configure(text=aluno.nome)
            self.label_obs_info.configure(text=f"Série: {aluno.serie} | Sala: {aluno.sala} | Gravidade: {aluno.gravidade}")
            
            self.texto_observacoes.delete("1.0", ctk.END)
            self.texto_observacoes.insert("1.0", aluno.observacoes or "")
            self.mostrar_frame("observacoes")

    def salvar_observacoes(self):
        if self.aluno_id_observacao is None:
            messagebox.showerror("Erro", "Nenhum aluno selecionado.")
            return
        novas_observacoes = self.texto_observacoes.get("1.0", ctk.END).strip()
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

    def atualizar_exibicao_alunos(self):
        self.tree_alunos.delete(*self.tree_alunos.get_children())
        if self.usuario_logado:
            alunos_do_usuario = self.db.get_alunos_by_user(self.usuario_logado)
            for aluno in alunos_do_usuario:
                self.tree_alunos.insert("", "end", iid=aluno.id, values=(aluno.nome, aluno.sala, aluno.serie, aluno.gravidade))

    def salvar_aluno(self):
        if self.user_type != 'psicologa':
            messagebox.showerror("Acesso Negado", "Apenas psicólogas podem registrar alunos.")
            return
    
        nome, sala, serie, gravidade = self.entry_nome.get(), self.entry_sala.get(), self.entry_serie.get(), self.gravidade_combo.get()
        if not all([nome, sala, serie, gravidade]):
            messagebox.showerror("Registro", "Preencha todos os campos.")
            return
    
        try:
            int(sala); int(serie)
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

        self.entry_nome.delete(0, ctk.END)
        self.entry_sala.delete(0, ctk.END)
        self.entry_serie.delete(0, ctk.END)
        self.gravidade_combo.set('')
        self.atualizar_exibicao_alunos()
    
    def excluir_aluno(self):
        item_selecionado = self.tree_alunos.focus()
        if not item_selecionado:
            messagebox.showerror("Exclusão", "Selecione um aluno para excluir.")
            return
        
        aluno_id = item_selecionado
        aluno_nome = self.tree_alunos.item(item_selecionado, "values")[0]
    
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o aluno '{aluno_nome}'?"):
            self.db.delete_aluno(aluno_id)
            self.atualizar_exibicao_alunos()
            messagebox.showinfo("Exclusão", f"Aluno '{aluno_nome}' excluído com sucesso.")

    def editar_aluno(self):
        item_selecionado = self.tree_alunos.focus()
        if not item_selecionado:
            messagebox.showerror("Edição", "Selecione um aluno para editar.")
            return
        
        valores = self.tree_alunos.item(item_selecionado, "values")
        self.entry_nome.delete(0, ctk.END); self.entry_nome.insert(0, valores[0])
        self.entry_sala.delete(0, ctk.END); self.entry_sala.insert(0, valores[1])
        self.entry_serie.delete(0, ctk.END); self.entry_serie.insert(0, valores[2])
        self.gravidade_combo.set(valores[3])
        self.aluno_id_edicao = item_selecionado

    def carregar_alunos_psicologa(self):
        psicologa = self.combo_psicologas.get()
        if not psicologa:
            messagebox.showerror("Erro", "Selecione uma psicóloga.")
            return
        self.tree_alunos_vinculo.delete(*self.tree_alunos_vinculo.get_children())
        alunos = self.db.get_alunos_by_user(psicologa)
        for aluno in alunos:
            self.tree_alunos_vinculo.insert("", "end", values=(aluno.id, aluno.nome, aluno.sala, aluno.serie))

    def ver_detalhes_aluno(self):
        selecionado = self.tree_alunos_pai.selection()
        if not selecionado:
            messagebox.showerror('Erro', 'Selecione um aluno')
            return
        
        aluno_id = selecionado[0]
        aluno = self.db.get_aluno_by_id(aluno_id)
        if aluno:
            detalhe_win = ctk.CTkToplevel(self.principal)
            detalhe_win.title(f"Detalhes de {aluno.nome}")
            detalhe_win.geometry("400x350")
            detalhe_win.transient(self.principal) # Mantém a janela no topo
            
            ctk.CTkLabel(detalhe_win, text=f"Nome: {aluno.nome}", font=("Arial", 14, "bold")).pack(pady=5)
            ctk.CTkLabel(detalhe_win, text=f"Sala: {aluno.sala} | Série: {aluno.serie} | Gravidade: {aluno.gravidade}").pack(pady=5)
            
            text_obs = ctk.CTkTextbox(detalhe_win, wrap="word")
            text_obs.pack(fill="both", expand=True, padx=10, pady=10)
            text_obs.insert("1.0", aluno.observacoes or "Nenhuma observação registrada.")
            text_obs.configure(state="disabled")

    def atualizar_alunos_pai(self):
        if self.user_type != "pai": return
        self.tree_alunos_pai.delete(*self.tree_alunos_pai.get_children())
        alunos = self.db.get_alunos_by_pai(self.usuario_logado)
        for aluno in alunos:
            self.tree_alunos_pai.insert("", "end", iid=aluno.id, values=(aluno.id, aluno.nome, aluno.sala, aluno.serie, aluno.gravidade))

    def excluir_conta(self):
        if messagebox.askyesno("Confirmação de Exclusão", "Tem certeza? Esta ação é definitiva e removerá todos os seus dados."):
            self.db.delete_user(self.usuario_logado)
            self.fazer_logout()
            messagebox.showinfo("Exclusão de Conta", "Sua conta foi excluída com sucesso.")

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")  # Define o tema (Dark, Light, System)
    ctk.set_default_color_theme("blue") # Define a cor (blue, green, dark-blue)
    
    root = ctk.CTk()
    app = SISPE(root)
    root.mainloop()
