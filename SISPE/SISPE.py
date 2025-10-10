import customtkinter as ctk
from tkinter import messagebox
from tkinter import ttk
import bcrypt
import sqlite3
import os
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import openpyxl

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
        return bcrypt.hashpw(senha.encode(), bcrypt.gensalt()).decode()

    def _verificar_senha(self, senha, senha_hash):
        return bcrypt.checkpw(senha.encode(), senha_hash.encode())

    def add_user(self, username, password, user_type):
        # Validate inputs
        if not username or not password or not user_type:
            raise ValueError("Todos os campos são obrigatórios.")
        if len(username) > 50 or len(password) > 50:
            raise ValueError("Usuário e senha devem ter no máximo 50 caracteres.")
        if user_type not in ["pai", "psicologa", "secretaria"]:
            raise ValueError("Tipo de usuário inválido.")

        password_hash = self._hash_senha(password)
        try:
            self.cursor.execute(
                "INSERT INTO usuarios (username, password_hash, user_type) VALUES (?, ?, ?)",
                (username, password_hash, user_type)
            )
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
        # Use parameterized query to prevent SQL injection
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

    def delete_aluno(self, aluno_id, pasta_relatorios=None):
        aluno = self.get_aluno_by_id(aluno_id)
        self.cursor.execute("DELETE FROM alunos WHERE id = ?", (aluno_id,))
        self.conn.commit()

        if aluno and pasta_relatorios:
            nome_limpo = aluno.nome.replace(" ", "_").replace("/", "-")
            arquivo_pdf = os.path.join(pasta_relatorios, f"Relatorio_{aluno.id}_{nome_limpo}.pdf")
            if os.path.exists(arquivo_pdf):
                try:
                    os.remove(arquivo_pdf)
                except Exception as e:
                    print(f"Erro ao excluir PDF: {e}")

    def close(self):
        self.conn.close()

    def delete_user(self, username):
        self.cursor.execute("DELETE FROM usuarios WHERE username = ?", (username,))
        self.conn.commit()

    def vincular_pai_aluno(self, aluno_id, pai_username):
        try:
            self.cursor.execute("INSERT INTO alunos_pais (aluno_id, pai_id) VALUES (?, ?)", (aluno_id, pai_username))
            self.conn.commit()
            messagebox.showinfo("Sucesso", f"Aluno vinculado a '{pai_username}' com sucesso!")
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

    def exportar_aluno_pdf(self, aluno_id, pasta_destino):
        aluno = self.get_aluno_by_id(aluno_id)
        if not aluno:
            return None

        os.makedirs(pasta_destino, exist_ok=True)
        nome_limpo = aluno.nome.replace(" ", "_").replace("/", "-")
        arquivo = os.path.join(pasta_destino, f"Relatorio_{aluno.id}_{nome_limpo}.pdf")

        c = canvas.Canvas(arquivo, pagesize=A4)
        largura, altura = A4

        c.setFont("Helvetica-Bold", 14)
        c.drawString(50, altura - 50, "Relatório do Aluno")

        c.setFont("Helvetica", 12)
        y = altura - 100
        c.drawString(50, y, f"ID: {aluno.id}")
        c.drawString(50, y - 20, f"Nome: {aluno.nome}")
        c.drawString(50, y - 40, f"Sala: {aluno.sala}")
        c.drawString(50, y - 60, f"Série: {aluno.serie}")
        c.drawString(50, y - 80, f"Gravidade: {aluno.gravidade}")

        c.setFont("Helvetica-Bold", 12)
        c.drawString(50, y - 120, "Observações:")
        c.setFont("Helvetica", 10)

        texto = aluno.observacoes or "Nenhuma observação registrada."
        linhas = texto.split("\n")
        y_texto = y - 140
        for linha in linhas:
            c.drawString(60, y_texto, linha)
            y_texto -= 15
            if y_texto < 50:
                c.showPage()
                y_texto = altura - 50
                c.setFont("Helvetica", 10)

        c.save()
        return arquivo

