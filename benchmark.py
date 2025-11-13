import tkinter as tk
from tkinter import ttk, messagebox
import time
import threading
import psutil
import math
from collections import defaultdict
import random
import os
from datetime import datetime
import subprocess
import platform

class BenchmarkTab:
    def __init__(self, parent, colors):
        self.parent = parent
        self.colors = colors
        self.benchmark_running = False
        self.benchmark_thread = None
        self.benchmark_history = []
        self.create_widgets()
        
    def create_widgets(self):
        """Tworzy interfejs zakładki Benchmark"""
        main_frame = ttk.Frame(self.parent, style='Modern.TFrame', padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Nagłówek
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.pack(fill='x', pady=(0, 20))
        
        title_label = ttk.Label(header_frame, 
                               text="System Benchmark - Prime Numbers", 
                               style='Modern.TLabel',
                               font=('Arial', 18, 'bold'))
        title_label.pack(side=tk.LEFT)
        
        # Opis benchmarku
        desc_frame = ttk.LabelFrame(main_frame, text="📊 Benchmark Description", 
                                   style='Modern.TLabelframe', padding="15")
        desc_frame.pack(fill='x', pady=(0, 15))
        
        desc_text = """
This benchmark measures your system's computational power by calculating prime numbers.
The test runs for 60 seconds and calculates how many prime numbers can be found.
"""
        desc_label = ttk.Label(desc_frame, text=desc_text, style='Modern.TLabel', justify=tk.LEFT)
        desc_label.pack(anchor='w')
        
        # Konfiguracja benchmarku
        config_frame = ttk.LabelFrame(main_frame, text="⚙️ Benchmark Configuration", 
                                     style='Modern.TLabelframe', padding="15")
        config_frame.pack(fill='x', pady=(0, 15))
        
        # Czas trwania
        duration_frame = ttk.Frame(config_frame, style='Modern.TFrame')
        duration_frame.pack(fill='x', pady=5)
        
        ttk.Label(duration_frame, text="Duration:", style='Modern.TLabel').pack(side=tk.LEFT)
        self.duration_var = tk.StringVar(value="60")
        duration_combo = ttk.Combobox(duration_frame, textvariable=self.duration_var,
                                     values=["30", "60", "120", "300"], state="readonly", width=10)
        duration_combo.pack(side=tk.LEFT, padx=10)
        ttk.Label(duration_frame, text="seconds", style='Modern.TLabel').pack(side=tk.LEFT)
        
        # Status programu C++
        program_frame = ttk.Frame(config_frame, style='Modern.TFrame')
        program_frame.pack(fill='x', pady=5)
        
        self.program_status_label = ttk.Label(program_frame, 
                                            text="🔍 Checking prime_numbers program...", 
                                            style='Modern.TLabel')
        self.program_status_label.pack(side=tk.LEFT)
        
        # Przyciski akcji
        button_frame = ttk.Frame(config_frame, style='Modern.TFrame')
        button_frame.pack(fill='x', pady=10)
        
        self.start_button = ttk.Button(button_frame, text="🚀 Start Benchmark", 
                                      style='Accent.TButton', command=self.start_benchmark)
        self.start_button.pack(side=tk.LEFT, padx=5)
        
        self.stop_button = ttk.Button(button_frame, text="⏹️ Stop Benchmark", 
                                     style='Danger.TButton', command=self.stop_benchmark, state='disabled')
        self.stop_button.pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="🔄 Check Program", 
                  style='Modern.TButton', command=self.check_cpp_program).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(button_frame, text="📊 View Results", 
                  style='Modern.TButton', command=self.view_results).pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(config_frame, style='Modern.Horizontal.TProgressbar', mode='determinate')
        self.progress.pack(fill='x', pady=5)
        
        # Timer display
        self.timer_label = ttk.Label(config_frame, text="Time: 0s / 60s", style='Modern.TLabel')
        self.timer_label.pack(pady=5)
        
        # Wyniki benchmarku
        results_frame = ttk.LabelFrame(main_frame, text="📈 Benchmark Results", 
                                      style='Modern.TLabelframe', padding="15")
        results_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Siatka z wynikami
        results_grid = ttk.Frame(results_frame, style='Modern.TFrame')
        results_grid.pack(fill='x', pady=5)
        
        # Wyniki główne
        main_results_frame = ttk.LabelFrame(results_grid, text="Main Scores", 
                                           style='Modern.TLabelframe', padding="10")
        main_results_frame.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
        
        self.main_results_labels = {}
        main_metrics = [
            ("Prime Numbers Found:", "total_primes"),
            ("Numbers Checked:", "numbers_checked"),
            ("Largest Prime:", "largest_prime"),
            ("Overall Score:", "overall_score")
        ]
        
        for i, (label_text, key) in enumerate(main_metrics):
            ttk.Label(main_results_frame, text=label_text, style='Modern.TLabel').grid(row=i, column=0, sticky='w', padx=5, pady=2)
            self.main_results_labels[key] = ttk.Label(main_results_frame, text="--", 
                                                     style='Modern.TLabel', font=('Arial', 10, 'bold'))
            self.main_results_labels[key].grid(row=i, column=1, sticky='w', padx=5, pady=2)
        
        # Wyniki szczegółowe
        detail_results_frame = ttk.LabelFrame(results_grid, text="Performance Metrics", 
                                             style='Modern.TLabelframe', padding="10")
        detail_results_frame.grid(row=0, column=1, sticky='nsew', padx=5, pady=5)
        
        self.detail_results_labels = {}
        detail_metrics = [
            ("Primes/Second:", "primes_per_sec"),
            ("Checks/Second:", "checks_per_sec"),
            ("CPU Usage:", "cpu_usage"),
            ("Performance Rank:", "performance_rank")
        ]
        
        for i, (label_text, key) in enumerate(detail_metrics):
            ttk.Label(detail_results_frame, text=label_text, style='Modern.TLabel').grid(row=i, column=0, sticky='w', padx=5, pady=2)
            self.detail_results_labels[key] = ttk.Label(detail_results_frame, text="--", 
                                                       style='Modern.TLabel', font=('Arial', 10, 'bold'))
            self.detail_results_labels[key].grid(row=i, column=1, sticky='w', padx=5, pady=2)
        
        results_grid.columnconfigure(0, weight=1)
        results_grid.columnconfigure(1, weight=1)
        
        # Historia benchmarków
        history_frame = ttk.LabelFrame(main_frame, text="📋 Benchmark History", 
                                      style='Modern.TLabelframe', padding="10")
        history_frame.pack(fill='both', expand=True)
        
        self.history_text = tk.Text(history_frame, 
                                   height=8, 
                                   bg=self.colors['bg_light'], 
                                   fg=self.colors['text'],
                                   font=('Courier', 9),
                                   wrap=tk.WORD)
        
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.history_text.yview)
        self.history_text.configure(yscrollcommand=scrollbar.set)
        
        self.history_text.pack(side=tk.LEFT, fill='both', expand=True)
        scrollbar.pack(side=tk.LEFT, fill='y')
        
        # Pasek statusu
        self.status_label = ttk.Label(main_frame, text="Ready to start benchmark", style='Modern.TLabel')
        self.status_label.pack(fill='x', pady=(5, 0))
        
        # Sprawdź dostępność programu C++
        self.check_cpp_program()
        
        # Inicjalizacja wyników
        self.clear_results()
    
    def find_prime_program(self):
        """Znajduje program prime_numbers - FIXED VERSION"""
        import subprocess
        
        # 1. NAJPIERW sprawdź zmienne środowiskowe z AppRun
        prime_env = os.environ.get('PRIME_NUMBERS_PATH')
        if prime_env and os.path.exists(prime_env):
            print(f"✅ Found via PRIME_NUMBERS_PATH: {prime_env}")
            return prime_env
        
        # 2. Sprawdź APPIMAGE_PATH
        appimage_path = os.environ.get('APPIMAGE_PATH')
        if appimage_path:
            prime_path = os.path.join(appimage_path, "usr/bin/prime_numbers")
            if os.path.exists(prime_path):
                print(f"✅ Found via APPIMAGE_PATH: {prime_path}")
                return prime_path
        
        # 3. Sprawdź czy jesteśmy w AppImage (mount point)
        if 'APPIMAGE' in os.environ:
            # Jesteśmy w AppImage - znajdź mount point
            import glob
            mount_points = glob.glob("/tmp/.mount_System*")
            for mount_point in mount_points:
                prime_path = os.path.join(mount_point, "usr/bin/prime_numbers")
                if os.path.exists(prime_path):
                    print(f"✅ Found in mount point: {prime_path}")
                    return prime_path
        
        # 4. Sprawdź względną ścieżkę (dla AppImage)
        current_dir = os.getcwd()
        prime_path = os.path.join(current_dir, "usr/bin/prime_numbers")
        if os.path.exists(prime_path):
            print(f"✅ Found in current dir: {prime_path}")
            return prime_path
        
        # 5. Traditional fallback
        traditional_paths = [
            "./usr/bin/prime_numbers",
            "./prime_numbers",
            "prime_numbers",
            "/usr/bin/prime_numbers", 
            "/usr/local/bin/prime_numbers"
        ]
        
        for path in traditional_paths:
            if os.path.exists(path):
                print(f"✅ Found in traditional path: {path}")
                return path
        
        print("❌ prime_numbers not found")
        return None
    
    def check_cpp_program(self):
        """Sprawdza dostępność skompilowanego programu C++"""
        program_path = self.find_prime_program()
        
        if program_path:
            self.program_status_label.config(text=f"✅ Found: {program_path}")
            self.start_button.config(state='normal')
            self.status_label.config(text="Ready - prime program found")
        else:
            self.program_status_label.config(text="❌ prime_numbers program not found")
            self.start_button.config(state='disabled')
            self.status_label.config(text="Error: prime_numbers program not found in current directory")
    
    def clear_results(self):
        """Czyści wyniki benchmarku"""
        for label in self.main_results_labels.values():
            label.config(text="--")
        for label in self.detail_results_labels.values():
            label.config(text="--")
    
    def start_benchmark(self):
        """Rozpoczyna benchmark liczb pierwszych"""
        if self.benchmark_running:
            return
        
        try:
            duration = int(self.duration_var.get())
            
            program_path = self.find_prime_program()
            if not program_path:
                messagebox.showerror("Error", "prime_numbers program not found in current directory.")
                return
            
            self.benchmark_running = True
            self.start_button.config(state='disabled')
            self.stop_button.config(state='normal')
            self.progress['value'] = 0
            
            # Uruchom benchmark w osobnym wątku
            self.benchmark_thread = threading.Thread(
                target=self.run_prime_benchmark,
                args=(duration, program_path),
                daemon=True
            )
            self.benchmark_thread.start()
            
            self.status_label.config(text=f"🚀 Prime benchmark started for {duration} seconds")
            
        except Exception as e:
            messagebox.showerror("Error", f"Error starting benchmark: {e}")
    
    def run_prime_benchmark(self, duration, program_path):
        """Uruchamia benchmark używając programu C++"""
        try:
            start_time = time.time()
            end_time = start_time + duration
            
            # Uruchom program C++
            process = subprocess.Popen(
                [program_path, "-t", str(duration)],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Monitoruj postęp
            while time.time() < end_time and self.benchmark_running:
                elapsed = time.time() - start_time
                progress = min(100, (elapsed / duration) * 100)
                
                # Aktualizuj progress bar i timer
                self.parent.after(0, lambda: self.progress.config(value=progress))
                self.parent.after(0, lambda: self.timer_label.config(
                    text=f"Time: {int(elapsed)}s / {duration}s"
                ))
                
                # Sprawdź czy proces nadal działa
                if process.poll() is not None:
                    break
                
                time.sleep(0.1)
            
            # Zatrzymaj proces jeśli benchmark został zatrzymany
            if not self.benchmark_running and process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
            
            # Poczekaj na zakończenie procesu
            stdout, stderr = process.communicate()
            
            if self.benchmark_running:
                self.parent.after(0, lambda: self.process_benchmark_results(stdout, stderr, duration))
            
        except Exception as e:
            self.parent.after(0, lambda: self.status_label.config(text=f"Benchmark error: {str(e)}"))
        finally:
            self.benchmark_running = False
            self.parent.after(0, self.finalize_benchmark)
    
    def process_benchmark_results(self, stdout, stderr, duration):
        """Przetwarza wyniki z programu C++"""
        try:
            # Przeanalizuj output programu C++
            primes_found = 0
            numbers_checked = 0
            largest_prime = 0
            
            # Parsuj output
            for line in stdout.split('\n'):
                if "Prime numbers found:" in line:
                    try:
                        primes_found = int(line.split(":")[1].strip())
                    except:
                        pass
                elif "Numbers checked:" in line:
                    try:
                        numbers_checked = int(line.split(":")[1].strip())
                    except:
                        pass
                elif "Largest prime number:" in line:
                    try:
                        largest_prime = int(line.split(":")[1].strip())
                    except:
                        pass
            
            # Oblicz metryki wydajności
            primes_per_sec = primes_found / duration if duration > 0 else 0
            checks_per_sec = numbers_checked / duration if duration > 0 else 0
            
            # Oblicz ogólny wynik
            overall_score = self.calculate_prime_score(primes_per_sec, checks_per_sec)
            performance_rank = self.get_prime_performance_rank(overall_score)
            
            # Aktualizuj wyniki
            self.main_results_labels['total_primes'].config(text=f"{primes_found:,}")
            self.main_results_labels['numbers_checked'].config(text=f"{numbers_checked:,}")
            self.main_results_labels['largest_prime'].config(text=f"{largest_prime:,}")
            self.main_results_labels['overall_score'].config(text=f"{overall_score:.0f}")
            
            self.detail_results_labels['primes_per_sec'].config(text=f"{primes_per_sec:.1f}")
            self.detail_results_labels['checks_per_sec'].config(text=f"{checks_per_sec:,}")
            self.detail_results_labels['cpu_usage'].config(text=f"{psutil.cpu_percent():.1f}%")
            self.detail_results_labels['performance_rank'].config(text=performance_rank)
            
            # Zapisz wyniki do historii
            result_data = {
                'timestamp': datetime.now(),
                'primes_found': primes_found,
                'numbers_checked': numbers_checked,
                'largest_prime': largest_prime,
                'overall_score': overall_score,
                'primes_per_sec': primes_per_sec,
                'checks_per_sec': checks_per_sec,
                'performance_rank': performance_rank,
                'duration': duration
            }
            self.benchmark_history.append(result_data)
            
            # Dodaj do historii
            self.add_to_history(result_data)
            
            self.status_label.config(text=f"✅ Benchmark completed! Score: {overall_score:.0f} - {performance_rank}")
            
            # Sprawdź czy plik HTML został wygenerowany
            if os.path.exists("benchmark_results.html"):
                self.parent.after(2000, self.view_results)  # Otwórz wyniki po 2 sekundach
            
        except Exception as e:
            self.status_label.config(text=f"Error processing results: {str(e)}")
    
    def calculate_prime_score(self, primes_per_sec, checks_per_sec):
        """Oblicza ogólny wynik na podstawie wydajności liczb pierwszych"""
        # Waga dla primes/second i checks/second
        base_score = (primes_per_sec * 100) + (checks_per_sec * 0.01)
        return base_score
    
    def get_prime_performance_rank(self, score):
        """Zwraca rangę wydajności na podstawie wyniku liczb pierwszych"""
        if score >= 25000000:
            return "🏆 Elite"
        elif score >= 15000000:
            return "🔥 Excellent"
        elif score >= 1000000:
            return "💪 Very Good"
        elif score >= 7500000:
            return "👍 Good"
        elif score >= 500000:
            return "🔰 Average"
        else:
            return "🐢 Basic"
    
    def add_to_history(self, result_data):
        """Dodaje wynik do historii"""
        timestamp = result_data['timestamp'].strftime("%Y-%m-%d %H:%M:%S")
        
        history_entry = f"""[{timestamp}] Prime Benchmark ({result_data['duration']}s)
• Primes found: {result_data['primes_found']:,}
• Numbers checked: {result_data['numbers_checked']:,}
• Largest prime: {result_data['largest_prime']:,}
• Performance: {result_data['performance_rank']}
• Score: {result_data['overall_score']:.0f}
{'-'*50}
"""
        
        self.history_text.insert('1.0', history_entry)
    
    def stop_benchmark(self):
        """Zatrzymuje benchmark"""
        self.benchmark_running = False
        self.status_label.config(text="Benchmark stopped by user")
    
    def finalize_benchmark(self):
        """Finalizuje benchmark i resetuje interfejs"""
        self.benchmark_running = False
        self.start_button.config(state='normal')
        self.stop_button.config(state='disabled')
        self.progress['value'] = 100
        self.timer_label.config(text=f"Time: {self.duration_var.get()}s / {self.duration_var.get()}s")
        
        if not any(label.cget('text') != '--' for label in self.main_results_labels.values()):
            self.status_label.config(text="Benchmark ready")
    
    def view_results(self):
        """Otwiera zapisany raport HTML w przeglądarce"""
        filename = "benchmark_results.html"
        
        if not os.path.exists(filename):
            messagebox.showwarning("Warning", f"File {filename} not found. Please run benchmark first.")
            return
        
        try:
            import webbrowser
            webbrowser.open(f'file://{os.path.abspath(filename)}')
            self.status_label.config(text="📊 Opening results in browser...")
        except Exception as e:
            messagebox.showerror("Error", f"Error opening browser: {e}")