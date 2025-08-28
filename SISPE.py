import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import hashlib
import sqlite3

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
        self.conn = sqlite3.connect(db_name)
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

    def delete_aluno(self, aluno_id):
        self.cursor.execute("DELETE FROM alunos WHERE id = ?", (aluno_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()

    def delete_user(self, username):
        self.cursor.execute("DELETE FROM usuarios WHERE username = ?", (username,))
        self.conn.commit()

class SISPE:
    def __init__(self, principal):
        self.principal = principal
        principal.title("SISPE")
        principal.geometry("500x500")
        principal.protocol("WM_DELETE_WINDOW", self.on_closing)

        self.frames = {}
        self.usuario_logado = None
        
        self.db = DatabaseManager()
        self.aluno_id_edicao = None

        self.criar_tela_login()
        self.criar_tela_gestao()
        self.criar_tela_principal()
        self.criar_tela_registro()
        self.criar_tela_perfil()
        self.criar_tela_observacoes()

        self.aluno_id_observacoes = None

        self.mostrar_frame("login")
    
    def on_closing(self):
        if messagebox.askokcancel("Sair", "Tem certeza que deseja sair?"):
            self.db.close()
            self.principal.destroy()

    def _hash_senha(self, senha):
        return hashlib.sha256(senha.encode()).hexdigest()

    def criar_tela_login(self):
        frame_login = ttk.Frame(self.principal, padding="30 20 30 20", relief="groove")
        self.frames["login"] = frame_login
        
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

    def criar_tela_gestao(self):
        frame_gestao = ttk.Frame(self.principal, padding ='50 30 50 30', relief='groove' )
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
        self.combo_admin_user_type.set('pai')

        ttk.Button(central_frame, text="Criar Usuário", command=self.criar_usuario_admin).grid(row=4, column=0, columnspan=2, pady=10)
        ttk.Button(central_frame, text="Voltar", command=lambda: self.mostrar_frame("principal")).grid(row=5, column=0, columnspan=2, pady=5)

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
        self.botao_gerenciar_usuarios.pack_forget()
        self.botao_registrar.pack_forget()

        if self.user_type in ( 'secretaria'):
            self.botao_gerenciar_usuarios.pack(pady=20)
            self.botao_registrar.pack(pady=20)

    def criar_tela_principal(self):
        frame_principal = ttk.Frame(self.principal, padding="50 30 50 30", relief="groove")
        self.frames["principal"] = frame_principal
        self.label_bem_vindo = ttk.Label(frame_principal, text="", font=("Arial", 14))
        self.label_bem_vindo.pack(pady=10)

        ttk.Label(frame_principal, text="tela principal").pack(pady=10)

        self.botao_gerenciar_usuarios = ttk.Button(frame_principal, text='Gerenciar Usuários', command=lambda: self.mostrar_frame("gestao"))
        self.botao_registrar = ttk.Button(frame_principal, text='Registrar aluno', command=self.ir_registro)
        self.botao_perfil = ttk.Button(frame_principal, text='Perfil', command=self.ir_perfil)
        self.botao_logout = ttk.Button(frame_principal, text="Sair", command=self.fazer_logout)

        self.botao_perfil.pack(pady=20)
        self.botao_logout.pack(pady=20)

    def criar_tela_registro(self):
        frame_registro = ttk.Frame(self.principal, padding="50 30 50 30", relief="groove")
        self.frames["registro"] = frame_registro

        frame_registro.grid_rowconfigure(0, weight=1)
        frame_registro.grid_rowconfigure(9, weight=1)
        frame_registro.grid_columnconfigure(0, weight=1)
        frame_registro.grid_columnconfigure(2, weight=1)

        central_frame = ttk.Frame(frame_registro)
        central_frame.grid(row=1, column=1, rowspan=8, sticky="nsew")

        central_frame.grid_columnconfigure(0, weight=1)
        central_frame.grid_columnconfigure(1, weight=1)
        
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

        botoes_acao_frame = ttk.Frame(central_frame)
        botoes_acao_frame.grid(row=8, column=0, columnspan=2, pady=5)
        
        ttk.Button(botoes_acao_frame, text='editar', command=self.editar_aluno).pack(side='left', padx=5)
        ttk.Button(botoes_acao_frame, text='excluir', command=self.excluir_aluno).pack(side='left', padx=5)

    def criar_tela_perfil(self):
        frame_perfil = ttk.Frame(self.principal, padding="50 30 50 30", relief="groove")
        self.frames["perfil"] = frame_perfil

        frame_perfil.grid_rowconfigure(0, weight=1)
        frame_perfil.grid_rowconfigure(9, weight=1)
        frame_perfil.grid_columnconfigure(0, weight=1)
        frame_perfil.grid_columnconfigure(2, weight=1)

        central_frame2 = ttk.Frame(frame_perfil)
        central_frame2.grid(row=1, column=1, rowspan=8, sticky="nsew")

        central_frame2.grid_columnconfigure(0, weight=1)
        central_frame2.grid_columnconfigure(1, weight=1)

        ttk.Label(central_frame2, text= 'perfil', font=("Arial", 16, "bold")).grid(row=0, column=0, columnspan=2, pady=5)

        ttk.Button(central_frame2, text="Voltar", command=lambda: self.mostrar_frame("principal")).grid(row=6, column=0, columnspan=2, pady=5)

        ttk.Button(central_frame2, text="Excluir Conta", command=self.excluir_conta, style='Danger.TButton').grid(row=4, column=0, columnspan=2, pady=20)

        ttk.Button(central_frame2, text="Voltar", command=lambda: self.mostrar_frame("principal")).grid(row=6, column=0, columnspan=2, pady=5)

    def criar_tela_observacoes(self):
        frame_obs = ttk.Frame(self.principal, padding='30 20 30 20', relief='groove')
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

    def mostrar_frame(self, nome_do_frame):
        if nome_do_frame == "registro":
            self.atualizar_exibicao()
            
        for frame in self.frames.values():
            frame.pack_forget()

        frame = self.frames[nome_do_frame]
        frame.pack(fill="both", expand=True)

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
            self.label_bem_vindo.config(text=f"Bem-vindo, {self.usuario_logado}!")
            
            self.configurar_interface_por_tipo()
            self.mostrar_frame("principal")
        else:
            messagebox.showerror("Login", "Usuário ou senha incorretos.")

    def ir_perfil(self):
        self.mostrar_frame('perfil')

    def ir_registro(self):
        self.mostrar_frame("registro")

    def fazer_logout(self):
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

    def salvar_observacoes(self):
        if self.aluno_id_observacao is None:
            messagebox.showerror("Erro", "Nenhum aluno selecionado.")
            return

        novas_observacoes = self.texto_observacoes.get("1.0", tk.END).strip()

        self.db.aluno_observação(self.aluno_id_observacao, novas_observacoes)

        messagebox.showinfo("Sucesso", "Observações salvas com sucesso!")
        
        self.aluno_id_observacao = None
        self.mostrar_frame("registro")

    def atualizar_exibicao(self):
        self.tree_alunos.delete(*self.tree_alunos.get_children())
        if self.usuario_logado:
            alunos_do_usuario = self.db.get_alunos_by_user(self.usuario_logado)
            for aluno in alunos_do_usuario:
                self.tree_alunos.insert("", "end", iid=aluno.id, values=(aluno.nome, aluno.sala, aluno.serie, aluno.gravidade))

    def salvar_aluno(self):
        if self.user_type not in ('psicologa', 'secretaria'):
            messagebox.showerror("Acesso Negado", "Você não tem permissão para registrar alunos.")
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
    
        confirmar = messagebox.askyesno(
            "Confirmar Exclusão",
            f"Tem certeza que deseja excluir o aluno '{aluno_nome}'?"
        )
    
        if confirmar:
            self.db.delete_aluno(aluno_id)
            self.atualizar_exibicao()
            messagebox.showinfo("Exclusão", f"Aluno '{aluno_nome}' excluído com sucesso.")

    def editar_aluno(self):
        item_selecionado = self.tree_alunos.focus()
        
        if not item_selecionado:
            messagebox.showerror("Edição", "Selecione um aluno para editar.")
            return
        
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

        self.aluno_id_edicao = aluno_id_para_editar

    def atualizar_exibicao(self):
        self.tree_alunos.delete(*self.tree_alunos.get_children())

        if self.usuario_logado:
            alunos_do_usuario = self.db.get_alunos_by_user(self.usuario_logado)
            for aluno in alunos_do_usuario:
                self.tree_alunos.insert("", "end", iid=aluno.id, values=(aluno.nome, aluno.sala, aluno.serie, aluno.gravidade))

    def excluir_conta(self):
        resposta = messagebox.askyesno(
            "Confirmação de Exclusão",
            "Tem certeza que deseja excluir sua conta? Esta ação é definitiva e removerá todos os seus dados."
        )

        if resposta:
            username = self.usuario_logado
            self.db.delete_user(username)
            self.fazer_logout()
            messagebox.showinfo("Exclusão de Conta", "Sua conta foi excluída com sucesso.")

if __name__ == "__main__":
    teste = tk.Tk()
    style = ttk.Style()
    style.theme_use('vista')
    style.configure("Accent.TButton", font=("Arial", 12, "bold"),
                    foreground="White", background="#0d3057",
                    padding=10, borderwidth=0, relief="flat")
    style.map("Accent.TButton", background=[('active', '#0056b3')])
    
    style.configure("Danger.TButton", font=("Arial", 12, "bold"),
                    foreground="red", background="#0d3057",
                    padding=5, borderwidth=0, relief="solid", fieldbackground='white', bordercolor="#0d3057",
                    focuscolor="#0d3057")
    style.map("Danger.TButton", background=[('active', '#a30000')], foreground=[('active', '#ff3333')])
    style.configure("TEntry", padding=5, font=("Arial", 12), fieldbackground="white",
                    foreground="#333333", borderwidth=1, relief="solid")

    style.configure("TLabel", foreground= "#3A0D0D")

    app = SISPE(teste)
    teste.mainloop()
