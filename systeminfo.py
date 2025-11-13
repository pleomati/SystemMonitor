import tkinter as tk
from tkinter import ttk
import platform
import psutil
import socket
import subprocess
import re
import os
from pathlib import Path

class SystemInfoTab:
    def __init__(self, parent, colors):
        self.parent = parent
        self.colors = colors
        self.create_widgets()
        
    def create_widgets(self):
        """Tworzy interfejs zakładki System Info"""
        main_frame = ttk.Frame(self.parent, style='Modern.TFrame', padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Nagłówek
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(header_frame, 
                               text="System Information", 
                               style='Modern.TLabel',
                               font=('Arial', 18, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Przyciski akcji
        button_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        button_frame.pack(fill='x', pady=(0, 15))
        
        ttk.Button(button_frame, 
                  text="🔄 Refresh", 
                  style='Modern.TButton',
                  command=self.refresh_info).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(button_frame, 
                  text="📋 Copy to Clipboard", 
                  style='Modern.TButton',
                  command=self.copy_to_clipboard).pack(side=tk.LEFT, padx=2)
        
        ttk.Button(button_frame, 
                  text="💾 Save to File", 
                  style='Modern.TButton',
                  command=self.save_to_file).pack(side=tk.LEFT, padx=2)
        
        # Ramka z informacjami systemowymi
        info_frame = ttk.LabelFrame(main_frame, text="📊 System Information", 
                                   style='Modern.TLabelframe', padding="15")
        info_frame.pack(fill='both', expand=True)
        
        # Tworzenie notebooka dla kategorii
        self.notebook = ttk.Notebook(info_frame, style='Modern.TNotebook')
        self.notebook.pack(fill='both', expand=True, padx=5, pady=5)
        
        # Tworzenie zakładek
        self.system_tab = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.cpu_tab = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.memory_tab = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.disk_tab = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.network_tab = ttk.Frame(self.notebook, style='Modern.TFrame')
        self.graphics_tab = ttk.Frame(self.notebook, style='Modern.TFrame')
        
        self.notebook.add(self.system_tab, text='💻 System')
        self.notebook.add(self.cpu_tab, text='🖥️ CPU')
        self.notebook.add(self.memory_tab, text='💾 Memory')
        self.notebook.add(self.disk_tab, text='💽 Disk')
        self.notebook.add(self.network_tab, text='🌐 Network')
        self.notebook.add(self.graphics_tab, text='🎮 Graphics')
        
        # Tworzenie zawartości zakładek
        self.create_system_tab()
        self.create_cpu_tab()
        self.create_memory_tab()
        self.create_disk_tab()
        self.create_network_tab()
        self.create_graphics_tab()
        
        # Pasek statusu
        self.status_label = ttk.Label(main_frame, text="Ready", style='Modern.TLabel')
        self.status_label.pack(fill='x', pady=(5, 0))
        
        # Załaduj dane
        self.refresh_info()
    
    def create_system_tab(self):
        """Tworzy zakładkę informacji systemowych"""
        # Ramka z przewijaniem
        canvas = tk.Canvas(self.system_tab, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.system_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Modern.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # System Information
        system_info_frame = ttk.LabelFrame(scrollable_frame, text="System", 
                                         style='Modern.TLabelframe', padding="10")
        system_info_frame.pack(fill='x', pady=5, padx=5)
        
        self.system_info_text = tk.Text(system_info_frame, 
                                      height=8, 
                                      bg=self.colors['bg_light'], 
                                      fg=self.colors['text'],
                                      font=('Courier', 9),
                                      wrap=tk.WORD,
                                      relief='flat')
        self.system_info_text.pack(fill='both', expand=True)
        
        # Machine Information
        machine_info_frame = ttk.LabelFrame(scrollable_frame, text="Machine", 
                                          style='Modern.TLabelframe', padding="10")
        machine_info_frame.pack(fill='x', pady=5, padx=5)
        
        self.machine_info_text = tk.Text(machine_info_frame, 
                                       height=6, 
                                       bg=self.colors['bg_light'], 
                                       fg=self.colors['text'],
                                       font=('Courier', 9),
                                       wrap=tk.WORD,
                                      relief='flat')
        self.machine_info_text.pack(fill='both', expand=True)
        
        # Battery Information
        battery_info_frame = ttk.LabelFrame(scrollable_frame, text="Battery", 
                                          style='Modern.TLabelframe', padding="10")
        battery_info_frame.pack(fill='x', pady=5, padx=5)
        
        self.battery_info_text = tk.Text(battery_info_frame, 
                                       height=4, 
                                       bg=self.colors['bg_light'], 
                                       fg=self.colors['text'],
                                       font=('Courier', 9),
                                       wrap=tk.WORD,
                                       relief='flat')
        self.battery_info_text.pack(fill='both', expand=True)
    
    def create_cpu_tab(self):
        """Tworzy zakładkę informacji o CPU"""
        canvas = tk.Canvas(self.cpu_tab, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.cpu_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Modern.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # CPU Information
        cpu_info_frame = ttk.LabelFrame(scrollable_frame, text="CPU Details", 
                                      style='Modern.TLabelframe', padding="10")
        cpu_info_frame.pack(fill='x', pady=5, padx=5)
        
        self.cpu_info_text = tk.Text(cpu_info_frame, 
                                   height=12, 
                                   bg=self.colors['bg_light'], 
                                   fg=self.colors['text'],
                                   font=('Courier', 9),
                                   wrap=tk.WORD,
                                   relief='flat')
        self.cpu_info_text.pack(fill='both', expand=True)
        
        # CPU Cores
        cores_info_frame = ttk.LabelFrame(scrollable_frame, text="CPU Cores", 
                                        style='Modern.TLabelframe', padding="10")
        cores_info_frame.pack(fill='x', pady=5, padx=5)
        
        self.cores_info_text = tk.Text(cores_info_frame, 
                                     height=8, 
                                     bg=self.colors['bg_light'], 
                                     fg=self.colors['text'],
                                     font=('Courier', 9),
                                     wrap=tk.WORD,
                                     relief='flat')
        self.cores_info_text.pack(fill='both', expand=True)
    
    def create_memory_tab(self):
        """Tworzy zakładkę informacji o pamięci"""
        canvas = tk.Canvas(self.memory_tab, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.memory_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Modern.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # RAM Information
        ram_info_frame = ttk.LabelFrame(scrollable_frame, text="RAM", 
                                      style='Modern.TLabelframe', padding="10")
        ram_info_frame.pack(fill='x', pady=5, padx=5)
        
        self.ram_info_text = tk.Text(ram_info_frame, 
                                   height=9, 
                                   bg=self.colors['bg_light'], 
                                   fg=self.colors['text'],
                                   font=('Courier', 9),
                                   wrap=tk.WORD,
                                   relief='flat')
        self.ram_info_text.pack(fill='both', expand=True)
        
        # SWAP Information
        swap_info_frame = ttk.LabelFrame(scrollable_frame, text="SWAP", 
                                       style='Modern.TLabelframe', padding="10")
        swap_info_frame.pack(fill='x', pady=5, padx=5)
        
        self.swap_info_text = tk.Text(swap_info_frame, 
                                    height=7, 
                                    bg=self.colors['bg_light'], 
                                    fg=self.colors['text'],
                                    font=('Courier', 9),
                                    wrap=tk.WORD,
                                    relief='flat')
        self.swap_info_text.pack(fill='both', expand=True)
    
    def create_disk_tab(self):
        """Tworzy zakładkę informacji o dyskach"""
        canvas = tk.Canvas(self.disk_tab, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.disk_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Modern.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Disk Information
        disk_info_frame = ttk.LabelFrame(scrollable_frame, text="Disks & Partitions", 
                                       style='Modern.TLabelframe', padding="10")
        disk_info_frame.pack(fill='x', pady=5, padx=5)
        
        self.disk_info_text = tk.Text(disk_info_frame, 
                                    height=95, 
                                    bg=self.colors['bg_light'], 
                                    fg=self.colors['text'],
                                    font=('Courier', 9),
                                    wrap=tk.WORD,
                                    relief='flat')
        self.disk_info_text.pack(fill='both', expand=True)
    
    def create_network_tab(self):
        """Tworzy zakładkę informacji o sieci"""
        canvas = tk.Canvas(self.network_tab, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.network_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Modern.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Network Information
        network_info_frame = ttk.LabelFrame(scrollable_frame, text="Network Interfaces", 
                                          style='Modern.TLabelframe', padding="10")
        network_info_frame.pack(fill='x', pady=5, padx=5)
        
        self.network_info_text = tk.Text(network_info_frame, 
                                       height=92, 
                                       bg=self.colors['bg_light'], 
                                       fg=self.colors['text'],
                                       font=('Courier', 9),
                                       wrap=tk.WORD,
                                       relief='flat')
        self.network_info_text.pack(fill='both', expand=True)
    
    def create_graphics_tab(self):
        """Tworzy zakładkę informacji o grafice"""
        canvas = tk.Canvas(self.graphics_tab, bg=self.colors['bg'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.graphics_tab, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas, style='Modern.TFrame')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # Graphics Information
        graphics_info_frame = ttk.LabelFrame(scrollable_frame, text="Graphics", 
                                           style='Modern.TLabelframe', padding="10")
        graphics_info_frame.pack(fill='x', pady=5, padx=5)
        
        self.graphics_info_text = tk.Text(graphics_info_frame, 
                                        height=10, 
                                        bg=self.colors['bg_light'], 
                                        fg=self.colors['text'],
                                        font=('Courier', 9),
                                        wrap=tk.WORD,
                                        relief='flat')
        self.graphics_info_text.pack(fill='both', expand=True)
    
    def refresh_info(self):
        """Odświeża wszystkie informacje systemowe"""
        self.status_label.config(text="🔄 Collecting system information...")
        
        try:
            # System Information
            self.update_system_info()
            
            # CPU Information
            self.update_cpu_info()
            
            # Memory Information
            self.update_memory_info()
            
            # Disk Information
            self.update_disk_info()
            
            # Network Information
            self.update_network_info()
            
            # Graphics Information
            self.update_graphics_info()
            
            self.status_label.config(text="✅ System information updated")
            
        except Exception as e:
            self.status_label.config(text=f"❌ Error: {str(e)}")
    
    def update_system_info(self):
        """Aktualizuje informacje systemowe"""
        # System info
        system_info = self.get_system_info()
        self.system_info_text.delete(1.0, tk.END)
        self.system_info_text.insert(1.0, system_info)
        
        # Machine info
        machine_info = self.get_machine_info()
        self.machine_info_text.delete(1.0, tk.END)
        self.machine_info_text.insert(1.0, machine_info)
        
        # Battery info
        battery_info = self.get_battery_info()
        self.battery_info_text.delete(1.0, tk.END)
        self.battery_info_text.insert(1.0, battery_info)
    
    def update_cpu_info(self):
        """Aktualizuje informacje o CPU"""
        cpu_info = self.get_cpu_info()
        self.cpu_info_text.delete(1.0, tk.END)
        self.cpu_info_text.insert(1.0, cpu_info)
        
        cores_info = self.get_cores_info()
        self.cores_info_text.delete(1.0, tk.END)
        self.cores_info_text.insert(1.0, cores_info)
    
    def update_memory_info(self):
        """Aktualizuje informacje o pamięci"""
        ram_info = self.get_ram_info()
        self.ram_info_text.delete(1.0, tk.END)
        self.ram_info_text.insert(1.0, ram_info)
        
        swap_info = self.get_swap_info()
        self.swap_info_text.delete(1.0, tk.END)
        self.swap_info_text.insert(1.0, swap_info)
    
    def update_disk_info(self):
        """Aktualizuje informacje o dyskach"""
        disk_info = self.get_disk_info()
        self.disk_info_text.delete(1.0, tk.END)
        self.disk_info_text.insert(1.0, disk_info)
    
    def update_network_info(self):
        """Aktualizuje informacje o sieci"""
        network_info = self.get_network_info()
        self.network_info_text.delete(1.0, tk.END)
        self.network_info_text.insert(1.0, network_info)
    
    def update_graphics_info(self):
        """Aktualizuje informacje o grafice"""
        graphics_info = self.get_graphics_info()
        self.graphics_info_text.delete(1.0, tk.END)
        self.graphics_info_text.insert(1.0, graphics_info)
    
    def get_system_info(self):
        """Pobiera informacje o systemie"""
        try:
            info = []
            info.append(f"System:     {platform.system()} {platform.release()}")
            info.append(f"Kernel:     {platform.version()}")
            info.append(f"Architecture: {platform.machine()}")
            info.append(f"Hostname:   {socket.gethostname()}")
            
            # Uptime
            boot_time = psutil.boot_time()
            from datetime import datetime
            uptime = datetime.now() - datetime.fromtimestamp(boot_time)
            days = uptime.days
            hours, remainder = divmod(uptime.seconds, 3600)
            minutes, seconds = divmod(remainder, 60)
            info.append(f"Uptime:     {days}d {hours}h {minutes}m {seconds}s")
            
            # Users
            users = len(psutil.users())
            info.append(f"Users:      {users} logged in")
            
            # Load average (Linux)
            if hasattr(os, 'getloadavg'):
                load = os.getloadavg()
                info.append(f"Load:       {load[0]:.2f}, {load[1]:.2f}, {load[2]:.2f}")
            
            # Processes
            processes = len(psutil.pids())
            info.append(f"Processes:  {processes}")
            
            return "\n".join(info)
        except Exception as e:
            return f"Error getting system info: {e}"
    
    def get_machine_info(self):
        """Pobiera informacje o maszynie"""
        try:
            info = []
            
            # Platform info
            if platform.system() == "Linux":
                # Try to get distro info
                try:
                    import distro
                    distro_info = distro.name(pretty=True)
                    info.append(f"Distro:     {distro_info}")
                except:
                    info.append(f"Platform:   {platform.platform()}")
            
            # Motherboard info (Linux)
            if platform.system() == "Linux":
                try:
                    with open('/sys/devices/virtual/dmi/id/board_vendor', 'r') as f:
                        vendor = f.read().strip()
                    with open('/sys/devices/virtual/dmi/id/board_name', 'r') as f:
                        name = f.read().strip()
                    info.append(f"Board:      {vendor} {name}")
                except:
                    pass
            
            # BIOS info (Linux)
            if platform.system() == "Linux":
                try:
                    with open('/sys/devices/virtual/dmi/id/bios_vendor', 'r') as f:
                        bios_vendor = f.read().strip()
                    with open('/sys/devices/virtual/dmi/id/bios_version', 'r') as f:
                        bios_version = f.read().strip()
                    with open('/sys/devices/virtual/dmi/id/bios_date', 'r') as f:
                        bios_date = f.read().strip()
                    info.append(f"BIOS:       {bios_vendor} {bios_version} ({bios_date})")
                except:
                    pass
            
            # Chassis info
            info.append(f"Machine:    {platform.node()}")
            
            return "\n".join(info) if info else "Machine information not available"
        except Exception as e:
            return f"Error getting machine info: {e}"
    
    def get_battery_info(self):
        """Pobiera informacje o baterii"""
        try:
            battery = psutil.sensors_battery()
            if battery:
                info = []
                info.append(f"Status:     {'Charging' if battery.power_plugged else 'Discharging'}")
                info.append(f"Level:      {battery.percent:.1f}%")
                if battery.secsleft != psutil.POWER_TIME_UNLIMITED:
                    if battery.secsleft != psutil.POWER_TIME_UNKNOWN:
                        hours = battery.secsleft // 3600
                        minutes = (battery.secsleft % 3600) // 60
                        info.append(f"Time left:  {hours}h {minutes}m")
                return "\n".join(info)
            else:
                return "No battery detected"
        except Exception as e:
            return f"Error getting battery info: {e}"
    
    def get_cpu_info(self):
        """Pobiera szczegółowe informacje o CPU"""
        try:
            info = []
            
            # Basic CPU info
            info.append(f"Model:      {platform.processor()}")
            
            # CPU frequency
            freq = psutil.cpu_freq()
            if freq:
                info.append(f"Frequency:  {freq.current:.0f} MHz (max: {freq.max:.0f} MHz)")
            
            # CPU usage
            usage = psutil.cpu_percent(interval=0.1)
            info.append(f"Usage:      {usage:.1f}%")
            
            # CPU times
            times = psutil.cpu_times()
            info.append(f"User time:  {times.user:.1f}s")
            info.append(f"System time: {times.system:.1f}s")
            info.append(f"Idle time:  {times.idle:.1f}s")
            
            # CPU stats
            stats = psutil.cpu_stats()
            info.append(f"CTX switches: {stats.ctx_switches}")
            info.append(f"Interrupts:   {stats.interrupts}")
            info.append(f"Soft IRQs:    {stats.soft_interrupts}")
            
            return "\n".join(info)
        except Exception as e:
            return f"Error getting CPU info: {e}"
    
    def get_cores_info(self):
        """Pobiera informacje o rdzeniach CPU"""
        try:
            info = []
            
            # CPU cores
            physical_cores = psutil.cpu_count(logical=False)
            logical_cores = psutil.cpu_count(logical=True)
            info.append(f"Physical:   {physical_cores} cores")
            info.append(f"Logical:    {logical_cores} threads")
            
            # Per-core frequencies
            if hasattr(psutil, 'cpu_freq') and callable(getattr(psutil.cpu_freq, 'percpu', None)):
                freqs = psutil.cpu_freq(percpu=True)
                if freqs:
                    info.append("\nPer-core frequencies:")
                    for i, freq in enumerate(freqs):
                        info.append(f"Core {i:2d}:    {freq.current:.0f} MHz")
            
            # Per-core usage
            usage = psutil.cpu_percent(interval=0.1, percpu=True)
            if usage:
                info.append("\nPer-core usage:")
                for i, core_usage in enumerate(usage):
                    info.append(f"Core {i:2d}:    {core_usage:.1f}%")
            
            return "\n".join(info)
        except Exception as e:
            return f"Error getting cores info: {e}"
    
    def get_ram_info(self):
        """Pobiera informacje o RAM"""
        try:
            info = []
            memory = psutil.virtual_memory()
            
            total_gb = memory.total / (1024**3)
            available_gb = memory.available / (1024**3)
            used_gb = memory.used / (1024**3)
            free_gb = memory.free / (1024**3)
            
            info.append(f"Total:      {total_gb:.1f} GB")
            info.append(f"Used:       {used_gb:.1f} GB ({memory.percent:.1f}%)")
            info.append(f"Free:       {free_gb:.1f} GB")
            info.append(f"Available:  {available_gb:.1f} GB")
            
            # Memory details
            info.append(f"Active:     {memory.active / (1024**3):.1f} GB")
            info.append(f"Inactive:   {memory.inactive / (1024**3):.1f} GB")
            info.append(f"Buffers:    {memory.buffers / (1024**3):.1f} GB")
            info.append(f"Cached:     {memory.cached / (1024**3):.1f} GB")
            info.append(f"Shared:     {memory.shared / (1024**3):.1f} GB")
            
            return "\n".join(info)
        except Exception as e:
            return f"Error getting RAM info: {e}"
    
    def get_swap_info(self):
        """Pobiera informacje o SWAP"""
        try:
            info = []
            swap = psutil.swap_memory()
            
            if swap.total > 0:
                total_gb = swap.total / (1024**3)
                used_gb = swap.used / (1024**3)
                free_gb = swap.free / (1024**3)
                
                info.append(f"Total:      {total_gb:.1f} GB")
                info.append(f"Used:       {used_gb:.1f} GB ({swap.percent:.1f}%)")
                info.append(f"Free:       {free_gb:.1f} GB")
                info.append(f"Swapped in: {swap.sin / (1024**2):.1f} MB")
                info.append(f"Swapped out: {swap.sout / (1024**2):.1f} MB")
            else:
                info.append("No swap space configured")
            
            return "\n".join(info)
        except Exception as e:
            return f"Error getting SWAP info: {e}"
    
    def get_disk_info(self):
        """Pobiera informacje o dyskach"""
        try:
            info = []
            partitions = psutil.disk_partitions()
            
            for partition in partitions:
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    total_gb = usage.total / (1024**3)
                    used_gb = usage.used / (1024**3)
                    free_gb = usage.free / (1024**3)
                    
                    info.append(f"Device:     {partition.device}")
                    info.append(f"Mount:      {partition.mountpoint}")
                    info.append(f"Type:       {partition.fstype}")
                    info.append(f"Size:       {total_gb:.1f} GB")
                    info.append(f"Used:       {used_gb:.1f} GB ({usage.percent:.1f}%)")
                    info.append(f"Free:       {free_gb:.1f} GB")
                    info.append("")
                    
                except PermissionError:
                    info.append(f"Device:     {partition.device} (Permission denied)")
                    info.append("")
            
            # Disk I/O statistics
            disk_io = psutil.disk_io_counters()
            if disk_io:
                info.append("Disk I/O Statistics:")
                info.append(f"Read count:  {disk_io.read_count}")
                info.append(f"Write count: {disk_io.write_count}")
                info.append(f"Read bytes:  {disk_io.read_bytes / (1024**3):.1f} GB")
                info.append(f"Write bytes: {disk_io.write_bytes / (1024**3):.1f} GB")
            
            return "\n".join(info)
        except Exception as e:
            return f"Error getting disk info: {e}"
    
    def get_network_info(self):
        """Pobiera informacje o sieci"""
        try:
            info = []
            interfaces = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            io_counters = psutil.net_io_counters(pernic=True)
            
            for interface, addrs in interfaces.items():
                info.append(f"Interface:  {interface}")
                
                # Status
                if interface in stats:
                    stat = stats[interface]
                    info.append(f"Status:     {'UP' if stat.isup else 'DOWN'}")
                    info.append(f"Speed:      {stat.speed} Mbps")
                    info.append(f"MTU:        {stat.mtu}")
                
                # Addresses
                for addr in addrs:
                    if addr.family == socket.AF_INET:  # IPv4
                        info.append(f"IPv4:       {addr.address}")
                        if addr.netmask:
                            info.append(f"Netmask:    {addr.netmask}")
                        if addr.broadcast:
                            info.append(f"Broadcast:  {addr.broadcast}")
                    elif addr.family == socket.AF_INET6:  # IPv6
                        info.append(f"IPv6:       {addr.address}")
                
                # I/O statistics
                if interface in io_counters:
                    io = io_counters[interface]
                    info.append(f"Bytes sent: {io.bytes_sent / (1024**2):.1f} MB")
                    info.append(f"Bytes recv: {io.bytes_recv / (1024**2):.1f} MB")
                    info.append(f"Packets sent: {io.packets_sent}")
                    info.append(f"Packets recv: {io.packets_recv}")
                
                info.append("")
            
            return "\n".join(info)
        except Exception as e:
            return f"Error getting network info: {e}"
    
    def get_graphics_info(self):
        """Pobiera informacje o grafice"""
        try:
            info = []
            
            # Try to get GPU info using various methods
            gpu_info = self.get_gpu_info_linux()
            if gpu_info:
                info.extend(gpu_info)
            else:
                # Try alternative methods
                alt_info = self.get_gpu_info_alternative()
                if alt_info:
                    info.extend(alt_info)
                else:
                    info.append("GPU information not available")
                
                # Try basic OpenGL info
                try:
                    import ctypes
                    from ctypes import util
                    libgl = ctypes.CDLL(util.find_library('GL'))
                    info.append("OpenGL library found")
                except:
                    info.append("OpenGL not available")
            
            # Display information
            try:
                if 'DISPLAY' in os.environ:
                    info.append(f"Display:    {os.environ['DISPLAY']}")
            except:
                pass
            
            return "\n".join(info)
        except Exception as e:
            return f"Error getting graphics info: {e}"
    
    def get_gpu_info_linux(self):
        """Pobiera informacje o GPU dla Linuxa"""
        try:
            info = []
            gpu_found = False
            
            # Check for NVIDIA GPU
            try:
                result = subprocess.run(['nvidia-smi', '--query-gpu=name,memory.total,driver_version', '--format=csv,noheader,nounits'], 
                                      capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.strip().split('\n')
                    for i, line in enumerate(lines):
                        parts = line.split(', ')
                        if len(parts) >= 3:
                            info.append(f"GPU {i}:     NVIDIA {parts[0]}")
                            info.append(f"Memory:     {parts[1]} MB")
                            info.append(f"Driver:     {parts[2]}")
                            info.append("")
                            gpu_found = True
            except:
                pass
            
            # Check for AMD GPU using lspci
            try:
                result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'VGA' in line or 'Display' in line:
                            if 'AMD' in line or 'ATI' in line or 'Radeon' in line:
                                gpu_info = line.split(': ')[-1]
                                info.append(f"GPU:        {gpu_info}")
                                gpu_found = True
            except:
                pass
            
            # Check for AMD GPU using /sys/class/drm
            try:
                drm_path = Path('/sys/class/drm')
                if drm_path.exists():
                    for card_path in drm_path.glob('card*'):
                        if card_path.is_dir() and not card_path.name.endswith('-DP'):
                            # Check if this is a GPU (not a DP connector)
                            device_path = card_path / 'device'
                            if device_path.exists():
                                try:
                                    with open(device_path / 'vendor', 'r') as f:
                                        vendor_id = f.read().strip()
                                    with open(device_path / 'device', 'r') as f:
                                        device_id = f.read().strip()
                                    
                                    # Convert vendor ID to name
                                    vendor_name = self.get_vendor_name(vendor_id)
                                    if vendor_name == "AMD" or vendor_name == "Advanced Micro Devices":
                                        # Try to get more info
                                        try:
                                            with open(device_path / 'uevent', 'r') as f:
                                                uevent_content = f.read()
                                            for uevent_line in uevent_content.split('\n'):
                                                if 'MODALIAS' in uevent_line:
                                                    modalias = uevent_line.split('=')[1]
                                                    if 'amd' in modalias.lower() or 'radeon' in modalias.lower():
                                                        info.append(f"GPU:        AMD Radeon Graphics")
                                                        gpu_found = True
                                                        break
                                        except:
                                            info.append(f"GPU:        AMD Graphics (Vendor: {vendor_id}, Device: {device_id})")
                                            gpu_found = True
                                except:
                                    pass
            except:
                pass
            
            # Check for GPU using glxinfo
            try:
                result = subprocess.run(['glxinfo'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'OpenGL renderer string' in line:
                            renderer = line.split(': ')[1].strip()
                            info.append(f"Renderer:   {renderer}")
                            gpu_found = True
                        elif 'OpenGL vendor string' in line:
                            vendor = line.split(': ')[1].strip()
                            info.append(f"Vendor:     {vendor}")
            except:
                pass
            
            return info if gpu_found else None
        except:
            return None
    
    def get_gpu_info_alternative(self):
        """Alternatywne metody wykrywania GPU"""
        try:
            info = []
            gpu_found = False
            
            # Method 1: Using lshw
            try:
                result = subprocess.run(['sudo', 'lshw', '-C', 'display'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    product = None
                    vendor = None
                    for line in lines:
                        if 'product:' in line:
                            product = line.split('product:')[-1].strip()
                        elif 'vendor:' in line:
                            vendor = line.split('vendor:')[-1].strip()
                        elif 'description:' in line and 'VGA' in line:
                            if product and vendor:
                                info.append(f"GPU:        {vendor} {product}")
                                gpu_found = True
                                break
            except:
                pass
            
            # Method 2: Using hwinfo
            try:
                result = subprocess.run(['hwinfo', '--gfxcard'], capture_output=True, text=True, timeout=10)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'Model:' in line and ('AMD' in line or 'Radeon' in line):
                            model = line.split('Model:')[-1].strip()
                            info.append(f"GPU:        {model}")
                            gpu_found = True
                            break
            except:
                pass
            
            # Method 3: Using inxi if available
            try:
                result = subprocess.run(['inxi', '-G'], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    lines = result.stdout.split('\n')
                    for line in lines:
                        if 'Graphics:' in line:
                            gpu_line = line.split('Graphics:')[-1].strip()
                            info.append(f"GPU:        {gpu_line}")
                            gpu_found = True
                            break
            except:
                pass
            
            return info if gpu_found else None
        except:
            return None
    
    def get_vendor_name(self, vendor_id):
        """Konwertuje ID vendor na nazwę"""
        vendor_map = {
            '0x1002': 'AMD',
            '0x10de': 'NVIDIA',
            '0x8086': 'Intel',
            '0x106b': 'Apple',
            '0x1a03': 'ASPEED'
        }
        return vendor_map.get(vendor_id, f"Unknown ({vendor_id})")
    
    def copy_to_clipboard(self):
        """Kopiuje wszystkie informacje systemowe do schowka"""
        try:
            all_info = self.get_all_info_text()
            self.parent.clipboard_clear()
            self.parent.clipboard_append(all_info)
            self.status_label.config(text="✅ All system information copied to clipboard")
        except Exception as e:
            self.status_label.config(text=f"❌ Error copying to clipboard: {e}")
    
    def save_to_file(self):
        """Zapisuje wszystkie informacje systemowe do pliku"""
        try:
            from tkinter import filedialog
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                all_info = self.get_all_info_text()
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(all_info)
                self.status_label.config(text=f"✅ System information saved to {filename}")
        except Exception as e:
            self.status_label.config(text=f"❌ Error saving to file: {e}")
    
    def get_all_info_text(self):
        """Zwraca wszystkie informacje systemowe jako tekst"""
        sections = []
        
        sections.append("=== SYSTEM INFORMATION ===\n")
        sections.append(self.system_info_text.get(1.0, tk.END))
        sections.append("\n=== MACHINE INFORMATION ===\n")
        sections.append(self.machine_info_text.get(1.0, tk.END))
        sections.append("\n=== BATTERY INFORMATION ===\n")
        sections.append(self.battery_info_text.get(1.0, tk.END))
        sections.append("\n=== CPU INFORMATION ===\n")
        sections.append(self.cpu_info_text.get(1.0, tk.END))
        sections.append("\n=== CPU CORES INFORMATION ===\n")
        sections.append(self.cores_info_text.get(1.0, tk.END))
        sections.append("\n=== MEMORY INFORMATION ===\n")
        sections.append(self.ram_info_text.get(1.0, tk.END))
        sections.append("\n=== SWAP INFORMATION ===\n")
        sections.append(self.swap_info_text.get(1.0, tk.END))
        sections.append("\n=== DISK INFORMATION ===\n")
        sections.append(self.disk_info_text.get(1.0, tk.END))
        sections.append("\n=== NETWORK INFORMATION ===\n")
        sections.append(self.network_info_text.get(1.0, tk.END))
        sections.append("\n=== GRAPHICS INFORMATION ===\n")
        sections.append(self.graphics_info_text.get(1.0, tk.END))
        
        return "".join(sections)