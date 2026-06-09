import customtkinter as ctk
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3
import os
from datetime import datetime
import json

# ==================== CONFIGURAÇÃO GLOBAL CTK ====================
ctk.set_appearance_mode("Light")
ctk.set_default_color_theme("green")

# ==================== ESTILO DE ENTRY PERSONALIZADO (CTK) ====================
class StyledEntry(ctk.CTkFrame):
    def __init__(self, parent, label="", placeholder="", icon="", show="", **kwargs):
        super().__init__(parent, fg_color="transparent")
        
        if label:
            self.label_widget = ctk.CTkLabel(self, text=label, font=("Segoe UI", 12, "bold"))
            self.label_widget.pack(anchor="w", pady=(0, 2))
            
        full_placeholder = f"{icon}  {placeholder}" if icon else placeholder
        
        self.entry = ctk.CTkEntry(self, placeholder_text=full_placeholder, show=show, height=35, **kwargs)
        self.entry.pack(fill="x", expand=True)
        
    def get(self):
        return self.entry.get().strip()
        
    def set(self, value):
        self.entry.delete(0, 'end')
        self.entry.insert(0, value)
        
    def clear(self):
        self.entry.delete(0, 'end')
        
    @property
    def entry_widget(self):
        return self.entry

# ==================== SIDEBAR BUTTON (CTK) ====================
class SidebarButton:
    def __init__(self, parent, texto, icone, comando, is_active=False):
        self.btn = ctk.CTkButton(parent, text=f"{icone}  {texto}", font=("Segoe UI", 13),
                                 anchor="w", fg_color="transparent", text_color=("gray10", "gray90"),
                                 hover_color=("gray85", "gray25"), height=40, command=comando)
        self.btn.pack(fill="x", pady=2, padx=12)
        if is_active:
            self.set_active(True)
            
    def set_active(self, active):
        if active:
            self.btn.configure(fg_color=("gray80", "gray20"), font=("Segoe UI", 13, "bold"))
        else:
            self.btn.configure(fg_color="transparent", font=("Segoe UI", 13))

# ==================== LOADING OVERLAY ====================
class LoadingOverlay:
    def __init__(self, parent):
        self.parent = parent
        self.overlay = None
        
    def show(self, message="Carregando..."):
        self.overlay = ctk.CTkFrame(self.parent, fg_color=("gray90", "gray10"), corner_radius=10)
        self.overlay.place(relx=0.5, rely=0.5, anchor="center")
        self.loading_label = ctk.CTkLabel(self.overlay, text=message, font=("Segoe UI", 14, "bold"))
        self.loading_label.pack(padx=40, pady=30)
        
    def hide(self):
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None

# ==================== TOAST NOTIFICATIONS ====================
class Toast:
    @staticmethod
    def show(parent, message, type='info', duration=3000):
        toast = ctk.CTkToplevel(parent)
        toast.wm_overrideredirect(True)
        
        colors = {'success': "#38A169", 'error': "#E53E3E", 'warning': "#DD6B20", 'info': "#3182CE"}
        bg_color = colors.get(type, colors['info'])
        
        parent.update_idletasks()
        x = parent.winfo_rootx() + parent.winfo_width() - 350
        y = parent.winfo_rooty() + parent.winfo_height() - 80
        toast.geometry(f"320x50+{x}+{y}")
        
        frame = ctk.CTkFrame(toast, fg_color=bg_color, corner_radius=0)
        frame.pack(fill="both", expand=True)
        
        icons = {'success': '✓', 'error': '✗', 'warning': '⚠', 'info': 'ℹ'}
        ctk.CTkLabel(frame, text=icons.get(type, 'ℹ'), font=("Segoe UI", 16), text_color="white").pack(side="left", padx=12)
        ctk.CTkLabel(frame, text=message, font=("Segoe UI", 12), text_color="white", wraplength=250).pack(side="left", padx=5)
        
        toast.after(duration, toast.destroy)

# ==================== MENU DE CONTEXTO (BOTÃO DIREITO) ====================
class ContextMenu:
    def __init__(self, parent, book_id_callback, title_callback):
        self.menu = tk.Menu(parent, tearoff=0)
        self.menu.add_command(label="✏️ Editar Livro", command=lambda: self.edit_callback())
        self.menu.add_command(label="📤 Emprestar Agora", command=lambda: self.issue_callback())
        self.menu.add_separator()
        self.menu.add_command(label="🗑️ Excluir Livro", command=lambda: self.delete_callback())
        
        self.book_id_callback = book_id_callback
        self.title_callback = title_callback
        self.current_book_id = None
        self.current_title = None
        
    def edit_callback(self):
        if self.current_book_id:
            self.book_id_callback(self.current_book_id, is_edit=True)
            
    def issue_callback(self):
        if self.current_book_id:
            self.title_callback(self.current_book_id)
            
    def delete_callback(self):
        if self.current_book_id:
            self.book_id_callback(self.current_book_id, is_edit=False)
            
    def show(self, event, book_id, title):
        self.current_book_id = book_id
        self.current_title = title
        self.menu.post(event.x_root, event.y_root)

