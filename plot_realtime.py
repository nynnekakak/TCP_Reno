#!/usr/bin/env python3
"""
TCP Reno Real-time Visualization
Monitors cwnd trace and TCP state log files for live plotting
Compatible with ns-3.43
Auto-saves screenshots when simulation ends or switches
"""

import matplotlib.pyplot as plt
import matplotlib.animation as animation
import networkx as nx
import time
import os
import re
import sys
import glob

# ===============================
#  Configuration
# ===============================
class Config:
    def __init__(self):
        # Thư mục chứa dữ liệu - có thể là đường dẫn tương đối hoặc tuyệt đối
        self.result_dirs = [
            "scratch/tcp_reno_project/results",
            "results",
            "scratch/tcp-reno-project/results"
        ]
        
        # Patterns để tìm file
        self.cwnd_patterns = [
            "*_cwnd_trace_RED.tr",
            "*_cwnd_trace_DropTail.tr",
            "*_cwnd_trace_*.tr",
            "cwnd_trace_RED.tr",
            "cwnd_trace_DropTail.tr",
            "cwnd_trace.tr"
        ]
        
        self.state_patterns = [
            "*_tcp_state_RED.log",
            "*_tcp_state_DropTail.log",
            "*_tcp_state_*.log",
            "tcp_state_RED.log",
            "tcp_state_DropTail.log",
            "tcp_state.log"
        ]
        
        self.cwnd_file = None
        self.state_file = None
        self.queue_type = "Unknown"
        self.result_dir = None

config = Config()

# ===============================
#  Tự động phát hiện thư mục và file
# ===============================
def find_result_dir():
    """Tìm thư mục results tồn tại"""
    for result_dir in config.result_dirs:
        # Thử đường dẫn tương đối
        if os.path.isdir(result_dir):
            print(f"[Plot] Found result directory: {result_dir}")
            return os.path.abspath(result_dir)
        
        # Thử từ thư mục hiện tại
        abs_path = os.path.abspath(result_dir)
        if os.path.isdir(abs_path):
            print(f"[Plot] Found result directory: {abs_path}")
            return abs_path
    
    # Tạo thư mục mặc định nếu không tìm thấy
    default_dir = config.result_dirs[0]
    print(f"[Plot] Creating result directory: {default_dir}")
    os.makedirs(default_dir, exist_ok=True)
    return os.path.abspath(default_dir)

def detect_files():
    """Tự động phát hiện file cwnd và state trong thư mục results/ - ưu tiên file mới nhất"""
    if not config.result_dir:
        config.result_dir = find_result_dir()
    
    cwnd_file = None
    state_file = None
    queue_type = "Unknown"
    
    # Tìm TẤT CẢ file cwnd, sau đó chọn file mới nhất
    all_cwnd_files = []
    for pattern in config.cwnd_patterns:
        search_pattern = os.path.join(config.result_dir, pattern)
        files = glob.glob(search_pattern)
        all_cwnd_files.extend(files)
    
    if all_cwnd_files:
        # Chọn file mới nhất dựa trên modification time
        cwnd_file = max(all_cwnd_files, key=os.path.getmtime)
        if "RED" in cwnd_file:
            queue_type = "RED"
        elif "DropTail" in cwnd_file:
            queue_type = "DropTail"
    
    # Tìm TẤT CẢ file state, sau đó chọn file mới nhất
    all_state_files = []
    for pattern in config.state_patterns:
        search_pattern = os.path.join(config.result_dir, pattern)
        files = glob.glob(search_pattern)
        all_state_files.extend(files)
    
    if all_state_files:
        state_file = max(all_state_files, key=os.path.getmtime)
        if queue_type == "Unknown":
            if "RED" in state_file:
                queue_type = "RED"
            elif "DropTail" in state_file:
                queue_type = "DropTail"
    
    return cwnd_file, state_file, queue_type

