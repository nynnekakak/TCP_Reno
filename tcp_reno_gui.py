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
        self.root.geometry("1200x800")
        
        # Project paths
        self.project_dir = Path(__file__).parent
        self.analyze_dir = self.project_dir / "analyze"
        self.results_dir = self.project_dir / "results"
        
        # Simulation process
        self.simulation_process = None
        self.is_running = False
        
        # Setup GUI
        self.setup_styles()
        self.create_widgets()
        
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
        # Configuration section
        config_frame = ttk.LabelFrame(self.tab_simulation, 
                                     text="⚙️ Simulation Configuration",
                                     padding=15)
        config_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Queue Types
        ttk.Label(config_frame, text="Queue Types to Simulate:", 
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, sticky=tk.W, pady=5)
        
        self.queue_droptail = tk.BooleanVar(value=True)
        self.queue_red = tk.BooleanVar(value=True)
        
        ttk.Checkbutton(config_frame, text="DropTail", 
                       variable=self.queue_droptail).grid(row=1, column=0, sticky=tk.W, padx=(20, 0))
        ttk.Checkbutton(config_frame, text="RED", 
                       variable=self.queue_red).grid(row=1, column=1, sticky=tk.W)
        
        # Simulation Time
        ttk.Label(config_frame, text="Simulation Time (seconds):", 
                 font=('Arial', 10, 'bold')).grid(row=2, column=0, sticky=tk.W, pady=(10, 5))
        
        self.sim_time = tk.StringVar(value="20.0")
        ttk.Entry(config_frame, textvariable=self.sim_time, 
                 width=15).grid(row=3, column=0, sticky=tk.W, padx=(20, 0))
        
        # Real-time Visualization
        self.show_realtime = tk.BooleanVar(value=False)
        ttk.Checkbutton(config_frame, 
                       text="Show Real-time Visualization (plot_realtime.py)",
                       variable=self.show_realtime).grid(row=4, column=0, columnspan=2, 
                                                         sticky=tk.W, pady=(10, 0))
        
        # Control buttons
        button_frame = ttk.Frame(self.tab_simulation)
        button_frame.grid(row=1, column=0, pady=10)
        
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
        
        # Output console
        console_frame = ttk.LabelFrame(self.tab_simulation,
                                      text="📟 Console Output",
                                      padding=10)
        console_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        self.tab_simulation.rowconfigure(2, weight=1)
        
        self.console = scrolledtext.ScrolledText(console_frame,
                                                 width=100, height=20,
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
        
        help_content = """
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

3️⃣ What happens:
   • Compiles NS-3 simulation (if needed)
   • Runs TCP Reno simulation with configured parameters
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
→ Check NS-3 installation path
→ Verify tcp_reno.cc is in scratch/tcp_reno_project/

Problem: Analysis shows no data
→ Run simulation first to generate trace files
→ Check results/ directory for .tr files

Problem: Real-time plot doesn't show
→ Ensure plot_realtime.py has execute permissions
→ Check Python and matplotlib are properly installed

═══════════════════════════════════════════════════════════════════════════════

📞 PROJECT STRUCTURE
────────────────────

TCP_Reno/
├── tcp_reno.cc              # NS-3 simulation code
├── tcp_reno_gui.py          # This GUI application
├── plot_realtime.py         # Real-time visualization
├── CMakeLists.txt           # Build configuration
├── analyze/                 # Analysis tools
│   ├── main.py             # CLI interface
│   └── analyzer/           # Analysis modules
└── results/                 # Generated data and plots

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
        
        # Run in thread to avoid blocking UI
        thread = threading.Thread(target=self._run_simulation_thread)
        thread.daemon = True
        thread.start()
        
    def _run_simulation_thread(self):
        """Thread worker for running simulation"""
        try:
            # Build NS-3 command
            sim_time = self.sim_time.get()
            
            self.log_to_console(f"📊 Simulation time: {sim_time} seconds\n")
            self.log_to_console(f"📦 Queue types: ", 'info')
            
            if self.queue_droptail.get():
                self.log_to_console("DropTail ", 'success')
            if self.queue_red.get():
                self.log_to_console("RED ", 'success')
            self.log_to_console("\n")
            
            self.log_to_console("\n🔨 Building NS-3 project...\n", 'info')
            
            # Change to NS-3 directory and run
            cmd = f'./ns3 run "scratch/tcp_reno_project/tcp_reno --simTime={sim_time}"'
            
            # Use PowerShell on Windows
            if sys.platform == 'win32':
                # For Windows, we need to run from NS-3 directory
                ns3_dir = Path.home() / "ns-allinone-3.43" / "ns-3.43"
                if not ns3_dir.exists():
                    self.log_to_console(f"\n❌ NS-3 not found at {ns3_dir}\n", 'error')
                    self.log_to_console("Please update NS-3 path in tcp_reno_gui.py\n", 'warning')
                    self._simulation_finished(False)
                    return
                
                full_cmd = f'cd {ns3_dir}; {cmd}'
                process = subprocess.Popen(['powershell', '-Command', full_cmd],
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT,
                                         text=True,
                                         bufsize=1)
            else:
                # Linux/Mac
                process = subprocess.Popen(cmd,
                                         shell=True,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.STDOUT,
                                         text=True,
                                         bufsize=1)
            
            self.simulation_process = process
            
            # Read output line by line
            for line in process.stdout:
                if not self.is_running:
                    process.kill()
                    break
                self.log_to_console(line)
            
            # Wait for completion
            return_code = process.wait()
            
            if return_code == 0:
                self.log_to_console("\n✅ Simulation completed successfully!\n", 'success')
                self.log_to_console("📁 Results saved to: results/\n", 'info')
                self._simulation_finished(True)
            else:
                self.log_to_console(f"\n❌ Simulation failed with code {return_code}\n", 'error')
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
        
        if success:
            self.status_var.set("✅ Simulation completed successfully")
            self.refresh_file_list()
        else:
            self.status_var.set("❌ Simulation failed or was stopped")
    
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
            'dashboard': f'python main.py --dashboard {queue_type}',
            'timeline': f'python main.py --timeline {queue_type}',
            'print': f'python main.py --print {queue_type}',
            'comparison': 'python main.py --comparison',
            'infographic-pdf': 'python main.py --infographic',
            'infographic-gui': 'python main.py --infographic --gui'
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
    root = tk.Tk()
    app = TCPRenoGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