# ==================== CLASSE PRINCIPAL ====================
class UnifiedLibrarySystem:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title('Library Management System')
        
        # Define um tamanho inicial moderno (Largura x Altura)
        self.root.geometry("1280x720") 
        
        # Tenta maximizar em seguida
        self.root.state('zoomed')
        
        self.load_settings()
        self.init_db()
        self.create_login_screen()
        self.setup_shortcuts()
        
        self.root.mainloop()
        
    def init_db(self):
        conn = sqlite3.connect('test.db')
        conn.execute('''CREATE TABLE IF NOT EXISTS book_info
        (ID VARCHAR PRIMARY KEY NOT NULL, TITLE VARTEXT NOT NULL, AUTHOR VARTEXT NOT NULL,
        GENRE VARTEXT NOT NULL, COPIES VARINT NOT NULL, LOCATION VARCHAR NOT NULL);''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS book_issued
        (BOOK_ID VARCHAR NOT NULL, STUDENT_ID VARCHAR NOT NULL, ISSUE_DATE DATE NOT NULL,
        RETURN_DATE DATE NOT NULL, PRIMARY KEY (BOOK_ID,STUDENT_ID));''')
        conn.commit()
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM book_info")
        if cursor.fetchone()[0] == 0:
            livros = [
                ("B1042", "Programação Python", "João Silva", "Tecnologia", 5, "A1"),
                ("B2056", "Fundamentos de Dados", "Maria Souza", "Tecnologia", 3, "A2"),
                ("B3089", "O Grande Gatsby", "Fitzgerald", "Ficção", 7, "B1"),
            ]
            for livro in livros:
                try: conn.execute("INSERT INTO book_info VALUES (?,?,?,?,?,?)", livro)
                except: pass
                
        cursor.execute("SELECT COUNT(*) FROM book_issued")
        if cursor.fetchone()[0] == 0:
            dados_exemplo = [("B1042", "S992", "2025-05-01", "2025-05-08")]
            for dados in dados_exemplo:
                try: conn.execute("INSERT INTO book_issued VALUES (?,?,?,?)", dados)
                except: pass
                
        conn.commit()
        conn.close()
        
        self.conn_login = sqlite3.connect("python1.db")
        self.cursor_login = self.conn_login.cursor()
        self.cursor_login.execute("CREATE TABLE IF NOT EXISTS `login` (mem_id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT, username TEXT, password TEXT)")
        self.cursor_login.execute("SELECT * FROM `login` WHERE `username` = 'admin' AND `password` = 'admin'")
        if self.cursor_login.fetchone() is None:
            self.cursor_login.execute("INSERT INTO `login` (username, password) VALUES('lorena', '1234')")
            self.conn_login.commit()

    def load_settings(self):
        self.settings = {}
        if os.path.exists('settings.json'):
            try:
                with open('settings.json', 'r') as f:
                    self.settings = json.load(f)
            except: pass
        if self.settings.get('dark_mode'):
            ctk.set_appearance_mode("Dark")
            
    def save_settings(self):
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f)
            
    def setup_shortcuts(self):
        self.root.bind('<Control-b>', lambda e: self.show_books_view())
        self.root.bind('<Control-e>', lambda e: self.show_loans_view())
        self.root.bind('<Control-l>', lambda e: self.create_login_screen())
        self.root.bind('<Control-s>', lambda e: self.show_settings())
        self.root.bind('<Control-d>', lambda e: self.toggle_theme())
        self.root.bind('<Delete>', lambda e: self.delete_selected_book())

    def create_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        # 1. Adicione o width (largura) e height (altura) desejados
        login_card = ctk.CTkFrame(self.root, width=550, height=650, corner_radius=15)
        
        # 2. Desligue o encolhimento automático
        login_card.pack_propagate(False) 
        
        login_card.place(relx=0.5, rely=0.5, anchor="center")
        
        ctk.CTkLabel(login_card, text="📚", font=("Segoe UI", 48)).pack(pady=(30, 10))
        ctk.CTkLabel(login_card, text="Bem-vindo ao Library Management", font=("Segoe UI", 18, "bold")).pack()
        ctk.CTkLabel(login_card, text="Sistema de Gerenciamento de Biblioteca", text_color="gray").pack(pady=(0, 30))
        
        self.username_var = tk.StringVar()
        self.password_var = tk.StringVar()
        
        inner = ctk.CTkFrame(login_card, fg_color="transparent")
        inner.pack(padx=40, fill="both", expand=True)
        
        self.username_field = StyledEntry(inner, "Usuário", "Digite seu usuário", "👤")
        self.username_field.pack(fill="x", pady=(0, 15))
        
        self.password_field = StyledEntry(inner, "Senha", "Digite sua senha", "🔒", show="•")
        self.password_field.pack(fill="x", pady=(0, 20))
        
        self.username_field.entry.configure(textvariable=self.username_var)
        self.password_field.entry.configure(textvariable=self.password_var)
        
        remember_var = tk.BooleanVar(value=self.settings.get('remember_login', False))
        ctk.CTkCheckBox(inner, text="Lembrar meu login", variable=remember_var).pack(anchor="w", pady=(0, 15))
        
        ctk.CTkButton(inner, text="ENTRAR", font=("Segoe UI", 14, "bold"), height=40,
                      command=lambda: self.do_login(remember_var.get())).pack(fill="x", pady=(0, 15))
                      
        self.login_error_label = ctk.CTkLabel(inner, text="", text_color="#E53E3E")
        self.login_error_label.pack()
        
        cred_frame = ctk.CTkFrame(inner, corner_radius=10)
        cred_frame.pack(fill="x", pady=20, ipadx=10, ipady=10)
        ctk.CTkLabel(cred_frame, text="🔐 Credenciais Demo: lorena / 1234", font=("Segoe UI", 12)).pack()
        
        ctk.CTkButton(inner, text="🔑 Login Rápido", fg_color="transparent", border_width=1,
                      text_color=("gray10", "gray90"), command=self.quick_login).pack(pady=(0, 30))
                      
        self.username_field.entry.bind('<Return>', lambda e: self.do_login(remember_var.get()))
        self.password_field.entry.bind('<Return>', lambda e: self.do_login(remember_var.get()))

    def quick_login(self):
        self.username_var.set("lorena")
        self.password_var.set("1234")
        self.do_login(False)
        
    def do_login(self, remember=False):
        username = self.username_var.get()
        password = self.password_var.get()
        
        if not username or not password:
            self.login_error_label.configure(text="⚠️ Por favor, preencha todos os campos!")
            return
            
        loading = LoadingOverlay(self.root)
        loading.show("Verificando credenciais...")
        self.root.after(100, lambda: self.check_login(username, password, remember, loading))
        
    def check_login(self, username, password, remember, loading):
        self.cursor_login.execute("SELECT * FROM login WHERE username=? AND password=?", (username, password))
        if self.cursor_login.fetchone():
            if remember:
                self.settings['remember_login'] = True
                self.settings['saved_username'] = username
                self.save_settings()
            loading.hide()
            Toast.show(self.root, f"Bem-vindo, {username}!", 'success')
            self.create_main_dashboard()
        else:
            loading.hide()
            self.login_error_label.configure(text="❌ Usuário ou senha inválidos!")
            self.username_var.set("")
            self.password_var.set("")

    def create_main_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()
            
        self.sidebar = ctk.CTkFrame(self.root, width=280, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)
        
        ctk.CTkLabel(self.sidebar, text="📚 Library Management", font=("Segoe UI", 18, "bold"), text_color="#2E7D32").pack(pady=(32, 5))
        ctk.CTkLabel(self.sidebar, text="Sistema de Biblioteca", text_color="gray").pack(pady=(0, 20))
        
        self.sidebar_buttons = []
        btn_books = SidebarButton(self.sidebar, "Livros", "📖", self.show_books_view, is_active=True)
        self.sidebar_buttons.append(btn_books)
        btn_loans = SidebarButton(self.sidebar, "Empréstimos", "👥", self.show_loans_view, is_active=False)
        self.sidebar_buttons.append(btn_loans)
        
        ctk.CTkLabel(self.sidebar, text="🟢 Sistema Online", text_color="#38A169").pack(pady=20)
        
        ctk.CTkButton(self.sidebar, text="🌓 Alternar Tema", fg_color="transparent", text_color=("gray10", "gray90"),
                      anchor="w", command=self.toggle_theme).pack(side="bottom", fill="x", padx=20, pady=10)
        ctk.CTkButton(self.sidebar, text="🚪 Sair", fg_color="#E53E3E", hover_color="#C53030",
                      anchor="w", command=self.create_login_screen).pack(side="bottom", fill="x", padx=20, pady=(10, 30))

        # O CTkScrollableFrame substitui TODO o seu código antigo de Canvas e barras de rolagem!
        self.content_area = ctk.CTkScrollableFrame(self.root, fg_color="transparent")
        self.content_area.pack(side="left", expand=True, fill="both", padx=20, pady=20)
        
        self.show_books_view()

    def toggle_theme(self):
        current = ctk.get_appearance_mode()
        new_theme = "Dark" if current == "Light" else "Light"
        ctk.set_appearance_mode(new_theme)
        self.settings['dark_mode'] = (new_theme == "Dark")
        self.save_settings()
        
        if hasattr(self, 'current_view'):
            self.style_treeview()
            
    def show_settings(self):
        dialog = ctk.CTkToplevel(self.root)
        dialog.title("Configurações")
        dialog.geometry("400x300")
        dialog.transient(self.root)
        dialog.grab_set()
        
        ctk.CTkLabel(dialog, text="Configurações", font=("Segoe UI", 18, "bold")).pack(pady=20)
        
        theme_var = tk.BooleanVar(value=ctk.get_appearance_mode() == "Dark")
        ctk.CTkCheckBox(dialog, text="Modo Escuro", variable=theme_var, command=self.toggle_theme).pack(pady=10)
        
        remember_var = tk.BooleanVar(value=self.settings.get('remember_login', False))
        ctk.CTkCheckBox(dialog, text="Lembrar meu login", variable=remember_var).pack(pady=10)
        
        def save():
            self.settings['remember_login'] = remember_var.get()
            self.save_settings()
            Toast.show(dialog, "Configurações salvas!", 'success')
            dialog.after(1000, dialog.destroy)
            
        ctk.CTkButton(dialog, text="Salvar", command=save).pack(pady=30)

    # ==================== ESTILIZAÇÃO DO TREEVIEW (PARA O TEMA) ====================
    def style_treeview(self):
        bg_color = ctk.ThemeManager.theme["CTkFrame"]["fg_color"][1 if ctk.get_appearance_mode() == "Dark" else 0]
        text_color = ctk.ThemeManager.theme["CTkLabel"]["text_color"][1 if ctk.get_appearance_mode() == "Dark" else 0]
        selected_color = ctk.ThemeManager.theme["CTkButton"]["fg_color"][1 if ctk.get_appearance_mode() == "Dark" else 0]
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=bg_color, foreground=text_color, fieldbackground=bg_color, borderwidth=0, rowheight=35)
        style.configure("Treeview.Heading", background=selected_color, foreground="white", font=("Segoe UI", 10, "bold"), borderwidth=0)
        style.map('Treeview', background=[('selected', selected_color)])

    # ==================== VISUAL DE LIVROS ====================
    def show_books_view(self):
        self.current_view = 'books'
        for btn in self.sidebar_buttons: btn.set_active(False)
        self.sidebar_buttons[0].set_active(True)
        
        for widget in self.content_area.winfo_children(): widget.destroy()
        
        header_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header_frame, text="Gerenciamento de Livros", font=("Segoe UI", 24, "bold")).pack(side="left")
        self.books_summary_label = ctk.CTkLabel(header_frame, text="", text_color="gray")
        self.books_summary_label.pack(side="right")
        
        stats_grid = ctk.CTkFrame(self.content_area, fg_color="transparent")
        stats_grid.pack(fill="x", pady=(0, 24))
        
        def create_stat(parent, icon, title, color):
            frame = ctk.CTkFrame(parent, corner_radius=10)
            frame.pack(side="left", expand=True, fill="both", padx=5)
            ctk.CTkLabel(frame, text=icon, font=("Segoe UI", 28)).pack(pady=(15, 0))
            lbl_val = ctk.CTkLabel(frame, text="0", font=("Segoe UI", 24, "bold"), text_color=color)
            lbl_val.pack()
            ctk.CTkLabel(frame, text=title, text_color="gray").pack(pady=(0, 15))
            return lbl_val

        self.total_books_label = create_stat(stats_grid, "📚", "Total de Livros", "#2E7D32")
        self.total_copies_label = create_stat(stats_grid, "📖", "Total de Cópias", "#3182CE")
        self.loaned_books_label = create_stat(stats_grid, "🔄", "Livros Emprestados", "#DD6B20")
        self.avail_books_label = create_stat(stats_grid, "✅", "Disponíveis", "#38A169")
        
        # Card de Adicionar Livro
        add_card = ctk.CTkFrame(self.content_area, corner_radius=10)
        add_card.pack(fill="x", pady=(0, 24)) 
        
        # 1. Adicionado padx=25 e pady para dar a margem interna no título
        ctk.CTkLabel(add_card, text="📝 ADICIONAR NOVO LIVRO", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=25, pady=(20, 15))
        
        fields_grid = ctk.CTkFrame(add_card, fg_color="transparent")
        # 2. Adicionado padx=25 para desgrudar as caixas de texto das laterais do fundo cinza!
        fields_grid.pack(fill="x", padx=25)
        
        left_col = ctk.CTkFrame(fields_grid, fg_color="transparent")
        # 3. Aumentei o padx=(0, 15) para dar mais espaço no meio entre as duas colunas
        left_col.pack(side="left", expand=True, fill="both", padx=(0, 15))
        self.book_id = StyledEntry(left_col, "ID do Livro *", "Ex: B1001", "🔖")
        self.book_id.pack(fill="x", pady=(0, 10))
        self.book_title = StyledEntry(left_col, "Título *", "Nome completo do livro", "📖")
        self.book_title.pack(fill="x", pady=(0, 10))
        self.book_author = StyledEntry(left_col, "Autor *", "Nome do autor", "✍️")
        self.book_author.pack(fill="x", pady=(0, 10))
        
        right_col = ctk.CTkFrame(fields_grid, fg_color="transparent")
        right_col.pack(side="right", expand=True, fill="both", padx=(15, 0)) 
        self.book_genre = StyledEntry(right_col, "Gênero *", "Ex: Ficção, Tecnologia...", "📚")
        self.book_genre.pack(fill="x", pady=(0, 10))
        self.book_copies = StyledEntry(right_col, "Nº de Cópias *", "Quantidade disponível", "📊")
        self.book_copies.pack(fill="x", pady=(0, 10))
        self.book_location = StyledEntry(right_col, "Localização *", "Ex: A1, B2", "📍")
        self.book_location.pack(fill="x", pady=(0, 10))
        
        btn_frame = ctk.CTkFrame(add_card, fg_color="transparent")
        # 4. Adicionado padx=25 e margem no fundo (pady) para os botões não colarem na base
        btn_frame.pack(fill="x", padx=25, pady=(15, 25))
        
        self.add_btn = ctk.CTkButton(btn_frame, text="➕ Adicionar Livro", font=("Segoe UI", 12, "bold"), height=40, command=self.add_book)
        self.add_btn.pack(side="left", padx=(0, 10))
        self.clear_btn = ctk.CTkButton(btn_frame, text="🗑️ Limpar", fg_color="transparent", border_width=1, text_color=("gray10", "gray90"), height=40, command=self.clear_book_form)
        self.clear_btn.pack(side="left")
        
       # Card de Catálogo
        catalog_card = ctk.CTkFrame(self.content_area, corner_radius=10)
        # Removi o ipadx e ipady daqui
        catalog_card.pack(fill="both", expand=True)
        
        catalog_header = ctk.CTkFrame(catalog_card, fg_color="transparent")
        # Adicionado padx=25 e pady=(20, 15) para desgrudar do topo e das laterais
        catalog_header.pack(fill="x", padx=25, pady=(20, 15))
        
        ctk.CTkLabel(catalog_header, text="📚 CATÁLOGO DE LIVROS", font=("Segoe UI", 16, "bold")).pack(side="left")
        
        search_frame = ctk.CTkFrame(catalog_header, fg_color="transparent")
        search_frame.pack(side="right")
        self.book_search = StyledEntry(search_frame, "", "Buscar...", "🔍")
        self.book_search.pack(side="left", padx=(0, 10))
        self.book_search.entry.bind('<KeyRelease>', lambda e: self.search_books())
        ctk.CTkButton(search_frame, text="Limpar", width=80, fg_color="transparent", border_width=1, text_color=("gray10", "gray90"), command=self.clear_book_search).pack(side="left")
        
        self.create_books_table(catalog_card)
        
        table_actions = ctk.CTkFrame(catalog_card, fg_color="transparent")
        # Adicionado padx=25 e margem no fundo pady=(15, 25)
        table_actions.pack(fill="x", padx=25, pady=(15, 25))
        
        ctk.CTkLabel(table_actions, text="ℹ️ Clique direito na tabela para + opções", text_color="gray").pack(side="left")
        ctk.CTkButton(table_actions, text="🗑️ Excluir", fg_color="#E53E3E", hover_color="#C53030", command=self.delete_selected_book).pack(side="right", padx=(10, 0))
        ctk.CTkButton(table_actions, text="✏️ Editar", fg_color="#3182CE", hover_color="#2B6CB0", command=self.edit_selected_book).pack(side="right")
        
        self.load_all_books()
        self.update_all_stats()

    def create_books_table(self, parent):
        self.style_treeview()
        table_frame = ctk.CTkFrame(parent, fg_color="transparent")
        table_frame.pack(fill="both", expand=True)
        
        scroll_y = ctk.CTkScrollbar(table_frame)
        scroll_y.pack(side="right", fill="y")
        
        columns = ("ID", "TÍTULO", "AUTOR", "GÊNERO", "CÓPIAS", "DISPONÍVEIS", "LOCAL", "STATUS")
        self.books_tree = ttk.Treeview(table_frame, columns=columns, show="headings", yscrollcommand=scroll_y.set, height=12)
        scroll_y.configure(command=self.books_tree.yview)
        
        col_widths = {"ID": 80, "TÍTULO": 200, "AUTOR": 160, "GÊNERO": 100, "CÓPIAS": 80, "DISPONÍVEIS": 100, "LOCAL": 80, "STATUS": 100}
        for col in columns:
            self.books_tree.heading(col, text=col)
            self.books_tree.column(col, width=col_widths.get(col, 120), anchor="center")
            
        self.books_tree.pack(side="left", fill="both", expand=True)
        
        # ==================== IMPLEMENTAÇÃO DO MENU DE BOTÃO DIREITO ====================
        # Cria o menu de contexto
        self.context_menu = ContextMenu(
            self.root,
            book_id_callback=self.handle_context_menu_action,
            title_callback=self.quick_issue_from_book_context
        )
        
        # Vincula o evento de botão direito à treeview
        self.books_tree.bind("<Button-3>", self.show_context_menu)
        
        # Duplo clique ainda funciona
        self.books_tree.bind("<Double-1>", lambda e: self.quick_issue_from_book())
        
    def show_context_menu(self, event):
        """Exibe o menu de contexto no clique do botão direito"""
        # Seleciona o item sob o cursor
        item = self.books_tree.identify_row(event.y)
        if item:
            self.books_tree.selection_set(item)
            values = self.books_tree.item(item, 'values')
            book_id = values[0]
            title = values[1]
            self.context_menu.show(event, book_id, title)
            
    def handle_context_menu_action(self, book_id, is_edit=False):
        """Gerencia as ações do menu de contexto"""
        if is_edit:
            # Editar livro - seleciona na tabela e chama edição
            for item in self.books_tree.get_children():
                if self.books_tree.item(item, 'values')[0] == book_id:
                    self.books_tree.selection_set(item)
                    self.edit_selected_book()
                    break
        else:
            # Excluir livro
            for item in self.books_tree.get_children():
                if self.books_tree.item(item, 'values')[0] == book_id:
                    self.books_tree.selection_set(item)
                    self.delete_selected_book()
                    break
                    
    def quick_issue_from_book_context(self, book_id):
        """Empréstimo rápido vindo do menu de contexto"""
        self.show_loans_view()
        self.loan_book_field.set(book_id)
        self.check_book_availability_loan()

    def update_books_summary(self):
        conn = sqlite3.connect('test.db')
        total_books = conn.execute("SELECT COUNT(*) FROM book_info").fetchone()[0]
        conn.close()
        self.books_summary_label.configure(text=f"📊 {total_books} livro(s) no catálogo")

    def update_all_stats(self):
        conn = sqlite3.connect('test.db')
        total_books = conn.execute("SELECT COUNT(*) FROM book_info").fetchone()[0]
        total_copies = conn.execute("SELECT SUM(COPIES) FROM book_info").fetchone()[0] or 0
        loaned_books = conn.execute("SELECT COUNT(*) FROM book_issued").fetchone()[0]
        conn.close()
        available_copies = total_copies - loaned_books
        
        self.total_books_label.configure(text=str(total_books))
        self.total_copies_label.configure(text=str(total_copies))
        self.loaned_books_label.configure(text=str(loaned_books))
        self.avail_books_label.configure(text=str(available_copies))
        self.update_books_summary()

    def load_all_books(self):
        for item in self.books_tree.get_children(): self.books_tree.delete(item)
        conn = sqlite3.connect('test.db')
        loaned_counts = {row[0]: row[1] for row in conn.execute("SELECT BOOK_ID, COUNT(*) FROM book_issued GROUP BY BOOK_ID").fetchall()}
        
        for row in conn.execute("SELECT ID, TITLE, AUTHOR, GENRE, COPIES, LOCATION FROM book_info ORDER BY TITLE").fetchall():
            book_id, title, author, genre, copies, location = row
            loaned = loaned_counts.get(book_id, 0)
            available = copies - loaned
            status = "❌ Indisponível" if available <= 0 else "📤 Parcial" if loaned > 0 else "✅ Disponível"
            self.books_tree.insert("", "end", values=(book_id, title, author, genre, copies, available, location, status))
        conn.close()
        self.update_all_stats()

    def search_books(self):
        term = self.book_search.get().upper()
        if not term:
            self.load_all_books()
            return
        for item in self.books_tree.get_children(): self.books_tree.delete(item)
        conn = sqlite3.connect('test.db')
        loaned_counts = {row[0]: row[1] for row in conn.execute("SELECT BOOK_ID, COUNT(*) FROM book_issued GROUP BY BOOK_ID").fetchall()}
        
        for row in conn.execute("SELECT ID, TITLE, AUTHOR, GENRE, COPIES, LOCATION FROM book_info WHERE ID LIKE ? OR UPPER(TITLE) LIKE ? OR UPPER(AUTHOR) LIKE ?", (f'%{term}%', f'%{term}%', f'%{term}%')).fetchall():
            book_id, title, author, genre, copies, location = row
            loaned = loaned_counts.get(book_id, 0)
            available = copies - loaned
            status = "❌ Indisponível" if available <= 0 else "✅ Disponível"
            self.books_tree.insert("", "end", values=(book_id, title, author, genre, copies, available, location, status))
        conn.close()

    def clear_book_search(self):
        self.book_search.clear()
        self.load_all_books()

    def clear_book_form(self):
        self.book_id.clear()
        self.book_title.clear()
        self.book_author.clear()
        self.book_genre.clear()
        self.book_copies.clear()
        self.book_location.clear()
        if self.book_id.entry.cget('state') == 'disabled':
            self.book_id.entry.configure(state='normal')
            self.add_btn.configure(text="➕ Adicionar Livro", command=self.add_book, fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"])
            self.clear_btn.configure(text="🗑️ Limpar")

    def edit_selected_book(self):
        selected = self.books_tree.selection()
        if not selected:
            Toast.show(self.root, "Selecione um livro para editar!", 'warning')
            return
        values = self.books_tree.item(selected[0])['values']
        self.clear_book_form()
        
        self.book_id.set(values[0])
        self.book_title.set(values[1])
        self.book_author.set(values[2])
        self.book_genre.set(values[3])
        self.book_copies.set(str(values[4]))
        self.book_location.set(values[6])
        
        self.book_id.entry.configure(state='disabled')
        self.add_btn.configure(text="✏️ Atualizar Livro", fg_color="#3182CE", command=self.update_book)
        self.clear_btn.configure(text="❌ Cancelar Edição", command=self.clear_book_form)
        Toast.show(self.root, f"Editando: {values[1]}", 'info')

    def update_book(self):
        if not all([self.book_title.get(), self.book_author.get(), self.book_genre.get(), self.book_location.get()]):
            Toast.show(self.root, "Preencha todos os campos!", 'warning')
            return
        try: copies = int(self.book_copies.get()) if self.book_copies.get() else 1
        except ValueError:
            Toast.show(self.root, "Número de cópias inválido!", 'warning')
            return
            
        conn = sqlite3.connect('test.db')
        conn.execute("UPDATE book_info SET TITLE=?, AUTHOR=?, GENRE=?, COPIES=?, LOCATION=? WHERE ID=?",
                     (self.book_title.get().capitalize(), self.book_author.get().capitalize(),
                      self.book_genre.get().capitalize(), copies, self.book_location.get().upper(), self.book_id.get()))
        conn.commit()
        conn.close()
        
        Toast.show(self.root, "Livro atualizado!", 'success')
        self.clear_book_form()
        self.load_all_books()

    def add_book(self):
        if not all([self.book_id.get(), self.book_title.get(), self.book_author.get(), self.book_genre.get(), self.book_location.get()]):
            Toast.show(self.root, "Preencha todos os campos!", 'warning')
            return
        conn = sqlite3.connect('test.db')
        try:
            copies = int(self.book_copies.get()) if self.book_copies.get() else 1
            conn.execute("INSERT INTO book_info VALUES (?,?,?,?,?,?)",
                         (self.book_id.get().upper(), self.book_title.get().capitalize(), self.book_author.get().capitalize(),
                          self.book_genre.get().capitalize(), copies, self.book_location.get().upper()))
            conn.commit()
            Toast.show(self.root, "Livro adicionado!", 'success')
            self.clear_book_form()
            self.load_all_books()
        except sqlite3.IntegrityError:
            Toast.show(self.root, "ID já existe!", 'error')
        except ValueError:
            Toast.show(self.root, "Cópias inválidas!", 'error')
        finally:
            conn.close()

    def delete_selected_book(self):
        selected = self.books_tree.selection()
        if not selected:
            Toast.show(self.root, "Selecione um livro!", 'warning')
            return
        book_id = self.books_tree.item(selected[0])['values'][0]
        conn = sqlite3.connect('test.db')
        if conn.execute("SELECT * FROM book_issued WHERE BOOK_ID = ?", (book_id,)).fetchone():
            Toast.show(self.root, "Livro está emprestado!", 'error')
            conn.close()
            return
        if messagebox.askyesno("Confirmar", f"Excluir livro ID: {book_id}?"):
            conn.execute("DELETE FROM book_info WHERE ID = ?", (book_id,))
            conn.commit()
            Toast.show(self.root, "Livro excluído!", 'success')
            self.load_all_books()
        conn.close()

    # ==================== VISUAL DE EMPRÉSTIMOS ====================
    def show_loans_view(self):
        self.current_view = 'loans'
        for btn in self.sidebar_buttons: btn.set_active(False)
        self.sidebar_buttons[1].set_active(True)
        
        for widget in self.content_area.winfo_children(): widget.destroy()
        
        header_frame = ctk.CTkFrame(self.content_area, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 20))
        ctk.CTkLabel(header_frame, text="Gerenciamento de Empréstimos", font=("Segoe UI", 24, "bold")).pack(side="left")
        self.summary_label = ctk.CTkLabel(header_frame, text="", text_color="gray")
        self.summary_label.pack(side="right")
        self.update_loan_summary()
        
        top_cards = ctk.CTkFrame(self.content_area, fg_color="transparent")
        top_cards.pack(fill="x", pady=(0, 24))
        
        # CARD EMPRESTAR
        loan_card = ctk.CTkFrame(top_cards, corner_radius=10)
        loan_card.pack(side="left", expand=True, fill="both", padx=(0, 10))
        
        ctk.CTkLabel(loan_card, text="📤 EMPRESTAR LIVRO", font=("Segoe UI", 16, "bold"), text_color="#2E7D32").pack(anchor="w", padx=25, pady=(20, 15))
        
        self.loan_book_field = StyledEntry(loan_card, "ID do Livro", "ID do livro", "📖")
        self.loan_book_field.pack(fill="x", padx=25, pady=(0, 5))
        self.loan_book_field.entry.bind('<KeyRelease>', lambda e: self.check_book_availability_loan())
        
        # Label para mostrar disponibilidade
        self.availability_text = ctk.CTkLabel(loan_card, text="", font=("Segoe UI", 12))
        self.availability_text.pack(anchor="w", padx=25, pady=(0, 10))
        
        self.loan_student_field = StyledEntry(loan_card, "ID do Estudante", "ID do estudante", "👤")
        self.loan_student_field.pack(fill="x", padx=25, pady=(0, 20))
        
        ctk.CTkButton(loan_card, text="Confirmar Empréstimo", font=("Segoe UI", 12, "bold"), height=40, command=self.make_loan).pack(fill="x", padx=25, pady=(0, 25))
        
        # CARD DEVOLVER
        return_card = ctk.CTkFrame(top_cards, corner_radius=10)
        return_card.pack(side="right", expand=True, fill="both", padx=(10, 0))
        
        ctk.CTkLabel(return_card, text="📥 DEVOLVER LIVRO", font=("Segoe UI", 16, "bold"), text_color="#3182CE").pack(anchor="w", padx=25, pady=(20, 15))
        
        self.return_book_field = StyledEntry(return_card, "ID do Livro", "ID do livro", "📖")
        self.return_book_field.pack(fill="x", padx=25, pady=(0, 5))
        self.return_book_field.entry.bind('<KeyRelease>', lambda e: self.check_loan_exists())
        
        # Label para mostrar informações do empréstimo
        self.loan_info_label = ctk.CTkLabel(return_card, text="", font=("Segoe UI", 12))
        self.loan_info_label.pack(anchor="w", padx=25, pady=(0, 10))
        
        self.return_student_field = StyledEntry(return_card, "ID do Estudante", "ID do estudante", "👤")
        self.return_student_field.pack(fill="x", padx=25, pady=(0, 20))
        
        ctk.CTkButton(return_card, text="Confirmar Devolução", fg_color="#3182CE", hover_color="#2B6CB0", font=("Segoe UI", 12, "bold"), height=40, command=self.make_return).pack(fill="x", padx=25, pady=(0, 25))
        
        # CARD HISTÓRICO
        activity_card = ctk.CTkFrame(self.content_area, corner_radius=10)
        activity_card.pack(fill="x", pady=(0, 20))
        
        ctk.CTkLabel(activity_card, text="📊 HISTÓRICO DE EMPRÉSTIMOS", font=("Segoe UI", 16, "bold")).pack(anchor="w", padx=25, pady=(20, 15))
        
        self.create_activity_table(activity_card)
        self.load_all_activity()

    def update_loan_summary(self):
        conn = sqlite3.connect('test.db')
        active_loans = conn.execute("SELECT COUNT(*) FROM book_issued").fetchone()[0]
        conn.close()
        self.summary_label.configure(text=f"📊 {active_loans} empréstimo(s) ativo(s)")

    def check_book_availability_loan(self):
        """Verifica disponibilidade do livro em tempo real"""
        book_id = self.loan_book_field.get()
        if not book_id:
            self.availability_text.configure(text="")
            return
        conn = sqlite3.connect('test.db')
        result = conn.execute("SELECT COPIES, TITLE FROM book_info WHERE ID=?", (book_id.upper(),)).fetchone()
        conn.close()
        
        if result:
            copies, title = result
            if copies > 0:
                self.availability_text.configure(text=f"✅ Disponível! {copies} cópia(s) de '{title}'", text_color="#38A169")
            else:
                self.availability_text.configure(text=f"❌ Indisponível - '{title}' sem cópias", text_color="#E53E3E")
        else:
            self.availability_text.configure(text="⚠️ Livro não encontrado no catálogo", text_color="#DD6B20")

    def check_loan_exists(self):
        """Verifica se o livro está emprestado para algum estudante"""
        book_id = self.return_book_field.get()
        if not book_id:
            self.loan_info_label.configure(text="")
            return
        conn = sqlite3.connect('test.db')
        result = conn.execute("SELECT STUDENT_ID, ISSUE_DATE, RETURN_DATE FROM book_issued WHERE BOOK_ID=?", (book_id.upper(),)).fetchone()
        conn.close()
        
        if result:
            student_id, issue_date, return_date = result
            self.loan_info_label.configure(text=f"📌 Emprestado para {student_id} em {issue_date} | Devolução: {return_date}", text_color="#3182CE")
        else:
            self.loan_info_label.configure(text="")

    def create_activity_table(self, parent):
        self.style_treeview()
        table_frame = ctk.CTkFrame(parent, fg_color="transparent")
        table_frame.pack(fill="x", padx=25, pady=(0, 25))
        
        scroll_y = ctk.CTkScrollbar(table_frame)
        scroll_y.pack(side="right", fill="y")
        
        columns = ("ID LIVRO", "TÍTULO", "ID ESTUDANTE", "DATA EMPRÉSTIMO", "DATA DEVOLUÇÃO", "STATUS")
        self.activity_tree = ttk.Treeview(table_frame, columns=columns, show="headings", yscrollcommand=scroll_y.set, height=12)
        scroll_y.configure(command=self.activity_tree.yview)
        
        col_widths = {"ID LIVRO": 100, "TÍTULO": 200, "ID ESTUDANTE": 120, "DATA EMPRÉSTIMO": 130, "DATA DEVOLUÇÃO": 130, "STATUS": 100}
        for col in columns:
            self.activity_tree.heading(col, text=col)
            self.activity_tree.column(col, width=col_widths.get(col, 120), anchor="center")
            
        self.activity_tree.pack(side="left", fill="both", expand=True)

    def load_all_activity(self):
        for item in self.activity_tree.get_children(): self.activity_tree.delete(item)
        conn = sqlite3.connect('test.db')
        cursor = conn.execute("SELECT bi.BOOK_ID, b.TITLE, bi.STUDENT_ID, bi.ISSUE_DATE, bi.RETURN_DATE FROM book_issued bi LEFT JOIN book_info b ON bi.BOOK_ID = b.ID ORDER BY bi.ISSUE_DATE DESC")
        
        today = datetime.now().strftime("%Y-%m-%d")
        for row in cursor.fetchall():
            book_id, title, student_id, issue_date, return_date = row
            status = "⚠️ Atrasado" if return_date < today else "✅ No Prazo"
            self.activity_tree.insert("", "end", values=(book_id, title or book_id, student_id, issue_date, return_date, status))
        conn.close()
        self.update_loan_summary()

    def make_loan(self):
        book_id = self.loan_book_field.get().upper()
        student_id = self.loan_student_field.get().upper()
        if not book_id or not student_id:
            Toast.show(self.root, "Preencha todos os campos!", 'warning')
            return
            
        conn = sqlite3.connect('test.db')
        result = conn.execute("SELECT COPIES FROM book_info WHERE ID=?", (book_id,)).fetchone()
        
        if not result: 
            Toast.show(self.root, "Livro não encontrado!", 'error')
        elif result[0] <= 0: 
            Toast.show(self.root, "Sem cópias disponíveis!", 'error')
        else:
            try:
                conn.execute("INSERT INTO book_issued VALUES (?,?,date('now'),date('now','+7 day'))", (book_id, student_id))
                conn.execute("UPDATE book_info SET COPIES = COPIES - 1 WHERE ID=?", (book_id,))
                conn.commit()
                Toast.show(self.root, "Livro emprestado!", 'success')
                self.loan_book_field.clear()
                self.loan_student_field.clear()
                self.availability_text.configure(text="")
                self.load_all_activity()
                self.load_all_books()
            except sqlite3.IntegrityError:
                Toast.show(self.root, "Livro já emprestado para este estudante!", 'error')
        conn.close()

    def make_return(self):
        book_id = self.return_book_field.get().upper()
        student_id = self.return_student_field.get().upper()
        if not book_id or not student_id:
            Toast.show(self.root, "Preencha todos os campos!", 'warning')
            return
            
        conn = sqlite3.connect('test.db')
        if conn.execute("SELECT * FROM book_issued WHERE BOOK_ID=? AND STUDENT_ID=?", (book_id, student_id)).fetchone():
            # Verificar multa por atraso
            return_date = conn.execute("SELECT RETURN_DATE FROM book_issued WHERE BOOK_ID=? AND STUDENT_ID=?", (book_id, student_id)).fetchone()[0]
            today = datetime.now().strftime("%Y-%m-%d")
            if return_date < today:
                days_late = (datetime.now() - datetime.strptime(return_date, "%Y-%m-%d")).days
                fine = days_late * 2
                if fine > 0:
                    Toast.show(self.root, f"Multa por atraso: R$ {fine:.2f}", 'warning', 4000)
            
            conn.execute("DELETE FROM book_issued WHERE BOOK_ID=? AND STUDENT_ID=?", (book_id, student_id))
            conn.execute("UPDATE book_info SET COPIES = COPIES + 1 WHERE ID=?", (book_id,))
            conn.commit()
            Toast.show(self.root, "Livro devolvido!", 'success')
            self.return_book_field.clear()
            self.return_student_field.clear()
            self.loan_info_label.configure(text="")
            self.load_all_activity()
            self.load_all_books()
        else:
            Toast.show(self.root, "Empréstimo não encontrado!", 'error')
        conn.close()

    def quick_issue_from_book(self):
        selected = self.books_tree.selection()
        if selected:
            book_id = self.books_tree.item(selected[0])['values'][0]
            self.show_loans_view()
            self.loan_book_field.set(book_id)
            self.check_book_availability_loan()

if __name__ == "__main__":
    app = UnifiedLibrarySystem()