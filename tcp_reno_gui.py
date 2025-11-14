"""
TCP RENO SIMULATION & ANALYSIS GUI
Complete graphical interface for running simulations and analyzing results
"""

import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import subprocess
import threading
import os
import sys
from pathlib import Path
import time

class TCPRenoGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TCP Reno Simulation & Analysis Tool")
        self.root.geometry("1000x700")
        # Make window resizable
        self.root.minsize(900, 600)
        
        # Project paths
        self.project_dir = Path(__file__).parent
        self.analyze_dir = self.project_dir / "analyze"
        self.results_dir = self.project_dir / "results"
        
        # NS-3 path - auto-detect or use default
        self.ns3_dir = self.find_ns3_directory()
        
        # Python command - detect correct one
        self.python_cmd = self.detect_python_command()
        
        # Default parameters (recommended values)
        self.default_params = {
            'sim_time': '20',
            'num_flows': '3',
            'mtu': '1500',
            'cwnd': '1',
            'ssthresh': '65535',
            'tcp_queue_size': '25',
            'bottleneck_bw': '5Mbps',
            'bottleneck_delay': '10ms',
            'sender_bw': '10Mbps',
            'receiver_bw': '10Mbps',
            'error_rate': '0',
            'enable_sack': True,
            'enable_nagle': False,
            'queue_droptail': True,
            'queue_red': True
        }
        
        # Simulation process
        self.simulation_process = None
        self.is_running = False
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        
    def find_ns3_directory(self):
        """Auto-detect NS-3 installation directory"""
        # Common NS-3 locations
        possible_paths = [
            Path.home() / "ns-allinone-3.43" / "ns-3.43",
            Path("/usr/local/ns-allinone-3.43/ns-3.43"),
            Path("/opt/ns-allinone-3.43/ns-3.43"),
            Path.home() / "ns-3.43",
        ]
        
        for path in possible_paths:
            if path.exists() and (path / "ns3").exists():
                return path
        
        # If not found, return default and let user configure
        return Path.home() / "ns-allinone-3.43" / "ns-3.43"
    
    def detect_python_command(self):
        """Detect correct Python command (python3 or python)"""
        try:
            # Try python3 first (common on Linux)
            result = subprocess.run(['python3', '--version'], 
                                  capture_output=True, 
                                  timeout=2)
            if result.returncode == 0:
                return 'python3'
        except:
            pass
        
        try:
            # Try python (common on Windows)
            result = subprocess.run(['python', '--version'], 
                                  capture_output=True, 
                                  timeout=2)
            if result.returncode == 0:
                return 'python'
        except:
            pass
        
        # Default to python3 on Linux, python on Windows
        return 'python3' if sys.platform != 'win32' else 'python'
        
    def setup_styles(self):
        """Configure ttk styles"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Custom colors
        style.configure('Header.TLabel', 
                       font=('Arial', 16, 'bold'),
                       foreground='#2C3E50',
                       background='#ECF0F1')
        
        style.configure('Title.TLabel',
                       font=('Arial', 12, 'bold'),
                       foreground='#2C3E50')
        
        style.configure('Success.TButton',
                       font=('Arial', 10, 'bold'),
                       foreground='white',
                       background='#27AE60')
        
        style.configure('Danger.TButton',
                       font=('Arial', 10, 'bold'),
                       foreground='white',
                       background='#E74C3C')
        
        style.configure('Primary.TButton',
                       font=('Arial', 10, 'bold'),
                       foreground='white',
                       background='#3498DB')
        
    def create_widgets(self):
        """Create all GUI widgets"""
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Header
        self.create_header(main_frame)
        
        # Tabs
        self.create_tabs(main_frame)
        
    def create_header(self, parent):
        """Create header section"""
        header_frame = ttk.Frame(parent, relief=tk.RAISED, borderwidth=2)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        header_frame.columnconfigure(0, weight=1)
        
        # Title
        title = ttk.Label(header_frame,
                         text="🚀 TCP RENO SIMULATION & ANALYSIS TOOL",
                         style='Header.TLabel',
                         background='#3498DB',
                         foreground='white',
                         padding=15)
        title.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Subtitle
        subtitle = ttk.Label(header_frame,
                            text="DropTail vs RED Queue Management Comparison",
                            font=('Arial', 10, 'italic'),
                            foreground='#7F8C8D',
                            padding=5)
        subtitle.grid(row=1, column=0)
        
    def create_tabs(self, parent):
        """Create tabbed interface"""
        self.notebook = ttk.Notebook(parent)
        self.notebook.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Tab 1: Run Simulation
        self.tab_simulation = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_simulation, text="  🎮 Run Simulation  ")
        self.create_simulation_tab()
        
        # Tab 2: Analysis
        self.tab_analysis = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_analysis, text="  📊 Analysis & Visualization  ")
        self.create_analysis_tab()
        
        # Tab 3: Results
        self.tab_results = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_results, text="  📁 Results Browser  ")
        self.create_results_tab()
        
        # Tab 4: Help
        self.tab_help = ttk.Frame(self.notebook, padding=10)
        self.notebook.add(self.tab_help, text="  ❓ Help & Guide  ")
        self.create_help_tab()
        
    def create_simulation_tab(self):
        """Create simulation configuration and execution tab"""
        # Configure tab grid
        self.tab_simulation.columnconfigure(0, weight=1)
        self.tab_simulation.rowconfigure(0, weight=1)
        
        # Create canvas with scrollbar for config section
        canvas = tk.Canvas(self.tab_simulation, highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.tab_simulation, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Enable mouse wheel scrolling (Windows and Linux)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        def _on_mousewheel_linux(event):
            if event.num == 4:
                canvas.yview_scroll(-1, "units")
            elif event.num == 5:
                canvas.yview_scroll(1, "units")
        
        # Bind for Windows
        canvas.bind_all("<MouseWheel>", _on_mousewheel)
        # Bind for Linux
        canvas.bind_all("<Button-4>", _on_mousewheel_linux)
        canvas.bind_all("<Button-5>", _on_mousewheel_linux)
        
        canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Main container (now inside scrollable frame)
        main_frame = ttk.Frame(scrollable_frame)
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=10, pady=10)
        main_frame.columnconfigure(0, weight=1)
        
        # Configuration section
        config_frame = ttk.LabelFrame(main_frame, 
                                     text="⚙️ Simulation Configuration",
                                     padding=15)
        config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Queue Types
        ttk.Label(config_frame, text="Queue Types to Simulate:", 
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.queue_droptail = tk.BooleanVar(value=True)
        self.queue_red = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(config_frame, text="DropTail", 
                       variable=self.queue_droptail).grid(row=1, column=0, sticky=tk.W, padx=(20, 0))
        ttk.Checkbutton(config_frame, text="RED", 
                       variable=self.queue_red).grid(row=1, column=1, sticky=tk.W)
        
        # Basic Parameters
        ttk.Separator(config_frame, orient=tk.HORIZONTAL).grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        ttk.Label(config_frame, text="Basic Parameters:", 
                 font=('Arial', 10, 'bold')).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Row 4: Duration and Num Flows
        ttk.Label(config_frame, text="Duration (s):").grid(row=4, column=0, sticky=tk.W, padx=(20, 0), pady=5)
        self.sim_time = tk.StringVar(value="20")
        ttk.Entry(config_frame, textvariable=self.sim_time, width=12).grid(row=4, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(config_frame, text="Num Flows:").grid(row=4, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        self.num_flows = tk.StringVar(value="3")
        ttk.Spinbox(config_frame, from_=1, to=3, textvariable=self.num_flows, width=10).grid(row=4, column=3, sticky=tk.W, pady=5)
        
        # Row 5: MTU and CWND
        ttk.Label(config_frame, text="MTU (bytes):").grid(row=5, column=0, sticky=tk.W, padx=(20, 0), pady=5)
        self.mtu = tk.StringVar(value="1500")
        ttk.Entry(config_frame, textvariable=self.mtu, width=12).grid(row=5, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(config_frame, text="Init CWND:").grid(row=5, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        self.cwnd = tk.StringVar(value="1")
        ttk.Entry(config_frame, textvariable=self.cwnd, width=10).grid(row=5, column=3, sticky=tk.W, pady=5)
        
        # Row 6: SSThresh and Queue Size
        ttk.Label(config_frame, text="SSThresh:").grid(row=6, column=0, sticky=tk.W, padx=(20, 0), pady=5)
        self.ssthresh = tk.StringVar(value="65535")
        ttk.Entry(config_frame, textvariable=self.ssthresh, width=12).grid(row=6, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(config_frame, text="Queue Size:").grid(row=6, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        self.tcp_queue_size = tk.StringVar(value="25")
        ttk.Entry(config_frame, textvariable=self.tcp_queue_size, width=10).grid(row=6, column=3, sticky=tk.W, pady=5)
        
        # Network Parameters
        ttk.Separator(config_frame, orient=tk.HORIZONTAL).grid(row=7, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        ttk.Label(config_frame, text="Network Parameters:", 
                 font=('Arial', 10, 'bold')).grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Row 9: Bottleneck
        ttk.Label(config_frame, text="Bottleneck BW:").grid(row=9, column=0, sticky=tk.W, padx=(20, 0), pady=5)
        self.bottleneck_bw = tk.StringVar(value="5Mbps")
        ttk.Entry(config_frame, textvariable=self.bottleneck_bw, width=12).grid(row=9, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(config_frame, text="Delay:").grid(row=9, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        self.bottleneck_delay = tk.StringVar(value="10ms")
        ttk.Entry(config_frame, textvariable=self.bottleneck_delay, width=10).grid(row=9, column=3, sticky=tk.W, pady=5)
        
        # Row 10: Sender/Receiver
        ttk.Label(config_frame, text="Sender BW:").grid(row=10, column=0, sticky=tk.W, padx=(20, 0), pady=5)
        self.sender_bw = tk.StringVar(value="10Mbps")
        ttk.Entry(config_frame, textvariable=self.sender_bw, width=12).grid(row=10, column=1, sticky=tk.W, pady=5)
        
        ttk.Label(config_frame, text="Receiver BW:").grid(row=10, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        self.receiver_bw = tk.StringVar(value="10Mbps")
        ttk.Entry(config_frame, textvariable=self.receiver_bw, width=10).grid(row=10, column=3, sticky=tk.W, pady=5)
        
        # Row 11: Error Rate
        ttk.Label(config_frame, text="Error Rate:").grid(row=11, column=0, sticky=tk.W, padx=(20, 0), pady=5)
        self.error_rate = tk.StringVar(value="0")
        ttk.Entry(config_frame, textvariable=self.error_rate, width=12).grid(row=11, column=1, sticky=tk.W, pady=5)
        
        # Options
        ttk.Separator(config_frame, orient=tk.HORIZONTAL).grid(row=12, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        ttk.Label(config_frame, text="Options:", 
                 font=('Arial', 10, 'bold')).grid(row=13, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.enable_sack = tk.BooleanVar(value=True)
        ttk.Checkbutton(config_frame, text="Enable SACK", 
                       variable=self.enable_sack).grid(row=14, column=0, columnspan=2, sticky=tk.W, padx=(20, 0), pady=2)
        
        self.enable_nagle = tk.BooleanVar(value=False)
        ttk.Checkbutton(config_frame, text="Enable Nagle", 
                       variable=self.enable_nagle).grid(row=14, column=2, columnspan=2, sticky=tk.W, pady=2)
        
        # NS-3 Directory
        ttk.Separator(config_frame, orient=tk.HORIZONTAL).grid(row=15, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        ttk.Label(config_frame, text="NS-3 Directory:", 
                 font=('Arial', 10, 'bold')).grid(row=16, column=0, columnspan=4, sticky=tk.W, pady=(5, 5))
        
        ns3_frame = ttk.Frame(config_frame)
        ns3_frame.grid(row=17, column=0, columnspan=4, sticky=(tk.W, tk.E), padx=(20, 0))
        
        self.ns3_path = tk.StringVar(value=str(self.ns3_dir))
        ns3_entry = ttk.Entry(ns3_frame, textvariable=self.ns3_path, width=60)
        ns3_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        ttk.Button(ns3_frame, text="Browse...", 
                  command=self.browse_ns3_dir,
                  width=10).grid(row=0, column=1, padx=(5, 0))
        
        ns3_frame.columnconfigure(0, weight=1)
        
        # Control buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=1, column=0, pady=(0, 10))
        
        self.btn_run = ttk.Button(button_frame, 
                                  text="▶️ Run Simulation",
                                  command=self.run_simulation,
                                  width=20)
        self.btn_run.grid(row=0, column=0, padx=5)
        
        self.btn_stop = ttk.Button(button_frame,
                                   text="⏹️ Stop Simulation",
                                   command=self.stop_simulation,
                                   state=tk.DISABLED,
                                   width=20)
        self.btn_stop.grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame,
                  text="🔄 Reset to Defaults",
                  command=self.reset_parameters,
                  width=20).grid(row=0, column=2, padx=5)
        
        # Progress section (below buttons) - separate frame
        progress_outer = ttk.Frame(main_frame)
        progress_outer.grid(row=1, column=0, pady=(55, 0), sticky=(tk.W, tk.E))
        
        progress_frame = ttk.Frame(progress_outer)
        progress_frame.pack(expand=True)
        
        self.progress_label = ttk.Label(progress_frame, text="Ready to run", 
                                       font=('Arial', 9, 'italic'), foreground='#7F8C8D')
        self.progress_label.grid(row=0, column=0, pady=(0, 5))
        
        self.progress_bar = ttk.Progressbar(progress_frame, length=700, mode='indeterminate')
        self.progress_bar.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=20)
        
        # Output console
        console_frame = ttk.LabelFrame(main_frame,
                                      text="📟 Console Output",
                                      padding=10)
        console_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        self.console = scrolledtext.ScrolledText(console_frame,
                                                 width=90, height=15,
                                                 font=('Courier', 9),
                                                 bg='#2C3E50',
                                                 fg='#ECF0F1',
                                                 insertbackground='white')
        self.console.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        console_frame.columnconfigure(0, weight=1)
        console_frame.rowconfigure(0, weight=1)
        
        # Status bar
        self.status_var = tk.StringVar(value="Ready to run simulation")
        status_bar = ttk.Label(self.tab_simulation,
                             textvariable=self.status_var,
                             relief=tk.SUNKEN,
                             padding=5,
                             font=('Arial', 9))
        status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E))
        
    def create_analysis_tab(self):
        """Create analysis and visualization tab"""
        # Instructions
        info_frame = ttk.Frame(self.tab_analysis)
        info_frame.grid(row=0, column=0, columnspan=2, pady=(0, 20), sticky=tk.W)
        
        ttk.Label(info_frame,
                 text="📊 Choose analysis and visualization options:",
                 font=('Arial', 12, 'bold'),
                 foreground='#2C3E50').grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(info_frame,
                 text="Make sure you have run the simulation first to generate data.",
                 font=('Arial', 9, 'italic'),
                 foreground='#7F8C8D').grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Left panel - Single Queue Analysis
        left_frame = ttk.LabelFrame(self.tab_analysis,
                                   text="📈 Single Queue Analysis",
                                   padding=15)
        left_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))
        
        ttk.Label(left_frame, text="Select Queue Type:",
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        self.analysis_queue = tk.StringVar(value="DropTail")
        ttk.Radiobutton(left_frame, text="DropTail", 
                       variable=self.analysis_queue,
                       value="DropTail").grid(row=1, column=0, sticky=tk.W)
        ttk.Radiobutton(left_frame, text="RED",
                       variable=self.analysis_queue,
                       value="RED").grid(row=2, column=0, sticky=tk.W)
        
        ttk.Separator(left_frame, orient='horizontal').grid(row=3, column=0, 
                                                           sticky=(tk.W, tk.E), pady=15)
        
        # Analysis buttons
        ttk.Button(left_frame,
                  text="📊 Show Dashboard",
                  command=lambda: self.run_analysis('dashboard'),
                  width=25).grid(row=4, column=0, pady=5)
        
        ttk.Button(left_frame,
                  text="📈 Show Timeline",
                  command=lambda: self.run_analysis('timeline'),
                  width=25).grid(row=5, column=0, pady=5)
        
        ttk.Button(left_frame,
                  text="📝 Print Analysis",
                  command=lambda: self.run_analysis('print'),
                  width=25).grid(row=6, column=0, pady=5)
        
        # Right panel - Comparison Analysis
        right_frame = ttk.LabelFrame(self.tab_analysis,
                                    text="⚖️ Comparison Analysis",
                                    padding=15)
        right_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N))
        
        ttk.Label(right_frame,
                 text="Compare DropTail vs RED",
                 font=('Arial', 10, 'bold'),
                 foreground='#2C3E50').grid(row=0, column=0, pady=(0, 15))
        
        ttk.Button(right_frame,
                  text="📊 Comparison Dashboard",
                  command=lambda: self.run_analysis('comparison'),
                  width=25).grid(row=1, column=0, pady=5)
        
        ttk.Button(right_frame,
                  text="📄 Infographic (PDF)",
                  command=lambda: self.run_analysis('infographic-pdf'),
                  width=25).grid(row=2, column=0, pady=5)
        
        ttk.Button(right_frame,
                  text="📱 Infographic (GUI)",
                  command=lambda: self.run_analysis('infographic-gui'),
                  width=25).grid(row=3, column=0, pady=5)
        
        # Output section
        output_frame = ttk.LabelFrame(self.tab_analysis,
                                     text="📟 Analysis Output",
                                     padding=10)
        output_frame.grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=20)
        self.tab_analysis.rowconfigure(2, weight=1)
        
        self.analysis_output = scrolledtext.ScrolledText(output_frame,
                                                        width=100, height=15,
                                                        font=('Courier', 9),
                                                        bg='#ECF0F1',
                                                        fg='#2C3E50')
        self.analysis_output.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
    def create_results_tab(self):
        """Create results browser tab"""
        # File list
        list_frame = ttk.LabelFrame(self.tab_results,
                                   text="📁 Generated Files",
                                   padding=10)
        list_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.tab_results.rowconfigure(0, weight=1)
        
        # Treeview for file list
        self.file_tree = ttk.Treeview(list_frame, 
                                     columns=('Type', 'Size', 'Modified'),
                                     height=15)
        self.file_tree.heading('#0', text='File Name')
        self.file_tree.heading('Type', text='Type')
        self.file_tree.heading('Size', text='Size')
        self.file_tree.heading('Modified', text='Last Modified')
        
        self.file_tree.column('#0', width=300)
        self.file_tree.column('Type', width=150)
        self.file_tree.column('Size', width=100)
        self.file_tree.column('Modified', width=150)
        
        self.file_tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, 
                                 command=self.file_tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.file_tree.configure(yscrollcommand=scrollbar.set)
        
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
        # Action buttons
        button_frame = ttk.Frame(self.tab_results)
        button_frame.grid(row=1, column=0, pady=10)
        
        ttk.Button(button_frame,
                  text="🔄 Refresh List",
                  command=self.refresh_file_list,
                  width=20).grid(row=0, column=0, padx=5)
        
        ttk.Button(button_frame,
                  text="📂 Open Results Folder",
                  command=self.open_results_folder,
                  width=20).grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame,
                  text="🗑️ Clear Results",
                  command=self.clear_results,
                  width=20).grid(row=0, column=2, padx=5)
        
        # Auto-refresh file list
        self.refresh_file_list()
        
    def create_help_tab(self):
        """Create help and documentation tab"""
        help_text = scrolledtext.ScrolledText(self.tab_help,
                                             width=100, height=30,
                                             font=('Arial', 10),
                                             wrap=tk.WORD)
        help_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        self.tab_help.columnconfigure(0, weight=1)
        self.tab_help.rowconfigure(0, weight=1)
        
        help_content = r"""