class SISPE:
    def __init__(self, principal):
        self.principal = principal
        principal.title("SISPE")
        principal.geometry("900x600")
        principal.protocol("WM_DELETE_WINDOW", self.on_closing)

        desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
        self.pasta_relatorios = os.path.join(desktop_path, "relatorios")
        os.makedirs(self.pasta_relatorios, exist_ok=True)

        self.frames = {}
        self.usuario_logado = None
        self.db = DatabaseManager()
        self.aluno_id_edicao = None
        self.aluno_id_observacao = None

        self.criar_tela_login()
        self.criar_tela_principal()
        self.criar_tela_gestao()
        self.criar_tela_registro()
        self.criar_tela_perfil()
        self.criar_tela_observacoes()
        self.criar_tela_vinculo()
        self.criar_tela_ver_alunos()

        self.mostrar_frame("login")

    def aplicar_efeito_hover(self, botao, escala=1.1,cor_hover="#2563EB"):
        fonte_original = botao.cget("font")  # Isso é um objeto CTkFont
        tamanho_original = fonte_original.cget("size")
        raio_original = botao.cget("corner_radius")
        cor_original = botao.cget("text_color")

        def ao_entrar(_):
            nova_fonte = ctk.CTkFont(family=fonte_original.cget("family"),
                                     size=int(tamanho_original * escala),
                                     weight=fonte_original.cget("weight"))
            botao.configure(font=nova_fonte, corner_radius=int(raio_original * escala),
            text_color= cor_hover)

        def ao_sair(_):
            botao.configure(font=fonte_original, corner_radius=raio_original, text_color= cor_original)

        botao.bind("<Enter>", ao_entrar)
        botao.bind("<Leave>", ao_sair)

    def fazer_login(self):
        usuario = self.campo_usuario_login.get().strip()
        senha = self.campo_senha_login.get().strip()

        if not usuario or not senha:
            messagebox.showerror("Login", "Usuário e senha são obrigatórios.")
            return

        result = self.db.get_user(usuario)
        if result:
            senha_hash = result[0]
            try:
                if self.db._verificar_senha(senha, senha_hash):
                    if not senha_hash.startswith("$2b$"):
                        novo_hash = self.db._hash_senha(senha)
                        self.db.cursor.execute("UPDATE usuarios SET password_hash = ? WHERE username = ?", (novo_hash, usuario))
                        self.db.conn.commit()

                    self.usuario_logado = usuario
                    self.user_type = result[1]

                    self.campo_usuario_login.delete(0, ctk.END)
                    self.campo_senha_login.delete(0, ctk.END)
                    self.label_bem_vindo.configure(text=f"Bem-vindo, {self.usuario_logado}!")

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
            except ValueError:
                messagebox.showerror("Erro", "O hash da senha é inválido. Entre em contato com o administrador.")
        else:
            messagebox.showerror("Login", "Usuário ou senha incorretos.")

    def on_closing(self):
        if messagebox.askokcancel("Sair", "Tem certeza que deseja sair?"):
            self.db.close()
            self.principal.destroy()

    def criar_tela_login(self):
        ctk.set_appearance_mode("light")
        ctk.set_default_color_theme("blue")

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
        senha_container = ctk.CTkFrame(self.card_login, fg_color="transparent")
        senha_container.pack(pady=10, padx=40, fill="x")

        self.campo_senha_login = ctk.CTkEntry(senha_container, placeholder_text="Senha", fg_color="white", text_color="black", show="•")
        self.campo_senha_login.pack(side="left", fill="x", expand=True)

        self.mostrar_senha = False
        self.botao_mostrar_senha = ctk.CTkButton(
            senha_container,
            text="🔒",
            command=self.alternar_visibilidade_senha,
            fg_color="transparent",
            hover=False,
            width=10,
            text_color="black"
        )
        self.botao_mostrar_senha.pack(side="right", padx=5)


        # Botão Login (verde escuro)
        self.botao_login = ctk.CTkButton(
            self.card_login,
            text="Entrar",
            fg_color="#047857",
            hover_color="#065F46",
            corner_radius=20,
            command= self.fazer_login
        )
        self.botao_login.pack(pady=25)

    def alternar_visibilidade_senha(self):
        if self.mostrar_senha:
            self.campo_senha_login.configure(show="•")
            self.botao_mostrar_senha.configure(text="🔒")
        else:
            self.campo_senha_login.configure(show="")
            self.botao_mostrar_senha.configure(text="🔓")
        self.mostrar_senha = not self.mostrar_senha

    def criar_usuario_admin(self):
        novo_usuario = self.campo_admin_novo_usuario.get().strip()
        nova_senha = self.campo_admin_nova_senha.get().strip()
        user_type = self.combo_admin_user_type.get().strip()

        if not all([novo_usuario, nova_senha, user_type]):
            messagebox.showerror("Erro", "Preencha todos os campos.")
            return

        if len(novo_usuario) > 50 or len(nova_senha) > 50:
            messagebox.showerror("Erro", "Usuário e senha devem ter no máximo 50 caracteres.")
            return

        if user_type not in ["psicologa", "secretaria", "responsável"]:
            messagebox.showerror("Erro", "Tipo de usuário inválido.")
            return

        if user_type == "responsável":
            user_type = "pai"

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
        frame_principal.pack(fill="both", expand=True)

        # Menu superior
        self.menu_frame = ctk.CTkFrame(frame_principal, fg_color="#1E3A8A", corner_radius=0)
        self.menu_frame.pack(side="top", fill="x")

        # === BOTÕES DO MENU ===
        self.botao_inicio = ctk.CTkButton(
            self.menu_frame, text='Início',
            fg_color="transparent", hover=False,
            command=lambda: self.mostrar_frame("principal"),
            width=100, height=35
        )
        self.botao_inicio.pack(padx=10, pady=10, side=ctk.LEFT)
        self.aplicar_efeito_hover(self.botao_inicio)

        self.botao_gerenciar_usuarios = ctk.CTkButton(
            self.menu_frame, text='Gerenciar Usuários',
            fg_color="transparent", hover=False,
            command=lambda: self.mostrar_frame("gestao"),
            width=150, height=35
        )
        self.botao_gerenciar_usuarios.pack(padx=10, pady=10, side=ctk.LEFT)
        self.aplicar_efeito_hover(self.botao_gerenciar_usuarios)

        self.botao_registrar = ctk.CTkButton(
            self.menu_frame, text='Registrar Aluno',
            fg_color="transparent", hover=False,
            command=self.ir_registro,
            width=130, height=35
        )
        self.botao_registrar.pack(padx=10, pady=10, side=ctk.LEFT)
        self.aplicar_efeito_hover(self.botao_registrar)

        self.botao_vinculo = ctk.CTkButton(
            self.menu_frame, text="Vincular Responsável ↔ Aluno",
            fg_color="transparent", hover=False,
            command=lambda: self.mostrar_frame("vinculo"),
            width=160, height=35
        )
        self.botao_vinculo.pack(padx=10, pady=10, side=ctk.LEFT)
        self.aplicar_efeito_hover(self.botao_vinculo)

        self.botao_ver_alunos = ctk.CTkButton(
            self.menu_frame, text="Meus Filhos",
            fg_color="transparent", hover=False,
            command=lambda: [self.atualizar_alunos_pai(), self.mostrar_frame("ver_alunos")],
            width=120, height=35
        )
        self.botao_ver_alunos.pack(padx=10, pady=10, side=ctk.LEFT)
        self.aplicar_efeito_hover(self.botao_ver_alunos)

        # Botão Perfil
        self.botao_perfil = ctk.CTkButton(
            self.menu_frame, text="Perfil",
            command=self.ir_perfil,
            fg_color="transparent", hover=False,
            width=100, height=35
        )
        self.botao_perfil.pack(padx=10, pady=10, side=ctk.LEFT)
        self.aplicar_efeito_hover(self.botao_perfil)

        # Botão Sair
        self.botao_sair = ctk.CTkButton(
            self.menu_frame, text="Sair",
            command=self.fazer_logout,
            fg_color="transparent", hover=False,
            width=100, height=35
        )
        self.botao_sair.pack(padx=10, pady=10, side=ctk.RIGHT)
        self.aplicar_efeito_hover(self.botao_sair, cor_hover= "#FF0000")

        # Área de conteúdo
        self.conteudo_frame = ctk.CTkFrame(frame_principal, fg_color="transparent")
        self.conteudo_frame.pack(side="bottom", expand=True, fill="both", padx=10, pady=10)

        self.label_bem_vindo = ctk.CTkLabel(self.conteudo_frame, text="", font=("Arial", 20))
        self.label_bem_vindo.pack(pady=20)

    def _configurar_estilo_treeview(self):
        style = ttk.Style()
        
        style.theme_use("clam")
        bg_color = "#ebebeb" 
        selected_color = "#3b8ed8" 
        text_color = "#363636"
        header_bg_color = "#e5e5e5" 

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
        # Fundo da tela
        frame_gestao = ctk.CTkFrame(self.conteudo_frame)
        self.frames['gestao'] = frame_gestao
        frame_gestao.pack(fill="both", expand=True)

        # Card central
        card = ctk.CTkFrame(frame_gestao, fg_color="#F5F5DC", corner_radius=15)
        card.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.4, relheight=0.7)

        # Título
        ctk.CTkLabel(card, text='Cadastro de Usuários', font=("Arial", 20, "bold"), text_color="#1E3A8A").pack(pady=(25, 15))

        # Campo: Nome do Usuário
        ctk.CTkLabel(card, text='Nome do Usuário:', anchor="w", text_color="black").pack(padx=30, fill="x")
        self.campo_admin_novo_usuario = ctk.CTkEntry(card, fg_color="white", text_color="black")
        self.campo_admin_novo_usuario.pack(padx=30, pady=8, fill="x")

        # Campo: Senha
        ctk.CTkLabel(card, text='Senha:', anchor="w", text_color="black").pack(padx=30, fill="x")
        self.campo_admin_nova_senha = ctk.CTkEntry(card, show="*", fg_color="white", text_color="black")
        self.campo_admin_nova_senha.pack(padx=30, pady=8, fill="x")

        # Campo: Tipo de Usuário
        ctk.CTkLabel(card, text="Tipo de Usuário:", anchor="w", text_color="black").pack(padx=30, fill="x")
        self.combo_admin_user_type = ctk.CTkComboBox(card, values=['psicologa', 'secretaria', 'responsável'], state='readonly')
        self.combo_admin_user_type.pack(padx=30, pady=8, fill="x")
        self.combo_admin_user_type.set('responsável')

        # Botão Criar Usuário
        ctk.CTkButton(
            card,
            text="Criar Usuário",
            command=self.criar_usuario_admin,
            fg_color="#2563EB",
            hover_color="#1E40AF",
            corner_radius=20
        ).pack(pady=25)

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
        
        # CTkTextbox substitui o tk.Text e já vem com negocinho de rolar pagina
        self.texto_observacoes = ctk.CTkTextbox(frame_obs, wrap="word", font=("Arial", 12))
        self.texto_observacoes.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)

        botoes_frame = ctk.CTkFrame(frame_obs, fg_color="transparent")
        botoes_frame.grid(row=3, column=0, pady=10)
        ctk.CTkButton(botoes_frame, text="Salvar Observações", command=self.salvar_observacoes).pack(side="left", padx=10)
        ctk.CTkButton(botoes_frame, text="Fechar", command=lambda: self.mostrar_frame("registro")).pack(side="left", padx=10)


    def criar_tela_vinculo(self):
        self._configurar_estilo_treeview()
        frame_vinculo = ctk.CTkFrame(self.conteudo_frame)
        self.frames["vinculo"] = frame_vinculo
        frame_vinculo.pack(fill="both", expand=True, padx=20, pady=20)
        
        ctk.CTkLabel(frame_vinculo, text="Vincular Responsável a Aluno", font=("Arial", 16, "bold")).pack(pady=10)
        
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

        ctk.CTkLabel(frame_vinculo, text="Selecione o Responsável:").pack(pady=(10,0))
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
        self.db.exportar_aluno_pdf(self.aluno_id_observacao, self.pasta_relatorios)
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
            messagebox.showerror("Erro", "Selecione um Responsável.")
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

        nome, sala, serie, gravidade = (
            self.entry_nome.get().strip(),
            self.entry_sala.get().strip(),
            self.entry_serie.get().strip(),
            self.gravidade_combo.get().strip()
        )

        if not all([nome, sala, serie, gravidade]):
            messagebox.showerror("Registro", "Preencha todos os campos.")
            return

        try:
            int(sala)
            int(serie)
        except ValueError:
            messagebox.showerror("Registro", "Sala e Série devem ser números.")
            return

        if self.aluno_id_edicao:
            aluno_id = int(self.aluno_id_edicao)

            aluno_antigo = self.db.get_aluno_by_id(aluno_id)
            if aluno_antigo and aluno_antigo.nome != nome:
                nome_antigo_limpo = aluno_antigo.nome.replace(" ", "_").replace("/", "-")
                arquivo_antigo = os.path.join(self.pasta_relatorios, f"Relatorio_{aluno_id}_{nome_antigo_limpo}.pdf")
                if os.path.exists(arquivo_antigo):
                    try:
                        os.remove(arquivo_antigo)
                        print(f"🗑️ PDF antigo removido: {arquivo_antigo}")
                    except Exception as e:
                        print(f"Erro ao remover PDF antigo: {e}")

            # Atualiza o aluno no banco
            self.db.update_aluno(aluno_id, nome, sala, serie, gravidade)

            # Gera novo PDF atualizado
            self.db.exportar_aluno_pdf(aluno_id, self.pasta_relatorios)
            messagebox.showinfo("Sucesso", f"Aluno '{nome}' e PDF atualizados com sucesso!")
            self.aluno_id_edicao = None

        # Criar novo aluno
        else:
            self.db.add_aluno(nome, sala, serie, gravidade, self.usuario_logado)
            novo_aluno = self.db.get_alunos_by_user(self.usuario_logado)[-1]
            self.db.exportar_aluno_pdf(novo_aluno.id, self.pasta_relatorios)
            messagebox.showinfo("Sucesso", f"Aluno '{nome}' registrado e PDF criado!")

        # Limpa os campos e atualiza lista
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
            self.db.delete_aluno(aluno_id, self.pasta_relatorios)
            self.atualizar_exibicao_alunos()
            messagebox.showinfo(
                "Exclusão", 
                f"Aluno '{aluno_nome}' e seu relatório PDF foram removidos com sucesso!"
            )

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
            detalhe_win.transient(self.principal)
            
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

    def exportar_relatorio(self, formato):
        if self.aluno_id_observacao is None:
            messagebox.showerror("Erro", "Nenhum aluno selecionado.")
            return
    
        if formato == "pdf":
            arquivo = self.db.exportar_aluno_pdf(self.aluno_id_observacao, self.pasta_relatorios)

        if arquivo:
            messagebox.showinfo("Sucesso", f"Relatório exportado: {arquivo}")
        else:
            messagebox.showerror("Erro", "Falha ao exportar relatório.")

    def excluir_conta(self):
        if messagebox.askyesno("Confirmação", "Excluir este usuário também removerá todos os dados relacionados. Deseja continuar?"):
            self.db.delete_user(self.usuario_logado)
            self.fazer_logout()
            messagebox.showinfo("Exclusão de Conta", "Sua conta foi excluída com sucesso.")

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    ctk.set_default_color_theme("blue")
    
    root = ctk.CTk()
    app = SISPE(root)
    root.mainloop()
    app = SISPE(root)
    root.mainloop()

