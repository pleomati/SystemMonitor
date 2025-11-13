import re
import psutil
import time
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import os
import datetime
import subprocess
from pathlib import Path
import shutil
from network import NetworkMonitor
from systeminfo import SystemInfoTab
from benchmark import BenchmarkTab
import stat

class ModernSystemMonitorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Modern System Monitor")
        self.root.geometry("1200x900")
        self.root.configure(bg='#2b2b2b')
        
        # Styl nowoczesny - ciemny motyw
        self.setup_styles()
        
        # Zmienne do przechowywania danych
        self.cpu_percent_per_core = []
        self.total_usage = 0
        self.thread_info = []
        self.cpu_freq = 0
        self.ram_usage = 0
        self.ram_total = 0
        self.ram_percent = 0
        self.swap_usage = 0
        self.swap_total = 0
        self.swap_percent = 0
        self.disk_usage = []
        self.disk_io = {}
        self.current_path = Path.home()
        self.process_sort_column = 'cpu'
        self.process_sort_reverse = True
        self.temperature_data = {}
        
        # Zmienne dla operacji na plikach
        self.clipboard = None
        self.clipboard_operation = None  # 'copy' lub 'cut'
        
        # Zmienne dla automatycznego odświeżania temperatury
        self.auto_refresh_temp = False
        self.temp_refresh_id = None
        
        # Zmienne dla automatycznego odświeżania procesów
        self.auto_refresh_processes = False
        self.process_refresh_id = None
        
        # Konfiguracja matplotlib dla ciemnego motywu
        plt.style.use('dark_background')
        
        # Tworzenie zakładek
        self.create_notebook()
        
        # Rozpocznij aktualizację danych
        self.update_data()
        
    def setup_styles(self):
        """Konfiguruje nowoczesne style dla aplikacji"""
        style = ttk.Style()
        
        # Konfiguracja motywu
        style.theme_use('clam')
        
        # Kolorystyka
        self.colors = {
            'bg': '#2b2b2b',
            'bg_light': '#3c3c3c',
            'bg_lighter': '#4a4a4a',
            'accent': '#007acc',
            'accent_hover': '#005a9e',
            'text': '#ffffff',
            'text_secondary': '#cccccc',
            'success': '#4caf50',
            'warning': '#ff9800',
            'danger': '#f44336',
            'cpu': '#ff6b6b',
            'ram': '#4ecdc4',
            'disk': '#45b7d1',
            'swap': '#96ceb4',
            'process_running': '#4caf50',
            'process_sleeping': '#2196f3',
            'process_stopped': '#ff9800',
            'process_zombie': '#f44336',
            'temp_cool': '#4caf50',
            'temp_warm': '#ff9800',
            'temp_hot': '#f44336',
            'temp_critical': '#d32f2f'
        }
        
        # Konfiguracja stylów
        style.configure('Modern.TFrame', background=self.colors['bg'])
        style.configure('Modern.TLabel', background=self.colors['bg'], foreground=self.colors['text'])
        style.configure('Modern.TButton', 
                       background=self.colors['accent'],
                       foreground=self.colors['text'],
                       borderwidth=0,
                       focuscolor='none')
        style.map('Modern.TButton',
                 background=[('active', self.colors['accent_hover']),
                           ('pressed', self.colors['accent_hover'])])
        
        style.configure('Accent.TButton',
                       background=self.colors['success'],
                       foreground=self.colors['text'])
        style.map('Accent.TButton',
                 background=[('active', '#45a049'),
                           ('pressed', '#45a049')])
        
        style.configure('Danger.TButton',
                       background=self.colors['danger'],
                       foreground=self.colors['text'])
        style.map('Danger.TButton',
                 background=[('active', '#d32f2f'),
                           ('pressed', '#d32f2f')])
        
        style.configure('Modern.TLabelframe', 
                       background=self.colors['bg'],
                       foreground=self.colors['text'],
                       bordercolor=self.colors['bg_lighter'])
        style.configure('Modern.TLabelframe.Label',
                       background=self.colors['bg'],
                       foreground=self.colors['accent'])
        
        # Styl dla progressbar
        style.configure('Modern.Horizontal.TProgressbar',
                       background=self.colors['accent'],
                       troughcolor=self.colors['bg_lighter'],
                       borderwidth=0,
                       lightcolor=self.colors['accent'],
                       darkcolor=self.colors['accent'])
        
        # Styl dla notebook
        style.configure('Modern.TNotebook',
                       background=self.colors['bg'],
                       borderwidth=0)
        style.configure('Modern.TNotebook.Tab',
                       background=self.colors['bg_light'],
                       foreground=self.colors['text_secondary'],
                       padding=[15, 5],
                       borderwidth=0)
        style.map('Modern.TNotebook.Tab',
                 background=[('selected', self.colors['accent']),
                           ('active', self.colors['accent_hover'])],
                 foreground=[('selected', self.colors['text']),
                           ('active', self.colors['text'])])
        
        # Styl dla Treeview
        style.configure('Treeview',
                       background=self.colors['bg_light'],
                       foreground=self.colors['text'],
                       fieldbackground=self.colors['bg_light'],
                       borderwidth=0)
        style.configure('Treeview.Heading',
                       background=self.colors['bg_lighter'],
                       foreground=self.colors['text'],
                       borderwidth=0)
        style.map('Treeview.Heading',
                 background=[('active', self.colors['accent'])])
        
    def create_notebook(self):
        """Tworzy nowoczesny interfejs zakładek"""
        # Główny notebook
        self.notebook = ttk.Notebook(self.root, style='Modern.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=15, pady=15)
        
        # Zakładki
        self.cpu_tab = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.disk_tab = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.files_tab = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.processes_tab = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.temperature_tab = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.network_tab = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.system_info_tab = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.benchmark_tab = ttk.Frame(self.notebook, style='Modern.TFrame')  # NOWA ZAKŁADKA
        
        self.notebook.add(self.cpu_tab, text='🖥️  CPU & RAM')
        self.notebook.add(self.disk_tab, text='💾 Disk')
        self.notebook.add(self.files_tab, text='📁 Files')
        self.notebook.add(self.processes_tab, text='⚙️  Processes')
        self.notebook.add(self.temperature_tab, text='🌡️  Temperature')
        self.notebook.add(self.network_tab, text='🌐 Network')
        self.notebook.add(self.system_info_tab, text='📊 System Info')
        self.notebook.add(self.benchmark_tab, text='🚀 Benchmark')  # NOWA ZAKŁADKA
        
        # Tworzenie interfejsu dla każdej zakładki
        self.create_cpu_tab()
        self.create_disk_tab()
        self.create_files_tab()
        self.create_processes_tab()
        self.create_temperature_tab()
        self.create_network_tab()
        self.create_system_info_tab()
        self.create_benchmark_tab()  # NOWA METODA
        
    def create_cpu_tab(self):
        """Tworzy nowoczesną zakładkę CPU/RAM"""
        # Główna ramka
        main_frame = ttk.Frame(self.cpu_tab, style='Modern.TFrame', padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Nagłówek
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(header_frame, 
                               text="System Performance Monitor", 
                               style='Modern.TLabel',
                               font=('Arial', 18, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Ramka z metrykami systemowymi
        metrics_frame = ttk.LabelFrame(main_frame, text="🔍 System Metrics", style='Modern.TLabelframe', padding="15")
        metrics_frame.pack(fill='x', pady=(0, 20))
        
        # CPU Info
        self.cpu_info_label = ttk.Label(metrics_frame, 
                                       text="Initializing CPU data...", 
                                       style='Modern.TLabel',
                                       font=('Arial', 10))
        self.cpu_info_label.pack(anchor='w', pady=5)
        
        # RAM Info z progress bar
        ram_frame = ttk.Frame(metrics_frame, style='Modern.TFrame')
        ram_frame.pack(fill='x', pady=10)
        
        self.ram_label = ttk.Label(ram_frame, 
                                  text="RAM: --/-- GB (--%)", 
                                  style='Modern.TLabel',
                                  font=('Arial', 10))
        self.ram_label.pack(anchor='w')
        
        self.ram_progress = ttk.Progressbar(ram_frame, 
                                          style='Modern.Horizontal.TProgressbar',
                                          length=300)
        self.ram_progress.pack(fill='x', pady=5)
        
        # SWAP Info
        self.swap_label = ttk.Label(metrics_frame, 
                                   text="SWAP: --/-- GB (--%)", 
                                   style='Modern.TLabel',
                                   font=('Arial', 10))
        self.swap_label.pack(anchor='w', pady=5)
        
        # Wykres CPU
        chart_frame = ttk.LabelFrame(main_frame, text="📊 CPU Core Usage", style='Modern.TLabelframe', padding="15")
        chart_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        self.fig = Figure(figsize=(10, 4), dpi=100, facecolor=self.colors['bg'])
        self.ax = self.fig.add_subplot(111)
        self.ax.set_facecolor(self.colors['bg_light'])
        self.canvas = FigureCanvasTkAgg(self.fig, chart_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Procesy i przyciski
        bottom_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        bottom_frame.pack(fill='x')
        
        # Lista procesów
        processes_frame = ttk.LabelFrame(bottom_frame, text="🔥 Top Processes", style='Modern.TLabelframe', padding="10")
        processes_frame.pack(side=tk.LEFT, fill='both', expand=True, padx=(0, 10))
        
        columns = ('pid', 'name', 'usage')
        self.tree = ttk.Treeview(processes_frame, columns=columns, show='headings', height=6)
        
        self.tree.heading('pid', text='PID')
        self.tree.heading('name', text='Process Name')
        self.tree.heading('usage', text='CPU %')
        
        self.tree.column('pid', width=80, anchor='center')
        self.tree.column('name', width=200)
        self.tree.column('usage', width=80, anchor='center')
        
        self.tree.pack(fill='both', expand=True)
        
        # Pasek przewijania
        scrollbar = ttk.Scrollbar(processes_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side=tk.RIGHT, fill='y')
        
        # Panel przycisków
        button_frame = ttk.Frame(bottom_frame, style='Modern.TFrame')
        button_frame.pack(side=tk.RIGHT, fill='y', padx=(10, 0))
        
        ttk.Button(button_frame, 
                  text="🔄 Refresh", 
                  style='Modern.TButton',
                  command=self.update_data).pack(fill='x', pady=5)
        
        ttk.Button(button_frame, 
                  text="📊 Details", 
                  style='Modern.TButton',
                  command=self.show_detailed_info).pack(fill='x', pady=5)
        
        ttk.Button(button_frame, 
                  text="⚙️ Settings", 
                  style='Modern.TButton',
                  command=self.show_settings).pack(fill='x', pady=5)
        
        ttk.Button(button_frame, 
                  text="❌ Exit", 
                  style='Accent.TButton',
                  command=self.root.destroy).pack(fill='x', pady=5)
        
    def create_disk_tab(self):
        """Tworzy nowoczesną zakładkę dysków"""
        main_frame = ttk.Frame(self.disk_tab, style='Modern.TFrame', padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Nagłówek
        title_label = ttk.Label(main_frame, 
                               text="Disk & Storage Monitor", 
                               style='Modern.TLabel',
                               font=('Arial', 18, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Partycje dyskowe
        partitions_frame = ttk.LabelFrame(main_frame, text="💽 Disk Partitions", style='Modern.TLabelframe', padding="15")
        partitions_frame.pack(fill='x', pady=(0, 20))
        
        columns = ('Device', 'Mountpoint', 'FSType', 'Total', 'Used', 'Free', 'Percent')
        self.disk_tree = ttk.Treeview(partitions_frame, columns=columns, show='headings', height=6)
        
        # Nagłówki
        headers = [
            ('Device', 'Device', 100),
            ('Mountpoint', 'Mount Point', 150),
            ('FSType', 'File System', 90),
            ('Total', 'Total Size', 90),
            ('Used', 'Used', 90),
            ('Free', 'Free', 90),
            ('Percent', 'Usage %', 80)
        ]
        
        for col, text, width in headers:
            self.disk_tree.heading(col, text=text)
            self.disk_tree.column(col, width=width, anchor='center')
        
        self.disk_tree.pack(fill='both', expand=True)
        
        # Pasek przewijania
        scrollbar_disk = ttk.Scrollbar(partitions_frame, orient=tk.VERTICAL, command=self.disk_tree.yview)
        self.disk_tree.configure(yscrollcommand=scrollbar_disk.set)
        scrollbar_disk.pack(side=tk.RIGHT, fill='y')
        
        # Wykres dysków
        chart_frame = ttk.LabelFrame(main_frame, text="📈 Disk Usage Overview", style='Modern.TLabelframe', padding="15")
        chart_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        self.fig_disk = Figure(figsize=(10, 4), dpi=100, facecolor=self.colors['bg'])
        self.ax_disk = self.fig_disk.add_subplot(111)
        self.ax_disk.set_facecolor(self.colors['bg_light'])
        self.canvas_disk = FigureCanvasTkAgg(self.fig_disk, chart_frame)
        self.canvas_disk.get_tk_widget().pack(fill='both', expand=True)
        
    def create_files_tab(self):
        """Tworzy nowoczesną zakładkę plików"""
        main_frame = ttk.Frame(self.files_tab, style='Modern.TFrame', padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Nagłówek
        title_label = ttk.Label(main_frame, 
                               text="File System Explorer", 
                               style='Modern.TLabel',
                               font=('Arial', 18, 'bold'))
        title_label.pack(pady=(0, 20))
        
        # Pasek nawigacji
        nav_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        nav_frame.pack(fill='x', pady=(0, 15))
        
        # Przyciski nawigacji
        nav_buttons = [
            ("⏪", self.go_back),
            ("⏩", self.go_forward),
            ("📁", self.go_up),
            ("🏠", self.go_home),
            ("🔍", self.browse_directory)
        ]
        
        for text, command in nav_buttons:
            btn = ttk.Button(nav_frame, text=text, style='Modern.TButton', command=command, width=4)
            btn.pack(side=tk.LEFT, padx=2)
        
        # Pole ścieżki
        self.path_var = tk.StringVar(value=str(self.current_path))
        self.path_entry = ttk.Entry(nav_frame, textvariable=self.path_var, font=('Arial', 10))
        self.path_entry.pack(side=tk.LEFT, fill='x', expand=True, padx=5)
        self.path_entry.bind('<Return>', self.on_path_enter)
        
        # Przyciski akcji
        action_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        action_frame.pack(fill='x', pady=(0, 15))
        
        actions = [
            ("🔄 Refresh", self.refresh_files),
            ("💾 Large Files", self.find_large_files),
            ("👁️ Show Hidden", self.toggle_hidden),
            ("📋 Info", self.show_file_info),
            ("🗑️ Delete", self.delete_selected)
        ]
        
        for text, command in actions:
            btn = ttk.Button(action_frame, text=text, style='Modern.TButton', command=command)
            btn.pack(side=tk.LEFT, padx=2)
        
        # Tabela plików
        file_frame = ttk.LabelFrame(main_frame, text="📂 Directory Contents", style='Modern.TLabelframe', padding="10")
        file_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('name', 'size', 'type', 'modified', 'permissions')
        self.files_tree = ttk.Treeview(file_frame, columns=columns, show='headings', height=15)
        
        # Nagłówki
        file_headers = [
            ('name', 'Name', 250),
            ('size', 'Size', 100),
            ('type', 'Type', 80),
            ('modified', 'Modified', 150),
            ('permissions', 'Permissions', 90)
        ]
        
        for col, text, width in file_headers:
            self.files_tree.heading(col, text=text, command=lambda c=col: self.sort_files(c))
            self.files_tree.column(col, width=width)
        
        self.files_tree.pack(fill='both', expand=True, side=tk.LEFT)
        self.files_tree.bind('<Double-1>', self.on_file_double_click)
        
        # Pasek przewijania
        scrollbar_files = ttk.Scrollbar(file_frame, orient=tk.VERTICAL, command=self.files_tree.yview)
        self.files_tree.configure(yscrollcommand=scrollbar_files.set)
        scrollbar_files.pack(side=tk.RIGHT, fill='y')
        
        # Menu kontekstowe
        self.create_context_menu()
        
        # Pasek statusu
        self.status_label = ttk.Label(main_frame, text="", style='Modern.TLabel')
        self.status_label.pack(fill='x')
        
        # Zmienne
        self.show_hidden = False
        self.sort_column = 'name'
        self.sort_reverse = False
        
        # Załaduj początkowy katalog
        self.load_directory()

    def create_context_menu(self):
        """Tworzy menu kontekstowe dla plików"""
        self.context_menu = tk.Menu(self.files_tree, tearoff=0, bg=self.colors['bg_light'], fg=self.colors['text'])
        self.context_menu.add_command(label="📋 Copy", command=self.copy_selected)
        self.context_menu.add_command(label="✂️ Cut", command=self.cut_selected)
        self.context_menu.add_command(label="📄 Paste", command=self.paste_files)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📂 Open", command=self.open_selected)
        self.context_menu.add_command(label="📝 Rename", command=self.rename_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="🗑️ Delete", command=self.delete_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="📋 Properties", command=self.show_file_info)
        
        # Bind prawy przycisk myszy do wyświetlenia menu kontekstowego
        self.files_tree.bind("<Button-3>", self.show_context_menu)

        # zamknij menu przy kliknięciu lewym przyciskiem
        self.files_tree.bind("<Button-1>", lambda e: self.context_menu.unpost() if self.context_menu else None)
        self.root.bind("<Button-1>", lambda e: self.context_menu.unpost() if self.context_menu else None)

    def show_context_menu(self, event):
        """Pokazuje menu kontekstowe"""
        # Wybierz element pod kursorem
        item = self.files_tree.identify_row(event.y)
        if item:
            self.files_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def copy_selected(self):
        """Kopiuje zaznaczone pliki/katalogi"""
        selection = self.files_tree.selection()
        if selection:
            self.clipboard = []
            for item in selection:
                item_values = self.files_tree.item(item)['values']
                name = item_values[0]
                # Pomijaj .. w operacjach schowka
                if name != "..":
                    self.clipboard.append(self.current_path / name)
            if self.clipboard:  # Tylko jeśli są elementy do skopiowania (oprócz ..)
                self.clipboard_operation = 'copy'
                self.status_label.config(text=f"📋 Copied {len(self.clipboard)} item(s) to clipboard")
            else:
                messagebox.showwarning("Warning", "Cannot copy parent directory (..)")

    def cut_selected(self):
        """Wycina zaznaczone pliki/katalogi"""
        selection = self.files_tree.selection()
        if selection:
            self.clipboard = []
            for item in selection:
                item_values = self.files_tree.item(item)['values']
                name = item_values[0]
                # Pomijaj .. w operacjach schowka
                if name != "..":
                    self.clipboard.append(self.current_path / name)
            if self.clipboard:  # Tylko jeśli są elementy do wycięcia (oprócz ..)
                self.clipboard_operation = 'cut'
                self.status_label.config(text=f"✂️ Cut {len(self.clipboard)} item(s) to clipboard")
            else:
                messagebox.showwarning("Warning", "Cannot cut parent directory (..)")

    def paste_files(self):
        """Wkleja pliki/katalogi z schowka"""
        if not self.clipboard:
            messagebox.showwarning("Warning", "Clipboard is empty")
            return
        
        try:
            for source_path in self.clipboard:
                if not source_path.exists():
                    continue
                
                destination_path = self.current_path / source_path.name
                
                # Jeśli plik już istnieje, zapytaj o nadpisanie
                if destination_path.exists():
                    result = messagebox.askyesno("Confirm", 
                                               f"'{source_path.name}' already exists. Overwrite?")
                    if not result:
                        continue
                
                if self.clipboard_operation == 'copy':
                    if source_path.is_file():
                        shutil.copy2(source_path, destination_path)
                    else:
                        shutil.copytree(source_path, destination_path)
                elif self.clipboard_operation == 'cut':
                    shutil.move(str(source_path), str(destination_path))
            
            # Po operacji cut wyczyść schowek
            if self.clipboard_operation == 'cut':
                self.clipboard = None
                self.clipboard_operation = None
            
            self.load_directory()
            self.status_label.config(text="✅ Paste operation completed")
            
        except Exception as e:
            messagebox.showerror("Error", f"Cannot paste files: {e}")

    def rename_selected(self):
        """Zmienia nazwę zaznaczonego pliku/katalogu"""
        selection = self.files_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a file or folder to rename")
            return
        
        if len(selection) > 1:
            messagebox.showwarning("Warning", "Please select only one item to rename")
            return
        
        item = selection[0]
        item_values = self.files_tree.item(item)['values']
        old_name = item_values[0]
        
        # Nie pozwól zmienić nazwy ..
        if old_name == "..":
            messagebox.showwarning("Warning", "Cannot rename parent directory")
            return
        
        old_path = self.current_path / old_name
        
        # Okno dialogowe do zmiany nazwy
        rename_window = tk.Toplevel(self.root)
        rename_window.title("Rename")
        rename_window.geometry("300x120")
        rename_window.configure(bg=self.colors['bg'])
        rename_window.resizable(False, False)
        
        # Wyśrodkuj okno
        rename_window.transient(self.root)
        rename_window.grab_set()
        
        ttk.Label(rename_window, text="New name:", style='Modern.TLabel').pack(pady=10)
        
        new_name_var = tk.StringVar(value=old_name)
        name_entry = ttk.Entry(rename_window, textvariable=new_name_var, font=('Arial', 10))
        name_entry.pack(fill='x', padx=20, pady=5)
        name_entry.select_range(0, tk.END)
        name_entry.focus()
        
        def confirm_rename():
            new_name = new_name_var.get().strip()
            if not new_name:
                messagebox.showwarning("Warning", "Name cannot be empty")
                return
            
            if new_name == old_name:
                rename_window.destroy()
                return
            
            new_path = self.current_path / new_name
            
            if new_path.exists():
                messagebox.showwarning("Warning", f"'{new_name}' already exists")
                return
            
            try:
                old_path.rename(new_path)
                rename_window.destroy()
                self.load_directory()
                self.status_label.config(text=f"✅ Renamed '{old_name}' to '{new_name}'")
            except Exception as e:
                messagebox.showerror("Error", f"Cannot rename: {e}")
        
        button_frame = ttk.Frame(rename_window, style='Modern.TFrame')
        button_frame.pack(fill='x', padx=20, pady=10)
        
        ttk.Button(button_frame, text="Cancel", style='Modern.TButton', 
                  command=rename_window.destroy).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Rename", style='Accent.TButton', 
                  command=confirm_rename).pack(side=tk.RIGHT, padx=5)
        
        # Bind Enter do potwierdzenia
        name_entry.bind('<Return>', lambda e: confirm_rename())

    def open_selected(self):
        """Otwiera zaznaczony plik/katalog"""
        selection = self.files_tree.selection()
        if selection:
            item = self.files_tree.item(selection[0])
            name = item['values'][0]
            
            # Specjalna obsługa dla ..
            if name == "..":
                self.go_up()
                return
                
            clicked_path = self.current_path / name
            
            if clicked_path.is_dir():
                self.current_path = clicked_path
                self.load_directory()
            else:
                self.open_file(clicked_path)

    def create_processes_tab(self):
        """Tworzy nowoczesną zakładkę procesów"""
        main_frame = ttk.Frame(self.processes_tab, style='Modern.TFrame', padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Nagłówek
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(header_frame, 
                               text="Process Manager", 
                               style='Modern.TLabel',
                               font=('Arial', 18, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Statystyki procesów
        stats_frame = ttk.LabelFrame(main_frame, text="📈 Process Statistics", style='Modern.TLabelframe', padding="15")
        stats_frame.pack(fill='x', pady=(0, 15))
        
        # Ramka dla statystyk
        stats_grid = ttk.Frame(stats_frame, style='Modern.TFrame')
        stats_grid.pack(fill='x')
        
        self.total_processes_label = ttk.Label(stats_grid, 
                                             text="Total Processes: --", 
                                             style='Modern.TLabel',
                                             font=('Arial', 10))
        self.total_processes_label.grid(row=0, column=0, sticky='w', padx=(0, 20))
        
        self.running_processes_label = ttk.Label(stats_grid, 
                                               text="Running: --", 
                                               style='Modern.TLabel',
                                               font=('Arial', 10))
        self.running_processes_label.grid(row=0, column=1, sticky='w', padx=(0, 20))
        
        self.sleeping_processes_label = ttk.Label(stats_grid, 
                                                text="Sleeping: --", 
                                                style='Modern.TLabel',
                                                font=('Arial', 10))
        self.sleeping_processes_label.grid(row=0, column=2, sticky='w', padx=(0, 20))
        
        self.cpu_usage_label = ttk.Label(stats_grid, 
                                       text="Total CPU: --%", 
                                       style='Modern.TLabel',
                                       font=('Arial', 10))
        self.cpu_usage_label.grid(row=0, column=3, sticky='w')
        
        # Przyciski akcji
        actions_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        actions_frame.pack(fill='x', pady=(0, 15))
        
        # Przycisk Auto odświeżania procesów
        self.auto_processes_button = ttk.Button(actions_frame, 
                                              text="▶️ Auto", 
                                              style='Modern.TButton',
                                              command=self.toggle_auto_refresh_processes)
        self.auto_processes_button.grid(row=0, column=0, padx=2)
        
        action_buttons = [
            ("🔄 Refresh", self.update_processes_data),
            ("🔍 Search", self.search_processes),
            ("📊 Details", self.show_process_details),
            ("⏹️  Stop", self.stop_process),
            ("🗑️  Kill", self.kill_process),
            ("📈 Resources", self.show_process_resources)
        ]
        
        for i, (text, command) in enumerate(action_buttons):
            btn_style = 'Modern.TButton'
            if "Kill" in text:
                btn_style = 'Danger.TButton'
            elif "Stop" in text:
                btn_style = 'Accent.TButton'
                
            btn = ttk.Button(actions_frame, text=text, style=btn_style, command=command)
            btn.grid(row=0, column=i+1, padx=2)  # +1 bo pierwsza kolumna to przycisk Auto
        
        # Pole wyszukiwania
        search_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        search_frame.pack(fill='x', pady=(0, 10))
        
        ttk.Label(search_frame, text="Search:", style='Modern.TLabel').pack(side=tk.LEFT, padx=(0, 5))
        self.process_search_var = tk.StringVar()
        self.process_search_entry = ttk.Entry(search_frame, textvariable=self.process_search_var, font=('Arial', 10))
        self.process_search_entry.pack(side=tk.LEFT, fill='x', expand=True)
        self.process_search_entry.bind('<KeyRelease>', self.on_process_search)
        
        # Tabela procesów
        process_frame = ttk.LabelFrame(main_frame, text="📋 All Processes", style='Modern.TLabelframe', padding="10")
        process_frame.pack(fill='both', expand=True)
        
        columns = ('pid', 'name', 'cpu', 'memory', 'status', 'user', 'threads', 'create_time')
        self.processes_tree = ttk.Treeview(process_frame, columns=columns, show='headings', height=20)
        
        # Nagłówki z funkcjami sortowania
        process_headers = [
            ('pid', 'PID', 70, 'numeric'),
            ('name', 'Process Name', 200, 'text'),
            ('cpu', 'CPU %', 80, 'numeric'),
            ('memory', 'Memory %', 90, 'numeric'),
            ('status', 'Status', 90, 'text'),
            ('user', 'User', 100, 'text'),
            ('threads', 'Threads', 70, 'numeric'),
            ('create_time', 'Created', 150, 'text')
        ]
        
        for col, text, width, sort_type in process_headers:
            self.processes_tree.heading(col, text=text, 
                                      command=lambda c=col: self.sort_processes(c))
            self.processes_tree.column(col, width=width, anchor='center')
        
        self.processes_tree.pack(fill='both', expand=True, side=tk.LEFT)
        
        # Podwójne kliknięcie dla szczegółów
        self.processes_tree.bind('<Double-1>', self.on_process_double_click)
        
        # Pasek przewijania
        scrollbar_processes = ttk.Scrollbar(process_frame, orient=tk.VERTICAL, command=self.processes_tree.yview)
        self.processes_tree.configure(yscrollcommand=scrollbar_processes.set)
        scrollbar_processes.pack(side=tk.RIGHT, fill='y')
        
        # Pasek statusu
        self.process_status_label = ttk.Label(main_frame, text="Ready", style='Modern.TLabel')
        self.process_status_label.pack(fill='x', pady=(5, 0))
        
        # Załaduj dane procesów
        self.update_processes_data()

    def toggle_auto_refresh_processes(self):
        """Przełącza automatyczne odświeżanie procesów"""
        if self.auto_refresh_processes:
            # Wyłącz automatyczne odświeżanie
            self.auto_refresh_processes = False
            if self.process_refresh_id:
                self.root.after_cancel(self.process_refresh_id)
                self.process_refresh_id = None
            self.auto_processes_button.config(text="▶️ Auto")
            self.process_status_label.config(text="Auto refresh disabled")
        else:
            # Włącz automatyczne odświeżanie
            self.auto_refresh_processes = True
            self.auto_processes_button.config(text="⏸️ Auto")
            self.process_status_label.config(text="Auto refresh enabled - updating every 2 seconds")
            self.start_auto_refresh_processes()

    def start_auto_refresh_processes(self):
        """Rozpoczyna automatyczne odświeżanie procesów"""
        if self.auto_refresh_processes:
            self.update_processes_data()
            # Zaplanuj kolejne odświeżanie za 2 sekundy
            self.process_refresh_id = self.root.after(2000, self.start_auto_refresh_processes)

    def create_temperature_tab(self):
        """Tworzy zakładkę temperatury"""
        main_frame = ttk.Frame(self.temperature_tab, style='Modern.TFrame', padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Nagłówek
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(header_frame, 
                               text="Temperature Monitor", 
                               style='Modern.TLabel',
                               font=('Arial', 18, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Przyciski akcji
        action_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        action_frame.pack(fill='x', pady=(0, 15))
        
        # Przycisk Auto z funkcją toggle
        self.auto_button = ttk.Button(action_frame, 
                                    text="⏸️ Auto", 
                                    style='Modern.TButton',
                                    command=self.toggle_auto_refresh)
        self.auto_button.pack(side=tk.LEFT, padx=2)
        
        ttk.Button(action_frame, 
                  text="🔄 Refresh Sensors", 
                  style='Modern.TButton',
                  command=self.update_temperature_data).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(action_frame, 
                  text="📊 Install lm-sensors", 
                  style='Accent.TButton',
                  command=self.install_lm_sensors).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(action_frame, 
                  text="🔧 Detect Sensors", 
                  style='Modern.TButton',
                  command=self.detect_sensors).pack(side=tk.LEFT, padx=2)
        
        # Status czujników
        self.sensors_status_label = ttk.Label(main_frame, 
                                            text="Checking sensors availability...", 
                                            style='Modern.TLabel',
                                            font=('Arial', 10))
        self.sensors_status_label.pack(fill='x', pady=(0, 10))
        
        # Tabela temperatur
        temp_frame = ttk.LabelFrame(main_frame, text="🌡️ Temperature Sensors", style='Modern.TLabelframe', padding="10")
        temp_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('sensor', 'current', 'high', 'critical', 'status')
        self.temp_tree = ttk.Treeview(temp_frame, columns=columns, show='headings', height=15)
        
        # Nagłówki
        temp_headers = [
            ('sensor', 'Sensor', 250),
            ('current', 'Current (°C)', 100),
            ('high', 'High (°C)', 90),
            ('critical', 'Critical (°C)', 100),
            ('status', 'Status', 100)
        ]
        
        for col, text, width in temp_headers:
            self.temp_tree.heading(col, text=text)
            self.temp_tree.column(col, width=width, anchor='center')
        
        self.temp_tree.pack(fill='both', expand=True, side=tk.LEFT)
        
        # Pasek przewijania
        scrollbar_temp = ttk.Scrollbar(temp_frame, orient=tk.VERTICAL, command=self.temp_tree.yview)
        self.temp_tree.configure(yscrollcommand=scrollbar_temp.set)
        scrollbar_temp.pack(side=tk.RIGHT, fill='y')
        
        # Output czujników (surowy tekst)
        output_frame = ttk.LabelFrame(main_frame, text="📋 Raw Sensors Output", style='Modern.TLabelframe', padding="10")
        output_frame.pack(fill='both', expand=True)
        
        # Pole tekstowe z surowym outputem
        self.sensors_output = tk.Text(output_frame, 
                                     height=8, 
                                     bg=self.colors['bg_light'], 
                                     fg=self.colors['text'],
                                     font=('Courier', 9),
                                     wrap=tk.WORD)
        
        scrollbar_output = ttk.Scrollbar(output_frame, orient=tk.VERTICAL, command=self.sensors_output.yview)
        self.sensors_output.configure(yscrollcommand=scrollbar_output.set)
        
        self.sensors_output.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar_output.pack(side=tk.RIGHT, fill='y')
        
        # Załaduj dane temperatury
        self.update_temperature_data()

    def create_network_tab(self):
        """Tworzy zakładkę Network"""
        self.network_monitor = NetworkMonitor(self.network_tab, self.colors)

    def create_system_info_tab(self):
        """Tworzy zakładkę System Info"""
        self.system_info = SystemInfoTab(self.system_info_tab, self.colors)

    def create_benchmark_tab(self):
        """Tworzy zakładkę Benchmark"""
        self.benchmark = BenchmarkTab(self.benchmark_tab, self.colors)

    def toggle_auto_refresh(self):
        """Przełącza automatyczne odświeżanie temperatury"""
        if self.auto_refresh_temp:
            # Wyłącz automatyczne odświeżanie
            self.auto_refresh_temp = False
            if self.temp_refresh_id:
                self.root.after_cancel(self.temp_refresh_id)
                self.temp_refresh_id = None
            self.auto_button.config(text="▶️ Auto")
            self.sensors_status_label.config(text="Auto refresh disabled")
        else:
            # Włącz automatyczne odświeżanie
            self.auto_refresh_temp = True
            self.auto_button.config(text="⏸️ Auto")
            self.sensors_status_label.config(text="Auto refresh enabled - updating every 1 second")
            self.start_auto_refresh()

    def start_auto_refresh(self):
        """Rozpoczyna automatyczne odświeżanie temperatury"""
        if self.auto_refresh_temp:
            self.update_temperature_data()
            # Zaplanuj kolejne odświeżanie za 1 sekundę
            self.temp_refresh_id = self.root.after(1000, self.start_auto_refresh)

    def update_data(self):
        """Aktualizuje dane systemowe"""
        try:
            self.update_cpu_ram_data()
            self.update_disk_data()
        except Exception as e:
            print(f"Error updating data: {e}")
        
        # Zaplanuj kolejną aktualizację po 2 sekundach
        self.root.after(2000, self.update_data)

    def update_cpu_ram_data(self):
        """Aktualizuje dane CPU i RAM z poprawionym odczytem częstotliwości"""
        # CPU Data
        self.cpu_percent_per_core = psutil.cpu_percent(interval=0.1, percpu=True)
        self.total_usage = psutil.cpu_percent(interval=0)
        
        physical_cores = psutil.cpu_count(logical=False)
        logical_cores = psutil.cpu_count(logical=True)
        
        # POPRAWIONY ODCZYT CZĘSTOTLIWOŚCI CPU
        cpu_freq = psutil.cpu_freq()
        if cpu_freq:
            # Sprawdź czy częstotliwość jest realistyczna (więcej niż 100 MHz)
            if cpu_freq.current > 100:  # Większe niż 100 MHz
                self.cpu_freq = int(cpu_freq.current)
            else:
                # Spróbuj alternatywnych metod odczytu częstotliwości
                self.cpu_freq = self.get_cpu_frequency_alternative()
        else:
            self.cpu_freq = self.get_cpu_frequency_alternative()
        
        # Update CPU info
        cpu_info_text = (f"🖥️  CPU Usage: {self.total_usage:.1f}% | "
                        f"Cores: {physical_cores}P + {logical_cores - physical_cores}L | "
                        f"Frequency: {self.cpu_freq} MHz")
        self.cpu_info_label.config(text=cpu_info_text)
        
        # RAM Data - zaawansowane obliczenia
        ram = psutil.virtual_memory()
        
        total_gb = ram.total / (1024 ** 3)
        
        # Różne metody obliczania użycia RAM
        # Metoda 1: Podobna do htop (total - available)
        used_htop = ram.total - ram.available
        used_gb_htop = used_htop / (1024 ** 3)
        percent_htop = (used_htop / ram.total) * 100
        
        # Metoda 2: Używana przez psutil
        used_gb_psutil = ram.used / (1024 ** 3)
        percent_psutil = ram.percent
        
        # Wybierz metodę która jest bliższa htop
        # Zazwyczaj metoda htop-style jest bardziej precyzyjna
        used_gb = used_gb_htop
        ram_percent = percent_htop
        
        # Update RAM info
        ram_text = f"💾 RAM: {used_gb:.1f} GB / {total_gb:.1f} GB ({ram_percent:.1f}%)"
        self.ram_label.config(text=ram_text)
        self.ram_progress['value'] = ram_percent
        
        # SWAP Data
        swap = psutil.swap_memory()
        self.swap_usage = swap.used / (1024 ** 3)
        self.swap_total = swap.total / (1024 ** 3)
        self.swap_percent = swap.percent
        
        swap_text = f"🔄 SWAP: {self.swap_usage:.1f} GB / {self.swap_total:.1f} GB ({self.swap_percent:.1f}%)"
        self.swap_label.config(text=swap_text)
        
        # Update charts and process list
        self.update_cpu_chart()
        self.update_process_list()
    def get_cpu_frequency_alternative(self):
        """Alternatywne metody odczytu częstotliwości CPU gdy psutil zwraca błędne dane"""
        try:
            # Metoda 1: Odczyt z /proc/cpuinfo (Linux)
            if os.path.exists('/proc/cpuinfo'):
                with open('/proc/cpuinfo', 'r') as f:
                    content = f.read()
                    # Szukaj częstotliwości w kHz i konwertuj na MHz
                    import re
                    matches = re.findall(r'cpu MHz\s*:\s*(\d+\.\d+)', content)
                    if matches:
                        frequencies = [float(m) for m in matches]
                        avg_freq = sum(frequencies) / len(frequencies)
                        if avg_freq > 100:  # Tylko jeśli realistyczna wartość
                            return int(avg_freq)
            
            # Metoda 2: Użyj lscpu (Linux)
            try:
                result = subprocess.run(['lscpu'], capture_output=True, text=True, timeout=2)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'CPU MHz:' in line:
                            freq = float(line.split(':')[1].strip())
                            if freq > 100:
                                return int(freq)
                        elif 'CPU max MHz:' in line:
                            freq = float(line.split(':')[1].strip())
                            if freq > 100:
                                return int(freq)
            except:
                pass
            
            # Metoda 3: Spróbuj ponownie psutil z innym interwałem
            time.sleep(0.1)
            cpu_freq = psutil.cpu_freq()
            if cpu_freq and cpu_freq.current > 100:
                return int(cpu_freq.current)
                
            # Metoda 4: Domyślna wartość dla nowoczesnych procesorów
            return 2000  # 2 GHz jako domyślna wartość
            
        except Exception as e:
            print(f"Błąd odczytu częstotliwości CPU: {e}")
            return 2000  # Fallback value
    
    def update_cpu_chart(self):
        """Aktualizuje wykres CPU - POPRAWIONA WERSJA"""
        self.ax.clear()
        
        # UŻYJ LICZB CAŁKOWITYCH dla rdzeni - KLUCZOWA ZMIANA
        cores = list(range(len(self.cpu_percent_per_core)))
        
        # Sprawdź czy mamy dane
        if not self.cpu_percent_per_core:
            print("Brak danych CPU do wyświetlenia")
            return
        
        colors = [self.colors['success'] if usage < 50 
                 else self.colors['warning'] if usage < 80 
                 else self.colors['danger'] 
                 for usage in self.cpu_percent_per_core]
        
        # Utwórz wykres słupkowy z POPRAWIONYMI etykietami
        bars = self.ax.bar(cores, self.cpu_percent_per_core, color=colors, 
                          edgecolor='white', linewidth=0.5, width=0.8)
        
        # POPRAWIONE: Ustaw etykiety rdzeni jako liczby całkowite
        self.ax.set_xlabel('CPU Cores', color=self.colors['text'], fontsize=12)
        self.ax.set_ylabel('Usage (%)', color=self.colors['text'], fontsize=12)
        self.ax.set_title(f'CPU Core Utilization - Total: {self.total_usage:.1f}%', 
                         color=self.colors['text'], pad=20, fontsize=14)
        self.ax.set_ylim(0, 100)
        
        # POPRAWIONE: Ustaw poprawne etykiety na osi X
        self.ax.set_xticks(cores)  # Ustaw ticki na pozycjach rdzeni
        self.ax.set_xticklabels([f'Core {i}' for i in cores])  # Etykiety jako "Core 0", "Core 1", etc.
        
        # Obracaj etykiety jeśli jest wiele rdzeni
        if len(cores) > 8:
            plt.setp(self.ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
        
        self.ax.grid(True, alpha=0.3, color=self.colors['text_secondary'])
        
        # Customize ticks
        self.ax.tick_params(colors=self.colors['text_secondary'], labelsize=10)
        
        # Add values on bars - POPRAWIONE pozycjonowanie
        for i, bar in enumerate(bars):
            height = bar.get_height()
            if height > 5:  # Tylko jeśli wartość jest widoczna
                self.ax.text(bar.get_x() + bar.get_width()/2., height + 1,
                            f'{height:.1f}%', ha='center', va='bottom', 
                            fontsize=8, color=self.colors['text'], weight='bold')
        
        # Dodaj informację o liczbie rdzeni
        physical_cores = psutil.cpu_count(logical=False)
        logical_cores = psutil.cpu_count(logical=True)
        
        if physical_cores and logical_cores:
            cores_info = f"Physical: {physical_cores}, Logical: {logical_cores}"
            self.ax.text(0.02, 0.98, cores_info, transform=self.ax.transAxes, 
                        fontsize=9, color=self.colors['text_secondary'],
                        verticalalignment='top', bbox=dict(boxstyle='round', 
                        facecolor=self.colors['bg_light'], alpha=0.7))
        
        self.canvas.draw()

    def update_process_list(self):
        """Aktualizuje listę procesów w zakładce CPU"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        processes = psutil.process_iter(attrs=['pid', 'name', 'cpu_percent'])
        process_info = []
        
        for process in processes:
            try:
                cpu_percent = process.info['cpu_percent']
                if cpu_percent > 0:
                    process_info.append((process.info['pid'], process.info['name'], cpu_percent))
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        
        process_info.sort(key=lambda x: x[2], reverse=True)
        
        for i in range(min(8, len(process_info))):
            pid, name, cpu = process_info[i]
            if len(name) > 25:
                name = name[:22] + "..."
            
            # Color code based on CPU usage
            tags = ('low',) if cpu < 10 else ('medium',) if cpu < 30 else ('high',)
            self.tree.insert('', 'end', values=(pid, name, f"{cpu:.1f}%"), tags=tags)
        
        # Configure tags for colors
        self.tree.tag_configure('low', foreground=self.colors['success'])
        self.tree.tag_configure('medium', foreground=self.colors['warning'])
        self.tree.tag_configure('high', foreground=self.colors['danger'])

    def update_disk_data(self):
        """Aktualizuje dane dysków"""
        self.disk_usage = psutil.disk_partitions()
        
        # Clear current list
        for item in self.disk_tree.get_children():
            self.disk_tree.delete(item)
        
        # Add partitions
        for partition in self.disk_usage:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                
                total_gb = usage.total / (1024 ** 3)
                used_gb = usage.used / (1024 ** 3)
                free_gb = usage.free / (1024 ** 3)
                percent = usage.percent
                
                # Determine color based on usage
                tags = ('low',) if percent < 70 else ('medium',) if percent < 90 else ('high',)
                
                self.disk_tree.insert('', 'end', 
                                    values=(partition.device, 
                                           partition.mountpoint, 
                                           partition.fstype,
                                           f"{total_gb:.1f}G",
                                           f"{used_gb:.1f}G", 
                                           f"{free_gb:.1f}G",
                                           f"{percent:.1f}%"),
                                    tags=tags)
                
            except PermissionError:
                continue
        
        # Configure tags
        self.disk_tree.tag_configure('low', foreground=self.colors['success'])
        self.disk_tree.tag_configure('medium', foreground=self.colors['warning'])
        self.disk_tree.tag_configure('high', foreground=self.colors['danger'])
        
        self.update_disk_chart()

    def update_disk_chart(self):
        """Aktualizuje wykres dysków"""
        self.ax_disk.clear()
        
        devices = []
        usage_percent = []
        colors = []
        
        for partition in self.disk_usage:
            try:
                usage = psutil.disk_usage(partition.mountpoint)
                device_name = partition.device.split('/')[-1]
                devices.append(device_name)
                usage_percent.append(usage.percent)
                
                # Color based on usage
                if usage.percent > 90:
                    colors.append(self.colors['danger'])
                elif usage.percent > 70:
                    colors.append(self.colors['warning'])
                else:
                    colors.append(self.colors['success'])
                    
            except (PermissionError, OSError):
                continue
        
        if devices:
            bars = self.ax_disk.bar(devices, usage_percent, color=colors, edgecolor='white', linewidth=0.5)
            self.ax_disk.set_xlabel('Storage Devices', color=self.colors['text'])
            self.ax_disk.set_ylabel('Usage (%)', color=self.colors['text'])
            self.ax_disk.set_title('Disk Partition Usage', color=self.colors['text'], pad=20)
            self.ax_disk.set_ylim(0, 100)
            self.ax_disk.grid(True, alpha=0.3, color=self.colors['text_secondary'])
            self.ax_disk.tick_params(colors=self.colors['text_secondary'])
            
            # Rotate labels for better readability
            if hasattr(self.ax_disk, 'xaxis'):
                plt.setp(self.ax_disk.xaxis.get_majorticklabels(), rotation=45, ha='right')
            
            # Add values on bars
            for i, bar in enumerate(bars):
                height = bar.get_height()
                self.ax_disk.text(bar.get_x() + bar.get_width()/2., height + 1,
                                f'{height:.1f}%', ha='center', va='bottom', 
                                fontsize=8, color=self.colors['text'])
            
            self.canvas_disk.draw()

    def show_detailed_info(self):
        """Pokazuje szczegółowe informacje o systemie"""
        try:
            # Pobierz szczegółowe informacje o systemie
            boot_time = datetime.datetime.fromtimestamp(psutil.boot_time())
            uptime = datetime.datetime.now() - boot_time
            
            # Informacje o CPU
            cpu_info = f"""
🖥️ CPU DETAILS:
  Physical cores: {psutil.cpu_count(logical=False)}
  Logical cores: {psutil.cpu_count(logical=True)}
  Current frequency: {psutil.cpu_freq().current if psutil.cpu_freq() else 'N/A'} MHz
  Max frequency: {psutil.cpu_freq().max if psutil.cpu_freq() else 'N/A'} MHz
  Min frequency: {psutil.cpu_freq().min if psutil.cpu_freq() else 'N/A'} MHz
"""
            
            # Informacje o pamięci
            memory = psutil.virtual_memory()
            swap = psutil.swap_memory()
            
            memory_info = f"""
💾 MEMORY DETAILS:
  Total RAM: {memory.total / (1024**3):.1f} GB
  Available: {memory.available / (1024**3):.1f} GB
  Used: {memory.used / (1024**3):.1f} GB
  Free: {memory.free / (1024**3):.1f} GB
  Usage: {memory.percent:.1f}%
  
  Total SWAP: {swap.total / (1024**3):.1f} GB
  Used SWAP: {swap.used / (1024**3):.1f} GB
  Free SWAP: {swap.free / (1024**3):.1f} GB
  SWAP Usage: {swap.percent:.1f}%
"""
            
            # Informacje o systemę
            system_info = f"""
⚙️ SYSTEM DETAILS:
  Boot time: {boot_time.strftime('%Y-%m-%d %H:%M:%S')}
  Uptime: {str(uptime).split('.')[0]}
  Platform: {psutil.sys.platform}
  Users: {len(psutil.users())}
"""
            
            detailed_info = cpu_info + memory_info + system_info
            messagebox.showinfo("System Details", detailed_info)
            
        except Exception as e:
            messagebox.showerror("Error", f"Cannot get system details: {e}")

    def show_settings(self):
        """Pokazuje ustawienia"""
        messagebox.showinfo("Settings", "Settings panel coming soon!\n\nCurrent features:\n- Dark theme\n- Real-time monitoring\n- Process management\n- File explorer\n- Temperature monitoring\n- System information")

    def load_directory(self):
        """Ładuje zawartość bieżącego katalogu z dodaniem .. dla katalogu nadrzędnego"""
        try:
            # Wyczyść poprzednią zawartość
            for item in self.files_tree.get_children():
                self.files_tree.delete(item)
            
            self.path_var.set(str(self.current_path))
            
            # Sprawdź czy katalog istnieje i jest dostępny
            if not self.current_path.exists():
                messagebox.showerror("Error", f"Directory does not exist: {self.current_path}")
                return
                
            if not self.current_path.is_dir():
                messagebox.showerror("Error", f"Path is not a directory: {self.current_path}")
                return

            # DODAJ .. DLA KATALOGU NADRZĘDNEGO - KLUCZOWA ZMIANA
            items = []
            
            # Dodaj .. tylko jeśli nie jesteśmy w root
            if self.current_path.parent != self.current_path:
                items.append("..")  # Specjalny wpis dla katalogu nadrzędnego

            try:
                # Użyj listdir zamiast iterdir dla lepszej kompatybilności
                for item_name in os.listdir(self.current_path):
                    item_path = self.current_path / item_name
                    
                    # Sprawdź czy plik/katalog jest dostępny
                    try:
                        # Sprawdź dostępność przez próbę dostępu do metadanych
                        item_path.stat()
                        
                        if not self.show_hidden and item_name.startswith('.'):
                            continue
                        items.append(item_path)
                    except (OSError, PermissionError):
                        # Pomijaj elementy do których nie ma dostępu
                        continue
                        
            except (OSError, PermissionError) as e:
                messagebox.showerror("Error", f"Cannot access directory: {e}")
                return
            
            # Sortowanie: najpierw .., potem katalogi alfabetycznie, potem pliki alfabetycznie
            directories = []
            files = []
            
            for item in items:
                if item == "..":
                    # .. traktujemy jako specjalny katalog
                    directories.insert(0, item)  # Zawsze na początku
                    continue
                    
                try:
                    if item.is_dir():
                        directories.append(item)
                    else:
                        files.append(item)
                except (OSError, PermissionError):
                    # Pomijaj elementy do których stracono dostęp
                    continue
            
            # Sortowanie alfabetyczne katalogów (oprócz .. które jest już na początku)
            directories[1:] = sorted(directories[1:], key=lambda x: x.name.lower())
            
            # Sortowanie alfabetyczne plików
            files.sort(key=lambda x: x.name.lower())
            
            # Połącz posortowane listy
            sorted_items = directories + files
            
            # Dodaj elementy do treeview
            for item in sorted_items:
                try:
                    if item == "..":
                        # Specjalne traktowanie dla ..
                        display_name = ".."
                        size = "📁 UP"
                        file_type = "📁 Parent Directory"
                        modified = ""
                        permissions = "drwxr-xr-x"  # Typowe uprawnienia dla katalogu
                        
                        self.files_tree.insert('', 'end', 
                                             values=(display_name, size, file_type, modified, permissions),
                                             tags=('parent',))
                        
                    else:
                        stat = item.stat()
                        size = self.format_size(stat.st_size) if item.is_file() else "📁 DIR"
                        file_type = "📄 File" if item.is_file() else "📁 Folder"
                        modified = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M')
                        permissions = self.get_permissions(stat.st_mode)
                        
                        # Użyj nazwy z path dla lepszej kompatybilności
                        display_name = item.name
                        
                        self.files_tree.insert('', 'end', 
                                             values=(display_name, size, file_type, modified, permissions),
                                             tags=('file' if item.is_file() else 'dir'))
                        
                except (OSError, PermissionError) as e:
                    # Jeśli nie można odczytać stat, pokaż podstawowe informacje
                    if item == "..":
                        display_name = ".."
                    else:
                        display_name = item.name
                        
                    self.files_tree.insert('', 'end', 
                                         values=(display_name, "N/A", "Unknown", "N/A", "N/A"),
                                         tags=('unknown',))
                    continue
            
            # Konfiguruj tagi dla kolorów - DODAJ NOWY TAG DLA ..
            self.files_tree.tag_configure('parent', foreground='#2196f3', font=('Arial', 10, 'bold'))  # Niebieski, pogrubiony
            self.files_tree.tag_configure('dir', foreground='#4caf50')  # Zielony
            self.files_tree.tag_configure('file', foreground='#ff9800')  # Pomarańczowo-żółty
            self.files_tree.tag_configure('unknown', foreground='#9e9e9e')  # Szary dla nieznanych
            
            file_count = len(files)
            dir_count = len([d for d in directories if d != ".."])  # Nie licz .. jako normalnego katalogu
            self.status_label.config(text=f"📊 Folders: {dir_count} | Files: {file_count} | Path: {self.current_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Cannot load directory: {e}")

    def get_permissions(self, st_mode):
        """Zwraca uprawnienia w formacie tekstowym dla różnych systemów"""
        try:
            permissions = ""
            
            # Uprawnienia dla właściciela
            permissions += 'r' if st_mode & stat.S_IRUSR else '-'
            permissions += 'w' if st_mode & stat.S_IWUSR else '-'
            permissions += 'x' if st_mode & stat.S_IXUSR else '-'
            
            # Uprawnienia dla grupy
            permissions += 'r' if st_mode & stat.S_IRGRP else '-'
            permissions += 'w' if st_mode & stat.S_IWGRP else '-'
            permissions += 'x' if st_mode & stat.S_IXGRP else '-'
            
            # Uprawnienia dla innych
            permissions += 'r' if st_mode & stat.S_IROTH else '-'
            permissions += 'w' if st_mode & stat.S_IWOTH else '-'
            permissions += 'x' if st_mode & stat.S_IXOTH else '-'
            
            return permissions
            
        except:
            # Fallback: octal permissions
            return oct(st_mode)[-3:]

    def format_size(self, size_bytes):
        """Formatuje rozmiar pliku"""
        if size_bytes == 0:
            return "0 B"
        size_names = ["B", "KB", "MB", "GB", "TB"]
        i = 0
        while size_bytes >= 1024 and i < len(size_names)-1:
            size_bytes /= 1024.0
            i += 1
        return f"{size_bytes:.1f} {size_names[i]}"

    def on_file_double_click(self, event):
        """Obsługa podwójnego kliknięcia z uwzględnieniem .."""
        selection = self.files_tree.selection()
        if selection:
            item = self.files_tree.item(selection[0])
            values = item['values']
            
            if not values:  # Zabezpieczenie przed pustymi wartościami
                return
                
            name = values[0]
        
            # SPECJALNA OBSŁUGA DLA .. - KLUCZOWA ZMIANA
            if name == "..":
                self.go_up()
                return
                
            clicked_path = self.current_path / name
        
            try:
                # Sprawdź czy ścieżka istnieje
                if clicked_path.exists():
                    if clicked_path.is_dir():
                        self.current_path = clicked_path
                        self.load_directory()
                    else:
                        self.open_file(clicked_path)
                else:
                    messagebox.showerror("Error", f"Path no longer exists: {clicked_path}")
                    self.load_directory()  # Odśwież widok
                    
            except Exception as e:
                messagebox.showerror("Error", f"Cannot access: {e}")

    def open_file(self, file_path):
        """Otwiera plik z obsługą błędów"""
        try:
            if os.name == 'nt':  # Windows
                os.startfile(str(file_path))
            elif os.name == 'posix':  # Linux, Mac
                subprocess.run(['xdg-open', str(file_path)], check=False)
            else:
                messagebox.showinfo("Info", f"Cannot open file on this system: {file_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open file: {e}")

    def go_back(self):
        """Powrót do poprzedniego katalogu z obsługą błędów"""
        try:
            parent = self.current_path.parent
            if parent != self.current_path:  # Zapobiegaj nieskończonej pętli
                self.current_path = parent
                self.load_directory()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot go back: {e}")

    def go_forward(self):
        """Do przodu"""
        messagebox.showinfo("Info", "Forward navigation coming soon!")

    def go_up(self):
        """Do katalogu nadrzędnego z obsługą błędów"""
        try:
            parent = self.current_path.parent
            if parent != self.current_path:
                self.current_path = parent
                self.load_directory()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot go up: {e}")

    def go_home(self):
        """Do katalogu domowego z obsługą błędów"""
        try:
            home_path = Path.home()
            if home_path.exists() and home_path.is_dir():
                self.current_path = home_path
                self.load_directory()
            else:
                messagebox.showerror("Error", "Home directory not found or inaccessible")
        except Exception as e:
            messagebox.showerror("Error", f"Cannot access home directory: {e}")

    def on_path_enter(self, event):
        """Obsługa wprowadzania ścieżki z obsługą błędów"""
        try:
            new_path = Path(self.path_var.get().strip())
            
            # Rozwiń ścieżki użytkownika (~)
            if str(new_path).startswith('~'):
                new_path = new_path.expanduser()
            
            if new_path.exists() and new_path.is_dir():
                self.current_path = new_path
                self.load_directory()
            else:
                messagebox.showerror("Error", "Path does not exist or is not a directory")
                
        except Exception as e:
            messagebox.showerror("Error", f"Invalid path: {e}")

    def browse_directory(self):
        """Przeglądanie katalogów z obsługą błędów"""
        try:
            directory = filedialog.askdirectory(initialdir=str(self.current_path))
            if directory:
                new_path = Path(directory)
                if new_path.exists() and new_path.is_dir():
                    self.current_path = new_path
                    self.load_directory()
        except Exception as e:
            messagebox.showerror("Error", f"Cannot browse directory: {e}")

    def refresh_files(self):
        """Odświeża pliki"""
        self.load_directory()

    def find_large_files(self):
        """Znajduje duże pliki"""
        large_files = []
        try:
            for item in self.current_path.rglob('*'):
                if item.is_file():
                    try:
                        size = item.stat().st_size
                        if size > 100 * 1024 * 1024:  # 100 MB
                            large_files.append((item, size))
                    except (OSError, PermissionError):
                        continue
            
            if large_files:
                large_files.sort(key=lambda x: x[1], reverse=True)
                
                large_files_window = tk.Toplevel(self.root)
                large_files_window.title("Large Files (>100 MB)")
                large_files_window.geometry("700x500")
                large_files_window.configure(bg=self.colors['bg'])
                
                tree = ttk.Treeview(large_files_window, columns=('path', 'size'), show='headings')
                tree.heading('path', text='Path')
                tree.heading('size', text='Size')
                tree.column('path', width=500)
                tree.column('size', width=150)
                
                for file_path, size in large_files[:50]:
                    tree.insert('', 'end', values=(str(file_path), self.format_size(size)))
                
                tree.pack(fill='both', expand=True, padx=10, pady=10)
                
            else:
                messagebox.showinfo("Large Files", "No files larger than 100 MB found")
                
        except Exception as e:
            messagebox.showerror("Error", f"Error searching for large files: {e}")

    def toggle_hidden(self):
        """Przełącza ukryte pliki"""
        self.show_hidden = not self.show_hidden
        self.load_directory()

    def show_file_info(self):
        """Pokazuje informacje o pliku z obsługą .."""
        selection = self.files_tree.selection()
        if selection:
            item = self.files_tree.item(selection[0])
            values = item['values']
            
            if not values:
                messagebox.showwarning("Warning", "No file information available")
                return
                
            name = values[0]
        
            # SPECJALNA OBSŁUGA DLA ..
            if name == "..":
                parent_path = self.current_path.parent
                info_text = f"""
📋 Directory Information: Parent Directory

📍 Path: {parent_path}
📁 Type: Parent Directory
🔒 Permissions: drwxr-xr-x
💡 Description: Click to go up one directory level
                """
                messagebox.showinfo("Parent Directory", info_text)
                return
                
            file_path = self.current_path / name
        
            try:
                if file_path.exists():
                    stat = file_path.stat()
                    info_text = f"""
📋 File Information: {name}

📍 Path: {file_path}
📏 Size: {self.format_size(stat.st_size) if file_path.is_file() else 'N/A'}
📁 Type: {'File' if file_path.is_file() else 'Folder'}
🔒 Permissions: {self.get_permissions(stat.st_mode)}
📅 Modified: {datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d %H:%M:%S')}
📅 Created: {datetime.datetime.fromtimestamp(stat.st_ctime).strftime('%Y-%m-%d %H:%M:%S')}
👤 Owner: {stat.st_uid}
👥 Group: {stat.st_gid}
                    """
                    messagebox.showinfo("File Information", info_text)
                else:
                    messagebox.showerror("Error", "File no longer exists")
                    
            except Exception as e:
                messagebox.showerror("Error", f"Cannot read file info: {e}")
        else:
            messagebox.showwarning("Warning", "Please select a file or folder")

    def delete_selected(self):
        """Usuwa zaznaczony plik"""
        selection = self.files_tree.selection()
        if selection:
            items_to_delete = []
            for item in selection:
                item_values = self.files_tree.item(item)['values']
                name = item_values[0]
                # Nie pozwól usunąć ..
                if name == "..":
                    messagebox.showwarning("Warning", "Cannot delete parent directory")
                    continue
                items_to_delete.append((name, self.current_path / name))
            
            if not items_to_delete:
                return
                
            if len(items_to_delete) == 1:
                message = f"Are you sure you want to delete '{items_to_delete[0][0]}'?"
            else:
                message = f"Are you sure you want to delete {len(items_to_delete)} items?"
            
            if messagebox.askyesno("Confirm", message):
                try:
                    for name, file_path in items_to_delete:
                        if file_path.is_file():
                            file_path.unlink()
                        else:
                            shutil.rmtree(file_path)
                    self.load_directory()
                except Exception as e:
                    messagebox.showerror("Error", f"Cannot delete: {e}")
        else:
            messagebox.showwarning("Warning", "Please select a file or folder to delete")

    def sort_files(self, column):
        """Sortuje pliki z zachowaniem kolejności: .., katalogi, potem pliki"""
        if self.sort_column == column:
            self.sort_reverse = not self.sort_reverse
        else:
            self.sort_column = column
            self.sort_reverse = False
    
        # Pobierz wszystkie elementy z treeview
        all_items = []
        for item in self.files_tree.get_children():
            values = self.files_tree.item(item)['values']
            is_parent = values[0] == ".."  # Sprawdź czy to ..
            is_dir = values[2] == "📁 Folder" or values[2] == "📁 Parent Directory"  # Sprawdź czy to katalog
            all_items.append((item, values, is_parent, is_dir))
    
        # Podziel na .., katalogi i pliki
        parent_dir = [(item, values) for item, values, is_parent, is_dir in all_items if is_parent]
        directories = [(item, values) for item, values, is_parent, is_dir in all_items if not is_parent and is_dir]
        files = [(item, values) for item, values, is_parent, is_dir in all_items if not is_parent and not is_dir]
    
        # Sortuj katalogi (oprócz ..) według wybranej kolumny
        if column == 'name':
            directories.sort(key=lambda x: x[1][0].lower(), reverse=self.sort_reverse)
        elif column == 'size':
            directories.sort(key=lambda x: x[1][1], reverse=self.sort_reverse)
        elif column == 'modified':
            directories.sort(key=lambda x: x[1][3], reverse=self.sort_reverse)
        elif column == 'permissions':
            directories.sort(key=lambda x: x[1][4], reverse=self.sort_reverse)
        else:
            directories.sort(key=lambda x: x[1][0].lower(), reverse=self.sort_reverse)
    
        # Sortuj pliki według wybranej kolumny
        if column == 'name':
            files.sort(key=lambda x: x[1][0].lower(), reverse=self.sort_reverse)
        elif column == 'size':
            # Konwertuj rozmiar pliku na bajty dla poprawnego sortowania
            def parse_size(size_str):
                if size_str == "📁 DIR" or size_str == "📁 UP":
                    return 0
                size_map = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
                try:
                    num, unit = size_str.split()
                    num = float(num)
                    return num * size_map.get(unit, 1)
                except:
                    return 0
        
            files.sort(key=lambda x: parse_size(x[1][1]), reverse=self.sort_reverse)
        elif column == 'modified':
            files.sort(key=lambda x: x[1][3], reverse=self.sort_reverse)
        elif column == 'permissions':
            files.sort(key=lambda x: x[1][4], reverse=self.sort_reverse)
        else:
            files.sort(key=lambda x: x[1][0].lower(), reverse=self.sort_reverse)
    
        # Połącz posortowane listy (najpierw .., potem katalogi, potem pliki)
        sorted_items = parent_dir + directories + files
    
        # Wyczyść i dodaj posortowane elementy
        for item in self.files_tree.get_children():
            self.files_tree.delete(item)
    
        for item, values in sorted_items:
            # Określ tag na podstawie typu
            if values[0] == "..":
                tag = 'parent'
            elif values[2] == "📁 Folder" or values[2] == "📁 Parent Directory":
                tag = 'dir'
            else:
                tag = 'file'
            
            self.files_tree.insert('', 'end', values=values, tags=(tag,))

    # Metody dla zakładki Processes
    def update_processes_data(self):
        """Aktualizuje dane procesów"""
        try:
            # Pobierz wszystkie procesy
            processes = []
            total_cpu = 0
            status_count = {'running': 0, 'sleeping': 0, 'idle': 0, 'zombie': 0, 'other': 0}
            
            for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent', 
                                           'status', 'username', 'num_threads', 'create_time']):
                try:
                    process_info = proc.info
                    
                    # Konwertuj czas stworzenia
                    create_time = datetime.datetime.fromtimestamp(process_info['create_time']).strftime('%H:%M:%S') if process_info['create_time'] else 'N/A'
                    
                    processes.append({
                        'pid': process_info['pid'],
                        'name': process_info['name'],
                        'cpu': process_info['cpu_percent'] or 0,
                        'memory': process_info['memory_percent'] or 0,
                        'status': process_info['status'],
                        'user': process_info['username'] or 'N/A',
                        'threads': process_info['num_threads'] or 0,
                        'create_time': create_time
                    })
                    
                    total_cpu += process_info['cpu_percent'] or 0
                    
                    # Zlicz statusy
                    status = process_info['status'].lower()
                    if status in status_count:
                        status_count[status] += 1
                    else:
                        status_count['other'] += 1
                        
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
            
            # Posortuj procesy
            processes.sort(key=lambda x: x.get(self.process_sort_column, 0), 
                          reverse=self.process_sort_reverse)
            
            # Wyczyść i wypełnij tabelę
            for item in self.processes_tree.get_children():
                self.processes_tree.delete(item)
            
            for proc in processes:
                status = proc['status']
                status_color = self.get_status_color(status)
                
                self.processes_tree.insert('', 'end', 
                                         values=(proc['pid'],
                                                proc['name'][:30] + '...' if len(proc['name']) > 30 else proc['name'],
                                                f"{proc['cpu']:.1f}",
                                                f"{proc['memory']:.2f}",
                                                status,
                                                proc['user'][:15] if proc['user'] != 'N/A' else 'N/A',
                                                proc['threads'],
                                                proc['create_time']),
                                         tags=(status_color,))
            
            # Konfiguruj kolory statusów
            for status, color in [('running', 'running'), ('sleeping', 'sleeping'), 
                                ('idle', 'stopped'), ('zombie', 'zombie')]:
                self.processes_tree.tag_configure(color, foreground=self.colors[f'process_{color}'])
            
            # Aktualizuj statystyki
            self.total_processes_label.config(text=f"Total Processes: {len(processes)}")
            self.running_processes_label.config(text=f"Running: {status_count['running']}")
            self.sleeping_processes_label.config(text=f"Sleeping: {status_count['sleeping']}")
            self.cpu_usage_label.config(text=f"Total CPU: {total_cpu:.1f}%")
            
            self.process_status_label.config(text=f"Last updated: {datetime.datetime.now().strftime('%H:%M:%S')}")
            
        except Exception as e:
            self.process_status_label.config(text=f"Error: {str(e)}")

    def get_status_color(self, status):
        """Zwraca kolor dla statusu procesu"""
        status = status.lower()
        if status == 'running':
            return 'running'
        elif status in ['sleeping', 'waiting']:
            return 'sleeping'
        elif status in ['stopped', 'idle']:
            return 'stopped'
        elif status == 'zombie':
            return 'zombie'
        else:
            return 'sleeping'

    def sort_processes(self, column):
        """Sortuje procesy według wybranej kolumny"""
        if self.process_sort_column == column:
            self.process_sort_reverse = not self.process_sort_reverse
        else:
            self.process_sort_column = column
            self.process_sort_reverse = True
        
        self.update_processes_data()

    def on_process_search(self, event):
        """Filtruje procesy na podstawie wyszukiwania"""
        search_term = self.process_search_var.get().lower()
        
        if not search_term:
            # Pokaż wszystkie procesy jeśli wyszukiwanie jest puste
            for item in self.processes_tree.get_children():
                self.processes_tree.delete(item)
            self.update_processes_data()
            return
        
        # Filtruj widoczne procesy
        for item in self.processes_tree.get_children():
            values = self.processes_tree.item(item)['values']
            process_name = values[1].lower() if len(values) > 1 else ''
            pid = str(values[0]) if len(values) > 0 else ''
            
            if search_term in process_name or search_term in pid:
                self.processes_tree.item(item, tags=())
            else:
                self.processes_tree.item(item, tags=('hidden',))
        
        # Ukryj niepasujące wiersze
        self.processes_tree.tag_configure('hidden', foreground=self.colors['bg_light'])

    def on_process_double_click(self, event):
        """Obsługa podwójnego kliknięcia na proces"""
        selection = self.processes_tree.selection()
        if selection:
            self.show_process_details()

    def show_process_details(self):
        """Pokazuje szczegółowe informacje o wybranym procesie"""
        selection = self.processes_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a process first")
            return
        
        item = self.processes_tree.item(selection[0])
        pid = item['values'][0]
        
        try:
            process = psutil.Process(pid)
            with process.oneshot():
                info = process.as_dict(attrs=['name', 'cpu_percent', 'memory_percent', 
                                            'status', 'username', 'num_threads', 
                                            'create_time', 'memory_info', 'cpu_times',
                                            'io_counters', 'connections', 'open_files'])
                
                # Formatuj informacje
                details = f"""
📋 PROCESS DETAILS: {info['name']} (PID: {pid})

👤 User: {info['username']}
📊 Status: {info['status']}
🧵 Threads: {info['num_threads']}
⏰ Created: {datetime.datetime.fromtimestamp(info['create_time']).strftime('%Y-%m-%d %H:%M:%S')}

💻 CPU:
  Usage: {info['cpu_percent']:.1f}%
  User Time: {info['cpu_times'].user:.2f}s
  System Time: {info['cpu_times'].system:.2f}s

💾 Memory:
  Usage: {info['memory_percent']:.2f}%
  RSS: {info['memory_info'].rss / 1024 / 1024:.1f} MB
  VMS: {info['memory_info'].vms / 1024 / 1024:.1f} MB

📁 I/O:
  Read Bytes: {info['io_counters'].read_bytes / 1024 / 1024:.1f} MB
  Write Bytes: {info['io_counters'].write_bytes / 1024 / 1024:.1f} MB

🌐 Network:
  Connections: {len(info['connections'])}
  Open Files: {len(info['open_files'])}
                """
                
                messagebox.showinfo(f"Process Details - {info['name']}", details)
                
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            messagebox.showerror("Error", f"Cannot access process details: {e}")

    def stop_process(self):
        """Zatrzymuje wybrany proces"""
        selection = self.processes_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a process first")
            return
        
        item = self.processes_tree.item(selection[0])
        pid = item['values'][0]
        name = item['values'][1]
        
        if messagebox.askyesno("Confirm Stop", f"Are you sure you want to stop process:\n{name} (PID: {pid})?"):
            try:
                process = psutil.Process(pid)
                process.suspend()
                messagebox.showinfo("Success", f"Process {name} stopped successfully")
                self.update_processes_data()
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                messagebox.showerror("Error", f"Cannot stop process: {e}")

    def kill_process(self):
        """Zabija wybrany proces"""
        selection = self.processes_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a process first")
            return
        
        item = self.processes_tree.item(selection[0])
        pid = item['values'][0]
        name = item['values'][1]
        
        if messagebox.askyesno("Confirm Kill", f"Are you sure you want to KILL process:\n{name} (PID: {pid})?\n\nThis action cannot be undone!"):
            try:
                process = psutil.Process(pid)
                process.terminate()
                messagebox.showinfo("Success", f"Process {name} killed successfully")
                self.update_processes_data()
            except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
                messagebox.showerror("Error", f"Cannot kill process: {e}")

    def search_processes(self):
        """Otwiera okno wyszukiwania procesów"""
        search_term = self.process_search_var.get()
        if search_term:
            messagebox.showinfo("Search", f"Searching for: {search_term}")
        else:
            messagebox.showinfo("Search", "Enter search term in the field above")

    def show_process_resources(self):
        """Pokazuje wykorzystanie zasobów przez procesy"""
        selection = self.processes_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a process first")
            return
        
        item = self.processes_tree.item(selection[0])
        pid = item['values'][0]
        name = item['values'][1]
        
        try:
            process = psutil.Process(pid)
            memory_mb = process.memory_info().rss / 1024 / 1024
            cpu_percent = process.cpu_percent()
            
            resources_info = f"""
📊 RESOURCE USAGE: {name} (PID: {pid})

💻 CPU Usage: {cpu_percent:.1f}%
💾 Memory Usage: {memory_mb:.1f} MB
🎯 Status: {process.status()}
            """
            
            messagebox.showinfo("Resource Usage", resources_info)
            
        except (psutil.NoSuchProcess, psutil.AccessDenied) as e:
            messagebox.showerror("Error", f"Cannot get resource usage: {e}")

    # Metody dla zakładki Temperature
    def update_temperature_data(self):
        """Aktualizuje dane temperatury z czujników"""
        try:
            # Sprawdź czy sensors jest dostępne
            result = subprocess.run(['which', 'sensors'], capture_output=True, text=True)
            if result.returncode != 0:
                self.sensors_status_label.config(text="❌ lm-sensors not installed. Click 'Install lm-sensors' to install.")
                self.clear_temperature_data()
                return
            
            # Pobierz dane z czujników
            sensors_result = subprocess.run(['sensors'], capture_output=True, text=True)
            
            if sensors_result.returncode != 0:
                self.sensors_status_label.config(text="❌ Error reading sensors. Try running 'sudo sensors-detect' first.")
                self.clear_temperature_data()
                return
            
            sensors_output = sensors_result.stdout
            self.parse_sensors_data(sensors_output)
            
            # Aktualizuj status
            if self.auto_refresh_temp:
                status_text = f"✅ Auto refresh enabled - Last updated: {datetime.datetime.now().strftime('%H:%M:%S')}"
            else:
                status_text = f"✅ Last updated: {datetime.datetime.now().strftime('%H:%M:%S')}"
            self.sensors_status_label.config(text=status_text)
            
        except Exception as e:
            error_text = f"❌ Error: {str(e)}"
            if self.auto_refresh_temp:
                error_text += " - Auto refresh continues"
            self.sensors_status_label.config(text=error_text)
            self.clear_temperature_data()

    def parse_sensors_data(self, sensors_output):
        """Parsuje output z czujników i wyświetla w tabeli"""
        # Wyczyść poprzednie dane
        for item in self.temp_tree.get_children():
            self.temp_tree.delete(item)
        
        # Wyświetl surowy output
        self.sensors_output.delete(1.0, tk.END)
        self.sensors_output.insert(1.0, sensors_output)
        
        lines = sensors_output.split('\n')
        current_adapter = ""
        sensor_count = 0
        
        for line in lines:
            line = line.strip()
            
            # Pomiń puste linie
            if not line:
                continue
                
            # Sprawdź czy to nowy adapter
            if line.startswith('Adapter:'):
                current_adapter = line
                continue
                
            # Parsuj linię z temperaturą
            if ':' in line and ('°C' in line or '°F' in line):
                parts = line.split(':')
                if len(parts) >= 2:
                    sensor_name = parts[0].strip()
                    temp_data = parts[1].strip()
                    
                    # Ekstraktuj wartości temperatur
                    current_temp = self.extract_temperature_value(temp_data, 'current')
                    high_temp = self.extract_temperature_value(temp_data, 'high')
                    crit_temp = self.extract_temperature_value(temp_data, 'crit')
                    
                    # Określ status na podstawie temperatury
                    status, status_color = self.get_temperature_status(current_temp, high_temp, crit_temp)
                    
                    # Dodaj do tabeli
                    full_sensor_name = f"{sensor_name}"
                    if current_adapter:
                        full_sensor_name += f" ({current_adapter})"
                    
                    self.temp_tree.insert('', 'end', 
                                        values=(full_sensor_name,
                                               f"{current_temp:.1f}" if current_temp is not None else "N/A",
                                               f"{high_temp:.1f}" if high_temp is not None else "N/A",
                                               f"{crit_temp:.1f}" if crit_temp is not None else "N/A",
                                               status),
                                        tags=(status_color,))
                    sensor_count += 1
        
        # Konfiguruj kolory statusów
        self.temp_tree.tag_configure('cool', foreground=self.colors['temp_cool'])
        self.temp_tree.tag_configure('warm', foreground=self.colors['temp_warm'])
        self.temp_tree.tag_configure('hot', foreground=self.colors['temp_hot'])
        self.temp_tree.tag_configure('critical', foreground=self.colors['temp_critical'])
        
        # Aktualizuj status
        if sensor_count > 0:
            base_text = f"✅ Found {sensor_count} temperature sensors"
            if self.auto_refresh_temp:
                self.sensors_status_label.config(text=f"{base_text} - Auto refresh enabled - Last updated: {datetime.datetime.now().strftime('%H:%M:%S')}")
            else:
                self.sensors_status_label.config(text=f"{base_text} - Last updated: {datetime.datetime.now().strftime('%H:%M:%S')}")
        else:
            self.sensors_status_label.config(text="⚠️ No temperature sensors found. Try running 'sudo sensors-detect'")

    def extract_temperature_value(self, temp_data, temp_type):
        """Ekstraktuje wartość temperatury z tekstu"""
        try:
            # JAWNY IMPORT W FUNKCJI
            import re
            
            if temp_type == 'current':
                # Szukaj wzorca: +XX.X°C (np.: +45.0°C)
                match = re.search(r'([+-]?\d+\.\d+)°C', temp_data)
                if match:
                    return float(match.group(1))
                
                # Alternatywny wzorzec
                match = re.search(r'(\d+\.\d+)°C', temp_data)
                if match:
                    return float(match.group(1))
                    
            elif temp_type == 'high':
                # Szukaj high temp (high = +YY.Y°C)
                match = re.search(r'high\s*=\s*([+-]?\d+\.\d+)', temp_data)
                if match:
                    return float(match.group(1))
                    
            elif temp_type == 'crit':
                # Szukaj critical temp (crit = +ZZ.Z°C)
                match = re.search(r'crit\s*=\s*([+-]?\d+\.\d+)', temp_data)
                if match:
                    return float(match.group(1))
                
        except (ValueError, AttributeError):
            pass
        
        return None

    def get_temperature_status(self, current_temp, high_temp, crit_temp):
        """Określa status temperatury na podstawie wartości"""
        if current_temp is None:
            return "Unknown", "cool"
        
        if crit_temp and current_temp >= crit_temp:
            return "CRITICAL", "critical"
        elif high_temp and current_temp >= high_temp:
            return "HIGH", "hot"
        elif current_temp > 60:
            return "WARM", "warm"
        else:
            return "NORMAL", "cool"

    def clear_temperature_data(self):
        """Czyści dane temperatury"""
        for item in self.temp_tree.get_children():
            self.temp_tree.delete(item)
        
        self.sensors_output.delete(1.0, tk.END)
        self.sensors_output.insert(1.0, "No sensor data available.\n\nPlease install lm-sensors package and run 'sudo sensors-detect' to configure sensors.")

    def install_lm_sensors(self):
        """Instaluje pakiet lm-sensors"""
        try:
            result = messagebox.askyesno("Install lm-sensors", 
                                       "This will install lm-sensors package using your system's package manager.\n\nDo you want to continue?")
            if not result:
                return
            
            self.sensors_status_label.config(text="🔄 Installing lm-sensors...")
            self.root.update()
            
            # Sprawdź menadżer pakietów
            for pkg_manager in ['apt-get', 'dnf', 'yum', 'pacman', 'zypper']:
                if subprocess.run(['which', pkg_manager], capture_output=True).returncode == 0:
                    if pkg_manager in ['apt-get', 'apt']:
                        cmd = ['sudo', 'apt-get', 'update', '&&', 'sudo', 'apt-get', 'install', '-y', 'lm-sensors']
                    elif pkg_manager in ['dnf', 'yum']:
                        cmd = ['sudo', pkg_manager, 'install', '-y', 'lm-sensors']
                    elif pkg_manager == 'pacman':
                        cmd = ['sudo', 'pacman', '-S', '--noconfirm', 'lm_sensors']
                    elif pkg_manager == 'zypper':
                        cmd = ['sudo', 'zypper', 'install', '-y', 'sensors']
                    
                    # Uruchom instalację
                    process = subprocess.run(' '.join(cmd), shell=True, capture_output=True, text=True)
                    
                    if process.returncode == 0:
                        messagebox.showinfo("Success", "lm-sensors installed successfully!\n\nNow run 'Detect Sensors' to configure sensors.")
                        self.sensors_status_label.config(text="✅ lm-sensors installed. Click 'Detect Sensors' to configure.")
                    else:
                        messagebox.showerror("Error", f"Failed to install lm-sensors:\n{process.stderr}")
                        self.sensors_status_label.config(text="❌ Installation failed")
                    return
            
            messagebox.showerror("Error", "Could not determine package manager")
            self.sensors_status_label.config(text="❌ Unknown package manager")
            
        except Exception as e:
            messagebox.showerror("Error", f"Installation failed: {str(e)}")
            self.sensors_status_label.config(text="❌ Installation error")

    def detect_sensors(self):
        """Uruchamia sensors-detect do konfiguracji czujników"""
        try:
            result = messagebox.askyesno("Detect Sensors", 
                                       "This will run 'sensors-detect' to configure your hardware sensors.\n\nIt may ask for sudo password and require answering questions about your hardware.\n\nDo you want to continue?")
            if not result:
                return
            
            self.sensors_status_label.config(text="🔄 Detecting sensors...")
            self.root.update()
            
            # Uruchom sensors-detect z automatycznymi odpowiedziami (yes)
            process = subprocess.run(['sudo', 'sensors-detect', '--auto'], 
                                   capture_output=True, text=True)
            
            if process.returncode == 0:
                messagebox.showinfo("Success", "Sensors detection completed!\n\nYou may need to reload modules or restart the system.")
                self.sensors_status_label.config(text="✅ Sensors detection completed. Refreshing data...")
                self.update_temperature_data()
            else:
                messagebox.showerror("Error", f"Sensors detection failed:\n{process.stderr}")
                self.sensors_status_label.config(text="❌ Detection failed")
                
        except Exception as e:
            messagebox.showerror("Error", f"Sensors detection failed: {str(e)}")
            self.sensors_status_label.config(text="❌ Detection error")

def main():
    root = tk.Tk()
    app = ModernSystemMonitorApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()