📚 TCP RENO SIMULATION & ANALYSIS TOOL - USER GUIDE

═══════════════════════════════════════════════════════════════════════════════

🎯 OVERVIEW
───────────
This tool helps you simulate and analyze TCP Reno performance with two different 
queue management algorithms: DropTail and RED (Random Early Detection).

═══════════════════════════════════════════════════════════════════════════════

🎮 TAB 1: RUN SIMULATION
─────────────────────────

1️⃣ Configuration:
   • Select which queue types to simulate (DropTail, RED, or both)
   • Set simulation time (default: 20 seconds)
   • Optionally enable real-time visualization

2️⃣ Running:
   • Click "▶️ Run Simulation" to start
   • Watch console output for progress
   • Click "⏹️ Stop Simulation" to abort if needed

3️⃣ NS-3 Directory:
   ⚠️  IMPORTANT: You must specify the correct NS-3 installation path!
   
   Example paths:
   • Linux: ~/ns-allinone-3.43/ns-3.43
   • Windows: C:/Users/YourName/ns-allinone-3.43/ns-3.43
   
   The GUI will auto-detect common locations, but you can browse to select manually.

4️⃣ What happens:
   • Changes to NS-3 directory
   • Compiles NS-3 simulation (if needed)
   • Runs: ./ns3 run "scratch/tcp_reno_project/tcp_reno --simTime=XX"
   • Generates trace files in results/ directory
   • Shows real-time CWND plots (if enabled)