# ===============================
#  Đợi file được tạo
# ===============================
def wait_for_files(timeout=30):
    """Đợi file simulation được tạo với timeout"""
    print("="*60)
    print("[Plot] TCP Reno Real-time Visualization Starting...")
    print("="*60)
    print(f"[Plot] Working directory: {os.getcwd()}")
    print(f"[Plot] Result directory: {config.result_dir}")
    print(f"[Plot] Waiting for simulation files (timeout: {timeout}s)...")
    print("[Plot] Press Ctrl+C to exit")
    print("="*60)
    
    start = time.time()
    attempt = 0
    
    while time.time() - start < timeout:
        attempt += 1
        cwnd_file, state_file, queue_type = detect_files()
        
        if cwnd_file and os.path.exists(cwnd_file):
            # Kiểm tra xem file có dữ liệu chưa
            try:
                size = os.path.getsize(cwnd_file)
                if size > 0:
                    print(f"\n[Plot] ✓ Files detected!")
                    print(f"[Plot]   CWND file: {cwnd_file} ({size} bytes)")
                    if state_file and os.path.exists(state_file):
                        print(f"[Plot]   State file: {state_file} ({os.path.getsize(state_file)} bytes)")
                    print(f"[Plot]   Queue type: {queue_type}")
                    print("="*60)
                    return cwnd_file, state_file, queue_type
            except:
                pass
        
        # Progress indicator
        if attempt % 4 == 0:
            elapsed = time.time() - start
            print(f"[Plot] Waiting... {elapsed:.1f}s / {timeout}s", end='\r')
        
        time.sleep(0.5)
    
    print(f"\n[Plot] ⚠ Warning: Files not found after {timeout}s")
    print(f"[Plot] Monitoring directory: {config.result_dir}")
    print(f"[Plot] Will continue checking during visualization...")
    print("="*60)
    
    # Trả về đường dẫn mặc định
    default_cwnd = os.path.join(config.result_dir, "cwnd_trace.tr")
    default_state = os.path.join(config.result_dir, "tcp_state.log")
    return default_cwnd, default_state, "Unknown"

# ===============================
#  Khởi tạo
# ===============================
config.result_dir = find_result_dir()
config.cwnd_file, config.state_file, config.queue_type = wait_for_files(timeout=15)

print(f"[Plot] Monitoring files:")
print(f"[Plot]   CWND: {config.cwnd_file}")
print(f"[Plot]   State: {config.state_file}")
print(f"[Plot]   Queue: {config.queue_type}")
print("="*60 + "\n")

# ===============================
#  FSM TCP Reno
# ===============================
STATES = ["SlowStart", "CongestionAvoidance", "FastRecovery"]
TRANSITIONS = [
    ("SlowStart", "CongestionAvoidance"),
    ("CongestionAvoidance", "FastRecovery"),
    ("FastRecovery", "CongestionAvoidance"),
    ("FastRecovery", "SlowStart"),
    ("SlowStart", "FastRecovery"),
    ("CongestionAvoidance", "SlowStart"),
]

# ===============================
#  Thiết lập giao diện đồ thị
# ===============================
try:
    plt.style.use('seaborn-v0_8-darkgrid')
except:
    try:
        plt.style.use('seaborn-darkgrid')
    except:
        plt.style.use('ggplot')

fig, (ax_cwnd, ax_fsm) = plt.subplots(1, 2, figsize=(15, 6))
title = f"TCP Reno: Congestion Window & FSM State - {config.queue_type} Queue" if config.queue_type != "Unknown" else "TCP Reno: Congestion Window & FSM State [Waiting for data...]"
fig.suptitle(title, fontsize=14, fontweight='bold')

# --- Biểu đồ CWND ---
ax_cwnd.set_title("Congestion Window Over Time", fontweight='bold')
ax_cwnd.set_xlabel("Time (s)", fontsize=11)
ax_cwnd.set_ylabel("CWND (KB)", fontsize=11)
line, = ax_cwnd.plot([], [], lw=2.5, color='tab:blue', label='CWND', marker='o', markersize=3, markevery=10)
ax_cwnd.legend(loc='upper left', fontsize=10)
ax_cwnd.grid(True, alpha=0.3, linestyle='--')

# Text boxes
state_text = ax_cwnd.text(0.05, 0.95, "", transform=ax_cwnd.transAxes, fontsize=10,
                          verticalalignment='top', 
                          bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))

stats_text = ax_cwnd.text(0.95, 0.05, "", transform=ax_cwnd.transAxes, fontsize=9,
                          verticalalignment='bottom', horizontalalignment='right',
                          bbox=dict(boxstyle="round", facecolor="lightblue", alpha=0.7))

# --- Biểu đồ FSM ---
ax_fsm.set_title("TCP Reno FSM (Current State Highlighted)", fontweight='bold')
G = nx.DiGraph()
G.add_nodes_from(STATES)
G.add_edges_from(TRANSITIONS)
pos = {
    "SlowStart": (-1, 0),
    "CongestionAvoidance": (1, 0),
    "FastRecovery": (0, -1.2)
}

