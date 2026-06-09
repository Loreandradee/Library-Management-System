from tkinter import*
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import sqlite3
import os
from datetime import datetime, timedelta
import json
import csv
from tkinter import font as tkfont

# ==================== DESIGN SYSTEM ====================
class Theme:
    LIGHT = {
        'BG_GLOBAL': "#F4F7F6",
        'BG_CARDS': "#FFFFFF",
        'PRIMARY': "#2E7D32",
        'PRIMARY_LIGHT': "#A5D6A7",
        'DANGER': "#E53E3E",
        'SUCCESS': "#38A169",
        'WARNING': "#DD6B20",
        'INFO': "#3182CE",
        'TEXT_PRIMARY': "#1A202C",
        'TEXT_SECONDARY': "#4A5568",
        'TEXT_BODY': "#2D3748",
        'BORDER': "#CBD5E0",
        'ACTIVE': "#E8F5E9",
        'INPUT_BG': "#FFFFFF",
        'CARD_SHADOW': "#E2E8F0"
    }
    
    DARK = {
        'BG_GLOBAL': "#1a1a2e",
        'BG_CARDS': "#16213e",
        'PRIMARY': "#4CAF50",
        'PRIMARY_LIGHT': "#2E7D32",
        'DANGER': "#f44336",
        'SUCCESS': "#4CAF50",
        'WARNING': "#ff9800",
        'INFO': "#4299E1",
        'TEXT_PRIMARY': "#ffffff",
        'TEXT_SECONDARY': "#a0a0a0",
        'TEXT_BODY': "#e0e0e0",
        'BORDER': "#4a4a5e",
        'ACTIVE': "#1a3a2a",
        'INPUT_BG': "#2a2a3e",
        'CARD_SHADOW': "#2a2a3e"
    }
    
    current = LIGHT

