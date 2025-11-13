import tkinter as tk
from tkinter import ttk
import psutil
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import threading
import time
from collections import deque

class NetworkMonitor:
    def __init__(self, parent_frame, colors):
        self.parent_frame = parent_frame
        self.colors = colors
        self.setup_network_tab()
        
        # Dane historyczne dla wykresów
        self.sent_history = deque(maxlen=60)
        self.recv_history = deque(maxlen=60)
        self.timestamps = deque(maxlen=60)
        
        # Poprzednie wartości do obliczania prędkości
        self.prev_sent = 0
        self.prev_recv = 0
        self.prev_time = time.time()
        
        # Uruchom monitoring sieci
        self.update_network_data()

    def setup_network_tab(self):
        """Konfiguruje zakładkę Network"""
        main_frame = ttk.Frame(self.parent_frame, style='Modern.TFrame', padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Nagłówek
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(header_frame, 
                               text="Network Monitor", 
                               style='Modern.TLabel',
                               font=('Arial', 18, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Statystyki sieciowe
        stats_frame = ttk.LabelFrame(main_frame, text="📊 Network Statistics", style='Modern.TLabelframe', padding="15")
        stats_frame.pack(fill='x', pady=(0, 20))
        
        # Ramka dla statystyk
        stats_grid = ttk.Frame(stats_frame, style='Modern.TFrame')
        stats_grid.pack(fill='x')
        
        self.download_label = ttk.Label(stats_grid, 
                                      text="Download: -- MB/s", 
                                      style='Modern.TLabel',
                                      font=('Arial', 10))
        self.download_label.grid(row=0, column=0, sticky='w', padx=(0, 20))
        
        self.upload_label = ttk.Label(stats_grid, 
                                    text="Upload: -- MB/s", 
                                    style='Modern.TLabel',
                                    font=('Arial', 10))
        self.upload_label.grid(row=0, column=1, sticky='w', padx=(0, 20))
        
        self.total_download_label = ttk.Label(stats_grid, 
                                            text="Total Downloaded: -- GB", 
                                            style='Modern.TLabel',
                                            font=('Arial', 10))
        self.total_download_label.grid(row=0, column=2, sticky='w', padx=(0, 20))
        
        self.total_upload_label = ttk.Label(stats_grid, 
                                          text="Total Uploaded: -- GB", 
                                          style='Modern.TLabel',
                                          font=('Arial', 10))
        self.total_upload_label.grid(row=0, column=3, sticky='w')
        
        # Wykresy sieciowe
        charts_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        charts_frame.pack(fill='both', expand=True, pady=(0, 20))
        
        # Wykres prędkości sieci
        speed_frame = ttk.LabelFrame(charts_frame, text="📈 Network Speed", style='Modern.TLabelframe', padding="15")
        speed_frame.pack(fill='both', expand=True, side=tk.LEFT, padx=(0, 10))
        
        self.fig_speed = Figure(figsize=(8, 4), dpi=100, facecolor=self.colors['bg'])
        self.ax_speed = self.fig_speed.add_subplot(111)
        self.ax_speed.set_facecolor(self.colors['bg_light'])
        self.canvas_speed = FigureCanvasTkAgg(self.fig_speed, speed_frame)
        self.canvas_speed.get_tk_widget().pack(fill='both', expand=True)
        
        # Wykres wykorzystania interfejsów
        interfaces_frame = ttk.LabelFrame(charts_frame, text="🔌 Network Interfaces", style='Modern.TLabelframe', padding="15")
        interfaces_frame.pack(fill='both', expand=True, side=tk.RIGHT, padx=(10, 0))
        
        self.fig_interfaces = Figure(figsize=(8, 4), dpi=100, facecolor=self.colors['bg'])
        self.ax_interfaces = self.fig_interfaces.add_subplot(111)
        self.ax_interfaces.set_facecolor(self.colors['bg_light'])
        self.canvas_interfaces = FigureCanvasTkAgg(self.fig_interfaces, interfaces_frame)
        self.canvas_interfaces.get_tk_widget().pack(fill='both', expand=True)
        
        # Lista interfejsów sieciowych
        interfaces_list_frame = ttk.LabelFrame(main_frame, text="🌐 Network Interfaces", style='Modern.TLabelframe', padding="10")
        interfaces_list_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        columns = ('interface', 'ip', 'netmask', 'broadcast', 'speed', 'status')
        self.interfaces_tree = ttk.Treeview(interfaces_list_frame, columns=columns, show='headings', height=8)
        
        # Nagłówki
        interface_headers = [
            ('interface', 'Interface', 120),
            ('ip', 'IP Address', 150),
            ('netmask', 'Netmask', 120),
            ('broadcast', 'Broadcast', 120),
            ('speed', 'Speed', 100),
            ('status', 'Status', 100)
        ]
        
        for col, text, width in interface_headers:
            self.interfaces_tree.heading(col, text=text)
            self.interfaces_tree.column(col, width=width, anchor='center')
        
        self.interfaces_tree.pack(fill='both', expand=True, side=tk.LEFT)
        
        # Pasek przewijania
        scrollbar_interfaces = ttk.Scrollbar(interfaces_list_frame, orient=tk.VERTICAL, command=self.interfaces_tree.yview)
        self.interfaces_tree.configure(yscrollcommand=scrollbar_interfaces.set)
        scrollbar_interfaces.pack(side=tk.RIGHT, fill='y')
        
        # Przyciski akcji
        action_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        action_frame.pack(fill='x', pady=(0, 10))
        
        action_buttons = [
            ("🔄 Refresh", self.refresh_network_data),
            ("📊 Details", self.show_network_details),
            ("🔍 Connections", self.show_network_connections),
            ("⚙️ Settings", self.show_network_settings)
        ]
        
        for i, (text, command) in enumerate(action_buttons):
            btn = ttk.Button(action_frame, text=text, style='Modern.TButton', command=command)
            btn.grid(row=0, column=i, padx=2)
        
        # Pasek statusu
        self.network_status_label = ttk.Label(main_frame, text="Monitoring network traffic...", style='Modern.TLabel')
        self.network_status_label.pack(fill='x')
        
        # Inicjalizacja danych
        self.refresh_network_data()

    def update_network_data(self):
        """Aktualizuje dane sieciowe"""
        try:
            # Pobierz aktualne statystyki sieciowe
            net_io = psutil.net_io_counters()
            current_time = time.time()
            time_diff = current_time - self.prev_time
            
            if time_diff > 0:
                # Oblicz prędkości w MB/s
                sent_speed = (net_io.bytes_sent - self.prev_sent) / time_diff / 1024 / 1024
                recv_speed = (net_io.bytes_recv - self.prev_recv) / time_diff / 1024 / 1024
                
                # Aktualizuj etykiety
                self.download_label.config(text=f"Download: {recv_speed:.2f} MB/s")
                self.upload_label.config(text=f"Upload: {sent_speed:.2f} MB/s")
                self.total_download_label.config(text=f"Total Downloaded: {net_io.bytes_recv / 1024 / 1024 / 1024:.2f} GB")
                self.total_upload_label.config(text=f"Total Uploaded: {net_io.bytes_sent / 1024 / 1024 / 1024:.2f} GB")
                
                # Dodaj dane do historii
                self.sent_history.append(sent_speed)
                self.recv_history.append(recv_speed)
                self.timestamps.append(current_time)
                
                # Zaktualizuj wykresy
                self.update_speed_chart()
                self.update_interfaces_chart()
                
                # Zapisz poprzednie wartości
                self.prev_sent = net_io.bytes_sent
                self.prev_recv = net_io.bytes_recv
                self.prev_time = current_time
            
            # Aktualizuj status
            self.network_status_label.config(text=f"Last updated: {time.strftime('%H:%M:%S')} | Interfaces: {len(psutil.net_if_addrs())}")
            
        except Exception as e:
            self.network_status_label.config(text=f"Error: {str(e)}")
        
        # Zaplanuj kolejną aktualizację
        self.parent_frame.after(1000, self.update_network_data)

    def update_speed_chart(self):
        """Aktualizuje wykres prędkości sieci"""
        self.ax_speed.clear()
        
        if len(self.timestamps) > 1:
            # Konwertuj timestampy na względny czas
            relative_times = [t - self.timestamps[0] for t in self.timestamps]
            
            # Rysuj wykresy
            self.ax_speed.plot(relative_times, self.sent_history, label='Upload', color=self.colors['danger'], linewidth=2)
            self.ax_speed.plot(relative_times, self.recv_history, label='Download', color=self.colors['success'], linewidth=2)
            
            self.ax_speed.set_xlabel('Time (seconds)', color=self.colors['text'])
            self.ax_speed.set_ylabel('Speed (MB/s)', color=self.colors['text'])
            self.ax_speed.set_title('Network Speed Over Time', color=self.colors['text'], pad=20)
            self.ax_speed.legend()
            self.ax_speed.grid(True, alpha=0.3, color=self.colors['text_secondary'])
            self.ax_speed.tick_params(colors=self.colors['text_secondary'])
            
            # Automatyczne skalowanie osi Y
            max_speed = max(max(self.sent_history) if self.sent_history else 0, 
                           max(self.recv_history) if self.recv_history else 0)
            self.ax_speed.set_ylim(0, max(1, max_speed * 1.1))
        
        self.canvas_speed.draw()

    def update_interfaces_chart(self):
        """Aktualizuje wykres interfejsów sieciowych"""
        self.ax_interfaces.clear()
        
        try:
            interfaces = psutil.net_io_counters(pernic=True)
            interface_names = []
            sent_speeds = []
            recv_speeds = []
            
            for interface, stats in interfaces.items():
                if interface not in ['lo', 'loopback']:  # Pomiń interfejs pętli zwrotnej
                    interface_names.append(interface)
                    # Przybliżona prędkość (w MB/s) - w prawdziwej aplikacji potrzebowalibyśmy historii per interfejs
                    sent_speeds.append(stats.bytes_sent / 1024 / 1024)
                    recv_speeds.append(stats.bytes_recv / 1024 / 1024)
            
            if interface_names:
                x = range(len(interface_names))
                width = 0.35
                
                bars_sent = self.ax_interfaces.bar([i - width/2 for i in x], sent_speeds, width, 
                                                 label='Sent', color=self.colors['danger'], alpha=0.7)
                bars_recv = self.ax_interfaces.bar([i + width/2 for i in x], recv_speeds, width, 
                                                 label='Received', color=self.colors['success'], alpha=0.7)
                
                self.ax_interfaces.set_xlabel('Network Interfaces', color=self.colors['text'])
                self.ax_interfaces.set_ylabel('Total Data (MB)', color=self.colors['text'])
                self.ax_interfaces.set_title('Network Interface Usage', color=self.colors['text'], pad=20)
                self.ax_interfaces.set_xticks(x)
                self.ax_interfaces.set_xticklabels(interface_names, rotation=45, ha='right')
                self.ax_interfaces.legend()
                self.ax_interfaces.grid(True, alpha=0.3, color=self.colors['text_secondary'])
                self.ax_interfaces.tick_params(colors=self.colors['text_secondary'])
        
        except Exception as e:
            self.ax_interfaces.text(0.5, 0.5, 'Error loading interface data', 
                                  ha='center', va='center', transform=self.ax_interfaces.transAxes,
                                  color=self.colors['text'])
        
        self.canvas_interfaces.draw()

    def refresh_network_data(self):
        """Odświeża listę interfejsów sieciowych"""
        try:
            # Wyczyść poprzednie dane
            for item in self.interfaces_tree.get_children():
                self.interfaces_tree.delete(item)
            
            # Pobierz informacje o interfejsach
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            io_counters = psutil.net_io_counters(pernic=True)
            
            for interface, addresses in interfaces.items():
                # Znajdź adres IPv4
                ip_address = "N/A"
                netmask = "N/A"
                broadcast = "N/A"
                
                for addr in addresses:
                    if addr.family == 2:  # IPv4
                        ip_address = addr.address
                        netmask = addr.netmask
                        broadcast = addr.broadcast
                        break
                
                # Pobierz statystyki interfejsu
                interface_stats = stats.get(interface, None)
                speed = "N/A"
                status = "Down"
                
                if interface_stats:
                    speed = f"{interface_stats.speed} Mbps" if interface_stats.speed > 0 else "Unknown"
                    status = "Up" if interface_stats.isup else "Down"
                
                # Określ kolor statusu
                tags = ('up',) if status == "Up" else ('down',)
                
                self.interfaces_tree.insert('', 'end', 
                                          values=(interface, ip_address, netmask, broadcast, speed, status),
                                          tags=tags)
            
            # Konfiguruj kolory statusów
            self.interfaces_tree.tag_configure('up', foreground=self.colors['success'])
            self.interfaces_tree.tag_configure('down', foreground=self.colors['danger'])
            
        except Exception as e:
            self.network_status_label.config(text=f"Error refreshing interfaces: {str(e)}")

    def show_network_details(self):
        """Pokazuje szczegółowe informacje o sieci"""
        try:
            # Pobierz statystyki sieciowe
            net_io = psutil.net_io_counters()
            connections = psutil.net_connections()
            
            # Grupuj połączenia według statusu
            connection_stats = {}
            for conn in connections:
                status = conn.status
                connection_stats[status] = connection_stats.get(status, 0) + 1
            
            details = f"""
🌐 NETWORK DETAILS:

📊 Traffic Statistics:
  Bytes Sent: {net_io.bytes_sent / 1024 / 1024:.2f} MB
  Bytes Received: {net_io.bytes_recv / 1024 / 1024:.2f} MB
  Packets Sent: {net_io.packets_sent}
  Packets Received: {net_io.packets_recv}
  Errors In: {net_io.errin}
  Errors Out: {net_io.errout}
  Drops In: {net_io.dropin}
  Drops Out: {net_io.dropout}

🔌 Connections:
  Total Connections: {len(connections)}
"""
            # Dodaj statystyki połączeń
            for status, count in connection_stats.items():
                details += f"  {status}: {count}\n"
            
            # Informacje o interfejsach
            interfaces = psutil.net_if_addrs()
            details += f"\n📡 Network Interfaces: {len(interfaces)}"
            
            # Pokaż okno dialogowe
            import tkinter.messagebox as messagebox
            messagebox.showinfo("Network Details", details)
            
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", f"Cannot get network details: {e}")

    def show_network_connections(self):
        """Pokazuje aktywne połączenia sieciowe"""
        try:
            connections = psutil.net_connections()
            
            # Utwórz nowe okno dla połączeń
            connections_window = tk.Toplevel(self.parent_frame)
            connections_window.title("Network Connections")
            connections_window.geometry("800x600")
            connections_window.configure(bg=self.colors['bg'])
            
            # Ramka z połączeniami
            conn_frame = ttk.Frame(connections_window, style='Modern.TFrame', padding="10")
            conn_frame.pack(fill='both', expand=True)
            
            # Tabela połączeń
            columns = ('pid', 'laddr', 'raddr', 'status', 'family', 'type')
            conn_tree = ttk.Treeview(conn_frame, columns=columns, show='headings', height=20)
            
            # Nagłówki
            conn_headers = [
                ('pid', 'PID', 80),
                ('laddr', 'Local Address', 200),
                ('raddr', 'Remote Address', 200),
                ('status', 'Status', 100),
                ('family', 'Family', 80),
                ('type', 'Type', 80)
            ]
            
            for col, text, width in conn_headers:
                conn_tree.heading(col, text=text)
                conn_tree.column(col, width=width, anchor='center')
            
            conn_tree.pack(fill='both', expand=True, side=tk.LEFT)
            
            # Pasek przewijania
            scrollbar_conn = ttk.Scrollbar(conn_frame, orient=tk.VERTICAL, command=conn_tree.yview)
            conn_tree.configure(yscrollcommand=scrollbar_conn.set)
            scrollbar_conn.pack(side=tk.RIGHT, fill='y')
            
            # Wypełnij danymi
            for conn in connections:
                try:
                    laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
                    raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                    
                    # Konwertuj rodzinę adresów
                    family = "IPv4" if conn.family == 2 else "IPv6" if conn.family == 10 else "Other"
                    
                    # Konwertuj typ
                    type_map = {1: "TCP", 2: "UDP", 3: "Other"}
                    conn_type = type_map.get(conn.type, "Unknown")
                    
                    conn_tree.insert('', 'end', 
                                   values=(conn.pid or "N/A", laddr, raddr, conn.status, family, conn_type))
                except:
                    continue
            
            # Przycisk odświeżania
            refresh_btn = ttk.Button(connections_window, text="🔄 Refresh", 
                                   style='Modern.TButton',
                                   command=lambda: self.refresh_connections(conn_tree))
            refresh_btn.pack(pady=10)
            
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", f"Cannot show network connections: {e}")

    def refresh_connections(self, tree):
        """Odświeża listę połączeń sieciowych"""
        try:
            # Wyczyść poprzednie dane
            for item in tree.get_children():
                tree.delete(item)
            
            # Pobierz nowe połączenia
            connections = psutil.net_connections()
            
            # Wypełnij danymi
            for conn in connections:
                try:
                    laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
                    raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
                    
                    family = "IPv4" if conn.family == 2 else "IPv6" if conn.family == 10 else "Other"
                    type_map = {1: "TCP", 2: "UDP", 3: "Other"}
                    conn_type = type_map.get(conn.type, "Unknown")
                    
                    tree.insert('', 'end', 
                              values=(conn.pid or "N/A", laddr, raddr, conn.status, family, conn_type))
                except:
                    continue
                    
        except Exception as e:
            import tkinter.messagebox as messagebox
            messagebox.showerror("Error", f"Cannot refresh connections: {e}")

    def show_network_settings(self):
        """Pokazuje ustawienia sieci"""
        import tkinter.messagebox as messagebox
        messagebox.showinfo("Network Settings", 
                          "Network settings panel coming soon!\n\n"
                          "Current features:\n"
                          "- Real-time network speed monitoring\n"
                          "- Interface statistics\n"
                          "- Connection monitoring\n"
                          "- Historical data charts")
