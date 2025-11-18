"""
Data loading and parsing utilities
Các hàm tiện ích cho load và parse dữ liệu
"""

import re
import glob
from pathlib import Path


def find_latest_file(results_dir, prefix, queue_type, suffix):
    """
    Tìm file mới nhất với timestamp
    
    Args:
        results_dir (Path): Thư mục chứa kết quả
        prefix (str): Prefix của files
        queue_type (str): Loại hàng đợi (DropTail/RED)
        suffix (str): Suffix của file (vd: cwnd_trace, summary, tcp_state)
    
    Returns:
        Path: Đường dẫn đến file mới nhất hoặc None
    """
    # Tìm tất cả files match pattern với timestamp
    pattern = f"{prefix}_*_{suffix}_{queue_type}"
    if suffix == "cwnd_trace":
        pattern += ".tr"
    elif suffix == "tcp_state":
        pattern += ".log"
    elif suffix == "summary":
        pattern += ".txt"
    
    files = list(results_dir.glob(pattern))
    
    # Nếu không tìm thấy file với timestamp, thử tìm file cũ không có timestamp
    if not files:
        old_pattern = f"{prefix}_{suffix}_{queue_type}"
        if suffix == "cwnd_trace":
            old_pattern += ".tr"
        elif suffix == "tcp_state":
            old_pattern += ".log"
        elif suffix == "summary":
            old_pattern += ".txt"
        old_file = results_dir / old_pattern
        if old_file.exists():
            return old_file
        return None
    
    # Trả về file mới nhất (sắp xếp theo tên, timestamp sẽ sắp xếp đúng)
    return sorted(files)[-1]


def load_data(results_dir, prefix, queue_type):
    """
    Load dữ liệu cho một loại hàng đợi
    
    Args:
        results_dir (Path): Thư mục chứa kết quả
        prefix (str): Prefix của files
        queue_type (str): Loại hàng đợi (DropTail/RED)
    
    Returns:
        dict: Dữ liệu đã load
    """
    print(f"\n{'='*70}")
    print(f"📊 Đang tải dữ liệu cho hàng đợi {queue_type}...")
    print(f"{'='*70}")

    data = {
        'queue_type': queue_type,
        'cwnd': [],
        'time': [],
        'state_changes': [],
        'events': [],
        'summary': {}
    }

    # Load CWND trace
    cwnd_file = find_latest_file(results_dir, prefix, queue_type, "cwnd_trace")
    if cwnd_file and cwnd_file.exists():
        print(f"📄 Đang đọc: {cwnd_file.name}")
        with open(cwnd_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    data['time'].append(float(parts[0]))
                    data['cwnd'].append(float(parts[1]))
        print(f"✅ Đã tải {len(data['time'])} điểm dữ liệu CWND")
    else:
        print(f"❌ Không tìm thấy file CWND cho {queue_type}")

    # Load state changes
    state_file = find_latest_file(results_dir, prefix, queue_type, "tcp_state")
    if state_file and state_file.exists():
        print(f"📄 Đang đọc: {state_file.name}")
        with open(state_file, 'r') as f:
            for line in f:
                if line.startswith('#') or line.startswith('-'):
                    continue
                parts = line.strip().split()
                if len(parts) >= 2:
                    try:
                        time = float(parts[0].rstrip('s:'))
                        event = parts[1]
                        detail = ' '.join(parts[2:]) if len(parts) > 2 else ''
                        data['events'].append({
                            'time': time,
                            'event': event,
                            'detail': detail
                        })
                        if event == 'STATE_CHANGE':
                            data['state_changes'].append({
                                'time': time,
                                'detail': detail
                            })
                    except ValueError:
                        continue
        print(f"✅ Đã tải {len(data['events'])} sự kiện")
    else:
        print(f"❌ Không tìm thấy file state log")

    # Load summary
    summary_file = find_latest_file(results_dir, prefix, queue_type, "summary")
    if summary_file and summary_file.exists():
        print(f"📄 Đang đọc: {summary_file.name}")
        with open(summary_file, 'r') as f:
            content = f.read()
            data['summary'] = parse_summary(content)
        print(f"✅ Đã tải thống kê tổng hợp")
    else:
        print(f"❌ Không tìm thấy file summary")

    return data


def parse_summary(content):
    """
    Parse summary file content
    
    Args:
        content (str): Nội dung file summary
    
    Returns:
        dict: Thống kê đã parse
    """
    summary = {}
    patterns = {
        'total_throughput': r'Total Throughput:\s+([\d.]+)\s+Mbps',
        'avg_throughput': r'Average Throughput per Flow:\s+([\d.]+)\s+Mbps',
        'total_tx': r'Total Packets Sent:\s+(\d+)',
        'total_rx': r'Total Packets Received:\s+(\d+)',
        'total_lost': r'Total Lost Packets:\s+(\d+)',
        'loss_rate': r'Total Lost Packets:.*?\(([\d.]+)%\)',
        'avg_delay': r'Average Delay:\s+([\d.]+)\s+ms',
        'state_changes': r'Total State Changes:\s+(\d+)',
        'dup_acks': r'Total Duplicate ACKs:\s+(\d+)',
        'fast_retransmits': r'Total Fast Retransmits:\s+(\d+)',
        'fast_recoveries': r'Total Fast Recoveries:\s+(\d+)',
        'timeouts': r'Total Timeouts:\s+(\d+)',
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, content)
        if match:
            try:
                summary[key] = float(match.group(1))
            except ValueError:
                summary[key] = 0
    return summary


def count_events(events):
    """
    Đếm số lượng mỗi loại sự kiện
    
    Args:
        events (list): Danh sách các sự kiện
    
    Returns:
        dict: Số lượng từng loại sự kiện
    """
    counts = {}
    for event in events:
        event_type = event['event']
        counts[event_type] = counts.get(event_type, 0) + 1
    return counts