═══════════════════════════════════════════════════════════════════════════════

📊 TAB 2: ANALYSIS & VISUALIZATION
───────────────────────────────────

📈 Single Queue Analysis:
   • Dashboard: Comprehensive performance dashboard
   • Timeline: Detailed event timeline with annotations
   • Print Analysis: Text-based statistics in console

⚖️ Comparison Analysis:
   • Comparison Dashboard: Side-by-side performance metrics
   • Infographic (PDF): 5-page detailed report saved as PDF
   • Infographic (GUI): Interactive scrollable visualization

═══════════════════════════════════════════════════════════════════════════════

📁 TAB 3: RESULTS BROWSER
──────────────────────────

• View all generated files (traces, plots, reports)
• Refresh list to see new files
• Open results folder in file explorer
• Clear all results to start fresh

═══════════════════════════════════════════════════════════════════════════════

📋 OUTPUT FILES
───────────────

Simulation generates:
   📊 *_cwnd_trace_DropTail.tr    - CWND trace data
   📊 *_cwnd_trace_RED.tr         - CWND trace data
   📝 *_summary_DropTail.txt      - Performance summary
   📝 *_summary_RED.txt           - Performance summary

Analysis generates:
   📈 *_dashboard_*.png           - Performance dashboards
   📊 *_comparison_dashboard.png  - Comparison charts
   📄 *_infographic.pdf           - Complete analysis report
   📈 *_timeline_*.png            - Event timelines

