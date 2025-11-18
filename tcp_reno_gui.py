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

# Tooltip class for hover help
class ToolTip:
    """Create a tooltip for a given widget"""
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)
    
    def show_tooltip(self, event=None):
        # Get widget position
        x = self.widget.winfo_rootx() + 25
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5
        
        # Create tooltip window
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        
        # Create label with text
        label = tk.Label(self.tooltip, text=self.text, 
                        justify=tk.LEFT,
                        background="#FFFFDD", 
                        foreground="#000000",
                        relief=tk.SOLID, 
                        borderwidth=1,
                        font=("Arial", 9),
                        wraplength=500,
                        padx=10, pady=8)
        label.pack()
    
    def hide_tooltip(self, event=None):
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None

class TCPRenoGUI:
    # Parameter descriptions and help text
    PARAM_INFO = {
        'duration': {
            'name': 'Duration (s)',
            'desc': 'Thời gian chạy simulation (giây)',
            'help': 'Thời gian mô phỏng sẽ chạy. Giá trị càng lớn, càng thu thập được nhiều dữ liệu về hành vi TCP, nhưng mất nhiều thời gian hơn.\n\nĐề xuất: 20-100 giây\nVí dụ: 20 (cho test nhanh), 60 (cho phân tích chi tiết)'
        },
        'num_flows': {
            'name': 'Number of Flows',
            'desc': 'Số luồng TCP đồng thời (1-3)',
            'help': 'Số lượng kết nối TCP chạy song song qua bottleneck link. Nhiều flows → tranh chấp bandwidth nhiều hơn → dễ quan sát congestion.\n\nĐề xuất: 3 flows\n• 1 flow: Quan sát thuần túy 1 kết nối\n• 2-3 flows: Quan sát sự cạnh tranh và fairness'
        },
        'mtu': {
            'name': 'MTU (Maximum Transmission Unit)',
            'desc': 'Kích thước tối đa của gói IP (bytes)',
            'help': 'Kích thước tối đa của một IP packet (bao gồm header). MTU càng lớn → packet càng lớn → hiệu quả truyền tải cao hơn nhưng nếu mất packet thì mất nhiều data hơn.\n\nĐề xuất: 1500 bytes (chuẩn Ethernet)\nPhạm vi: 576-9000 bytes\n\n• 1500: Ethernet chuẩn\n• 1420-1460: Khi có VPN/tunneling\n• 9000: Jumbo frames (mạng datacenter)'
        },
        'cwnd': {
            'name': 'Initial CWND',
            'desc': 'Congestion Window ban đầu (segments)',
            'help': 'Kích thước Congestion Window khi bắt đầu kết nối. CWND quy định số segments có thể gửi trước khi nhận ACK.\n\nĐề xuất: 1 segment (theo RFC 5681)\nPhạm vi: 1-10 segments\n\n• 1: Slow start từ đầu (chuẩn TCP Reno)\n• 10: Initial Window cải tiến (RFC 6928)\n\nCWND sẽ tăng exponentially trong slow start phase, sau đó linear trong congestion avoidance.'
        },
        'ssthresh': {
            'name': 'Slow Start Threshold',
            'desc': 'Ngưỡng chuyển từ Slow Start sang Congestion Avoidance',
            'help': 'Ngưỡng quyết định khi nào TCP chuyển từ Slow Start (tăng gấp đôi CWND) sang Congestion Avoidance (tăng tuyến tính).\n\nĐề xuất: 65535 segments (vô hạn thực tế)\nPhạm vi: 2-65535 segments\n\n• 65535: Để TCP tự động điều chỉnh dựa trên packet loss\n• Giá trị nhỏ hơn: Buộc vào CA mode sớm hơn\n\nKhi có packet loss, ssthresh = cwnd/2, sau đó CWND reset về 1.'
        },
        'queue_size': {
            'name': 'Queue Size',
            'desc': 'Kích thước buffer tại bottleneck router (packets)',
            'help': 'Số lượng packets tối đa có thể chờ trong queue tại router bottleneck. Queue càng lớn → delay càng cao nhưng ít loss hơn.\n\nĐề xuất: 25 packets\nPhạm vi: 10-100 packets\n\n• Nhỏ (10-20): Ít delay, nhiều loss → RED hiệu quả\n• Trung bình (25-50): Cân bằng\n• Lớn (>50): Bufferbloat → delay cao\n\nQueue đầy → DropTail drop hết packets mới, RED drop ngẫu nhiên sớm hơn.'
        },
        'bottleneck_bw': {
            'name': 'Bottleneck Bandwidth',
            'desc': 'Băng thông của link nghẽn (bottleneck)',
            'help': 'Băng thông của link chậm nhất trong mạng - nơi xảy ra congestion. Đây là điểm chính để quan sát hành vi queue.\n\nĐề xuất: 5Mbps\nFormat: số + đơn vị (bps, Kbps, Mbps, Gbps)\n\n• 1-5Mbps: Dễ tạo congestion\n• 10-100Mbps: Mạng trung bình\n• 1Gbps+: Mạng tốc độ cao\n\nBottleneck < Sender/Receiver BW → packets tích tụ trong queue → quan sát được TCP congestion control.'
        },
        'bottleneck_delay': {
            'name': 'Bottleneck Delay',
            'desc': 'Độ trễ lan truyền của bottleneck link',
            'help': 'Propagation delay của bottleneck link (thời gian 1 bit đi từ đầu này sang đầu kia). Delay cao → RTT cao → TCP phản ứng chậm hơn.\n\nĐề xuất: 10ms\nPhạm vi: 1-100ms\n\n• 1-10ms: LAN, datacenter\n• 10-50ms: WAN trong nước\n• 50-200ms: Quốc tế, vệ tinh\n\nTotal RTT = 2×(sender_delay + bottleneck_delay + receiver_delay) + queueing delay'
        },
        'sender_bw': {
            'name': 'Sender Bandwidth',
            'desc': 'Băng thông link từ sender đến router',
            'help': 'Băng thông kết nối từ máy gửi tới router. Thường lớn hơn bottleneck để không tạo nghẽn tại đây.\n\nĐề xuất: 10Mbps (gấp đôi bottleneck)\nFormat: số + đơn vị (Mbps, Gbps)\n\n• Nên >= 2× bottleneck BW\n• Nếu sender BW < bottleneck → nghẽn ngay tại sender (không đúng mục đích test)'
        },
        'receiver_bw': {
            'name': 'Receiver Bandwidth',
            'desc': 'Băng thông link từ router đến receiver',
            'help': 'Băng thông kết nối từ router tới máy nhận. Thường lớn hơn bottleneck để không tạo nghẽn tại đây.\n\nĐề xuất: 10Mbps (gấp đôi bottleneck)\nFormat: số + đơn vị (Mbps, Gbps)\n\n• Nên >= 2× bottleneck BW\n• Nếu receiver BW < bottleneck → nghẽn tại receiver (không đúng mục đích test)'
        },
        'error_rate': {
            'name': 'Packet Error Rate',
            'desc': 'Tỷ lệ mất gói ngẫu nhiên (0.0-1.0)',
            'help': 'Xác suất một packet bị drop ngẫu nhiên do lỗi đường truyền (không phải do queue full). Dùng để mô phỏng mạng không tin cậy.\n\n⚠️ LUU Ý: Error rate quá cao có thể làm simulation THẤT BẠI!\n\nĐề xuất: 0 hoặc 0.001-0.01 (0.1-1%)\nPhạm vi an toàn: 0.0-0.02\n\n• 0: Không có lỗi truyền (chỉ loss do queue)\n• 0.001-0.01 (0.1-1%): Mạng kém, vẫn hoạt động\n• 0.01-0.02 (1-2%): Mạng wireless/mobile\n• >0.02 (>2%): NGUY HIỂM - có thể không thiết lập được TCP connection!\n\n❗ Error rate 0.05 (5%) sẽ drop 5% packets, kể cả SYN packets → TCP không thể handshake → simulation thất bại với 0 throughput.\n\nNếu muốn test với loss cao, dùng queue size nhỏ thay vì error rate.'
        },
        'sack': {
            'name': 'SACK (Selective Acknowledgment)',
            'desc': 'Cho phép ACK từng segment riêng lẻ',
            'help': 'SACK (RFC 2018) cho phép receiver thông báo chính xác segments nào đã nhận được, giúp sender chỉ retransmit các segments bị mất thay vì toàn bộ window.\n\nĐề xuất: Enabled (true)\n\n• Enabled: Hiệu quả cao hơn, ít retransmit lãng phí\n• Disabled: TCP truyền thống, phải retransmit nhiều segments\n\nVí dụ: Mất segment 5 trong chuỗi 1-10\n→ Với SACK: Chỉ gửi lại segment 5\n→ Không SACK: Phải gửi lại 5-10'
        },
        'nagle': {
            'name': "Nagle's Algorithm",
            'desc': 'Gộp các gói nhỏ thành gói lớn',
            'help': "Nagle's Algorithm (RFC 896) trì hoãn gửi các packets nhỏ, đợi gộp thành packets lớn hơn hoặc đợi ACK của packet trước. Giảm overhead nhưng tăng latency.\n\nĐề xuất: Disabled (false)\n\n• Enabled: Giảm số packets → ít overhead\n  → Tốt cho: Telnet, SSH (gõ từng ký tự)\n\n• Disabled: Gửi ngay lập tức\n  → Tốt cho: Bulk transfer, game online (cần low latency)\n\nVới TCP Reno test, thường disable để quan sát pure TCP behavior."
        },
        'queue_type': {
            'name': 'Queue Management Algorithm',
            'desc': 'Thuật toán quản lý hàng đợi tại router',
            'help': 'Cơ chế quyết định khi nào và packet nào bị drop khi queue đầy:\n\n📦 DropTail (FIFO):\n• Drop packets khi queue đầy 100%\n• Đơn giản nhưng gây "global synchronization"\n• Tất cả flows cùng lúc giảm CWND → underutilization\n\n🔴 RED (Random Early Detection):\n• Drop ngẫu nhiên packets khi queue đạt ngưỡng (MinTh)\n• Tăng xác suất drop khi queue càng đầy\n• Phòng ngừa global sync, cải thiện fairness\n• Phức tạp hơn nhưng hiệu quả cao hơn\n\n💡 So sánh: RED thường cho throughput ổn định hơn và delay thấp hơn DropTail.'
        }
    }
    
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
        
        # Queue Types with help
        queue_label = ttk.Label(config_frame, text="Queue Types to Simulate:", 
                 font=('Arial', 10, 'bold'))
        queue_label.grid(row=0, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        help_btn = ttk.Button(config_frame, text="?", width=3,
                             command=lambda: messagebox.showinfo("Queue Types Help", 
                                                                 self.PARAM_INFO['queue_type']['help']))
        help_btn.grid(row=0, column=2, sticky=tk.W, padx=5)
        
        self.queue_droptail = tk.BooleanVar(value=True)
        self.queue_red = tk.BooleanVar(value=True)
        
        dt_cb = ttk.Checkbutton(config_frame, text="DropTail", variable=self.queue_droptail)
        dt_cb.grid(row=1, column=0, sticky=tk.W, padx=(20, 0))
        ToolTip(dt_cb, "DropTail: Simple FIFO queue, drops when full")
        
        red_cb = ttk.Checkbutton(config_frame, text="RED", variable=self.queue_red)
        red_cb.grid(row=1, column=1, sticky=tk.W)
        ToolTip(red_cb, "RED: Random Early Detection, proactive dropping")
        
        # Basic Parameters
        ttk.Separator(config_frame, orient=tk.HORIZONTAL).grid(row=2, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        ttk.Label(config_frame, text="Basic Parameters:", 
                 font=('Arial', 10, 'bold')).grid(row=3, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Row 4: Duration and Num Flows
        dur_label = ttk.Label(config_frame, text="Duration (s):")
        dur_label.grid(row=4, column=0, sticky=tk.W, padx=(20, 0), pady=5)
        ToolTip(dur_label, self.PARAM_INFO['duration']['desc'])
        
        self.sim_time = tk.StringVar(value="20")
        dur_entry = ttk.Entry(config_frame, textvariable=self.sim_time, width=12)
        dur_entry.grid(row=4, column=1, sticky=tk.W, pady=5)
        ToolTip(dur_entry, self.PARAM_INFO['duration']['help'])
        
        nf_label = ttk.Label(config_frame, text="Num Flows:")
        nf_label.grid(row=4, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        ToolTip(nf_label, self.PARAM_INFO['num_flows']['desc'])
        
        self.num_flows = tk.StringVar(value="3")
        nf_spin = ttk.Spinbox(config_frame, from_=1, to=3, textvariable=self.num_flows, width=10)
        nf_spin.grid(row=4, column=3, sticky=tk.W, pady=5)
        ToolTip(nf_spin, self.PARAM_INFO['num_flows']['help'])
        
        # Row 5: MTU and CWND
        mtu_label = ttk.Label(config_frame, text="MTU (bytes):")
        mtu_label.grid(row=5, column=0, sticky=tk.W, padx=(20, 0), pady=5)
        ToolTip(mtu_label, self.PARAM_INFO['mtu']['desc'])
        
        self.mtu = tk.StringVar(value="1500")
        mtu_entry = ttk.Entry(config_frame, textvariable=self.mtu, width=12)
        mtu_entry.grid(row=5, column=1, sticky=tk.W, pady=5)
        ToolTip(mtu_entry, self.PARAM_INFO['mtu']['help'])
        
        cwnd_label = ttk.Label(config_frame, text="Init CWND:")
        cwnd_label.grid(row=5, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        ToolTip(cwnd_label, self.PARAM_INFO['cwnd']['desc'])
        
        self.cwnd = tk.StringVar(value="1")
        cwnd_entry = ttk.Entry(config_frame, textvariable=self.cwnd, width=10)
        cwnd_entry.grid(row=5, column=3, sticky=tk.W, pady=5)
        ToolTip(cwnd_entry, self.PARAM_INFO['cwnd']['help'])
        
        # Row 6: SSThresh and Queue Size
        sst_label = ttk.Label(config_frame, text="SSThresh:")
        sst_label.grid(row=6, column=0, sticky=tk.W, padx=(20, 0), pady=5)
        ToolTip(sst_label, self.PARAM_INFO['ssthresh']['desc'])
        
        self.ssthresh = tk.StringVar(value="65535")
        sst_entry = ttk.Entry(config_frame, textvariable=self.ssthresh, width=12)
        sst_entry.grid(row=6, column=1, sticky=tk.W, pady=5)
        ToolTip(sst_entry, self.PARAM_INFO['ssthresh']['help'])
        
        qs_label = ttk.Label(config_frame, text="Queue Size:")
        qs_label.grid(row=6, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        ToolTip(qs_label, self.PARAM_INFO['queue_size']['desc'])
        
        self.tcp_queue_size = tk.StringVar(value="25")
        qs_entry = ttk.Entry(config_frame, textvariable=self.tcp_queue_size, width=10)
        qs_entry.grid(row=6, column=3, sticky=tk.W, pady=5)
        ToolTip(qs_entry, self.PARAM_INFO['queue_size']['help'])
        
        # Network Parameters
        ttk.Separator(config_frame, orient=tk.HORIZONTAL).grid(row=7, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        ttk.Label(config_frame, text="Network Parameters:", 
                 font=('Arial', 10, 'bold')).grid(row=8, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        # Row 9: Bottleneck
        bb_label = ttk.Label(config_frame, text="Bottleneck BW:")
        bb_label.grid(row=9, column=0, sticky=tk.W, padx=(20, 0), pady=5)
        ToolTip(bb_label, self.PARAM_INFO['bottleneck_bw']['desc'])
        
        self.bottleneck_bw = tk.StringVar(value="5Mbps")
        bb_entry = ttk.Entry(config_frame, textvariable=self.bottleneck_bw, width=12)
        bb_entry.grid(row=9, column=1, sticky=tk.W, pady=5)
        ToolTip(bb_entry, self.PARAM_INFO['bottleneck_bw']['help'])
        
        bd_label = ttk.Label(config_frame, text="Delay:")
        bd_label.grid(row=9, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        ToolTip(bd_label, self.PARAM_INFO['bottleneck_delay']['desc'])
        
        self.bottleneck_delay = tk.StringVar(value="10ms")
        bd_entry = ttk.Entry(config_frame, textvariable=self.bottleneck_delay, width=10)
        bd_entry.grid(row=9, column=3, sticky=tk.W, pady=5)
        ToolTip(bd_entry, self.PARAM_INFO['bottleneck_delay']['help'])
        
        # Row 10: Sender/Receiver
        sb_label = ttk.Label(config_frame, text="Sender BW:")
        sb_label.grid(row=10, column=0, sticky=tk.W, padx=(20, 0), pady=5)
        ToolTip(sb_label, self.PARAM_INFO['sender_bw']['desc'])
        
        self.sender_bw = tk.StringVar(value="10Mbps")
        sb_entry = ttk.Entry(config_frame, textvariable=self.sender_bw, width=12)
        sb_entry.grid(row=10, column=1, sticky=tk.W, pady=5)
        ToolTip(sb_entry, self.PARAM_INFO['sender_bw']['help'])
        
        rb_label = ttk.Label(config_frame, text="Receiver BW:")
        rb_label.grid(row=10, column=2, sticky=tk.W, padx=(20, 0), pady=5)
        ToolTip(rb_label, self.PARAM_INFO['receiver_bw']['desc'])
        
        self.receiver_bw = tk.StringVar(value="10Mbps")
        rb_entry = ttk.Entry(config_frame, textvariable=self.receiver_bw, width=10)
        rb_entry.grid(row=10, column=3, sticky=tk.W, pady=5)
        ToolTip(rb_entry, self.PARAM_INFO['receiver_bw']['help'])
        
        # Row 11: Error Rate
        err_label = ttk.Label(config_frame, text="Error Rate:")
        err_label.grid(row=11, column=0, sticky=tk.W, padx=(20, 0), pady=5)
        ToolTip(err_label, self.PARAM_INFO['error_rate']['desc'])
        
        self.error_rate = tk.StringVar(value="0")
        err_entry = ttk.Entry(config_frame, textvariable=self.error_rate, width=12)
        err_entry.grid(row=11, column=1, sticky=tk.W, pady=5)
        ToolTip(err_entry, self.PARAM_INFO['error_rate']['help'])
        
        # Options
        ttk.Separator(config_frame, orient=tk.HORIZONTAL).grid(row=12, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=10)
        ttk.Label(config_frame, text="Options:", 
                 font=('Arial', 10, 'bold')).grid(row=13, column=0, columnspan=2, sticky=tk.W, pady=5)
        
        self.enable_sack = tk.BooleanVar(value=True)
        sack_cb = ttk.Checkbutton(config_frame, text="Enable SACK", variable=self.enable_sack)
        sack_cb.grid(row=14, column=0, columnspan=2, sticky=tk.W, padx=(20, 0), pady=2)
        ToolTip(sack_cb, self.PARAM_INFO['sack']['help'])
        
        self.enable_nagle = tk.BooleanVar(value=False)
        nagle_cb = ttk.Checkbutton(config_frame, text="Enable Nagle", variable=self.enable_nagle)
        nagle_cb.grid(row=14, column=2, columnspan=2, sticky=tk.W, pady=2)
        ToolTip(nagle_cb, self.PARAM_INFO['nagle']['help'])
        
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
        info_frame.grid(row=0, column=0, columnspan=2, pady=(0, 10), sticky=tk.W)
        
        ttk.Label(info_frame,
                 text="📊 Choose analysis and visualization options:",
                 font=('Arial', 12, 'bold'),
                 foreground='#2C3E50').grid(row=0, column=0, sticky=tk.W)
        
        ttk.Label(info_frame,
                 text="Make sure you have run the simulation first to generate data.",
                 font=('Arial', 9, 'italic'),
                 foreground='#7F8C8D').grid(row=1, column=0, sticky=tk.W, pady=(5, 0))
        
        # Run selector
        run_frame = ttk.Frame(self.tab_analysis)
        run_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 15))
        
        ttk.Label(run_frame, text="🔍 Select Run to Analyze:",
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, sticky=tk.W)
        
        self.analysis_run_filter = ttk.Combobox(run_frame, width=50, state='readonly')
        self.analysis_run_filter.grid(row=0, column=1, padx=5)
        self.analysis_run_filter['values'] = ['Latest Run']
        self.analysis_run_filter.current(0)
        
        ttk.Button(run_frame, text="🔄",
                  command=self.update_analysis_runs,
                  width=3).grid(row=0, column=2, padx=5)
        
        # Left panel - Single Queue Analysis
        left_frame = ttk.LabelFrame(self.tab_analysis,
                                   text="📈 Single Queue Analysis",
                                   padding=15)
        left_frame.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N), padx=(0, 10))
        
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
        right_frame.grid(row=2, column=1, sticky=(tk.W, tk.E, tk.N))
        
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
        output_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S), pady=20)
        self.tab_analysis.rowconfigure(3, weight=1)
        
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
        # Filter section
        filter_frame = ttk.Frame(self.tab_results)
        filter_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        ttk.Label(filter_frame, text="🔍 Filter by Run:",
                 font=('Arial', 10, 'bold')).grid(row=0, column=0, padx=5, sticky=tk.W)
        
        self.run_filter = ttk.Combobox(filter_frame, width=40, state='readonly')
        self.run_filter.grid(row=0, column=1, padx=5)
        self.run_filter.bind('<<ComboboxSelected>>', lambda e: self.refresh_file_list())
        
        ttk.Button(filter_frame, text="🔄 Refresh",
                  command=self.update_run_filter,
                  width=15).grid(row=0, column=2, padx=5)
        
        # File list
        list_frame = ttk.LabelFrame(self.tab_results,
                                   text="📁 Generated Files",
                                   padding=10)
        list_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        self.tab_results.rowconfigure(1, weight=1)
        
        # Treeview for file list
        self.file_tree = ttk.Treeview(list_frame, 
                                     columns=('Type', 'Queue', 'Size', 'Modified'),
                                     height=15)
        self.file_tree.heading('#0', text='File Name')
        self.file_tree.heading('Type', text='Type')
        self.file_tree.heading('Queue', text='Queue Type')
        self.file_tree.heading('Size', text='Size')
        self.file_tree.heading('Modified', text='Last Modified')
        
        self.file_tree.column('#0', width=350)
        self.file_tree.column('Type', width=120)
        self.file_tree.column('Queue', width=100)
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
        button_frame.grid(row=2, column=0, pady=10)
        
        ttk.Button(button_frame,
                  text="📂 Open Results Folder",
                  command=self.open_results_folder,
                  width=20).grid(row=0, column=0, padx=5)
        
        ttk.Button(button_frame,
                  text="🗑️ Clear All Results",
                  command=self.clear_results,
                  width=20).grid(row=0, column=1, padx=5)
        
        ttk.Button(button_frame,
                  text="🗑️ Delete Selected Run",
                  command=self.delete_selected_run,
                  width=20).grid(row=0, column=2, padx=5)
        
        # Auto-refresh file list
        self.update_run_filter()
        
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
        
    def create_labeled_entry_with_help(self, parent, row, col, param_key, variable, **kwargs):
        """Create label + entry + help icon with tooltip"""
        info = self.PARAM_INFO.get(param_key, {})
        
        # Label
        label = ttk.Label(parent, text=info.get('name', param_key) + ":")
        label.grid(row=row, column=col, sticky=tk.W, padx=(20, 0), pady=5)
        
        # Add tooltip to label if description exists
        if 'desc' in info:
            ToolTip(label, info['desc'])
        
        # Entry widget
        entry = ttk.Entry(parent, textvariable=variable, **kwargs)
        entry.grid(row=row, column=col+1, sticky=tk.W, pady=5)
        
        # Add tooltip to entry with full help text
        if 'help' in info:
            ToolTip(entry, info['help'])
        
        return label, entry
    
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
                if error_rate > 0.02:
                    self.log_to_console(f"⚠️  WARNING: High error rate ({error_rate*100:.1f}%) may prevent TCP connection establishment!\n", 'warning')
                    self.log_to_console("   Recommended: 0-0.01 (0-1%) for stable connections\n", 'warning')
                    
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
                # Use consistent decimal format for error_rate (ensure . not ,)
                error_rate_str = str(error_rate).replace(',', '.')
                
                cmd_params = [
                    f"--queueType={queue_type}",
                    f"--duration={sim_time}",
                    f"--numFlows={num_flows}",
                    f"--mtu={mtu}",
                    f"--cwnd={cwnd}",
                    f"--ssthresh={ssthresh}",
                    f"--tcp_queue_size={tcp_queue_size}",
                    f"--error_p={error_rate_str}",
                    f"--bottleneck_bandwidth={self.bottleneck_bw.get()}",
                    f"--bottleneck_delay={self.bottleneck_delay.get()}",
                    f"--s_bandwidth={self.sender_bw.get()}",
                    f"--r_bandwidth={self.receiver_bw.get()}",
                    f"--sack={'true' if self.enable_sack.get() else 'false'}",
                    f"--nagle={'true' if self.enable_nagle.get() else 'false'}"
                ]
                
                cmd_string = " ".join(cmd_params)
                
                # Log the command for debugging
                self.log_to_console(f"\n📝 Command: ./ns3 run \"scratch/tcp_reno_project/tcp_reno {cmd_string}\"\n\n", 'info')
                
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
            self.update_run_filter()
            self.update_analysis_runs()
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
    
    def update_analysis_runs(self):
        """Update run filter in analysis tab"""
        if not self.results_dir.exists():
            self.analysis_run_filter['values'] = ['Latest Run']
            self.analysis_run_filter.current(0)
            return
        
        # Find all unique run identifiers
        runs = set()
        import re
        
        for file_path in self.results_dir.glob('*'):
            if file_path.is_file():
                # Extract timestamp from filename
                match = re.search(r'P2P-project_(\d{8}_\d{6})', file_path.name)
                if match:
                    timestamp = match.group(1)
                    runs.add(timestamp)
        
        # Sort runs by timestamp (newest first)
        sorted_runs = sorted(runs, reverse=True)
        
        # Format timestamps for display
        formatted_runs = []
        for run in sorted_runs:
            if len(run) == 15:
                formatted = f"{run[0:4]}-{run[4:6]}-{run[6:8]} {run[9:11]}:{run[11:13]}:{run[13:15]}"
                formatted_runs.append(f"{formatted} ({run})")
            else:
                formatted_runs.append(run)
        
        # Add options
        all_options = ['Latest Run', 'Legacy Files (no timestamp)'] + formatted_runs
        
        # Update combobox
        current = self.analysis_run_filter.get()
        self.analysis_run_filter['values'] = all_options
        
        if current not in all_options:
            self.analysis_run_filter.current(0)
    
    def run_analysis(self, analysis_type):
        """Run analysis command"""
        self.analysis_output.delete('1.0', tk.END)
        
        # Check if results exist
        if not self.results_dir.exists() or not any(self.results_dir.glob('*.tr')):
            messagebox.showwarning("Warning", 
                                 "No simulation data found!\nPlease run simulation first.")
            return
        
        # Get selected run
        run_selection = self.analysis_run_filter.get()
        prefix = "P2P-project"
        
        import re
        if run_selection and run_selection != 'Latest Run':
            if run_selection == 'Legacy Files (no timestamp)':
                prefix = "P2P-project"
            else:
                # Extract timestamp
                match = re.search(r'\((\d{8}_\d{6})\)', run_selection)
                if match:
                    timestamp = match.group(1)
                    prefix = f"P2P-project_{timestamp}"
        
        # Build command
        queue_type = self.analysis_queue.get()
        
        commands = {
            'dashboard': f'{self.python_cmd} main.py --prefix "{prefix}" --queue {queue_type} --dashboard',
            'timeline': f'{self.python_cmd} main.py --prefix "{prefix}" --queue {queue_type} --timeline',
            'print': f'{self.python_cmd} main.py --prefix "{prefix}" --queue {queue_type} --print',
            'comparison': f'{self.python_cmd} main.py --prefix "{prefix}" --compare --dashboard',
            'infographic-pdf': f'{self.python_cmd} main.py --prefix "{prefix}" --infographic',
            'infographic-gui': f'{self.python_cmd} main.py --prefix "{prefix}" --infographic --gui'
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
    
    def update_run_filter(self):
        """Update run filter combobox with available runs"""
        if not self.results_dir.exists():
            self.run_filter['values'] = ['All Runs']
            self.run_filter.current(0)
            self.refresh_file_list()
            return
        
        # Find all unique run identifiers (timestamps)
        runs = set()
        import re
        
        for file_path in self.results_dir.glob('*'):
            if file_path.is_file():
                # Extract timestamp from filename
                # Pattern: P2P-project_YYYYMMDD_HHMMSS_*
                match = re.search(r'P2P-project_(\d{8}_\d{6})', file_path.name)
                if match:
                    timestamp = match.group(1)
                    runs.add(timestamp)
        
        # Sort runs by timestamp (newest first)
        sorted_runs = sorted(runs, reverse=True)
        
        # Format timestamps for display
        formatted_runs = []
        for run in sorted_runs:
            # Format: YYYYMMDD_HHMMSS -> YYYY-MM-DD HH:MM:SS
            if len(run) == 15:  # YYYYMMDD_HHMMSS
                formatted = f"{run[0:4]}-{run[4:6]}-{run[6:8]} {run[9:11]}:{run[11:13]}:{run[13:15]}"
                formatted_runs.append(f"{formatted} ({run})")
            else:
                formatted_runs.append(run)
        
        # Add "All Runs" option
        all_options = ['All Runs', 'Legacy Files (no timestamp)'] + formatted_runs
        
        # Update combobox
        current = self.run_filter.get()
        self.run_filter['values'] = all_options
        
        # Set to first option if current is not valid
        if current not in all_options:
            self.run_filter.current(0)
        
        # Refresh file list
        self.refresh_file_list()
    
    def refresh_file_list(self):
        """Refresh file list in results browser"""
        # Clear current items
        for item in self.file_tree.get_children():
            self.file_tree.delete(item)
        
        # Check if results directory exists
        if not self.results_dir.exists():
            return
        
        # Get selected run filter
        filter_value = self.run_filter.get()
        import re
        
        # Extract timestamp from filter if selected
        selected_timestamp = None
        if filter_value and filter_value != 'All Runs':
            if filter_value == 'Legacy Files (no timestamp)':
                selected_timestamp = 'LEGACY'
            else:
                # Extract timestamp from formatted string
                match = re.search(r'\((\d{8}_\d{6})\)', filter_value)
                if match:
                    selected_timestamp = match.group(1)
        
        # List all files
        for file_path in sorted(self.results_dir.glob('*'), reverse=True):
            if file_path.is_file():
                # Check if file matches filter
                if selected_timestamp:
                    if selected_timestamp == 'LEGACY':
                        # Legacy files don't have timestamp
                        if re.search(r'P2P-project_\d{8}_\d{6}', file_path.name):
                            continue
                    else:
                        # Only show files with matching timestamp
                        if selected_timestamp not in file_path.name:
                            continue
                
                # Get file info
                stat = file_path.stat()
                size_kb = stat.st_size / 1024
                mod_time = time.strftime('%Y-%m-%d %H:%M:%S', 
                                        time.localtime(stat.st_mtime))
                
                # Determine file type
                ext = file_path.suffix.lower()
                if ext == '.tr':
                    file_type = '📊 Trace'
                elif ext == '.txt':
                    file_type = '📝 Summary'
                elif ext == '.log':
                    file_type = '📋 State Log'
                elif ext == '.png':
                    file_type = '🖼️ Plot'
                elif ext == '.pdf':
                    file_type = '📄 Report'
                else:
                    file_type = '📄 File'
                
                # Determine queue type
                queue_type = ''
                if 'DropTail' in file_path.name:
                    queue_type = 'DropTail'
                elif 'RED' in file_path.name:
                    queue_type = 'RED'
                
                # Add to tree
                self.file_tree.insert('', tk.END,
                                    text=file_path.name,
                                    values=(file_type,
                                          queue_type,
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
    
    def delete_selected_run(self):
        """Delete files from selected run"""
        if not self.results_dir.exists():
            return
        
        filter_value = self.run_filter.get()
        if filter_value == 'All Runs':
            messagebox.showinfo("Info", "Please select a specific run to delete.")
            return
        
        import re
        
        # Extract timestamp
        selected_timestamp = None
        if filter_value == 'Legacy Files (no timestamp)':
            selected_timestamp = 'LEGACY'
        else:
            match = re.search(r'\((\d{8}_\d{6})\)', filter_value)
            if match:
                selected_timestamp = match.group(1)
        
        if not selected_timestamp:
            messagebox.showerror("Error", "Could not identify run to delete.")
            return
        
        # Confirm deletion
        result = messagebox.askyesno("Confirm Delete", 
                                     f"Delete all files from run:\n{filter_value}\n\nThis cannot be undone!")
        if not result:
            return
        
        try:
            deleted_count = 0
            for file_path in self.results_dir.glob('*'):
                if file_path.is_file():
                    # Check if file belongs to selected run
                    if selected_timestamp == 'LEGACY':
                        # Delete legacy files (no timestamp)
                        if not re.search(r'P2P-project_\d{8}_\d{6}', file_path.name):
                            file_path.unlink()
                            deleted_count += 1
                    else:
                        # Delete files with matching timestamp
                        if selected_timestamp in file_path.name:
                            file_path.unlink()
                            deleted_count += 1
            
            messagebox.showinfo("Success", f"Deleted {deleted_count} files from selected run!")
            self.update_run_filter()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to delete files:\n{str(e)}")
    
    def clear_results(self):
        """Clear all results"""
        if not self.results_dir.exists():
            return
        
        result = messagebox.askyesno("Confirm", 
                                    "Delete ALL files in results folder?\nThis cannot be undone!")
        if result:
            try:
                deleted_count = 0
                for file_path in self.results_dir.glob('*'):
                    if file_path.is_file():
                        file_path.unlink()
                        deleted_count += 1
                messagebox.showinfo("Success", f"Deleted {deleted_count} files!")
                self.update_run_filter()
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