# ===============================
#  Thống kê và cache
# ===============================
class DataCache:
    def __init__(self):
        self.cwnd_times = []
        self.cwnd_values = []
        self.last_cwnd_size = 0
        self.last_cwnd_mtime = 0
        
        self.stats = {
            'state_changes': 0,
            'dup_acks': 0,
            'fast_retransmits': 0,
            'timeouts': 0,
            'last_state_size': 0
        }
        
        self.current_state = "SlowStart"
        self.last_reason = "Waiting for data..."
        self.last_state_time = 0.0
        
        self.data_available = False
        self.file_check_counter = 0
        self.last_data_update = 0  # Theo dõi lần cập nhật cuối
        self.simulation_ended = False
        self.screenshot_saved = False
    
    def clear(self):
        """Clear cache khi phát hiện file mới"""
        self.cwnd_times = []
        self.cwnd_values = []
        self.last_cwnd_size = 0
        self.last_cwnd_mtime = 0
        self.stats = {
            'state_changes': 0,
            'dup_acks': 0,
            'fast_retransmits': 0,
            'timeouts': 0,
            'last_state_size': 0
        }
        self.current_state = "SlowStart"
        self.last_reason = "Waiting for data..."
        self.last_state_time = 0.0
        self.data_available = False
        self.last_data_update = 0
        self.simulation_ended = False
        self.screenshot_saved = False

cache = DataCache()