═══════════════════════════════════════════════════════════════════════════════

💡 TIPS FOR LEARNING
────────────────────

1. Start Simple:
   → Run with default settings first
   → Study the dashboard for one queue type
   → Compare results between DropTail and RED

2. Understand Metrics:
   → Throughput: Data transfer rate (higher is better)
   → Loss Rate: Percentage of lost packets (lower is better)
   → Delay: Average packet delay (lower is better)
   → CWND: Congestion window size (shows TCP behavior)

3. Key Observations:
   → DropTail: Simple but can cause global synchronization
   → RED: Prevents synchronization through early dropping
   → Watch for timeouts (red X) and fast retransmits (yellow)

═══════════════════════════════════════════════════════════════════════════════

🔧 REQUIREMENTS
───────────────

• NS-3 Network Simulator (version 3.43)
• Python 3.7+
• Required Python packages:
  - matplotlib
  - numpy
  - seaborn
  - networkx

═══════════════════════════════════════════════════════════════════════════════

❓ TROUBLESHOOTING
──────────────────

Problem: Simulation fails to run
→ Check NS-3 directory path is correct (click Browse button)
→ Verify NS-3 is installed: should see "ns3" script in the directory
→ Verify tcp_reno.cc is in: NS-3-DIR/scratch/tcp_reno_project/tcp_reno.cc
→ Make sure you copied the project files to NS-3 scratch folder

