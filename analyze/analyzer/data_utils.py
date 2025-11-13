"""
Data loading and parsing utilities
Các hàm tiện ích cho load và parse dữ liệu
"""

import re
from pathlib import Path


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
    cwnd_file = results_dir / f"{prefix}_cwnd_trace_{queue_type}.tr"
    if cwnd_file.exists():
        with open(cwnd_file, 'r') as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) == 2:
                    data['time'].append(float(parts[0]))
                    data['cwnd'].append(float(parts[1]))
        print(f"✅ Đã tải {len(data['time'])} điểm dữ liệu CWND")
    else:
        print(f"❌ Không tìm thấy file CWND: {cwnd_file}")

    # Load state changes
    state_file = results_dir / f"{prefix}_tcp_state_{queue_type}.log"
    if state_file.exists():
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
    summary_file = results_dir / f"{prefix}_summary_{queue_type}.txt"
    if summary_file.exists():
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