# ==================== ESTILO DE ENTRY PERSONALIZADO ====================
class StyledEntry(Frame):
    def __init__(self, parent, label="", placeholder="", icon="", **kwargs):
        super().__init__(parent, bg=Theme.current['BG_CARDS'])
        
        self.label_text = label
        self.placeholder = placeholder
        self.icon = icon
        
        if label:
            self.label_widget = Label(self, text=label, font=("Segoe UI", 11, "bold"),
                                      bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_SECONDARY'])
            self.label_widget.pack(anchor="w", pady=(0, 5))
        
        # Frame principal com borda (mais fina)
        self.entry_frame = Frame(self, bg=Theme.current['BORDER'], bd=0, highlightthickness=0)
        self.entry_frame.pack(fill=X)
        
        # Borda padrão (cinza) - mais fina: highlightthickness=1
        self.entry_frame.config(highlightbackground=Theme.current['BORDER'],
                               highlightcolor=Theme.current['PRIMARY'],
                               highlightthickness=1)  # Borda fina
        
        # Frame interno com fundo branco
        inner_frame = Frame(self.entry_frame, bg=Theme.current['INPUT_BG'])
        inner_frame.pack(fill=BOTH, expand=True, padx=1, pady=1)
        
        if icon:
            self.icon_label = Label(inner_frame, text=icon, font=("Segoe UI", 12),
                                    bg=Theme.current['INPUT_BG'], fg=Theme.current['TEXT_SECONDARY'])
            self.icon_label.pack(side=LEFT, padx=(12, 5))
        
        self.entry = Entry(inner_frame, font=("Segoe UI", 11),
                          bg=Theme.current['INPUT_BG'], fg=Theme.current['TEXT_BODY'],
                          bd=0, highlightthickness=0, **kwargs)
        self.entry.pack(side=LEFT, fill=BOTH, expand=True, padx=(0, 12), pady=12)
        
        self.entry.bind('<FocusIn>', self.on_focus_in)
        self.entry.bind('<FocusOut>', self.on_focus_out)
        
        self.has_placeholder = False
        if placeholder:
            self.set_placeholder()
    
    def on_focus_in(self, event):
        # Quando ganha foco, a borda fica verde escuro (PRIMARY) - mantém a mesma espessura (1)
        self.entry_frame.config(highlightbackground=Theme.current['PRIMARY'],
                               highlightcolor=Theme.current['PRIMARY'],
                               highlightthickness=1)  # Borda fina
        if self.has_placeholder and self.entry.get() == self.placeholder:
            self.entry.delete(0, END)
            self.entry.config(fg=Theme.current['TEXT_BODY'])
            self.has_placeholder = False
    
    def on_focus_out(self, event):
        # Quando perde foco, a borda volta a ser cinza
        self.entry_frame.config(highlightbackground=Theme.current['BORDER'],
                               highlightcolor=Theme.current['BORDER'],
                               highlightthickness=1)  # Borda fina
        if self.placeholder and not self.entry.get():
            self.set_placeholder()
    
    def set_placeholder(self):
        self.entry.delete(0, END)
        self.entry.insert(0, self.placeholder)
        self.entry.config(fg=Theme.current['TEXT_SECONDARY'])
        self.has_placeholder = True
    
    def get(self):
        if self.has_placeholder:
            return ""
        return self.entry.get().strip()
    
    def set(self, value):
        self.entry.delete(0, END)
        self.entry.insert(0, value)
        self.entry.config(fg=Theme.current['TEXT_BODY'])
        self.has_placeholder = False
    
    def clear(self):
        self.entry.delete(0, END)
        if self.placeholder:
            self.set_placeholder()
    
    @property
    def entry_widget(self):
        return self.entry

# ==================== SIDEBAR BUTTON ====================
class SidebarButton:
    def __init__(self, parent, texto, icone, comando, is_active=False):
        self.parent = parent
        self.comando = comando
        self.btn_frame = Frame(parent, bg=Theme.current['BG_CARDS'], height=45)
        self.btn_frame.pack(fill=X, pady=2, padx=12)
        
        self.btn = Button(self.btn_frame, text=f"{icone}  {texto}", 
                         font=("Segoe UI", 11), fg=Theme.current['TEXT_BODY'], 
                         bg=Theme.current['BG_CARDS'],
                         bd=0, anchor="w", padx=16, pady=10,
                         cursor="hand2", command=self.click)
        self.btn.pack(fill=BOTH, expand=True)
        
        self.active_line = Frame(self.btn_frame, bg=Theme.current['PRIMARY'], width=4)
        
        if is_active:
            self.set_active(True)
    
    def click(self):
        self.comando()
    
    def set_active(self, active):
        if active:
            self.btn_frame.config(bg=Theme.current['ACTIVE'])
            self.btn.config(bg=Theme.current['ACTIVE'], fg=Theme.current['PRIMARY'], 
                          font=("Segoe UI", 11, "bold"))
            self.active_line.place(x=0, y=0, relheight=1)
        else:
            self.btn_frame.config(bg=Theme.current['BG_CARDS'])
            self.btn.config(bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_BODY'], 
                          font=("Segoe UI", 11))
            self.active_line.place_forget()

# ==================== LOADING OVERLAY ====================
class LoadingOverlay:
    def __init__(self, parent):
        self.parent = parent
        self.overlay = None
    
    def show(self, message="Carregando..."):
        self.overlay = Frame(self.parent, bg='black', bd=0)
        self.overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        
        loading_frame = Frame(self.overlay, bg=Theme.current['BG_CARDS'], bd=2, relief=FLAT)
        loading_frame.place(relx=0.5, rely=0.5, anchor=CENTER)
        
        self.loading_label = Label(loading_frame, text=message, font=("Segoe UI", 12),
                                   bg=Theme.current['BG_CARDS'], fg=Theme.current['PRIMARY'])
        self.loading_label.pack(padx=30, pady=20)
        
        self.animate_loading()
    
    def animate_loading(self):
        dots = 0
        def update():
            nonlocal dots
            if self.loading_label and self.loading_label.winfo_exists():
                dots = (dots + 1) % 4
                text = "Carregando" + "." * dots
                self.loading_label.config(text=text)
                self.parent.after(500, update)
        update()
    
    def hide(self):
        if self.overlay:
            self.overlay.destroy()
            self.overlay = None

# ==================== TOAST NOTIFICATIONS ====================
class Toast:
    @staticmethod
    def show(parent, message, type='info', duration=3000):
        toast = Toplevel(parent)
        toast.wm_overrideredirect(True)
        
        colors = {
            'success': Theme.current['SUCCESS'],
            'error': Theme.current['DANGER'],
            'warning': Theme.current['WARNING'],
            'info': Theme.current['PRIMARY']
        }
        
        parent.update_idletasks()
        x = parent.winfo_rootx() + parent.winfo_width() - 350
        y = parent.winfo_rooty() + parent.winfo_height() - 80
        toast.geometry(f"320x50+{x}+{y}")
        
        frame = Frame(toast, bg=colors.get(type, colors['info']), bd=0)
        frame.pack(fill=BOTH, expand=True)
        
        icons = {'success': '✓', 'error': '✗', 'warning': '⚠', 'info': 'ℹ'}
        Label(frame, text=icons.get(type, 'ℹ'), font=("Segoe UI", 16),
              bg=frame['bg'], fg='white').pack(side=LEFT, padx=12)
        
        Label(frame, text=message, font=("Segoe UI", 10),
              bg=frame['bg'], fg='white', wraplength=250).pack(side=LEFT, padx=5)
        
        toast.after(duration, toast.destroy)

# ==================== CLASSE PRINCIPAL ====================
class UnifiedLibrarySystem:
    def __init__(self):
        self.root = Tk()
        self.root.title('Library Management System')
        self.root.state('zoomed')
        self.root.configure(bg=Theme.current['BG_GLOBAL'])
        
        self.load_settings()
        self.init_db()
        self.create_login_screen()
        self.setup_shortcuts()
        
        self.root.mainloop()
    
    def init_db(self):
        conn = sqlite3.connect('test.db')
        conn.execute('''CREATE TABLE IF NOT EXISTS book_info
        (ID VARCHAR PRIMARY KEY NOT NULL,
        TITLE VARTEXT NOT NULL,
        AUTHOR VARTEXT NOT NULL,
        GENRE VARTEXT NOT NULL,
        COPIES VARINT NOT NULL,
        LOCATION VARCHAR NOT NULL);''')
        
        conn.execute('''CREATE TABLE IF NOT EXISTS book_issued
        (BOOK_ID VARCHAR NOT NULL,
        STUDENT_ID VARCHAR NOT NULL,
        ISSUE_DATE DATE NOT NULL,
        RETURN_DATE DATE NOT NULL,
        PRIMARY KEY (BOOK_ID,STUDENT_ID));''')
        conn.commit()
        
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM book_info")
        if cursor.fetchone()[0] == 0:
            livros = [
                ("B1042", "Programação Python", "João Silva", "Tecnologia", 5, "A1"),
                ("B2056", "Fundamentos de Dados", "Maria Souza", "Tecnologia", 3, "A2"),
                ("B3089", "O Grande Gatsby", "Fitzgerald", "Ficção", 7, "B1"),
                ("B4123", "Aprendizado de Máquina", "André Ng", "Tecnologia", 4, "A3"),
                ("B5678", "Guia JavaScript", "Carlos Costa", "Tecnologia", 6, "B2"),
                ("B6789", "Código Limpo", "Roberto Martins", "Tecnologia", 4, "C1"),
                ("B7890", "Inteligência Artificial", "Stuart Russell", "Tecnologia", 3, "A4"),
                ("B8901", "Design Patterns", "Erich Gamma", "Tecnologia", 5, "B3"),
            ]
            for livro in livros:
                try:
                    conn.execute("INSERT INTO book_info VALUES (?,?,?,?,?,?)", livro)
                except:
                    pass
        
        cursor.execute("SELECT COUNT(*) FROM book_issued")
        if cursor.fetchone()[0] == 0:
            dados_exemplo = [
                ("B1042", "S992", "2025-05-01", "2025-05-08"),
                ("B2056", "S451", "2025-05-02", "2025-05-09"),
                ("B3089", "S783", "2025-05-03", "2025-05-10"),
            ]
            for dados in dados_exemplo:
                try:
                    conn.execute("INSERT INTO book_issued VALUES (?,?,?,?)", dados)
                except:
                    pass
        
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
            except:
                self.settings = {}
        
        if self.settings.get('dark_mode'):
            Theme.current = Theme.DARK
    
    def save_settings(self):
        with open('settings.json', 'w') as f:
            json.dump(self.settings, f)
    
    def setup_shortcuts(self):
        self.root.bind('<Control-b>', lambda e: self.show_books_view())
        self.root.bind('<Control-e>', lambda e: self.show_loans_view())
        self.root.bind('<Control-l>', lambda e: self.create_login_screen())
        self.root.bind('<F1>', lambda e: self.show_help())
        self.root.bind('<Control-s>', lambda e: self.show_settings())
        self.root.bind('<Control-d>', lambda e: self.toggle_theme())
        self.root.bind('<Delete>', lambda e: self.delete_selected_book())
    
    def create_login_screen(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.configure(bg=Theme.current['PRIMARY_LIGHT'])
        
        login_card = Frame(self.root, bg=Theme.current['BG_CARDS'], bd=1, relief=FLAT,
                          highlightbackground=Theme.current['PRIMARY'], highlightthickness=1)
        login_card.place(relx=0.5, rely=0.5, anchor=CENTER, width=450, height=600)
        
        inner = Frame(login_card, bg=Theme.current['BG_CARDS'])
        inner.pack(fill=BOTH, expand=True, padx=40, pady=40)
        
        Label(inner, text="📚", font=("Segoe UI", 48), 
              bg=Theme.current['BG_CARDS'], fg=Theme.current['PRIMARY']).pack(pady=(0, 10))
        Label(inner, text="Bem-vindo ao Library Management", font=("Segoe UI", 15, "bold"),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_PRIMARY']).pack()
        Label(inner, text="Sistema de Gerenciamento de Biblioteca", font=("Segoe UI", 10),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_SECONDARY']).pack(pady=(0, 30))
        
        Frame(inner, bg=Theme.current['BORDER'], height=1).pack(fill=X, pady=(0, 25))
        
        self.username_var = StringVar()
        self.password_var = StringVar()
        
        # ==================== CAMPO USUÁRIO (USANDO STYLEDENTRY) ====================
        self.username_field = StyledEntry(inner, "Usuário", "Digite seu usuário", "👤")
        self.username_field.pack(fill=X, pady=(0, 20))
        
        # ==================== CAMPO SENHA (USANDO STYLEDENTRY) ====================
        self.password_field = StyledEntry(inner, "Senha", "Digite sua senha", "🔒", show="•")
        self.password_field.pack(fill=X, pady=(0, 25))
        
        # Conectar as variáveis
        self.username_field.entry.config(textvariable=self.username_var)
        self.password_field.entry.config(textvariable=self.password_var)
        
        # ==================== BOTÕES ====================
        remember_var = BooleanVar(value=self.settings.get('remember_login', False))
        Checkbutton(inner, text="Lembrar meu login", variable=remember_var,
                   bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_SECONDARY'],
                   selectcolor=Theme.current['BG_CARDS']).pack(anchor="w", pady=(0, 15))
        
        btn_login = Button(inner, text="ENTRAR", font=("Segoe UI", 12, "bold"),
                          fg="white", bg=Theme.current['PRIMARY'], bd=0, cursor="hand2",
                          padx=30, pady=12, command=lambda: self.do_login(remember_var.get()))
        btn_login.pack(fill=X, pady=(0, 15))
        
        self.login_error_label = Label(inner, text="", font=("Segoe UI", 10),
                                       bg=Theme.current['BG_CARDS'], fg=Theme.current['DANGER'])
        self.login_error_label.pack()
        
        Frame(inner, bg=Theme.current['BORDER'], height=1).pack(fill=X, pady=(0, 15))
        
        cred_frame = Frame(inner, bg=Theme.current['BG_CARDS'], bd=1, relief=FLAT,
                          highlightbackground=Theme.current['BORDER'], highlightthickness=1)
        cred_frame.pack(fill=X)
        Label(cred_frame, text="🔐 Credenciais de Demonstração", font=("Segoe UI", 10, "bold"),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_SECONDARY']).pack(pady=(8, 4))
        Label(cred_frame, text="Usuário: Prakarsha  |  Senha: root", 
              font=("Segoe UI", 10), bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_BODY']).pack(pady=(0, 8))
        
        # Botão de login rápido
        quick_login_frame = Frame(inner, bg=Theme.current['BG_CARDS'])
        quick_login_frame.pack(fill=X, pady=(15, 0))
        
        Button(quick_login_frame, text="🔑 Login Rápido", font=("Segoe UI", 10),
              fg=Theme.current['PRIMARY'], bg=Theme.current['BG_CARDS'], bd=1,
              cursor="hand2", padx=20, pady=5,
              command=lambda: self.quick_login()).pack()
        
        self.username_field.entry.bind('<Return>', lambda e: self.do_login(remember_var.get()))
        self.password_field.entry.bind('<Return>', lambda e: self.do_login(remember_var.get()))
    
    def quick_login(self):
        self.username_var.set("Prakarsha")
        self.password_var.set("root")
        self.do_login(False)
    
    def do_login(self, remember=False):
        username = self.username_var.get()
        password = self.password_var.get()
        
        if not username or not password:
            self.login_error_label.config(text="⚠️ Por favor, preencha todos os campos!")
            return
        
        loading = LoadingOverlay(self.root)
        loading.show("Verificando credenciais...")
        
        self.root.after(100, lambda: self.check_login(username, password, remember, loading))
    
    def check_login(self, username, password, remember, loading):
        self.cursor_login.execute("SELECT * FROM login WHERE username=? AND password=?", 
                                  (username, password))
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
            self.login_error_label.config(text="❌ Usuário ou senha inválidos!")
            self.username_var.set("")
            self.password_var.set("")
            self.root.bell()
    
    def create_main_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        
        self.root.configure(bg=Theme.current['BG_GLOBAL'])
        
        # Sidebar
        self.sidebar = Frame(self.root, bg=Theme.current['BG_CARDS'], width=280)
        self.sidebar.pack(side=LEFT, fill=Y)
        self.sidebar.pack_propagate(False)
        Frame(self.sidebar, bg=Theme.current['BORDER'], width=1).pack(side=RIGHT, fill=Y)
        
        # Logo
        logo_frame = Frame(self.sidebar, bg=Theme.current['BG_CARDS'], height=100)
        logo_frame.pack(fill=X, pady=(32, 24))
        Label(logo_frame, text="📚 Library Management", font=("Segoe UI", 15, "bold"),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['PRIMARY']).pack()
        Label(logo_frame, text="Sistema de Biblioteca", font=("Segoe UI", 10),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_SECONDARY']).pack()
        
        Frame(self.sidebar, bg=Theme.current['BORDER'], height=1).pack(fill=X, padx=20, pady=8)
        
        self.sidebar_buttons = []
        btn_books = SidebarButton(self.sidebar, "Livros", "📖", self.show_books_view, is_active=True)
        self.sidebar_buttons.append(btn_books)
        btn_loans = SidebarButton(self.sidebar, "Empréstimos", "👥", self.show_loans_view, is_active=False)
        self.sidebar_buttons.append(btn_loans)
        
        status_frame = Frame(self.sidebar, bg=Theme.current['BG_CARDS'])
        status_frame.pack(fill=X, padx=20, pady=10)
        Label(status_frame, text="🟢 Sistema Online", font=("Segoe UI", 9),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['SUCCESS']).pack()
        
        Frame(self.sidebar, bg=Theme.current['BG_CARDS'], height=300).pack(fill=BOTH, expand=True)
        
        Frame(self.sidebar, bg=Theme.current['BORDER'], height=1).pack(fill=X, padx=20, pady=16)
        
        theme_btn = Button(self.sidebar, text="🌓 Alternar Tema", font=("Segoe UI", 10),
                          fg=Theme.current['TEXT_BODY'], bg=Theme.current['BG_CARDS'], 
                          bd=0, anchor="w", padx=28, pady=8, cursor="hand2", command=self.toggle_theme)
        theme_btn.pack(fill=X)
        
        help_btn = Button(self.sidebar, text="❓ Ajuda (F1)", font=("Segoe UI", 10),
                         fg=Theme.current['TEXT_BODY'], bg=Theme.current['BG_CARDS'], 
                         bd=0, anchor="w", padx=28, pady=8, cursor="hand2", command=self.show_help)
        help_btn.pack(fill=X)
        
        logout_btn = Button(self.sidebar, text="🚪 Sair", font=("Segoe UI", 10),
                           fg=Theme.current['DANGER'], bg=Theme.current['BG_CARDS'], 
                           bd=0, anchor="w", padx=28, pady=12, cursor="hand2", command=self.create_login_screen)
        logout_btn.pack(fill=X, pady=(0, 24))
        
        # Área de conteúdo com scroll
        main_container = Frame(self.root, bg=Theme.current['BG_GLOBAL'])
        main_container.pack(side=LEFT, expand=True, fill=BOTH)
        
        self.content_canvas = Canvas(main_container, bg=Theme.current['BG_GLOBAL'], highlightthickness=0)
        self.content_canvas.pack(side=LEFT, expand=True, fill=BOTH)
        
        self.content_scrollbar = ttk.Scrollbar(main_container, orient="vertical", command=self.content_canvas.yview)
        self.content_scrollbar.pack(side=RIGHT, fill=Y)
        self.content_canvas.configure(yscrollcommand=self.content_scrollbar.set)
        
        self.content_area = Frame(self.content_canvas, bg=Theme.current['BG_GLOBAL'])
        self.canvas_window = self.content_canvas.create_window((0, 0), window=self.content_area, anchor="nw")
        
        def configure_scroll_region(event):
            self.content_canvas.configure(scrollregion=self.content_canvas.bbox("all"))
        
        def configure_canvas_width(event):
            canvas_width = event.width
            self.content_canvas.itemconfig(self.canvas_window, width=canvas_width)
        
        self.content_area.bind("<Configure>", configure_scroll_region)
        self.content_canvas.bind("<Configure>", configure_canvas_width)
        
        def on_mousewheel(event):
            if hasattr(event, 'delta'):
                self.content_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            elif hasattr(event, 'num'):
                if event.num == 4:
                    self.content_canvas.yview_scroll(-1, "units")
                elif event.num == 5:
                    self.content_canvas.yview_scroll(1, "units")
        
        self.content_canvas.bind("<MouseWheel>", on_mousewheel)
        self.content_canvas.bind("<Button-4>", on_mousewheel)
        self.content_canvas.bind("<Button-5>", on_mousewheel)
        self.content_area.bind("<MouseWheel>", on_mousewheel)
        self.content_area.bind("<Button-4>", on_mousewheel)
        self.content_area.bind("<Button-5>", on_mousewheel)
        
        def on_arrow_up(event):
            self.content_canvas.yview_scroll(-1, "units")
        
        def on_arrow_down(event):
            self.content_canvas.yview_scroll(1, "units")
        
        self.content_canvas.bind("<Up>", on_arrow_up)
        self.content_canvas.bind("<Down>", on_arrow_down)
        self.content_area.bind("<Up>", on_arrow_up)
        self.content_area.bind("<Down>", on_arrow_down)
        
        self.content_padding = Frame(self.content_area, bg=Theme.current['BG_GLOBAL'])
        self.content_padding.pack(fill=BOTH, expand=True, padx=32, pady=32)
        
        self.show_books_view()
    
    def toggle_theme(self):
        if Theme.current == Theme.LIGHT:
            Theme.current = Theme.DARK
        else:
            Theme.current = Theme.LIGHT
        
        self.settings['dark_mode'] = Theme.current == Theme.DARK
        self.save_settings()
        
        if hasattr(self, 'content_padding'):
            current_view = self.current_view if hasattr(self, 'current_view') else 'books'
            self.create_main_dashboard()
            if current_view == 'books':
                self.show_books_view()
            else:
                self.show_loans_view()
    
    def show_help(self):
        help_text = """
        📚 AJUDA RÁPIDA - LIBRARY MANAGEMENT
        
        ATALHOS DE TECLADO:
        • Ctrl+B - Abrir Livros
        • Ctrl+E - Abrir Empréstimos
        • Ctrl+L - Voltar ao Login
        • Ctrl+S - Configurações
        • Ctrl+D - Alternar Tema
        • Delete - Excluir livro selecionado
        • F1 - Esta ajuda
        
        DICAS:
        • Role a página com o mouse ou scrollbar
        • Clique direito na tabela para ações rápidas
        • Duplo clique no livro para emprestar
        """
        
        dialog = Toplevel(self.root)
        dialog.title("Ajuda")
        dialog.geometry("500x500")
        dialog.configure(bg=Theme.current['BG_CARDS'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (500 // 2)
        y = (dialog.winfo_screenheight() // 2) - (500 // 2)
        dialog.geometry(f"500x500+{x}+{y}")
        
        text_widget = Text(dialog, font=("Segoe UI", 11), bg=Theme.current['BG_CARDS'],
                          fg=Theme.current['TEXT_BODY'], wrap=WORD, padx=20, pady=20)
        text_widget.pack(fill=BOTH, expand=True)
        text_widget.insert("1.0", help_text)
        text_widget.config(state=DISABLED)
        
        Button(dialog, text="Fechar", font=("Segoe UI", 11, "bold"),
              fg="white", bg=Theme.current['PRIMARY'], bd=0, cursor="hand2",
              padx=20, pady=10, command=dialog.destroy).pack(pady=20)
    
    def show_settings(self):
        dialog = Toplevel(self.root)
        dialog.title("Configurações")
        dialog.geometry("400x300")
        dialog.configure(bg=Theme.current['BG_CARDS'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"400x300+{x}+{y}")
        
        Label(dialog, text="Configurações", font=("Segoe UI", 16, "bold"),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_PRIMARY']).pack(pady=20)
        
        theme_frame = Frame(dialog, bg=Theme.current['BG_CARDS'])
        theme_frame.pack(fill=X, padx=40, pady=10)
        Label(theme_frame, text="🌓 Tema:", font=("Segoe UI", 11),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_BODY']).pack(side=LEFT)
        
        theme_var = BooleanVar(value=Theme.current == Theme.DARK)
        def toggle_theme_setting():
            self.toggle_theme()
            theme_var.set(Theme.current == Theme.DARK)
        
        Checkbutton(theme_frame, text="Modo Escuro", variable=theme_var,
                   command=toggle_theme_setting,
                   bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_BODY']).pack(side=LEFT, padx=10)
        
        remember_frame = Frame(dialog, bg=Theme.current['BG_CARDS'])
        remember_frame.pack(fill=X, padx=40, pady=10)
        Label(remember_frame, text="🔐 Sessão:", font=("Segoe UI", 11),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_BODY']).pack(side=LEFT)
        
        self.remember_var = BooleanVar(value=self.settings.get('remember_login', False))
        Checkbutton(remember_frame, text="Lembrar meu login", variable=self.remember_var,
                   bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_BODY']).pack(side=LEFT, padx=10)
        
        def save_settings():
            self.settings['remember_login'] = self.remember_var.get()
            self.settings['dark_mode'] = Theme.current == Theme.DARK
            self.save_settings()
            Toast.show(dialog, "Configurações salvas!", 'success')
            dialog.after(1000, dialog.destroy)
        
        Button(dialog, text="Salvar", font=("Segoe UI", 11, "bold"),
              fg="white", bg=Theme.current['PRIMARY'], bd=0, cursor="hand2",
              padx=20, pady=10, command=save_settings).pack(pady=20)
    
    # ==================== VISUAL DE LIVROS ====================
    def show_books_view(self):
        self.current_view = 'books'
        
        for btn in self.sidebar_buttons:
            btn.set_active(False)
        self.sidebar_buttons[0].set_active(True)
        
        for widget in self.content_padding.winfo_children():
            widget.destroy()
        
        title_frame = Frame(self.content_padding, bg=Theme.current['BG_GLOBAL'])
        title_frame.pack(fill=X, pady=(0, 24))
        
        Label(title_frame, text="Gerenciamento de Livros", font=("Segoe UI", 24, "bold"),
              bg=Theme.current['BG_GLOBAL'], fg=Theme.current['TEXT_PRIMARY']).pack(side=LEFT)
        
        summary_frame = Frame(title_frame, bg=Theme.current['BG_GLOBAL'])
        summary_frame.pack(side=RIGHT)
        
        self.books_summary_label = Label(summary_frame, text="", font=("Segoe UI", 11),
                                         bg=Theme.current['BG_GLOBAL'], fg=Theme.current['TEXT_SECONDARY'])
        self.books_summary_label.pack()
        self.update_books_summary()
        
        # Card de Estatísticas
        stats_card = Frame(self.content_padding, bg=Theme.current['BG_CARDS'], bd=1, relief=FLAT,
                          highlightbackground=Theme.current['BORDER'], highlightthickness=1)
        stats_card.pack(fill=X, pady=(0, 24))
        
        stats_inner = Frame(stats_card, bg=Theme.current['BG_CARDS'])
        stats_inner.pack(fill=BOTH, padx=24, pady=20)
        
        stats_grid = Frame(stats_inner, bg=Theme.current['BG_CARDS'])
        stats_grid.pack(fill=X)
        
        # Total de Livros
        total_frame = Frame(stats_grid, bg=Theme.current['BG_CARDS'], relief=FLAT, bd=1,
                           highlightbackground=Theme.current['BORDER'], highlightthickness=1)
        total_frame.pack(side=LEFT, expand=True, fill=BOTH, padx=(0, 10))
        total_inner = Frame(total_frame, bg=Theme.current['BG_CARDS'])
        total_inner.pack(fill=BOTH, padx=15, pady=15)
        Label(total_inner, text="📚", font=("Segoe UI", 24), bg=Theme.current['BG_CARDS']).pack()
        self.total_books_label = Label(total_inner, text="0", font=("Segoe UI", 18, "bold"),
                                       bg=Theme.current['BG_CARDS'], fg=Theme.current['PRIMARY'])
        self.total_books_label.pack()
        Label(total_inner, text="Total de Livros", font=("Segoe UI", 10),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_SECONDARY']).pack()
        
        # Total de Cópias
        copies_frame = Frame(stats_grid, bg=Theme.current['BG_CARDS'], relief=FLAT, bd=1,
                            highlightbackground=Theme.current['BORDER'], highlightthickness=1)
        copies_frame.pack(side=LEFT, expand=True, fill=BOTH, padx=(5, 5))
        copies_inner = Frame(copies_frame, bg=Theme.current['BG_CARDS'])
        copies_inner.pack(fill=BOTH, padx=15, pady=15)
        Label(copies_inner, text="📖", font=("Segoe UI", 24), bg=Theme.current['BG_CARDS']).pack()
        self.total_copies_label = Label(copies_inner, text="0", font=("Segoe UI", 18, "bold"),
                                        bg=Theme.current['BG_CARDS'], fg=Theme.current['INFO'])
        self.total_copies_label.pack()
        Label(copies_inner, text="Total de Cópias", font=("Segoe UI", 10),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_SECONDARY']).pack()
        
        # Livros Emprestados
        loaned_frame = Frame(stats_grid, bg=Theme.current['BG_CARDS'], relief=FLAT, bd=1,
                            highlightbackground=Theme.current['BORDER'], highlightthickness=1)
        loaned_frame.pack(side=LEFT, expand=True, fill=BOTH, padx=(5, 5))
        loaned_inner = Frame(loaned_frame, bg=Theme.current['BG_CARDS'])
        loaned_inner.pack(fill=BOTH, padx=15, pady=15)
        Label(loaned_inner, text="🔄", font=("Segoe UI", 24), bg=Theme.current['BG_CARDS']).pack()
        self.loaned_books_label = Label(loaned_inner, text="0", font=("Segoe UI", 18, "bold"),
                                        bg=Theme.current['BG_CARDS'], fg=Theme.current['WARNING'])
        self.loaned_books_label.pack()
        Label(loaned_inner, text="Livros Emprestados", font=("Segoe UI", 10),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_SECONDARY']).pack()
        
        # Disponíveis
        avail_frame = Frame(stats_grid, bg=Theme.current['BG_CARDS'], relief=FLAT, bd=1,
                           highlightbackground=Theme.current['BORDER'], highlightthickness=1)
        avail_frame.pack(side=LEFT, expand=True, fill=BOTH, padx=(10, 0))
        avail_inner = Frame(avail_frame, bg=Theme.current['BG_CARDS'])
        avail_inner.pack(fill=BOTH, padx=15, pady=15)
        Label(avail_inner, text="✅", font=("Segoe UI", 24), bg=Theme.current['BG_CARDS']).pack()
        self.avail_books_label = Label(avail_inner, text="0", font=("Segoe UI", 18, "bold"),
                                       bg=Theme.current['BG_CARDS'], fg=Theme.current['SUCCESS'])
        self.avail_books_label.pack()
        Label(avail_inner, text="Disponíveis", font=("Segoe UI", 10),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_SECONDARY']).pack()
        
        # Card de Adicionar Livro
        add_card = Frame(self.content_padding, bg=Theme.current['BG_CARDS'], bd=1, relief=FLAT,
                        highlightbackground=Theme.current['BORDER'], highlightthickness=1)
        add_card.pack(fill=X, pady=(0, 24))
        
        add_header = Frame(add_card, bg=Theme.current['BG_CARDS'], height=55)
        add_header.pack(fill=X, padx=24, pady=(16, 0))
        
        Label(add_header, text="📝 ADICIONAR NOVO LIVRO", font=("Segoe UI", 14, "bold"),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['PRIMARY']).pack(side=LEFT)
        Label(add_header, text="Preencha todos os campos", font=("Segoe UI", 10),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_SECONDARY']).pack(side=RIGHT)
        
        Frame(add_card, bg=Theme.current['BORDER'], height=1).pack(fill=X, padx=24, pady=(12, 0))
        
        add_inner = Frame(add_card, bg=Theme.current['BG_CARDS'])
        add_inner.pack(fill=BOTH, padx=24, pady=24)
        
        # Grid de campos (2 colunas)
        fields_grid = Frame(add_inner, bg=Theme.current['BG_CARDS'])
        fields_grid.pack(fill=X)
        
        # Coluna Esquerda
        left_col = Frame(fields_grid, bg=Theme.current['BG_CARDS'])
        left_col.pack(side=LEFT, expand=True, fill=BOTH, padx=(0, 10))
        
        self.book_id = StyledEntry(left_col, "ID do Livro *", "Ex: B1001", "🔖")
        self.book_id.pack(fill=X, pady=(0, 15))
        
        self.book_title = StyledEntry(left_col, "Título *", "Nome completo do livro", "📖")
        self.book_title.pack(fill=X, pady=(0, 15))
        
        self.book_author = StyledEntry(left_col, "Autor *", "Nome do autor", "✍️")
        self.book_author.pack(fill=X, pady=(0, 15))
        
        # Coluna Direita
        right_col = Frame(fields_grid, bg=Theme.current['BG_CARDS'])
        right_col.pack(side=RIGHT, expand=True, fill=BOTH, padx=(10, 0))
        
        self.book_genre = StyledEntry(right_col, "Gênero *", "Ex: Ficção, Tecnologia...", "📚")
        self.book_genre.pack(fill=X, pady=(0, 15))
        
        self.book_copies = StyledEntry(right_col, "Nº de Cópias *", "Quantidade disponível", "📊")
        self.book_copies.pack(fill=X, pady=(0, 15))
        
        self.book_location = StyledEntry(right_col, "Localização *", "Ex: A1, B2", "📍")
        self.book_location.pack(fill=X, pady=(0, 15))
        
        # Botões do formulário
        btn_frame = Frame(add_inner, bg=Theme.current['BG_CARDS'])
        btn_frame.pack(fill=X, pady=(15, 0))
        
        self.add_btn = Button(btn_frame, text="➕ Adicionar Livro", font=("Segoe UI", 11, "bold"),
                              fg="white", bg=Theme.current['PRIMARY'], bd=0, cursor="hand2",
                              padx=25, pady=12, command=self.add_book)
        self.add_btn.pack(side=LEFT, padx=(0, 10))
        
        self.clear_btn = Button(btn_frame, text="🗑️ Limpar Campos", font=("Segoe UI", 11),
                                fg=Theme.current['TEXT_BODY'], bg=Theme.current['INPUT_BG'], bd=1,
                                cursor="hand2", padx=20, pady=12, command=self.clear_book_form)
        self.clear_btn.pack(side=LEFT)
        
        # Card de Catálogo
        catalog_card = Frame(self.content_padding, bg=Theme.current['BG_CARDS'], bd=1, relief=FLAT,
                            highlightbackground=Theme.current['BORDER'], highlightthickness=1)
        catalog_card.pack(fill=BOTH, expand=True)
        
        catalog_header = Frame(catalog_card, bg=Theme.current['BG_CARDS'], height=55)
        catalog_header.pack(fill=X, padx=24, pady=(16, 0))
        
        Label(catalog_header, text="📚 CATÁLOGO DE LIVROS", font=("Segoe UI", 14, "bold"),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_PRIMARY']).pack(side=LEFT)
        
        search_frame = Frame(catalog_header, bg=Theme.current['BG_CARDS'])
        search_frame.pack(side=RIGHT)
        
        self.book_search = StyledEntry(search_frame, "", "Buscar por ID, título, autor ou gênero...", "🔍")
        self.book_search.pack(side=LEFT)
        self.book_search.entry.bind('<KeyRelease>', lambda e: self.search_books())
        
        Button(search_frame, text="Limpar", font=("Segoe UI", 10),
              fg=Theme.current['TEXT_BODY'], bg=Theme.current['INPUT_BG'], bd=1,
              cursor="hand2", padx=15, pady=8, command=self.clear_book_search).pack(side=LEFT, padx=(10, 0))
        
        Frame(catalog_card, bg=Theme.current['BORDER'], height=1).pack(fill=X, padx=24, pady=(12, 0))
        
        self.create_books_table(catalog_card)
        
        # ==================== BOTÕES DE AÇÃO ABAIXO DA TABELA ====================
        table_actions_frame = Frame(catalog_card, bg=Theme.current['BG_CARDS'])
        table_actions_frame.pack(fill=X, padx=24, pady=(15, 24))
        
        # Label informativa
        info_label = Label(table_actions_frame, 
                          text="ℹ️ Selecione um livro na tabela acima para editar ou excluir",
                          font=("Segoe UI", 10), bg=Theme.current['BG_CARDS'], 
                          fg=Theme.current['TEXT_SECONDARY'])
        info_label.pack(side=LEFT, padx=(0, 20))
        
        # Botão Editar Selecionado
        edit_selected_btn = Button(table_actions_frame, text="✏️ Editar Selecionado", 
                                   font=("Segoe UI", 11, "bold"),
                                   fg="white", bg=Theme.current['INFO'], bd=0, cursor="hand2",
                                   padx=25, pady=10, command=self.edit_selected_book)
        edit_selected_btn.pack(side=RIGHT, padx=(0, 10))
        
        # Botão Excluir Selecionado
        delete_selected_btn = Button(table_actions_frame, text="🗑️ Excluir Selecionado", 
                                     font=("Segoe UI", 11, "bold"),
                                     fg="white", bg=Theme.current['DANGER'], bd=0, cursor="hand2",
                                     padx=25, pady=10, command=self.delete_selected_book)
        delete_selected_btn.pack(side=RIGHT)
        
        self.load_all_books()
        self.update_all_stats()
    
    def create_books_table(self, parent):
        table_frame = Frame(parent, bg=Theme.current['BORDER'], bd=1, relief=FLAT)
        table_frame.pack(fill=BOTH, expand=True, padx=24, pady=(0, 24))
        
        inner_table = Frame(table_frame, bg=Theme.current['BG_CARDS'])
        inner_table.pack(fill=BOTH, expand=True, padx=1, pady=1)
        
        scroll_y = ttk.Scrollbar(inner_table, orient="vertical")
        scroll_x = ttk.Scrollbar(inner_table, orient="horizontal")
        
        # Colunas incluindo DISPONÍVEIS
        columns = ("ID", "TÍTULO", "AUTOR", "GÊNERO", "CÓPIAS", "DISPONÍVEIS", "LOCAL", "STATUS")
        self.books_tree = ttk.Treeview(inner_table, columns=columns, show="headings",
                                      yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set,
                                      height=12)
        
        scroll_y.config(command=self.books_tree.yview)
        scroll_x.config(command=self.books_tree.xview)
        
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview", background=Theme.current['BG_CARDS'], 
                       foreground=Theme.current['TEXT_BODY'],
                       rowheight=45, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=Theme.current['INPUT_BG'], 
                       foreground=Theme.current['TEXT_PRIMARY'],
                       font=("Segoe UI", 10, "bold"))
        style.map('Treeview', background=[('selected', Theme.current['PRIMARY_LIGHT'])])
        
        col_widths = {"ID": 80, "TÍTULO": 200, "AUTOR": 160, "GÊNERO": 100, 
                      "CÓPIAS": 80, "DISPONÍVEIS": 100, "LOCAL": 80, "STATUS": 100}
        for col in columns:
            self.books_tree.heading(col, text=col)
            self.books_tree.column(col, width=col_widths.get(col, 120), anchor="center")
        
        self.books_tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        
        inner_table.grid_rowconfigure(0, weight=1)
        inner_table.grid_columnconfigure(0, weight=1)
        
        self.books_tree.bind("<Button-3>", self.show_book_context_menu)
        self.books_tree.bind("<Double-1>", lambda e: self.quick_issue_from_book())
    
    def update_books_summary(self):
        conn = sqlite3.connect('test.db')
        cursor = conn.execute("SELECT COUNT(*) FROM book_info")
        total_books = cursor.fetchone()[0]
        conn.close()
        self.books_summary_label.config(text=f"📊 {total_books} livro(s) no catálogo")
    
    def update_all_stats(self):
        conn = sqlite3.connect('test.db')
        cursor = conn.execute("SELECT COUNT(*) FROM book_info")
        total_books = cursor.fetchone()[0]
        cursor = conn.execute("SELECT SUM(COPIES) FROM book_info")
        total_copies = cursor.fetchone()[0] or 0
        cursor = conn.execute("SELECT COUNT(*) FROM book_issued")
        loaned_books = cursor.fetchone()[0]
        conn.close()
        available_copies = total_copies - loaned_books
        self.total_books_label.config(text=str(total_books))
        self.total_copies_label.config(text=str(total_copies))
        self.loaned_books_label.config(text=str(loaned_books))
        self.avail_books_label.config(text=str(available_copies))
        self.update_books_summary()
    
    def load_all_books(self):
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
        
        conn = sqlite3.connect('test.db')
        
        # Contar quantas cópias de cada livro estão emprestadas
        cursor = conn.execute("""
            SELECT BOOK_ID, COUNT(*) as loaned_count 
            FROM book_issued 
            GROUP BY BOOK_ID
        """)
        loaned_counts = {}
        for row in cursor.fetchall():
            loaned_counts[row[0]] = row[1]
        
        cursor = conn.execute("SELECT ID, TITLE, AUTHOR, GENRE, COPIES, LOCATION FROM book_info ORDER BY TITLE")
        
        for row in cursor.fetchall():
            book_id, title, author, genre, copies, location = row
            
            # Calcular cópias disponíveis
            loaned = loaned_counts.get(book_id, 0)
            available = copies - loaned
            
            # Determinar status
            if available <= 0:
                status = "❌ Indisponível"
            elif loaned > 0:
                status = "📤 Parcial"
            else:
                status = "✅ Disponível"
            
            self.books_tree.insert("", END, values=(book_id, title, author, genre, copies, available, location, status))
        
        conn.close()
        self.update_all_stats()
    
    def search_books(self):
        term = self.book_search.get()
        if not term:
            self.load_all_books()
            return
        
        for item in self.books_tree.get_children():
            self.books_tree.delete(item)
        
        conn = sqlite3.connect('test.db')
        
        # Contar quantas cópias de cada livro estão emprestadas
        cursor = conn.execute("""
            SELECT BOOK_ID, COUNT(*) as loaned_count 
            FROM book_issued 
            GROUP BY BOOK_ID
        """)
        loaned_counts = {}
        for row in cursor.fetchall():
            loaned_counts[row[0]] = row[1]
        
        cursor = conn.execute("""SELECT ID, TITLE, AUTHOR, GENRE, COPIES, LOCATION 
                               FROM book_info 
                               WHERE ID LIKE ? OR TITLE LIKE ? OR AUTHOR LIKE ? OR GENRE LIKE ?
                               ORDER BY TITLE""",
                             (f'%{term.upper()}%', f'%{term.capitalize()}%', 
                              f'%{term.capitalize()}%', f'%{term.capitalize()}%'))
        
        for row in cursor.fetchall():
            book_id, title, author, genre, copies, location = row
            
            # Calcular cópias disponíveis
            loaned = loaned_counts.get(book_id, 0)
            available = copies - loaned
            
            # Determinar status
            if available <= 0:
                status = "❌ Indisponível"
            elif loaned > 0:
                status = "📤 Parcial"
            else:
                status = "✅ Disponível"
            
            self.books_tree.insert("", END, values=(book_id, title, author, genre, copies, available, location, status))
        
        conn.close()
    
    def quick_issue_from_book(self):
        selected = self.books_tree.selection()
        if selected:
            book_id = self.books_tree.item(selected[0])['values'][0]
            self.show_loans_view()
            self.root.after(500, lambda: self.set_loan_book_id(book_id))
    
    def set_loan_book_id(self, book_id):
        if hasattr(self, 'loan_book_field'):
            self.loan_book_field.set(book_id)
            self.check_book_availability_loan()
            Toast.show(self.root, f"Livro {book_id} pronto para empréstimo", 'info')
    
    def show_book_context_menu(self, event):
        item = self.books_tree.identify_row(event.y)
        if item:
            self.books_tree.selection_set(item)
            menu = Menu(self.root, tearoff=0, bg=Theme.current['BG_CARDS'], 
                       fg=Theme.current['TEXT_BODY'])
            menu.add_command(label="➕ Adicionar Cópias", command=self.add_copies)
            menu.add_command(label="➖ Remover Cópias", command=self.remove_copies)
            menu.add_separator()
            menu.add_command(label="📤 Emprestar Agora", command=self.quick_issue)
            menu.add_separator()
            menu.add_command(label="✏️ Editar Livro", command=self.edit_selected_book)
            menu.add_separator()
            menu.add_command(label="🗑️ Excluir Livro", command=self.delete_selected_book, 
                           foreground=Theme.current['DANGER'])
            menu.post(event.x_root, event.y_root)
    
    def quick_issue(self):
        selected = self.books_tree.selection()
        if selected:
            book_id = self.books_tree.item(selected[0])['values'][0]
            self.show_loans_view()
            self.root.after(500, lambda: self.set_loan_book_id(book_id))
    
    def edit_selected_book(self):
        """Edita o livro selecionado na tabela"""
        selected = self.books_tree.selection()
        if not selected:
            Toast.show(self.root, "Selecione um livro para editar!", 'warning')
            return
        
        values = self.books_tree.item(selected[0])['values']
        
        # Preencher o formulário com os dados do livro selecionado
        self.book_id.set(values[0])
        self.book_title.set(values[1])
        self.book_author.set(values[2])
        self.book_genre.set(values[3])
        self.book_copies.set(str(values[4]))
        self.book_location.set(values[6])  # LOCAL está na posição 6
        
        # Desabilitar o campo ID (não pode ser editado)
        self.book_id.entry.config(state='readonly')
        self.book_id.entry.config(bg=Theme.current['INPUT_BG'], 
                                   fg=Theme.current['TEXT_SECONDARY'])
        
        # Mudar o botão de Adicionar para Atualizar
        self.add_btn.config(text="✏️ Atualizar Livro", bg=Theme.current['INFO'], 
                           command=self.update_book)
        self.clear_btn.config(text="🗑️ Cancelar Edição", command=self.cancel_edit)
        
        # Scroll para o topo para ver o formulário
        self.content_canvas.yview_moveto(0)
        Toast.show(self.root, f"Editando livro: {values[1]}", 'info')
    
    def cancel_edit(self):
        """Cancela a edição e restaura o formulário"""
        # Limpar todos os campos
        self.book_id.clear()
        self.book_title.clear()
        self.book_author.clear()
        self.book_genre.clear()
        self.book_copies.clear()
        self.book_location.clear()
        
        # Habilitar o campo ID novamente
        self.book_id.entry.config(state='normal')
        
        # Restaurar botões
        self.add_btn.config(text="➕ Adicionar Livro", bg=Theme.current['PRIMARY'], 
                           command=self.add_book)
        self.clear_btn.config(text="🗑️ Limpar Campos", command=self.clear_book_form)
        
        Toast.show(self.root, "Edição cancelada!", 'info')
    
    def update_book(self):
        """Atualiza o livro existente (sem alterar o ID)"""
        book_id = self.book_id.get()
        
        # Verificar se os campos obrigatórios estão preenchidos
        if not all([self.book_title.get(), self.book_author.get(),
                   self.book_genre.get(), self.book_location.get()]):
            Toast.show(self.root, "Preencha todos os campos!", 'warning')
            return
        
        # Verificar se o número de cópias é válido
        try:
            copies = int(self.book_copies.get()) if self.book_copies.get() else 1
            if copies < 0:
                Toast.show(self.root, "Número de cópias não pode ser negativo!", 'warning')
                return
        except ValueError:
            Toast.show(self.root, "Número de cópias inválido!", 'warning')
            return
        
        loading = LoadingOverlay(self.root)
        loading.show("Atualizando livro...")
        self.root.after(100, lambda: self.process_update_book(book_id, copies, loading))
    
    def process_update_book(self, book_id, copies, loading):
        """Processa a atualização do livro no banco de dados"""
        conn = sqlite3.connect('test.db')
        try:
            # ATUALIZAR sem modificar o ID (que é a chave primária)
            conn.execute("""UPDATE book_info 
                           SET TITLE=?, AUTHOR=?, GENRE=?, COPIES=?, LOCATION=?
                           WHERE ID=?""",
                        (self.book_title.get().capitalize(),
                         self.book_author.get().capitalize(),
                         self.book_genre.get().capitalize(),
                         copies,
                         self.book_location.get().upper(),
                         book_id))
            conn.commit()
            
            loading.hide()
            Toast.show(self.root, "Livro atualizado com sucesso!", 'success')
            
            # Limpar e restaurar o formulário
            self.cancel_edit()
            
            # Recarregar a tabela e estatísticas
            self.load_all_books()
            self.update_all_stats()
            
        except Exception as e:
            loading.hide()
            Toast.show(self.root, f"Erro ao atualizar: {str(e)}", 'error')
        finally:
            conn.close()
    
    def clear_book_form(self):
        self.book_id.clear()
        self.book_title.clear()
        self.book_author.clear()
        self.book_genre.clear()
        self.book_copies.clear()
        self.book_location.clear()
        if hasattr(self, 'book_id') and self.book_id.entry.cget('state') == 'readonly':
            self.book_id.entry.config(state='normal')
        Toast.show(self.root, "Formulário limpo!", 'info')
    
    def clear_book_search(self):
        self.book_search.clear()
        self.load_all_books()
    
    def add_book(self):
        if not all([self.book_id.get(), self.book_title.get(), self.book_author.get(),
                   self.book_genre.get(), self.book_location.get()]):
            Toast.show(self.root, "Preencha todos os campos obrigatórios (*)!", 'warning')
            return
        
        loading = LoadingOverlay(self.root)
        loading.show("Adicionando livro...")
        self.root.after(100, lambda: self.process_add_book(loading))
    
    def process_add_book(self, loading):
        conn = sqlite3.connect('test.db')
        try:
            copies = int(self.book_copies.get()) if self.book_copies.get() else 1
            conn.execute("INSERT INTO book_info VALUES (?,?,?,?,?,?)",
                        (self.book_id.get().upper(), self.book_title.get().capitalize(),
                         self.book_author.get().capitalize(), self.book_genre.get().capitalize(),
                         copies, self.book_location.get().upper()))
            conn.commit()
            loading.hide()
            Toast.show(self.root, "Livro adicionado com sucesso!", 'success')
            self.clear_book_form()
            self.load_all_books()
            self.update_all_stats()
        except sqlite3.IntegrityError:
            loading.hide()
            Toast.show(self.root, f"ID {self.book_id.get()} já existe!", 'error')
        except ValueError:
            loading.hide()
            Toast.show(self.root, "Número de cópias inválido!", 'error')
        finally:
            conn.close()
    
    def add_copies(self):
        selected = self.books_tree.selection()
        if not selected:
            Toast.show(self.root, "Selecione um livro!", 'warning')
            return
        
        values = self.books_tree.item(selected[0])['values']
        book_id = values[0]
        current = values[4]
        
        dialog = Toplevel(self.root)
        dialog.title("Adicionar Cópias")
        dialog.geometry("400x300")
        dialog.configure(bg=Theme.current['BG_CARDS'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"400x300+{x}+{y}")
        
        Label(dialog, text=f"📖 {book_id}", font=("Segoe UI", 14, "bold"),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['PRIMARY']).pack(pady=20)
        Label(dialog, text=f"Cópias atuais: {current}", font=("Segoe UI", 11),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_BODY']).pack()
        
        copies_field = StyledEntry(dialog, "Número de cópias", "Quantidade a adicionar", "➕")
        copies_field.pack(fill=X, padx=40, pady=20)
        
        def confirm():
            if copies_field.get():
                try:
                    copies = int(copies_field.get())
                    if copies > 0:
                        conn = sqlite3.connect('test.db')
                        conn.execute("UPDATE book_info SET COPIES = COPIES + ? WHERE ID = ?", 
                                   (copies, book_id))
                        conn.commit()
                        conn.close()
                        Toast.show(dialog, f"{copies} cópia(s) adicionada(s)!", 'success')
                        dialog.destroy()
                        self.load_all_books()
                    else:
                        Toast.show(dialog, "Número inválido!", 'error')
                except ValueError:
                    Toast.show(dialog, "Digite um número válido!", 'error')
        
        btn_frame = Frame(dialog, bg=Theme.current['BG_CARDS'])
        btn_frame.pack(pady=20)
        Button(btn_frame, text="Confirmar", font=("Segoe UI", 11, "bold"),
              fg="white", bg=Theme.current['PRIMARY'], bd=0, cursor="hand2",
              padx=20, pady=8, command=confirm).pack(side=LEFT, padx=10)
        Button(btn_frame, text="Cancelar", font=("Segoe UI", 11),
              fg=Theme.current['TEXT_BODY'], bg=Theme.current['INPUT_BG'], bd=0,
              cursor="hand2", padx=20, pady=8, command=dialog.destroy).pack(side=LEFT)
    
    def remove_copies(self):
        selected = self.books_tree.selection()
        if not selected:
            Toast.show(self.root, "Selecione um livro!", 'warning')
            return
        
        values = self.books_tree.item(selected[0])['values']
        book_id = values[0]
        current = int(values[4])
        
        if current <= 0:
            Toast.show(self.root, "Não há cópias para remover!", 'error')
            return
        
        dialog = Toplevel(self.root)
        dialog.title("Remover Cópias")
        dialog.geometry("400x300")
        dialog.configure(bg=Theme.current['BG_CARDS'])
        dialog.transient(self.root)
        dialog.grab_set()
        
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (400 // 2)
        y = (dialog.winfo_screenheight() // 2) - (300 // 2)
        dialog.geometry(f"400x300+{x}+{y}")
        
        Label(dialog, text=f"📖 {book_id}", font=("Segoe UI", 14, "bold"),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['WARNING']).pack(pady=20)
        Label(dialog, text=f"Cópias disponíveis: {current}", font=("Segoe UI", 11),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_BODY']).pack()
        
        copies_field = StyledEntry(dialog, "Número de cópias a remover", "Quantidade a remover", "➖")
        copies_field.pack(fill=X, padx=40, pady=20)
        
        def confirm():
            if copies_field.get():
                try:
                    copies = int(copies_field.get())
                    if 0 < copies <= current:
                        conn = sqlite3.connect('test.db')
                        conn.execute("UPDATE book_info SET COPIES = COPIES - ? WHERE ID = ?", 
                                   (copies, book_id))
                        conn.commit()
                        conn.close()
                        Toast.show(dialog, f"{copies} cópia(s) removida(s)!", 'success')
                        dialog.destroy()
                        self.load_all_books()
                    else:
                        Toast.show(dialog, f"Número inválido! (1-{current})", 'error')
                except ValueError:
                    Toast.show(dialog, "Digite um número válido!", 'error')
        
        btn_frame = Frame(dialog, bg=Theme.current['BG_CARDS'])
        btn_frame.pack(pady=20)
        Button(btn_frame, text="Confirmar", font=("Segoe UI", 11, "bold"),
              fg="white", bg=Theme.current['WARNING'], bd=0, cursor="hand2",
              padx=20, pady=8, command=confirm).pack(side=LEFT, padx=10)
        Button(btn_frame, text="Cancelar", font=("Segoe UI", 11),
              fg=Theme.current['TEXT_BODY'], bg=Theme.current['INPUT_BG'], bd=0,
              cursor="hand2", padx=20, pady=8, command=dialog.destroy).pack(side=LEFT)
    
    def delete_selected_book(self):
        """Exclui o livro selecionado na tabela"""
        selected = self.books_tree.selection()
        if not selected:
            Toast.show(self.root, "Selecione um livro para excluir!", 'warning')
            return
        
        values = self.books_tree.item(selected[0])['values']
        book_id = values[0]
        title = values[1]
        
        conn = sqlite3.connect('test.db')
        cursor = conn.execute("SELECT * FROM book_issued WHERE BOOK_ID = ?", (book_id,))
        if cursor.fetchone():
            Toast.show(self.root, f"Livro '{title}' está emprestado e não pode ser excluído!", 'error')
            conn.close()
            return
        conn.close()
        
        if messagebox.askyesno("Confirmar Exclusão", f"Tem certeza que deseja excluir o livro\n'{title}' (ID: {book_id})?"):
            loading = LoadingOverlay(self.root)
            loading.show("Excluindo livro...")
            self.root.after(100, lambda: self.process_delete_book(book_id, loading))
    
    def process_delete_book(self, book_id, loading):
        conn = sqlite3.connect('test.db')
        conn.execute("DELETE FROM book_info WHERE ID = ?", (book_id,))
        conn.commit()
        conn.close()
        loading.hide()
        Toast.show(self.root, "Livro excluído com sucesso!", 'success')
        self.load_all_books()
    
    # ==================== VISUAL DE EMPRÉSTIMOS ====================
    def show_loans_view(self):
        self.current_view = 'loans'
        
        for btn in self.sidebar_buttons:
            btn.set_active(False)
        self.sidebar_buttons[1].set_active(True)
        
        for widget in self.content_padding.winfo_children():
            widget.destroy()
        
        title_frame = Frame(self.content_padding, bg=Theme.current['BG_GLOBAL'])
        title_frame.pack(fill=X, pady=(0, 24))
        
        Label(title_frame, text="Gerenciamento de Empréstimos", font=("Segoe UI", 24, "bold"),
              bg=Theme.current['BG_GLOBAL'], fg=Theme.current['TEXT_PRIMARY']).pack(side=LEFT)
        
        summary_frame = Frame(title_frame, bg=Theme.current['BG_GLOBAL'])
        summary_frame.pack(side=RIGHT)
        
        self.summary_label = Label(summary_frame, text="", font=("Segoe UI", 11),
                                   bg=Theme.current['BG_GLOBAL'], fg=Theme.current['TEXT_SECONDARY'])
        self.summary_label.pack()
        self.update_loan_summary()
        
        cards_container = Frame(self.content_padding, bg=Theme.current['BG_GLOBAL'])
        cards_container.pack(fill=BOTH, expand=True)
        
        top_cards = Frame(cards_container, bg=Theme.current['BG_GLOBAL'])
        top_cards.pack(fill=X, pady=(0, 24))
        
        # Card de Empréstimo
        loan_card = Frame(top_cards, bg=Theme.current['BG_CARDS'], bd=1, relief=FLAT,
                         highlightbackground=Theme.current['BORDER'], highlightthickness=1)
        loan_card.pack(side=LEFT, expand=True, fill=BOTH, padx=(0, 16))
        
        loan_header = Frame(loan_card, bg=Theme.current['BG_CARDS'], height=55)
        loan_header.pack(fill=X, padx=24, pady=(16, 0))
        
        Label(loan_header, text="📤 EMPRESTAR LIVRO", font=("Segoe UI", 14, "bold"),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['PRIMARY']).pack(side=LEFT)
        Label(loan_header, text="Prazo: 7 dias", font=("Segoe UI", 10),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_SECONDARY']).pack(side=RIGHT)
        
        Frame(loan_card, bg=Theme.current['BORDER'], height=1).pack(fill=X, padx=24, pady=(12, 0))
        
        loan_inner = Frame(loan_card, bg=Theme.current['BG_CARDS'])
        loan_inner.pack(fill=BOTH, expand=True, padx=24, pady=24)
        
        self.loan_book_field = StyledEntry(loan_inner, "ID do Livro", "Digite o ID do livro", "📖")
        self.loan_book_field.pack(fill=X, pady=(0, 16))
        self.loan_book_field.entry.bind('<KeyRelease>', lambda e: self.check_book_availability_loan())
        
        self.availability_frame = Frame(loan_inner, bg=Theme.current['BG_CARDS'])
        self.availability_frame.pack(fill=X, pady=(0, 16))
        self.availability_icon = Label(self.availability_frame, text="", font=("Segoe UI", 12),
                                       bg=Theme.current['BG_CARDS'])
        self.availability_icon.pack(side=LEFT, padx=(0, 8))
        self.availability_text = Label(self.availability_frame, text="", font=("Segoe UI", 10),
                                       bg=Theme.current['BG_CARDS'])
        self.availability_text.pack(side=LEFT)
        
        self.loan_student_field = StyledEntry(loan_inner, "ID do Estudante", "Digite o ID do estudante", "👤")
        self.loan_student_field.pack(fill=X, pady=(0, 24))
        
        loan_btn = Button(loan_inner, text="Confirmar Empréstimo", font=("Segoe UI", 12, "bold"),
                         fg="white", bg=Theme.current['PRIMARY'], bd=0, cursor="hand2",
                         padx=20, pady=14, command=self.make_loan)
        loan_btn.pack(fill=X)
        
        # Card de Devolução
        return_card = Frame(top_cards, bg=Theme.current['BG_CARDS'], bd=1, relief=FLAT,
                           highlightbackground=Theme.current['BORDER'], highlightthickness=1)
        return_card.pack(side=RIGHT, expand=True, fill=BOTH, padx=(16, 0))
        
        return_header = Frame(return_card, bg=Theme.current['BG_CARDS'], height=55)
        return_header.pack(fill=X, padx=24, pady=(16, 0))
        
        Label(return_header, text="📥 DEVOLVER LIVRO", font=("Segoe UI", 14, "bold"),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['PRIMARY']).pack(side=LEFT)
        Label(return_header, text="Multa: R$ 2,00/dia", font=("Segoe UI", 10),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['WARNING']).pack(side=RIGHT)
        
        Frame(return_card, bg=Theme.current['BORDER'], height=1).pack(fill=X, padx=24, pady=(12, 0))
        
        return_inner = Frame(return_card, bg=Theme.current['BG_CARDS'])
        return_inner.pack(fill=BOTH, expand=True, padx=24, pady=24)
        
        self.return_book_field = StyledEntry(return_inner, "ID do Livro", "Digite o ID do livro", "📖")
        self.return_book_field.pack(fill=X, pady=(0, 16))
        self.return_book_field.entry.bind('<KeyRelease>', lambda e: self.check_loan_exists())
        
        self.loan_info_frame = Frame(return_inner, bg=Theme.current['BG_CARDS'])
        self.loan_info_frame.pack(fill=X, pady=(0, 16))
        self.loan_info_label = Label(self.loan_info_frame, text="", font=("Segoe UI", 10),
                                     bg=Theme.current['BG_CARDS'])
        self.loan_info_label.pack()
        
        self.return_student_field = StyledEntry(return_inner, "ID do Estudante", "Digite o ID do estudante", "👤")
        self.return_student_field.pack(fill=X, pady=(0, 24))
        
        return_btn = Button(return_inner, text="Confirmar Devolução", font=("Segoe UI", 12, "bold"),
                           fg="white", bg=Theme.current['PRIMARY'], bd=0, cursor="hand2",
                           padx=20, pady=14, command=self.make_return)
        return_btn.pack(fill=X)
        
        # Tabela de Atividades
        activity_card = Frame(cards_container, bg=Theme.current['BG_CARDS'], bd=1, relief=FLAT,
                             highlightbackground=Theme.current['BORDER'], highlightthickness=1)
        activity_card.pack(fill=BOTH, expand=True)
        
        activity_header = Frame(activity_card, bg=Theme.current['BG_CARDS'], height=55)
        activity_header.pack(fill=X, padx=24, pady=(16, 0))
        
        Label(activity_header, text="📊 HISTÓRICO DE EMPRÉSTIMOS", font=("Segoe UI", 14, "bold"),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_PRIMARY']).pack(side=LEFT)
        
        self.active_loans_label = Label(activity_header, text="", font=("Segoe UI", 10, "bold"),
                                        bg=Theme.current['BG_CARDS'], fg=Theme.current['INFO'])
        self.active_loans_label.pack(side=RIGHT)
        
        Frame(activity_card, bg=Theme.current['BORDER'], height=1).pack(fill=X, padx=24, pady=(12, 0))
        
        search_container = Frame(activity_card, bg=Theme.current['BG_CARDS'])
        search_container.pack(fill=X, padx=24, pady=(16, 12))
        
        Label(search_container, text="Buscar:", font=("Segoe UI", 10, "bold"),
              bg=Theme.current['BG_CARDS'], fg=Theme.current['TEXT_SECONDARY']).pack(side=LEFT, padx=(0, 8))
        
        self.activity_search = StyledEntry(search_container, "", "ID do livro ou estudante", "🔍")
        self.activity_search.pack(side=LEFT, expand=True, fill=X, padx=(0, 10))
        self.activity_search.entry.bind('<KeyRelease>', lambda e: self.search_activity())
        
        Button(search_container, text="Limpar", font=("Segoe UI", 10),
              fg=Theme.current['TEXT_BODY'], bg=Theme.current['INPUT_BG'], bd=1,
              cursor="hand2", padx=15, pady=8, command=self.clear_activity_search).pack(side=LEFT)
        
        self.create_activity_table(activity_card)
        self.load_all_activity()
    
    def update_loan_summary(self):
        conn = sqlite3.connect('test.db')
        cursor = conn.execute("SELECT COUNT(*) FROM book_issued")
        active_loans = cursor.fetchone()[0]
        conn.close()
        self.summary_label.config(text=f"📊 {active_loans} empréstimo(s) ativo(s)")
    
    def check_book_availability_loan(self):
        book_id = self.loan_book_field.get()
        if not book_id:
            self.availability_icon.config(text="")
            self.availability_text.config(text="")
            return
        
        conn = sqlite3.connect('test.db')
        cursor = conn.execute("SELECT COPIES, TITLE FROM book_info WHERE ID=?", (book_id.upper(),))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            copies, title = result
            if copies > 0:
                self.availability_icon.config(text="✅", fg=Theme.current['SUCCESS'])
                self.availability_text.config(text=f"Disponível! {copies} cópia(s) de '{title}'",
                                             fg=Theme.current['SUCCESS'])
            else:
                self.availability_icon.config(text="❌", fg=Theme.current['DANGER'])
                self.availability_text.config(text=f"Indisponível - '{title}' sem cópias",
                                             fg=Theme.current['DANGER'])
        else:
            self.availability_icon.config(text="⚠️", fg=Theme.current['WARNING'])
            self.availability_text.config(text="Livro não encontrado no catálogo",
                                         fg=Theme.current['WARNING'])
    
    def check_loan_exists(self):
        book_id = self.return_book_field.get()
        if not book_id:
            self.loan_info_label.config(text="")
            return
        
        conn = sqlite3.connect('test.db')
        cursor = conn.execute("SELECT STUDENT_ID, ISSUE_DATE, RETURN_DATE FROM book_issued WHERE BOOK_ID=?", 
                             (book_id.upper(),))
        result = cursor.fetchone()
        conn.close()
        
        if result:
            student_id, issue_date, return_date = result
            self.loan_info_label.config(
                text=f"📌 Emprestado para {student_id} em {issue_date} | Devolução: {return_date}",
                fg=Theme.current['INFO']
            )
        else:
            self.loan_info_label.config(text="", fg=Theme.current['TEXT_SECONDARY'])
    
    def create_activity_table(self, parent):
        table_frame = Frame(parent, bg=Theme.current['BORDER'], bd=1, relief=FLAT)
        table_frame.pack(fill=BOTH, expand=True, padx=24, pady=(0, 24))
        
        inner_table = Frame(table_frame, bg=Theme.current['BG_CARDS'])
        inner_table.pack(fill=BOTH, expand=True, padx=1, pady=1)
        
        scroll_y = ttk.Scrollbar(inner_table, orient="vertical")
        scroll_x = ttk.Scrollbar(inner_table, orient="horizontal")
        
        columns = ("ID LIVRO", "TÍTULO", "ID ESTUDANTE", "DATA EMPRÉSTIMO", "DATA DEVOLUÇÃO", "STATUS")
        self.activity_tree = ttk.Treeview(inner_table, columns=columns, show="headings",
                                          yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set,
                                          height=12)
        
        scroll_y.config(command=self.activity_tree.yview)
        scroll_x.config(command=self.activity_tree.xview)
        
        style = ttk.Style()
        style.configure("Treeview", background=Theme.current['BG_CARDS'], 
                       foreground=Theme.current['TEXT_BODY'],
                       rowheight=45, font=("Segoe UI", 10))
        style.configure("Treeview.Heading", background=Theme.current['INPUT_BG'], 
                       foreground=Theme.current['TEXT_PRIMARY'],
                       font=("Segoe UI", 10, "bold"))
        
        col_widths = {"ID LIVRO": 100, "TÍTULO": 200, "ID ESTUDANTE": 120, 
                      "DATA EMPRÉSTIMO": 130, "DATA DEVOLUÇÃO": 130, "STATUS": 100}
        for col in columns:
            self.activity_tree.heading(col, text=col)
            self.activity_tree.column(col, width=col_widths.get(col, 120), anchor="center")
        
        self.activity_tree.grid(row=0, column=0, sticky="nsew")
        scroll_y.grid(row=0, column=1, sticky="ns")
        scroll_x.grid(row=1, column=0, sticky="ew")
        
        inner_table.grid_rowconfigure(0, weight=1)
        inner_table.grid_columnconfigure(0, weight=1)
    
    def load_all_activity(self):
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        
        conn = sqlite3.connect('test.db')
        cursor = conn.execute("""
            SELECT bi.BOOK_ID, b.TITLE, bi.STUDENT_ID, bi.ISSUE_DATE, bi.RETURN_DATE 
            FROM book_issued bi
            LEFT JOIN book_info b ON bi.BOOK_ID = b.ID
            ORDER BY bi.ISSUE_DATE DESC
        """)
        
        today = datetime.now().strftime("%Y-%m-%d")
        active_count = 0
        
        for row in cursor.fetchall():
            book_id, title, student_id, issue_date, return_date = row
            book_title = title if title else book_id
            if return_date < today:
                status = "⚠️ Atrasado"
            else:
                status = "✅ No Prazo"
                active_count += 1
            self.activity_tree.insert("", END, values=(book_id, book_title, student_id, issue_date, return_date, status))
        
        conn.close()
        self.active_loans_label.config(text=f"🎯 {active_count} empréstimo(s) no prazo")
        self.update_loan_summary()
    
    def search_activity(self):
        term = self.activity_search.get()
        if not term:
            self.load_all_activity()
            return
        
        for item in self.activity_tree.get_children():
            self.activity_tree.delete(item)
        
        conn = sqlite3.connect('test.db')
        cursor = conn.execute("""
            SELECT bi.BOOK_ID, b.TITLE, bi.STUDENT_ID, bi.ISSUE_DATE, bi.RETURN_DATE 
            FROM book_issued bi
            LEFT JOIN book_info b ON bi.BOOK_ID = b.ID
            WHERE bi.BOOK_ID LIKE ? OR bi.STUDENT_ID LIKE ? OR b.TITLE LIKE ?
            ORDER BY bi.ISSUE_DATE DESC
        """, (f'%{term.upper()}%', f'%{term.upper()}%', f'%{term.capitalize()}%'))
        
        today = datetime.now().strftime("%Y-%m-%d")
        
        for row in cursor.fetchall():
            book_id, title, student_id, issue_date, return_date = row
            book_title = title if title else book_id
            if return_date < today:
                status = "⚠️ Atrasado"
            else:
                status = "✅ No Prazo"
            self.activity_tree.insert("", END, values=(book_id, book_title, student_id, issue_date, return_date, status))
        
        conn.close()
    
    def clear_activity_search(self):
        self.activity_search.clear()
        self.load_all_activity()
    
    def make_loan(self):
        book_id = self.loan_book_field.get()
        student_id = self.loan_student_field.get()
        if not book_id or not student_id:
            Toast.show(self.root, "Preencha todos os campos!", 'warning')
            return
        
        loading = LoadingOverlay(self.root)
        loading.show("Processando empréstimo...")
        self.root.after(100, lambda: self.process_loan(book_id.upper(), student_id.upper(), loading))
    
    def process_loan(self, book_id, student_id, loading):
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        cursor.execute("SELECT COPIES, TITLE FROM book_info WHERE ID=?", (book_id,))
        result = cursor.fetchone()
        
        if not result:
            loading.hide()
            Toast.show(self.root, f"Livro {book_id} não encontrado!", 'error')
        elif result[0] <= 0:
            loading.hide()
            Toast.show(self.root, f"'{result[1]}' - Sem cópias disponíveis!", 'error')
        else:
            try:
                conn.execute("INSERT INTO book_issued VALUES (?,?,date('now'),date('now','+7 day'))",
                           (book_id, student_id))
                conn.execute("UPDATE book_info SET COPIES = COPIES - 1 WHERE ID=?", (book_id,))
                conn.commit()
                loading.hide()
                Toast.show(self.root, f"Livro emprestado para {student_id}!", 'success')
                self.loan_book_field.clear()
                self.loan_student_field.clear()
                self.availability_icon.config(text="")
                self.availability_text.config(text="")
                self.load_all_activity()
                self.load_all_books()
            except sqlite3.IntegrityError:
                loading.hide()
                Toast.show(self.root, "Livro já emprestado para este estudante!", 'error')
        conn.close()
    
    def make_return(self):
        book_id = self.return_book_field.get()
        student_id = self.return_student_field.get()
        if not book_id or not student_id:
            Toast.show(self.root, "Preencha todos os campos!", 'warning')
            return
        
        loading = LoadingOverlay(self.root)
        loading.show("Processando devolução...")
        self.root.after(100, lambda: self.process_return(book_id.upper(), student_id.upper(), loading))
    
    def process_return(self, book_id, student_id, loading):
        conn = sqlite3.connect('test.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM book_issued WHERE BOOK_ID=? AND STUDENT_ID=?", 
                      (book_id, student_id))
        
        if cursor.fetchone():
            cursor.execute("SELECT RETURN_DATE FROM book_issued WHERE BOOK_ID=? AND STUDENT_ID=?", 
                          (book_id, student_id))
            return_date = cursor.fetchone()[0]
            today = datetime.now().strftime("%Y-%m-%d")
            fine = 0
            if return_date < today:
                days_late = (datetime.now() - datetime.strptime(return_date, "%Y-%m-%d")).days
                fine = days_late * 2
                if fine > 0:
                    Toast.show(self.root, f"Multa por atraso: R$ {fine:.2f}", 'warning', 4000)
            
            conn.execute("DELETE FROM book_issued WHERE BOOK_ID=? AND STUDENT_ID=?", 
                        (book_id, student_id))
            conn.execute("UPDATE book_info SET COPIES = COPIES + 1 WHERE ID=?", (book_id,))
            conn.commit()
            loading.hide()
            Toast.show(self.root, "Livro devolvido com sucesso!", 'success')
            self.return_book_field.clear()
            self.return_student_field.clear()
            self.loan_info_label.config(text="")
            self.load_all_activity()
            self.load_all_books()
        else:
            loading.hide()
            Toast.show(self.root, "Registro não encontrado!", 'error')
        conn.close()

# ==================== INÍCIO ====================
if __name__ == "__main__":
    app = UnifiedLibrarySystem()