Problem: "NS-3 directory not found" error
→ Click Browse button and select: ~/ns-allinone-3.43/ns-3.43
→ On Linux/Mac: must have execute permission on ns3 script
→ On Windows: use full path like C:/Users/Name/ns-allinone-3.43/ns-3.43

Problem: Analysis shows no data
→ Run simulation first to generate trace files
→ Check results/ directory for .tr files

Problem: Real-time plot doesn't show
→ Ensure plot_realtime.py has execute permissions
→ Check Python and matplotlib are properly installed

═══════════════════════════════════════════════════════════════════════════════

📞 PROJECT STRUCTURE
────────────────────

TCP_Reno/ (Your workspace)
├── tcp_reno.cc              # NS-3 simulation code
├── tcp_reno_gui.py          # This GUI application ⭐
├── plot_realtime.py         # Real-time visualization
├── CMakeLists.txt           # Build configuration
├── analyze/                 # Analysis tools
│   ├── main.py             # CLI interface
│   └── analyzer/           # Analysis modules
└── results/                 # Generated data and plots

NS-3 Directory Structure (separate location!)
~/ns-allinone-3.43/ns-3.43/
├── ns3                      # NS-3 build script
├── scratch/
│   └── tcp_reno_project/   # ⚠️ YOU MUST COPY FILES HERE!
│       ├── tcp_reno.cc     # Copy from TCP_Reno/
│       └── CMakeLists.txt  # Copy from TCP_Reno/