# ===============================
#  Hàm đọc dữ liệu (optimized)
# ===============================
def read_cwnd():
    """Đọc dữ liệu CWND với caching thông minh"""
    # Auto-detect file nếu chưa có
    if not config.cwnd_file or not os.path.exists(config.cwnd_file):
        cwnd_file, _, queue = detect_files()
        if cwnd_file and os.path.exists(cwnd_file):
            config.cwnd_file = cwnd_file
            if queue != "Unknown":
                config.queue_type = queue
            print(f"[Plot] ✓ Detected CWND file: {config.cwnd_file}")
        else:
            return cache.cwnd_times, cache.cwnd_values
    
    try:
        # Kiểm tra nếu file đã thay đổi
        stat = os.stat(config.cwnd_file)
        if stat.st_size == cache.last_cwnd_size and stat.st_mtime == cache.last_cwnd_mtime:
            # Kiểm tra xem simulation có kết thúc không (không có dữ liệu mới trong 10s)
            if cache.data_available and len(cache.cwnd_times) > 0:
                if time.time() - cache.last_data_update > 10 and not cache.simulation_ended:
                    cache.simulation_ended = True
                    print(f"[Plot] 🏁 Simulation appears to have ended")
            return cache.cwnd_times, cache.cwnd_values
        
        cache.last_cwnd_size = stat.st_size
        cache.last_cwnd_mtime = stat.st_mtime
        cache.last_data_update = time.time()  # Cập nhật timestamp
        
        # Đọc toàn bộ file (vì file không quá lớn)
        times = []
        values = []
        with open(config.cwnd_file, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                parts = line.split()
                if len(parts) >= 2:
                    try:
                        times.append(float(parts[0]))
                        values.append(float(parts[1]))
                    except ValueError:
                        continue
        
        if times:
            cache.cwnd_times = times
            cache.cwnd_values = values
            if not cache.data_available:
                cache.data_available = True
                print(f"[Plot] ✓ Data started flowing! ({len(times)} points)")
    
    except Exception as e:
        pass
    
    return cache.cwnd_times, cache.cwnd_values

def read_state():
    """Đọc trạng thái TCP FSM"""
    # Auto-detect file
    if not config.state_file or not os.path.exists(config.state_file):
        _, state_file, queue = detect_files()
        if state_file and os.path.exists(state_file):
            config.state_file = state_file
            if queue != "Unknown":
                config.queue_type = queue
            print(f"[Plot] ✓ Detected State file: {config.state_file}")
        else:
            return cache.current_state, cache.last_reason, cache.last_state_time
    
    try:
        with open(config.state_file, 'r') as f:
            for line in f:
                if "STATE_CHANGE" in line:
                    m = re.search(r"([\d.]+)\s+STATE_CHANGE\s+(\S+)\s*->\s*(\S+)\s*\[Reason:\s*(.*?)\]", line)
                    if m:
                        t, old_state, new_state, reason = m.groups()
                        cache.current_state = new_state
                        cache.last_reason = reason.strip()
                        cache.last_state_time = float(t)
    except Exception as e:
        pass
    
    return cache.current_state, cache.last_reason, cache.last_state_time

def read_statistics():
    """Đọc thống kê từ state log"""
    if not config.state_file or not os.path.exists(config.state_file):
        return cache.stats
    
    try:
        current_size = os.path.getsize(config.state_file)
        if current_size == cache.stats['last_state_size']:
            return cache.stats
        
        cache.stats['last_state_size'] = current_size
        
        state_changes = dup_acks = fast_retransmits = timeouts = 0
        with open(config.state_file, 'r') as f:
            for line in f:
                if "STATE_CHANGE" in line:
                    state_changes += 1
                elif "DUP_ACK" in line:
                    dup_acks += 1
                elif "TRIPLE_DUP_ACK" in line or "Fast Retransmit" in line:
                    fast_retransmits += 1
                elif "TIMEOUT_EVENT" in line or "Timeout event" in line:
                    timeouts += 1
        
        cache.stats['state_changes'] = state_changes
        cache.stats['dup_acks'] = dup_acks
        cache.stats['fast_retransmits'] = fast_retransmits
        cache.stats['timeouts'] = timeouts
    
    except Exception as e:
        pass
    
    return cache.stats

# ===============================
#  Hàm lưu screenshot
# ===============================
def save_screenshot():
    """Lưu screenshot khi simulation kết thúc"""
    if cache.screenshot_saved:
        return
    
    try:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = f"tcp_reno_{config.queue_type}_{timestamp}.png"
        filepath = os.path.join(config.result_dir, filename)
        
        fig.savefig(filepath, dpi=150, bbox_inches='tight')
        cache.screenshot_saved = True
        
        print(f"\n{'='*60}")
        print(f"[Plot] [SCREENSHOT] Saved: {filename}")
        print(f"[Plot]             Location: {filepath}")
        print(f"{'='*60}\n")
        
        return filepath
    except Exception as e:
        print(f"[Plot] ⚠️  Could not save screenshot: {e}")
        return None

# ===============================
#  Animation update function
# ===============================
last_update_time = time.time()
frame_count = 0

def update(frame):
    """Cập nhật animation mỗi frame"""
    global last_update_time, frame_count
    frame_count += 1
    cache.file_check_counter += 1
    
    # Định kỳ kiểm tra file mới (mỗi 10 frames)
    if cache.file_check_counter >= 10:
        cache.file_check_counter = 0
        new_cwnd, new_state, new_queue = detect_files()
        
        # Kiểm tra nếu file thay đổi (dựa trên modification time)
        file_changed = False
        if new_cwnd and new_cwnd != config.cwnd_file:
            try:
                new_mtime = os.path.getmtime(new_cwnd)
                if config.cwnd_file and os.path.exists(config.cwnd_file):
                    old_mtime = os.path.getmtime(config.cwnd_file)
                    if new_mtime > old_mtime:
                        file_changed = True
                else:
                    file_changed = True
            except:
                file_changed = True
            
            if file_changed:
                # Lưu screenshot trước khi chuyển sang file mới
                if cache.data_available and len(cache.cwnd_times) > 0:
                    print(f"\n[Plot] [NEW RUN] Detected new simulation run!")
                    save_screenshot()
                
                config.cwnd_file = new_cwnd
                cache.clear()  # Clear toàn bộ cache
                print(f"[Plot] ✓ Switched to new CWND file: {new_cwnd}")
        
        if new_state and new_state != config.state_file:
            config.state_file = new_state
            if not file_changed:  # Chỉ log nếu chưa log ở trên
                print(f"[Plot] ✓ New State file detected: {new_state}")
        
        if new_queue != "Unknown" and new_queue != config.queue_type:
            config.queue_type = new_queue
            fig.suptitle(f"TCP Reno: Congestion Window & FSM State - {config.queue_type} Queue", 
                        fontsize=14, fontweight='bold')
    
    # Đọc dữ liệu CWND
    t, y = read_cwnd()
    
    # Nếu không có dữ liệu
    if len(t) == 0:
        elapsed = time.time() - last_update_time
        state_text.set_text(f"[WAITING] Simulation data...\n"
                           f"Frame: {frame_count}\n"
                           f"Monitoring: {os.path.basename(config.cwnd_file or 'N/A')}\n"
                           f"Directory: {os.path.basename(config.result_dir)}")
        stats_text.set_text(f"Status: Waiting\nUpdate: {elapsed:.1f}s ago\n"
                           f"Files checked: {cache.file_check_counter}")
        return line, state_text, stats_text
    
    # Cập nhật đồ thị CWND
    line.set_data(t, y)
    
    # Auto-scale axes với padding
    if len(t) > 0:
        window = 15  # Hiển thị 15 giây gần nhất
        if t[-1] > window:
            ax_cwnd.set_xlim(t[-1] - window, t[-1] + 1)
        else:
            ax_cwnd.set_xlim(0, max(t[-1] + 1, 5))
        
        max_cwnd = max(y) if y else 10
        ax_cwnd.set_ylim(0, max_cwnd * 1.15)
    
    # Đọc trạng thái FSM
    current_state, reason, state_time = read_state()
    time_in_state = t[-1] - state_time if len(t) > 0 and state_time > 0 else 0
    
    state_text.set_text(f"[STATE] {current_state}\n"
                       f"Reason: {reason}\n"
                       f"Time in state: {time_in_state:.2f}s\n"
                       f"Data points: {len(t)}")
    
    # Đọc thống kê
    stats = read_statistics()
    now = time.time()
    dt = now - last_update_time
    last_update_time = now
    fps = 1.0 / dt if dt > 0 else 0
    
    sim_time = t[-1] if len(t) > 0 else 0
    current_cwnd = y[-1] if len(y) > 0 else 0
    max_cwnd_val = max(y) if y else 0
    min_cwnd_val = min(y) if y else 0
    
    stats_text.set_text(
        f"Update: {dt:.2f}s ({fps:.1f} FPS)\n"
        f"Sim Time: {sim_time:.2f}s\n"
        f"Current CWND: {current_cwnd:.2f} KB\n"
        f"Max CWND: {max_cwnd_val:.2f} KB\n"
        f"Min CWND: {min_cwnd_val:.2f} KB\n"
        f"{'='*15}\n"
        f"State Changes: {stats['state_changes']}\n"
        f"Dup ACKs: {stats['dup_acks']}\n"
        f"Fast Retrans: {stats['fast_retransmits']}\n"
        f"Timeouts: {stats['timeouts']}"
    )
    
    # Cập nhật FSM graph
    ax_fsm.clear()
    node_colors = {state: "lightgray" for state in STATES}
    node_colors[current_state] = "tab:orange"
    
    nx.draw(G, pos, ax=ax_fsm, with_labels=True,
            node_color=[node_colors[n] for n in STATES],
            node_size=4000, font_size=11, font_weight='bold',
            arrowsize=20, edge_color='gray', width=2,
            connectionstyle="arc3,rad=0.1")
    
    ax_fsm.text(0.5, -1.85, 
               f"Queue Type: {config.queue_type}\n"
               f"Active State: {current_state}\n"
               f"Simulation Time: {sim_time:.2f}s", 
               ha='center', fontsize=10,
               bbox=dict(boxstyle="round", facecolor="lightyellow", alpha=0.8))
    
    ax_fsm.set_title("TCP Reno FSM (Current State Highlighted)", fontweight='bold')
    
    # Lưu screenshot nếu simulation kết thúc
    if cache.simulation_ended and not cache.screenshot_saved:
        save_screenshot()
    
    return line, state_text, stats_text

# ===============================
#  Main execution
# ===============================
if __name__ == "__main__":
    print("\n[Plot] [START] Starting Real-time Visualization...")
    print("[Plot] Press Ctrl+C or close window to exit\n")
    
    try:
        # Tạo animation với cache disabled để update real-time
        ani = animation.FuncAnimation(
            fig, 
            update, 
            interval=500,  # Update mỗi 500ms
            blit=False,    # Không dùng blitting vì cần redraw FSM
            repeat=True,   # Lặp lại animation
            cache_frame_data=False  # Không cache để luôn đọc dữ liệu mới
        )
        
        plt.tight_layout()
        plt.show()
        
    except KeyboardInterrupt:
        print("\n[Plot] [STOP] Visualization stopped by user")
        sys.exit(0)
    
    except Exception as e:
        print(f"\n[Plot] [ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    finally:
        print(f"\n[Plot] Final Statistics:")
        print(f"  - Total frames: {frame_count}")
        print(f"  - Data points: {len(cache.cwnd_times)}")
        if cache.cwnd_values:
            print(f"  - Max CWND: {max(cache.cwnd_values):.2f} KB")
            print(f"  - Final CWND: {cache.cwnd_values[-1]:.2f} KB")
        
        # Lưu screenshot cuối cùng nếu chưa lưu
        if cache.data_available and not cache.screenshot_saved:
            print(f"[Plot] [SCREENSHOT] Saving final screenshot...")
            save_screenshot()
        
        print("[Plot] Goodbye!\n")