⚠️  SETUP STEPS:
1. Copy tcp_reno.cc and CMakeLists.txt to NS-3's scratch/tcp_reno_project/
2. In GUI, set NS-3 directory to ~/ns-allinone-3.43/ns-3.43
3. Run simulation - GUI will execute from NS-3 directory
4. Results will be saved to TCP_Reno/results/

═══════════════════════════════════════════════════════════════════════════════

🎓 LEARNING PATH
────────────────

Week 1: Understand the basics
→ Run simulations with default settings
→ Study single queue dashboards
→ Learn about CWND evolution

Week 2: Compare algorithms
→ Run both DropTail and RED
→ Use comparison dashboard
→ Analyze differences in behavior

Week 3: Deep dive
→ Experiment with simulation time
→ Study timeline views
→ Read infographic reports

Week 4: Advanced topics
→ Modify simulation parameters in tcp_reno.cc
→ Compare multiple scenarios
→ Draw conclusions about queue management

═══════════════════════════════════════════════════════════════════════════════

✅ READY TO START!

Click on the "🎮 Run Simulation" tab to begin your learning journey!
        """
        
        help_text.insert('1.0', help_content)
        help_text.configure(state='disabled')
    
    # ============= SIMULATION METHODS =============
    
    def reset_parameters(self):
        """Reset all parameters to default recommended values"""
        self.sim_time.set(self.default_params['sim_time'])
        self.num_flows.set(self.default_params['num_flows'])
        self.mtu.set(self.default_params['mtu'])
        self.cwnd.set(self.default_params['cwnd'])
        self.ssthresh.set(self.default_params['ssthresh'])
        self.tcp_queue_size.set(self.default_params['tcp_queue_size'])
        self.bottleneck_bw.set(self.default_params['bottleneck_bw'])
        self.bottleneck_delay.set(self.default_params['bottleneck_delay'])
        self.sender_bw.set(self.default_params['sender_bw'])
        self.receiver_bw.set(self.default_params['receiver_bw'])
        self.error_rate.set(self.default_params['error_rate'])
        self.enable_sack.set(self.default_params['enable_sack'])
        self.enable_nagle.set(self.default_params['enable_nagle'])
        self.queue_droptail.set(self.default_params['queue_droptail'])
        self.queue_red.set(self.default_params['queue_red'])
        messagebox.showinfo("Reset", "All parameters reset to recommended defaults!")
    
    def run_simulation(self):
        """Run NS-3 simulation"""
        if self.is_running:
            messagebox.showwarning("Warning", "Simulation is already running!")
            return
            
        if not self.queue_droptail.get() and not self.queue_red.get():
            messagebox.showerror("Error", "Please select at least one queue type!")
            return
        
        # Clear console
        self.console.delete('1.0', tk.END)
        self.log_to_console("🚀 Starting TCP Reno Simulation...\n", 'info')
        
        # Update UI
        self.is_running = True
        self.btn_run.configure(state=tk.DISABLED)
        self.btn_stop.configure(state=tk.NORMAL)
        self.status_var.set("⏳ Simulation running...")
        self.progress_label.config(text="🔄 Starting simulation...")
        self.progress_bar.start(10)
        
        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=self._run_simulation_thread)
        thread.daemon = True
        thread.start()
        
    def browse_ns3_dir(self):
        """Browse for NS-3 directory"""
        directory = filedialog.askdirectory(
            title="Select NS-3 Directory",
            initialdir=str(Path.home()))
        if directory:
            self.ns3_path.set(directory)
            self.ns3_dir = Path(directory)
    
    def _run_simulation_thread(self):
        """Thread worker for running simulation"""
        try:
            # Get NS-3 directory
            ns3_dir = Path(self.ns3_path.get())
            
            # Validate NS-3 directory
            if not ns3_dir.exists():
                self.log_to_console(f"\n❌ NS-3 directory not found: {ns3_dir}\n", 'error')
                self.log_to_console("Please select correct NS-3 directory in configuration\n", 'warning')
                self._simulation_finished(False)
                return
            
            if not (ns3_dir / "ns3").exists():
                self.log_to_console(f"\n❌ Invalid NS-3 directory (ns3 script not found)\n", 'error')
                self.log_to_console(f"Expected: {ns3_dir / 'ns3'}\n", 'warning')
                self._simulation_finished(False)
                return
            
            # Get and validate parameters
            try:
                sim_time = int(self.sim_time.get())
                num_flows = int(self.num_flows.get())
                mtu = int(self.mtu.get())
                cwnd = int(self.cwnd.get())
                ssthresh = int(self.ssthresh.get())
                tcp_queue_size = int(self.tcp_queue_size.get())
                error_rate = float(self.error_rate.get())
                
                # Validate ranges
                if sim_time <= 0:
                    raise ValueError("Duration must be positive")
                if not 1 <= num_flows <= 3:
                    raise ValueError("Number of flows must be 1-3")
                if error_rate < 0 or error_rate > 1:
                    raise ValueError("Error rate must be between 0 and 1")
                    
            except ValueError as e:
                self.log_to_console(f"\n❌ Invalid parameter: {str(e)}\n", 'error')
                self.log_to_console("Please check your input values\n", 'warning')
                self._simulation_finished(False)
                return
            
            self.log_to_console(f"📂 NS-3 Directory: {ns3_dir}\n")
            self.log_to_console(f"📊 Simulation time: {sim_time} seconds\n")
            self.log_to_console(f"📦 Queue types: ", 'info')
            
            if self.queue_droptail.get():
                self.log_to_console("DropTail ", 'success')
            if self.queue_red.get():
                self.log_to_console("RED ", 'success')
            self.log_to_console("\n")
            
            self.log_to_console("\n🔨 Building and running NS-3 simulation...\n", 'info')
            
            # Build queue types list
            queue_types = []
            if self.queue_droptail.get():
                queue_types.append("DropTail")
            if self.queue_red.get():
                queue_types.append("RED")
            
            self.log_to_console(f"\n📋 Total queues to run: {len(queue_types)}\n", 'info')
            
            # Run simulation for each queue type
            all_success = True
            for i, queue_type in enumerate(queue_types):
                # Update progress label
                self.root.after(0, self.progress_label.config, 
                               {'text': f"🚀 Running {i+1}/{len(queue_types)}: {queue_type}"})
                
                self.log_to_console(f"\n{'='*60}\n", 'info')
                self.log_to_console(f"🚀 Running simulation {i+1}/{len(queue_types)}: {queue_type}\n", 'info')
                self.log_to_console(f"{'='*60}\n", 'info')
                
                # Build command with all parameters
                cmd_params = [
                    f"--queueType={queue_type}",
                    f"--duration={sim_time}",
                    f"--numFlows={num_flows}",
                    f"--mtu={mtu}",
                    f"--cwnd={cwnd}",
                    f"--ssthresh={ssthresh}",
                    f"--tcp_queue_size={tcp_queue_size}",
                    f"--error_p={error_rate}",
                    f"--bottleneck_bandwidth={self.bottleneck_bw.get()}",
                    f"--bottleneck_delay={self.bottleneck_delay.get()}",
                    f"--s_bandwidth={self.sender_bw.get()}",
                    f"--r_bandwidth={self.receiver_bw.get()}",
                    f"--sack={'true' if self.enable_sack.get() else 'false'}",
                    f"--nagle={'true' if self.enable_nagle.get() else 'false'}"
                ]
                
                cmd_string = " ".join(cmd_params)
                
                # Build command based on OS
                if sys.platform == 'win32':
                    # Windows with PowerShell
                    cmd = f'cd "{ns3_dir}"; ./ns3 run "scratch/tcp_reno_project/tcp_reno {cmd_string}"'
                    process = subprocess.Popen(['powershell', '-Command', cmd],
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.STDOUT,
                                             text=True,
                                             bufsize=1)
                else:
                    # Linux/Mac with bash
                    cmd = f'./ns3 run "scratch/tcp_reno_project/tcp_reno {cmd_string}"'
                    process = subprocess.Popen(cmd,
                                             shell=True,
                                             cwd=str(ns3_dir),
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.STDOUT,
                                             text=True,
                                             bufsize=1)
                
                self.simulation_process = process
                
                # Read output line by line
                for line in process.stdout:
                    if not self.is_running:
                        process.kill()
                        all_success = False
                        break
                    self.log_to_console(line)
                
                # Wait for completion
                return_code = process.wait()
                
                # Clean up process
                self.simulation_process = None
                
                if return_code != 0:
                    self.log_to_console(f"\n❌ Simulation {queue_type} failed with code {return_code}\n", 'error')
                    self.log_to_console(f"💡 Check if results directory exists and is writable\n", 'warning')
                    all_success = False
                    break
                else:
                    self.log_to_console(f"\n✅ {queue_type} simulation completed!\n", 'success')
                    # Small delay between simulations
                    if i < len(queue_types) - 1:
                        self.log_to_console(f"\n⏳ Waiting 2 seconds before next simulation...\n", 'info')
                        time.sleep(2)
            
            if all_success and self.is_running:
                self.log_to_console("\n" + "="*60 + "\n", 'info')
                self.log_to_console("✅ All simulations completed successfully!\n", 'success')
                self.log_to_console(f"📁 Results saved to: {self.project_dir / 'results'}\n", 'info')
                self._simulation_finished(True)
            else:
                self._simulation_finished(False)
                
        except Exception as e:
            self.log_to_console(f"\n❌ Error: {str(e)}\n", 'error')
            self._simulation_finished(False)
    
    def stop_simulation(self):
        """Stop running simulation"""
        if self.simulation_process:
            self.is_running = False
            self.simulation_process.kill()
            self.log_to_console("\n⏹️ Simulation stopped by user\n", 'warning')
            self._simulation_finished(False)
    
    def _simulation_finished(self, success):
        """Update UI after simulation finishes"""
        self.root.after(0, self._update_simulation_ui, success)
    
    def _update_simulation_ui(self, success):
        """Update UI on main thread"""
        self.is_running = False
        self.btn_run.configure(state=tk.NORMAL)
        self.btn_stop.configure(state=tk.DISABLED)
        self.progress_bar.stop()
        
        if success:
            self.status_var.set("✅ Simulation completed successfully")
            self.progress_label.config(text="✅ All simulations completed!")
            self.refresh_file_list()
        else:
            self.status_var.set("❌ Simulation failed or was stopped")
            self.progress_label.config(text="❌ Simulation stopped or failed")
    
    def log_to_console(self, message, tag='normal'):
        """Thread-safe logging to console"""
        self.root.after(0, self._append_to_console, message, tag)
    
    def _append_to_console(self, message, tag):
        """Append message to console (must run on main thread)"""
        self.console.insert(tk.END, message)
        self.console.see(tk.END)
        self.root.update_idletasks()
    
    # ============= ANALYSIS METHODS =============
    
    def run_analysis(self, analysis_type):
        """Run analysis command"""
        self.analysis_output.delete('1.0', tk.END)
        
        # Check if results exist
        if not self.results_dir.exists() or not any(self.results_dir.glob('*.tr')):
            messagebox.showwarning("Warning", 
                                 "No simulation data found!\nPlease run simulation first.")
            return
        
        # Build command
        queue_type = self.analysis_queue.get()
        
        commands = {
            'dashboard': f'{self.python_cmd} main.py --queue {queue_type} --dashboard',
            'timeline': f'{self.python_cmd} main.py --queue {queue_type} --timeline',
            'print': f'{self.python_cmd} main.py --queue {queue_type} --print',
            'comparison': f'{self.python_cmd} main.py --compare --dashboard',
            'infographic-pdf': f'{self.python_cmd} main.py --infographic',
            'infographic-gui': f'{self.python_cmd} main.py --infographic --gui'
        }
        
        cmd = commands.get(analysis_type)
        if not cmd:
            return
        
        self.analysis_output.insert(tk.END, f"🔄 Running: {cmd}\n\n")
        
        # Run in thread
        thread = threading.Thread(target=self._run_analysis_thread, args=(cmd,))
        thread.daemon = True
        thread.start()
    
    def _run_analysis_thread(self, cmd):
        """Thread worker for analysis"""
        try:
            # Run from analyze directory
            process = subprocess.Popen(cmd,
                                     shell=True,
                                     cwd=str(self.analyze_dir),
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT,
                                     text=True)
            
            # Read output
            for line in process.stdout:
                self.root.after(0, self._append_to_analysis, line)
            
            process.wait()
            
            if process.returncode == 0:
                self.root.after(0, self._append_to_analysis, 
                              "\n✅ Analysis completed!\n")
            else:
                self.root.after(0, self._append_to_analysis,
                              f"\n❌ Analysis failed with code {process.returncode}\n")
                              
        except Exception as e:
            self.root.after(0, self._append_to_analysis, 
                          f"\n❌ Error: {str(e)}\n")
    
    def _append_to_analysis(self, message):
        """Append to analysis output"""
        self.analysis_output.insert(tk.END, message)
        self.analysis_output.see(tk.END)
    
    # ============= RESULTS METHODS =============
    
    def refresh_file_list(self):
        """Refresh file list in results browser"""
        # Clear current items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Check if results directory exists
        if not self.results_dir.exists():
            return
        
        # List all files
        for file_path in sorted(self.results_dir.glob('*')):
            if file_path.is_file():
                # Get file info
                stat = file_path.stat()
                size_kb = stat.st_size / 1024
                mod_time = time.strftime('%Y-%m-%d %H:%M:%S', 
                                        time.localtime(stat.st_mtime))
                
                # Determine file type
                ext = file_path.suffix.lower()
                if ext == '.tr':
                    file_type = '📊 Trace File'
                elif ext == '.txt':
                    file_type = '📝 Summary'
                elif ext == '.png':
                    file_type = '🖼️ Plot'
                elif ext == '.pdf':
                    file_type = '📄 Report'
                else:
                    file_type = '📄 File'
                
                # Add to tree
                self.file_tree.insert('', tk.END,
                                    text=file_path.name,
                                    values=(file_type, 
                                          f'{size_kb:.1f} KB',
                                          mod_time))
    
    def open_results_folder(self):
        """Open results folder in file explorer"""
        if not self.results_dir.exists():
            messagebox.showinfo("Info", "Results folder doesn't exist yet.\nRun simulation first.")
            return
        
        if sys.platform == 'win32':
            os.startfile(self.results_dir)
        elif sys.platform == 'darwin':
            subprocess.run(['open', str(self.results_dir)])
        else:
            subprocess.run(['xdg-open', str(self.results_dir)])
    
    def clear_results(self):
        """Clear all results"""
        if not self.results_dir.exists():
            return
        
        result = messagebox.askyesno("Confirm", 
                                    "Delete all files in results folder?\nThis cannot be undone!")
        if result:
            try:
                for file_path in self.results_dir.glob('*'):
                    if file_path.is_file():
                        file_path.unlink()
                messagebox.showinfo("Success", "Results cleared!")
                self.refresh_file_list()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to clear results:\n{str(e)}")


def main():
    """Main entry point"""
    try:
        root = tk.Tk()
        app = TCPRenoGUI(root)
        root.mainloop()
    except Exception as e:
        import traceback
        print(f"❌ Error starting GUI: {str(e)}")
        print("\nFull traceback:")
        traceback.print_exc()
        input("\nPress Enter to exit...")


if __name__ == "__main__":
    main()
