#!/usr/bin/env python3
"""
TCP Reno Visual Analysis Tool - Enhanced Version with Emoji Support
Phân tích kết quả mô phỏng TCP Reno với đồ họa đẹp mắt
"""

import os
import sys
import argparse
import re
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.gridspec import GridSpec
import numpy as np
from matplotlib.patches import Rectangle
import seaborn as sns
from matplotlib import rcParams
import matplotlib.pyplot as plt

# Đặt thứ tự font: matplotlib sẽ dùng DejaVu Sans trước, nếu ký tự không có thì dùng Symbola
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['DejaVu Sans', 'Symbola']

# Cấu hình style đẹp hơn
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

class EnhancedTCPAnalyzer:
    def __init__(self, results_dir, prefix):
        self.results_dir = Path(results_dir)
        self.prefix = prefix
        self.data = {}
        
        # Màu sắc đẹp mắt
        self.colors = {
            'DropTail': '#FF6B6B',      # Đỏ cam
            'RED': '#4ECDC4',            # Xanh ngọc
            'background': '#F7F7F7',
            'grid': '#E0E0E0',
            'text': '#2C3E50',
            'accent1': '#FFD93D',        # Vàng
            'accent2': '#6BCB77',        # Xanh lá
            'accent3': '#4D96FF',        # Xanh dương
            'danger': '#E63946',         # Đỏ
            'warning': '#F77F00',        # Cam
            'success': '#06FFA5'         # Xanh mint
        }

    def load_data(self, queue_type):
        """Load dữ liệu với progress indicator"""
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
        cwnd_file = self.results_dir / f"{self.prefix}_cwnd_trace_{queue_type}.tr"
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
        state_file = self.results_dir / f"{self.prefix}_tcp_state_{queue_type}.log"
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
        summary_file = self.results_dir / f"{self.prefix}_summary_{queue_type}.txt"
        if summary_file.exists():
            with open(summary_file, 'r') as f:
                content = f.read()
                data['summary'] = self._parse_summary(content)
            print(f"✅ Đã tải thống kê tổng hợp")
        else:
            print(f"❌ Không tìm thấy file summary")

        self.data[queue_type] = data
        return data

    def _parse_summary(self, content):
        """Parse summary file"""
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

    def _count_events(self, events):
        """Đếm số lượng mỗi loại sự kiện"""
        counts = {}
        for event in events:
            event_type = event['event']
            counts[event_type] = counts.get(event_type, 0) + 1
        return counts

    def create_dashboard(self, queue_type):
        """Tạo dashboard trực quan đẹp mắt cho 1 loại hàng đợi"""
        if queue_type not in self.data:
            self.load_data(queue_type)

        data = self.data[queue_type]
        summary = data['summary']
        
        # Tạo figure với kích thước lớn
        fig = plt.figure(figsize=(20, 12))
        fig.patch.set_facecolor(self.colors['background'])
        
        # Tạo layout phức tạp hơn
        gs = GridSpec(4, 3, figure=fig, hspace=0.4, wspace=0.3,
                     left=0.05, right=0.95, top=0.92, bottom=0.05)

        # ===== 1. CWND Evolution - Biểu đồ chính (full width, top) =====
        ax1 = fig.add_subplot(gs[0:2, :])
        
        # Vẽ CWND với gradient color
        time = np.array(data['time'])
        cwnd = np.array(data['cwnd'])
        
        # Tạo gradient effect
        points = np.array([time, cwnd]).T.reshape(-1, 1, 2)
        segments = np.concatenate([points[:-1], points[1:]], axis=1)
        
        # Line plot với shadow effect
        ax1.plot(time, cwnd, linewidth=3, 
                color=self.colors[queue_type], 
                label=f'{queue_type} CWND',
                alpha=0.9, zorder=3)
        ax1.plot(time, cwnd, linewidth=6, 
                color=self.colors[queue_type], 
                alpha=0.2, zorder=2)
        
        # Fill area dưới đường
        ax1.fill_between(time, 0, cwnd, 
                        color=self.colors[queue_type], 
                        alpha=0.15, zorder=1)
        
        # Đánh dấu các sự kiện quan trọng
        timeouts = [e for e in data['events'] if e['event'] == 'TIMEOUT_EVENT']
        fast_retx = [e for e in data['events'] if e['event'] == 'TRIPLE_DUP_ACK']
        
        # Timeout events - màu đỏ
        for event in timeouts[:10]:
            t = event['time']
            if t < max(time):
                idx = np.argmin(np.abs(time - t))
                ax1.axvline(x=t, color=self.colors['danger'], 
                          linestyle='--', linewidth=2, alpha=0.6, zorder=4)
                ax1.scatter([t], [cwnd[idx]], color=self.colors['danger'], 
                          s=150, marker='X', edgecolors='white', 
                          linewidths=2, zorder=5, label='Timeout' if event == timeouts[0] else '')
        
        # Fast retransmit - màu cam
        for event in fast_retx[:10]:
            t = event['time']
            if t < max(time):
                idx = np.argmin(np.abs(time - t))
                ax1.scatter([t], [cwnd[idx]], color=self.colors['warning'], 
                          s=100, marker='v', edgecolors='white', 
                          linewidths=2, zorder=5, label='Fast Retransmit' if event == fast_retx[0] else '')
        
        ax1.set_xlabel('⏱ Thời gian (giây)', fontsize=14, fontweight='bold')
        ax1.set_ylabel('📊 Congestion Window (KB)', fontsize=14, fontweight='bold')
        ax1.set_title(f'🔄 Diễn biến Congestion Window - {queue_type}', 
                     fontsize=18, fontweight='bold', pad=20)
        ax1.legend(loc='upper right', fontsize=11, framealpha=0.9)
        ax1.grid(True, alpha=0.3, linestyle=':', linewidth=1)
        ax1.set_facecolor('white')
        
        # Thêm text box với thống kê
        stats_text = f'Max: {np.max(cwnd):.1f} KB\nAvg: {np.mean(cwnd):.1f} KB\nMin: {np.min(cwnd):.1f} KB'
        ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
                fontsize=11, verticalalignment='top',
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

        # ===== 2. Performance Metrics Cards (3 cards) =====
        metrics_data = [
            ('🚀 Throughput', f"{summary.get('avg_throughput', 0):.2f}", 'Mbps', self.colors['success']),
            ('📉 Packet Loss', f"{summary.get('loss_rate', 0):.2f}", '%', self.colors['danger']),
            ('⏳ Avg Delay', f"{summary.get('avg_delay', 0):.2f}", 'ms', self.colors['accent3'])
        ]
        
        for i, (title, value, unit, color) in enumerate(metrics_data):
            ax = fig.add_subplot(gs[2, i])
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.axis('off')
            
            # Vẽ card với gradient
            rect = Rectangle((0.05, 0.1), 0.9, 0.8, 
                           facecolor=color, alpha=0.2, 
                           edgecolor=color, linewidth=3)
            ax.add_patch(rect)
            
            # Text
            ax.text(0.5, 0.7, title, ha='center', va='center',
                   fontsize=14, fontweight='bold', color=self.colors['text'])
            ax.text(0.5, 0.4, value, ha='center', va='center',
                   fontsize=28, fontweight='bold', color=color)
            ax.text(0.5, 0.2, unit, ha='center', va='center',
                   fontsize=12, color=self.colors['text'], alpha=0.7)

        # ===== 3. Events Bar Chart =====
        ax4 = fig.add_subplot(gs[3, 0])
        event_counts = self._count_events(data['events'])
        
        events_to_plot = ['DUP_ACK', 'TRIPLE_DUP_ACK', 'TIMEOUT_EVENT', 'NEW_ACK']
        event_labels = ['Dup ACKs', 'Fast Retx', 'Timeouts', 'New ACKs']
        event_values = [event_counts.get(e, 0) for e in events_to_plot]
        event_colors = [self.colors['accent1'], self.colors['warning'], 
                       self.colors['danger'], self.colors['success']]
        
        bars = ax4.barh(event_labels, event_values, color=event_colors, 
                       alpha=0.8, edgecolor='white', linewidth=2)
        
        # Thêm giá trị trên mỗi bar
        for i, (bar, val) in enumerate(zip(bars, event_values)):
            width = bar.get_width()
            ax4.text(width + max(event_values)*0.02, bar.get_y() + bar.get_height()/2,
                    f'{int(val)}', ha='left', va='center', 
                    fontsize=12, fontweight='bold')
        
        ax4.set_xlabel('Số lượng', fontsize=12, fontweight='bold')
        ax4.set_title('📋 Thống kê Sự kiện TCP', fontsize=14, fontweight='bold', pad=15)
        ax4.grid(True, axis='x', alpha=0.3)
        ax4.set_facecolor('white')

        # ===== 4. CWND Distribution Histogram =====
        ax5 = fig.add_subplot(gs[3, 1])
        n, bins, patches = ax5.hist(cwnd, bins=30, color=self.colors[queue_type], 
                                    alpha=0.7, edgecolor='white', linewidth=1.5)
        
        # Tô màu gradient cho histogram
        cm = plt.cm.get_cmap('RdYlGn')
        bin_centers = 0.5 * (bins[:-1] + bins[1:])
        col = bin_centers - min(bin_centers)
        col /= max(col)
        for c, p in zip(col, patches):
            plt.setp(p, 'facecolor', cm(c))
        
        # Vẽ đường mean và median
        ax5.axvline(np.mean(cwnd), color='red', linestyle='--', 
                   linewidth=3, label=f'Mean: {np.mean(cwnd):.1f}', alpha=0.8)
        ax5.axvline(np.median(cwnd), color='blue', linestyle='--', 
                   linewidth=3, label=f'Median: {np.median(cwnd):.1f}', alpha=0.8)
        
        ax5.set_xlabel('CWND (KB)', fontsize=12, fontweight='bold')
        ax5.set_ylabel('Tần suất', fontsize=12, fontweight='bold')
        ax5.set_title('📊 Phân phối CWND', fontsize=14, fontweight='bold', pad=15)
        ax5.legend(fontsize=10)
        ax5.grid(True, alpha=0.3, axis='y')
        ax5.set_facecolor('white')

        # ===== 5. Summary Table =====
        ax6 = fig.add_subplot(gs[3, 2])
        ax6.axis('off')
        
        table_data = [
            ['📦 Packets Sent', f"{int(summary.get('total_tx', 0)):,}"],
            ['✅ Packets Received', f"{int(summary.get('total_rx', 0)):,}"],
            ['❌ Packets Lost', f"{int(summary.get('total_lost', 0)):,}"],
            ['🔄 State Changes', f"{int(summary.get('state_changes', 0)):,}"],
            ['⏱ Timeouts', f"{int(summary.get('timeouts', 0)):,}"],
            ['⚡ Fast Retransmits', f"{int(summary.get('fast_retransmits', 0)):,}"]
        ]
        
        table = ax6.table(cellText=table_data, cellLoc='left', loc='center',
                         colWidths=[0.6, 0.4])
        table.auto_set_font_size(False)
        table.set_fontsize(11)
        table.scale(1, 2.5)
        
        # Style table
        for i in range(len(table_data)):
            for j in range(2):
                cell = table[(i, j)]
                if i % 2 == 0:
                    cell.set_facecolor('#F0F0F0')
                else:
                    cell.set_facecolor('white')
                cell.set_edgecolor(self.colors['grid'])
                cell.set_linewidth(2)
                if j == 1:
                    cell.set_text_props(weight='bold', color=self.colors[queue_type])
        
        ax6.set_title('📈 Bảng Tổng hợp', fontsize=14, fontweight='bold', pad=20)

        # Main title
        fig.suptitle(f'🎯 TCP Reno Performance Dashboard - {queue_type} Queue', 
                    fontsize=24, fontweight='bold', y=0.98)

        # Save
        output_file = self.results_dir / f"{self.prefix}_dashboard_{queue_type}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight', 
                   facecolor=self.colors['background'])
        print(f"\n✅ Dashboard đã lưu: {output_file}")
        plt.show()

    def create_comparison_dashboard(self):
        """Tạo dashboard so sánh DropTail vs RED"""
        if 'DropTail' not in self.data or 'RED' not in self.data:
            print("❌ Cần dữ liệu cả DropTail và RED để so sánh")
            return

        fig = plt.figure(figsize=(24, 14))
        fig.patch.set_facecolor(self.colors['background'])
        
        gs = GridSpec(3, 3, figure=fig, hspace=0.35, wspace=0.25,
                     left=0.05, right=0.95, top=0.93, bottom=0.05)

        dt_data = self.data['DropTail']
        red_data = self.data['RED']

        # ===== 1. CWND Comparison (Full top row) =====
        ax1 = fig.add_subplot(gs[0, :])
        
        # DropTail
        ax1.plot(dt_data['time'], dt_data['cwnd'], 
                linewidth=3, color=self.colors['DropTail'], 
                label='DropTail', alpha=0.85, zorder=3)
        ax1.fill_between(dt_data['time'], 0, dt_data['cwnd'],
                        color=self.colors['DropTail'], alpha=0.15, zorder=1)
        
        # RED
        ax1.plot(red_data['time'], red_data['cwnd'], 
                linewidth=3, color=self.colors['RED'], 
                label='RED', alpha=0.85, zorder=3)
        ax1.fill_between(red_data['time'], 0, red_data['cwnd'],
                        color=self.colors['RED'], alpha=0.15, zorder=1)
        
        ax1.set_xlabel('⏱ Thời gian (giây)', fontsize=15, fontweight='bold')
        ax1.set_ylabel('📊 Congestion Window (KB)', fontsize=15, fontweight='bold')
        ax1.set_title('🔄 So sánh Diễn biến CWND: DropTail vs RED', 
                     fontsize=20, fontweight='bold', pad=20)
        ax1.legend(loc='upper right', fontsize=14, framealpha=0.95)
        ax1.grid(True, alpha=0.3, linestyle=':', linewidth=1.5)
        ax1.set_facecolor('white')

        # ===== 2. Performance Comparison Bars =====
        metrics = ['Throughput\n(Mbps)', 'Loss Rate\n(%)', 'Delay\n(ms)']
        dt_values = [
            dt_data['summary'].get('avg_throughput', 0),
            dt_data['summary'].get('loss_rate', 0),
            dt_data['summary'].get('avg_delay', 0)
        ]
        red_values = [
            red_data['summary'].get('avg_throughput', 0),
            red_data['summary'].get('loss_rate', 0),
            red_data['summary'].get('avg_delay', 0)
        ]

        for i, (metric, dt_val, red_val) in enumerate(zip(metrics, dt_values, red_values)):
            ax = fig.add_subplot(gs[1, i])
            
            x = [0, 1]
            values = [dt_val, red_val]
            colors = [self.colors['DropTail'], self.colors['RED']]
            
            bars = ax.bar(x, values, width=0.6, color=colors, 
                         alpha=0.8, edgecolor='white', linewidth=3)
            
            # Thêm giá trị
            for j, (bar, val) in enumerate(zip(bars, values)):
                height = bar.get_height()
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{val:.2f}', ha='center', va='bottom',
                       fontsize=16, fontweight='bold')
            
            ax.set_xticks(x)
            ax.set_xticklabels(['DropTail', 'RED'], fontsize=12, fontweight='bold')
            ax.set_ylabel('Value', fontsize=12, fontweight='bold')
            ax.set_title(metric, fontsize=14, fontweight='bold', pad=15)
            ax.grid(True, axis='y', alpha=0.3)
            ax.set_facecolor('white')
            
            # Highlight winner
            winner_idx = 0 if (i == 0 and dt_val > red_val) or (i > 0 and dt_val < red_val) else 1
            bars[winner_idx].set_linewidth(5)
            bars[winner_idx].set_edgecolor('gold')

        # ===== 3. Events Comparison =====
        ax4 = fig.add_subplot(gs[2, 0])
        
        events = ['Timeouts', 'Fast\nRetx', 'Dup\nACKs']
        dt_events = [
            dt_data['summary'].get('timeouts', 0),
            dt_data['summary'].get('fast_retransmits', 0),
            self._count_events(dt_data['events']).get('DUP_ACK', 0)
        ]
        red_events = [
            red_data['summary'].get('timeouts', 0),
            red_data['summary'].get('fast_retransmits', 0),
            self._count_events(red_data['events']).get('DUP_ACK', 0)
        ]
        
        x = np.arange(len(events))
        width = 0.35
        
        bars1 = ax4.bar(x - width/2, dt_events, width, 
                       label='DropTail', color=self.colors['DropTail'],
                       alpha=0.8, edgecolor='white', linewidth=2)
        bars2 = ax4.bar(x + width/2, red_events, width, 
                       label='RED', color=self.colors['RED'],
                       alpha=0.8, edgecolor='white', linewidth=2)
        
        ax4.set_ylabel('Số lượng', fontsize=12, fontweight='bold')
        ax4.set_title('📋 So sánh Sự kiện', fontsize=14, fontweight='bold', pad=15)
        ax4.set_xticks(x)
        ax4.set_xticklabels(events, fontsize=11)
        ax4.legend(fontsize=11)
        ax4.grid(True, axis='y', alpha=0.3)
        ax4.set_facecolor('white')
        
        # Thêm values
        for bars in [bars1, bars2]:
            for bar in bars:
                height = bar.get_height()
                ax4.text(bar.get_x() + bar.get_width()/2., height,
                        f'{int(height)}', ha='center', va='bottom',
                        fontsize=10, fontweight='bold')

        # ===== 4. CWND Statistics Comparison =====
        ax5 = fig.add_subplot(gs[2, 1])
        
        stats_labels = ['Max', 'Avg', 'Min', 'Std']
        dt_cwnd = np.array(dt_data['cwnd'])
        red_cwnd = np.array(red_data['cwnd'])
        
        dt_stats = [np.max(dt_cwnd), np.mean(dt_cwnd), 
                    np.min(dt_cwnd), np.std(dt_cwnd)]
        red_stats = [np.max(red_cwnd), np.mean(red_cwnd), 
                     np.min(red_cwnd), np.std(red_cwnd)]
        
        x = np.arange(len(stats_labels))
        width = 0.35
        
        bars1 = ax5.bar(x - width/2, dt_stats, width,
                       label='DropTail', color=self.colors['DropTail'],
                       alpha=0.8, edgecolor='white', linewidth=2)
        bars2 = ax5.bar(x + width/2, red_stats, width,
                       label='RED', color=self.colors['RED'],
                       alpha=0.8, edgecolor='white', linewidth=2)
        
        ax5.set_ylabel('CWND (KB)', fontsize=12, fontweight='bold')
        ax5.set_title('📊 Thống kê CWND', fontsize=14, fontweight='bold', pad=15)
        ax5.set_xticks(x)
        ax5.set_xticklabels(stats_labels, fontsize=11)
        ax5.legend(fontsize=11)
        ax5.grid(True, axis='y', alpha=0.3)
        ax5.set_facecolor('white')

        # ===== 5. Winner Summary =====
        ax6 = fig.add_subplot(gs[2, 2])
        ax6.axis('off')
        
        # Tính điểm
        scores = {'DropTail': 0, 'RED': 0}
        
        comparisons = [
            ('Throughput', dt_values[0], red_values[0], True),
            ('Loss Rate', dt_values[1], red_values[1], False),
            ('Delay', dt_values[2], red_values[2], False),
            ('Timeouts', dt_events[0], red_events[0], False)
        ]
        
        table_data = [['Metric', 'Winner', 'Score']]
        
        for metric, dt_val, red_val, higher_better in comparisons:
            if higher_better:
                winner = 'DropTail' if dt_val > red_val else 'RED'
                diff = f'+{abs(dt_val - red_val):.2f}'
            else:
                winner = 'DropTail' if dt_val < red_val else 'RED'
                diff = f'-{abs(dt_val - red_val):.2f}'
            
            scores[winner] += 1
            table_data.append([metric, winner, diff])
        
        table = ax6.table(cellText=table_data, cellLoc='center', loc='upper center',
                         colWidths=[0.4, 0.3, 0.3])
        table.auto_set_font_size(False)
        table.set_fontsize(12)
        table.scale(1, 3)
        
        # Style header
        for j in range(3):
            table[(0, j)].set_facecolor(self.colors['text'])
            table[(0, j)].set_text_props(weight='bold', color='white')
        
        # Style winner cells
        for i in range(1, len(table_data)):
            winner = table_data[i][1]
            color = self.colors['DropTail'] if winner == 'DropTail' else self.colors['RED']
            table[(i, 1)].set_facecolor(color)
            table[(i, 1)].set_text_props(weight='bold', color='white')
        
        # Overall winner
        overall_winner = 'DropTail' if scores['DropTail'] > scores['RED'] else 'RED'
        winner_color = self.colors[overall_winner]
        
        ax6.text(0.5, 0.3, '🏆 OVERALL WINNER', ha='center', va='center',
                fontsize=16, fontweight='bold', transform=ax6.transAxes)
        ax6.text(0.5, 0.15, overall_winner, ha='center', va='center',
                fontsize=32, fontweight='bold', color=winner_color,
                transform=ax6.transAxes)
        ax6.text(0.5, 0.05, f'Score: {scores[overall_winner]}/{len(comparisons)}', 
                ha='center', va='center', fontsize=14,
                transform=ax6.transAxes, style='italic')

        # Main title
        fig.suptitle('🎯 TCP Reno: So sánh DropTail vs RED Queue', 
                    fontsize=26, fontweight='bold', y=0.98)

        # Save
        output_file = self.results_dir / f"{self.prefix}_comparison_dashboard.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight',
                   facecolor=self.colors['background'])
        print(f"\n✅ Comparison Dashboard đã lưu: {output_file}")
        plt.show()

    def create_animated_timeline(self, queue_type):
        """Tạo timeline view với annotations"""
        if queue_type not in self.data:
            self.load_data(queue_type)

        data = self.data[queue_type]
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(18, 10), 
                                        gridspec_kw={'height_ratios': [3, 1]})
        fig.patch.set_facecolor(self.colors['background'])
        
        time = np.array(data['time'])
        cwnd = np.array(data['cwnd'])
        
        # Top plot: CWND with events
        ax1.plot(time, cwnd, linewidth=2.5, color=self.colors[queue_type], 
                alpha=0.9, label='CWND')
        ax1.fill_between(time, 0, cwnd, color=self.colors[queue_type], alpha=0.2)
        
        # Mark events với icons
        timeouts = [e for e in data['events'] if e['event'] == 'TIMEOUT_EVENT']
        fast_retx = [e for e in data['events'] if e['event'] == 'TRIPLE_DUP_ACK']
        dup_acks = [e for e in data['events'] if e['event'] == 'DUP_ACK']
        
        # Timeouts
        for event in timeouts:
            t = event['time']
            if t < max(time):
                idx = np.argmin(np.abs(time - t))
                ax1.scatter([t], [cwnd[idx]], s=200, marker='X', 
                          color=self.colors['danger'], edgecolors='white',
                          linewidths=2, zorder=10, label='Timeout' if event == timeouts[0] else '')
                ax1.axvline(x=t, color=self.colors['danger'], 
                          linestyle='--', alpha=0.3, linewidth=2)
        
        # Fast retransmits
        for event in fast_retx:
            t = event['time']
            if t < max(time):
                idx = np.argmin(np.abs(time - t))
                ax1.scatter([t], [cwnd[idx]], s=150, marker='v',
                          color=self.colors['warning'], edgecolors='white',
                          linewidths=2, zorder=10, label='Fast Retx' if event == fast_retx[0] else '')
        
        ax1.set_ylabel('📊 CWND (KB)', fontsize=14, fontweight='bold')
        ax1.set_title(f'⏱ Timeline Chi tiết - {queue_type}', 
                     fontsize=18, fontweight='bold', pad=20)
        ax1.legend(loc='upper right', fontsize=11, framealpha=0.95)
        ax1.grid(True, alpha=0.3, linestyle=':')
        ax1.set_facecolor('white')
        
        # Bottom plot: Event density heatmap
        event_times = [e['time'] for e in data['events']]
        if event_times:
            hist, bins = np.histogram(event_times, bins=50, range=(0, max(time)))
            colors_map = plt.cm.YlOrRd(hist / max(hist) if max(hist) > 0 else hist)
            
            for i in range(len(bins)-1):
                ax2.add_patch(Rectangle((bins[i], 0), bins[i+1]-bins[i], 1,
                                       facecolor=colors_map[i], edgecolor='none'))
        
        ax2.set_xlabel('⏱ Thời gian (giây)', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Event\nDensity', fontsize=11, fontweight='bold')
        ax2.set_xlim(0, max(time))
        ax2.set_ylim(0, 1)
        ax2.set_yticks([])
        ax2.set_facecolor('white')
        
        plt.tight_layout()
        
        output_file = self.results_dir / f"{self.prefix}_timeline_{queue_type}.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight',
                   facecolor=self.colors['background'])
        print(f"\n✅ Timeline đã lưu: {output_file}")
        plt.show()

    def print_analysis(self, queue_type):
        """In phân tích chi tiết với emoji và màu sắc"""
        if queue_type not in self.data:
            self.load_data(queue_type)

        data = self.data[queue_type]
        summary = data['summary']
        
        print(f"\n{'='*70}")
        print(f"📊 PHÂN TÍCH CHI TIẾT: {queue_type} Queue")
        print(f"{'='*70}")
        
        # 1. CWND Analysis
        if data['cwnd']:
            cwnd = np.array(data['cwnd'])
            print(f"\n🔄 CONGESTION WINDOW (CWND):")
            print(f"   {'─'*60}")
            print(f"   🚀 Initial CWND:    {cwnd[0]:>8.2f} KB")
            print(f"   📈 Maximum CWND:    {np.max(cwnd):>8.2f} KB")
            print(f"   📊 Average CWND:    {np.mean(cwnd):>8.2f} KB")
            print(f"   📉 Minimum CWND:    {np.min(cwnd):>8.2f} KB")
            print(f"   📐 Std Deviation:   {np.std(cwnd):>8.2f} KB")
            
            # Stability score
            variations = np.abs(np.diff(cwnd))
            stability = max(0, 100 - np.mean(variations/np.mean(cwnd))*100)
            
            if stability > 70:
                emoji = "✅"
                status = "Rất ổn định"
            elif stability > 50:
                emoji = "⚠️"
                status = "Khá ổn định"
            else:
                emoji = "❌"
                status = "Không ổn định"
            
            print(f"   {emoji} Độ ổn định:     {stability:>8.1f}% ({status})")
        
        # 2. Performance Metrics
        print(f"\n⚡ HIỆU NĂNG:")
        print(f"   {'─'*60}")
        
        tput = summary.get('avg_throughput', 0)
        if tput > 5:
            tput_emoji = "🚀"
        elif tput > 2:
            tput_emoji = "✅"
        else:
            tput_emoji = "⚠️"
        print(f"   {tput_emoji} Throughput:      {tput:>8.3f} Mbps")
        
        loss = summary.get('loss_rate', 0)
        if loss < 1:
            loss_emoji = "✅"
        elif loss < 5:
            loss_emoji = "⚠️"
        else:
            loss_emoji = "❌"
        print(f"   {loss_emoji} Packet Loss:     {loss:>8.2f} %")
        
        delay = summary.get('avg_delay', 0)
        if delay < 20:
            delay_emoji = "✅"
        elif delay < 50:
            delay_emoji = "⚠️"
        else:
            delay_emoji = "❌"
        print(f"   {delay_emoji} Average Delay:   {delay:>8.2f} ms")
        
        # 3. Packets
        print(f"\n📦 PACKETS:")
        print(f"   {'─'*60}")
        print(f"   📤 Sent:             {int(summary.get('total_tx', 0)):>8,}")
        print(f"   📥 Received:         {int(summary.get('total_rx', 0)):>8,}")
        print(f"   ❌ Lost:             {int(summary.get('total_lost', 0)):>8,}")
        
        if summary.get('total_tx', 0) > 0:
            efficiency = (summary.get('total_rx', 0) / summary.get('total_tx', 0)) * 100
            eff_emoji = "✅" if efficiency > 95 else "⚠️" if efficiency > 90 else "❌"
            print(f"   {eff_emoji} Efficiency:      {efficiency:>8.1f} %")
        
        # 4. Events
        print(f"\n🔔 SỰ KIỆN TCP:")
        print(f"   {'─'*60}")
        event_counts = self._count_events(data['events'])
        
        timeouts = int(summary.get('timeouts', 0))
        timeout_emoji = "✅" if timeouts < 3 else "⚠️" if timeouts < 10 else "❌"
        print(f"   {timeout_emoji} Timeouts:        {timeouts:>8,}")
        
        fast_retx = int(summary.get('fast_retransmits', 0))
        retx_emoji = "✅" if fast_retx < 5 else "⚠️"
        print(f"   {retx_emoji} Fast Retransmit: {fast_retx:>8,}")
        
        dup_acks = event_counts.get('DUP_ACK', 0)
        print(f"   📋 Dup ACKs:         {dup_acks:>8,}")
        
        state_changes = int(summary.get('state_changes', 0))
        print(f"   🔄 State Changes:    {state_changes:>8,}")
        
        # 5. Interpretation
        print(f"\n💡 ĐÁNH GIÁ:")
        print(f"   {'─'*60}")
        
        if loss < 1 and timeouts < 3:
            print(f"   ✅ Kết nối hoạt động rất tốt với ít mất gói")
            print(f"   ✅ Cơ chế kiểm soát tắc nghẽn hiệu quả")
        elif loss < 5 and timeouts < 10:
            print(f"   ⚠️  Có tắc nghẽn vừa phải, TCP đang điều chỉnh")
            print(f"   ⚠️  Hiệu năng chấp nhận được")
        else:
            print(f"   ❌ Tắc nghẽn nghiêm trọng hoặc quá tải")
            print(f"   ❌ Cần xem xét lại cấu hình hàng đợi")
        
        if queue_type == 'RED':
            print(f"\n   🎯 RED đang hoạt động:")
            if delay < 30:
                print(f"   ✅ Giữ delay thấp bằng early dropping")
            if timeouts < 5:
                print(f"   ✅ Giảm timeout qua cảnh báo sớm")
        elif queue_type == 'DropTail':
            print(f"\n   🎯 DropTail đang hoạt động:")
            if loss > 3:
                print(f"   ⚠️  Có thể xảy ra global synchronization")
            print(f"   ℹ️  Simple FIFO với tail drop")

    def create_infographic(self):
        """Tạo infographic tổng hợp"""
        if 'DropTail' not in self.data or 'RED' not in self.data:
            print("❌ Cần dữ liệu cả hai loại hàng đợi")
            return

        fig = plt.figure(figsize=(16, 20))
        fig.patch.set_facecolor('#FFFFFF')
        
        # Title section
        fig.text(0.5, 0.98, '🎯 TCP RENO INFOGRAPHIC', 
                ha='center', va='top', fontsize=32, fontweight='bold',
                color=self.colors['text'])
        fig.text(0.5, 0.955, 'So sánh DropTail vs RED Queue Management',
                ha='center', va='top', fontsize=16, style='italic',
                color=self.colors['text'], alpha=0.7)
        
        gs = GridSpec(6, 2, figure=fig, hspace=0.6, wspace=0.3,
                     left=0.08, right=0.92, top=0.93, bottom=0.05)
        
        dt_data = self.data['DropTail']
        red_data = self.data['RED']
        dt_summary = dt_data['summary']
        red_summary = red_data['summary']
        
        # Section 1: Queue Explanation
        ax1 = fig.add_subplot(gs[0, :])
        ax1.axis('off')
        
        explanation = """
        ┌─────────────────────────────────────────────────────────────────────┐
        │  📚 GIẢI THÍCH CƠ BẢN                                               │
        ├─────────────────────────────────────────────────────────────────────┤
        │                                                                     │
        │  🔴 DropTail (Tail Drop):                                          │
        │     • Nhận packets cho đến khi buffer đầy                          │
        │     • Drop packets mới đến khi buffer full                         │
        │     • Đơn giản, dễ implement                                       │
        │     • Có thể gây "global synchronization"                          │
        │                                                                     │
        │  🔵 RED (Random Early Detection):                                  │
        │     • Monitor average queue length                                 │
        │     • Drop packets ngẫu nhiên TRƯỚC KHI queue full                 │
        │     • Cảnh báo sớm cho TCP về tắc nghẽn                           │
        │     • Tránh global synchronization                                 │
        │                                                                     │
        └─────────────────────────────────────────────────────────────────────┘
        """
        ax1.text(0.5, 0.5, explanation, ha='center', va='center',
                fontfamily='monospace', fontsize=10,
                bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.3))
        
        # Section 2: Key Metrics Comparison (Speedometer style)
        metrics_info = [
            ('Throughput', 'Mbps', dt_summary.get('avg_throughput', 0), 
             red_summary.get('avg_throughput', 0), 10, True),
            ('Loss Rate', '%', dt_summary.get('loss_rate', 0),
             red_summary.get('loss_rate', 0), 10, False),
            ('Delay', 'ms', dt_summary.get('avg_delay', 0),
             red_summary.get('avg_delay', 0), 100, False)
        ]
        
        for i, (metric, unit, dt_val, red_val, max_val, higher_better) in enumerate(metrics_info):
            ax = fig.add_subplot(gs[1, i if i < 2 else 0])
            
            if i >= 2:  # Delay in second row
                ax = fig.add_subplot(gs[2, 0])
            
            ax.set_xlim(-1.2, 1.2)
            ax.set_ylim(-0.2, 1.2)
            ax.axis('off')
            
            # Draw semi-circle gauge
            theta = np.linspace(0, np.pi, 100)
            x = np.cos(theta)
            y = np.sin(theta)
            
            # Background arc
            ax.plot(x, y, linewidth=15, color='lightgray', alpha=0.3)
            
            # DropTail arc
            dt_angle = (dt_val / max_val) * np.pi
            theta_dt = np.linspace(0, min(dt_angle, np.pi), 50)
            ax.plot(np.cos(theta_dt), np.sin(theta_dt), linewidth=15,
                   color=self.colors['DropTail'], alpha=0.8)
            
            # RED arc  
            red_angle = (red_val / max_val) * np.pi
            theta_red = np.linspace(0, min(red_angle, np.pi), 50)
            ax.plot(np.cos(theta_red), np.sin(theta_red), linewidth=8,
                   color=self.colors['RED'], alpha=0.9, linestyle='--')
            
            # Labels
            ax.text(0, -0.15, metric, ha='center', va='top',
                   fontsize=14, fontweight='bold')
            ax.text(-1, 0, '0', ha='center', fontsize=10)
            ax.text(1, 0, f'{max_val}', ha='center', fontsize=10)
            
            # Values
            ax.text(-0.5, 0.6, f'DT: {dt_val:.2f}{unit}',
                   ha='center', fontsize=11, color=self.colors['DropTail'],
                   fontweight='bold')
            ax.text(0.5, 0.6, f'RED: {red_val:.2f}{unit}',
                   ha='center', fontsize=11, color=self.colors['RED'],
                   fontweight='bold')
            
            # Winner badge
            if higher_better:
                winner = 'DT' if dt_val > red_val else 'RED'
                winner_color = self.colors['DropTail'] if winner == 'DT' else self.colors['RED']
            else:
                winner = 'DT' if dt_val < red_val else 'RED'
                winner_color = self.colors['DropTail'] if winner == 'DT' else self.colors['RED']
            
            circle = plt.Circle((0, 0.5), 0.15, color=winner_color, alpha=0.3)
            ax.add_patch(circle)
            ax.text(0, 0.5, f'✓\n{winner}', ha='center', va='center',
                   fontsize=10, fontweight='bold', color=winner_color)
        
        # Section 3: Events comparison bars
        ax3 = fig.add_subplot(gs[2, 1])
        
        events_data = {
            'Timeouts': (dt_summary.get('timeouts', 0), red_summary.get('timeouts', 0)),
            'Fast\nRetx': (dt_summary.get('fast_retransmits', 0), red_summary.get('fast_retransmits', 0)),
            'State\nChanges': (dt_summary.get('state_changes', 0), red_summary.get('state_changes', 0))
        }
        
        y_pos = np.arange(len(events_data))
        dt_vals = [v[0] for v in events_data.values()]
        red_vals = [v[1] for v in events_data.values()]
        
        bars1 = ax3.barh(y_pos - 0.2, dt_vals, 0.35, 
                        label='DropTail', color=self.colors['DropTail'], alpha=0.8)
        bars2 = ax3.barh(y_pos + 0.2, red_vals, 0.35,
                        label='RED', color=self.colors['RED'], alpha=0.8)
        
        ax3.set_yticks(y_pos)
        ax3.set_yticklabels(events_data.keys(), fontsize=11)
        ax3.set_xlabel('Count', fontsize=12, fontweight='bold')
        ax3.set_title('🔔 TCP Events Comparison', fontsize=14, fontweight='bold', pad=15)
        ax3.legend(fontsize=10)
        ax3.grid(True, axis='x', alpha=0.3)
        
        # Add values on bars
        for bars in [bars1, bars2]:
            for bar in bars:
                width = bar.get_width()
                ax3.text(width, bar.get_y() + bar.get_height()/2,
                        f' {int(width)}', va='center', fontsize=10, fontweight='bold')
        
        # Section 4: CWND Evolution Mini
        ax4 = fig.add_subplot(gs[3, :])
        ax4.plot(dt_data['time'][::10], dt_data['cwnd'][::10],
                linewidth=2, color=self.colors['DropTail'], label='DropTail', alpha=0.8)
        ax4.plot(red_data['time'][::10], red_data['cwnd'][::10],
                linewidth=2, color=self.colors['RED'], label='RED', alpha=0.8)
        ax4.fill_between(dt_data['time'][::10], 0, dt_data['cwnd'][::10],
                        color=self.colors['DropTail'], alpha=0.1)
        ax4.fill_between(red_data['time'][::10], 0, red_data['cwnd'][::10],
                        color=self.colors['RED'], alpha=0.1)
        ax4.set_xlabel('Time (s)', fontsize=12, fontweight='bold')
        ax4.set_ylabel('CWND (KB)', fontsize=12, fontweight='bold')
        ax4.set_title('📈 Congestion Window Evolution', fontsize=14, fontweight='bold', pad=15)
        ax4.legend(fontsize=11, loc='upper right')
        ax4.grid(True, alpha=0.3, linestyle=':')
        ax4.set_facecolor('white')
        
        # Section 5: Pros & Cons
        ax5 = fig.add_subplot(gs[4, 0])
        ax5.axis('off')
        
        droptail_text = """
        ┌─── 🔴 DropTail ───────────┐
        │                           │
        │ ✅ ADVANTAGES:            │
        │  • Simple                 │
        │  • Low overhead           │
        │  • Easy to implement      │
        │  • Good for light load    │
        │                           │
        │ ❌ DISADVANTAGES:         │
        │  • Bursty drops           │
        │  • Global sync            │
        │  • High delay variance    │
        │  • Poor under heavy load  │
        │                           │
        └───────────────────────────┘
        """
        ax5.text(0.5, 0.5, droptail_text, ha='center', va='center',
                fontfamily='monospace', fontsize=9,
                bbox=dict(boxstyle='round', facecolor=self.colors['DropTail'], 
                         alpha=0.2, edgecolor=self.colors['DropTail'], linewidth=3))
        
        ax6 = fig.add_subplot(gs[4, 1])
        ax6.axis('off')
        
        red_text = """
        ┌─── 🔵 RED ────────────────┐
        │                           │
        │ ✅ ADVANTAGES:            │
        │  • Early detection        │
        │  • Prevents sync          │
        │  • Lower delay            │
        │  • Better for heavy load  │
        │                           │
        │ ❌ DISADVANTAGES:         │
        │  • More complex           │
        │  • Parameter tuning       │
        │  • Higher CPU usage       │
        │  • May drop unnecessarily │
        │                           │
        └───────────────────────────┘
        """
        ax6.text(0.5, 0.5, red_text, ha='center', va='center',
                fontfamily='monospace', fontsize=9,
                bbox=dict(boxstyle='round', facecolor=self.colors['RED'],
                         alpha=0.2, edgecolor=self.colors['RED'], linewidth=3))
        
        # Section 6: Final Recommendation
        ax7 = fig.add_subplot(gs[5, :])
        ax7.axis('off')
        
        # Calculate winner
        dt_score = 0
        red_score = 0
        
        if dt_summary.get('avg_throughput', 0) > red_summary.get('avg_throughput', 0):
            dt_score += 1
        else:
            red_score += 1
        
        if dt_summary.get('loss_rate', 100) < red_summary.get('loss_rate', 100):
            dt_score += 1
        else:
            red_score += 1
        
        if dt_summary.get('avg_delay', 100) < red_summary.get('avg_delay', 100):
            dt_score += 1
        else:
            red_score += 1
        
        if dt_summary.get('timeouts', 100) < red_summary.get('timeouts', 100):
            dt_score += 1
        else:
            red_score += 1
        
        winner = 'DropTail' if dt_score > red_score else 'RED'
        winner_color = self.colors[winner]
        
        recommendation = f"""
        ╔═══════════════════════════════════════════════════════════════════╗
        ║                    🏆 FINAL RECOMMENDATION                        ║
        ╠═══════════════════════════════════════════════════════════════════╣
        ║                                                                   ║
        ║         Winner: {winner.upper():^20}                              ║
        ║         Score: {max(dt_score, red_score)}/{dt_score + red_score}                                              ║
        ║                                                                   ║
        ║  📌 Use DropTail when:                                           ║
        ║     • Network load is light to moderate                          ║
        ║     • Simplicity is preferred                                    ║
        ║     • Resources are limited                                      ║
        ║                                                                   ║
        ║  📌 Use RED when:                                                ║
        ║     • Network experiences heavy congestion                       ║
        ║     • Low latency is critical                                    ║
        ║     • Multiple flows share the bottleneck                        ║
        ║     • Want to prevent global synchronization                     ║
        ║                                                                   ║
        ╚═══════════════════════════════════════════════════════════════════╝
        """
        
        ax7.text(0.5, 0.5, recommendation, ha='center', va='center',
                fontfamily='monospace', fontsize=10,
                bbox=dict(boxstyle='round', facecolor=winner_color,
                         alpha=0.15, edgecolor=winner_color, linewidth=4))
        
        plt.tight_layout()
        
        output_file = self.results_dir / f"{self.prefix}_infographic.png"
        plt.savefig(output_file, dpi=300, bbox_inches='tight',
                   facecolor='white')
        print(f"\n✅ Infographic đã lưu: {output_file}")
        plt.show()


def main():
    parser = argparse.ArgumentParser(
        description='TCP Reno Visual Analyzer - Enhanced Version',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎨 Examples:
  # Dashboard cho 1 loại hàng đợi
  python3 analyze.py --queue DropTail --dashboard
  
  # So sánh cả hai
  python3 analyze.py --compare --dashboard
  
  # Tạo infographic tổng hợp
  python3 analyze.py --infographic
  
  # Timeline chi tiết
  python3 analyze.py --queue RED --timeline
  
  # Full analysis
  python3 analyze.py --compare --dashboard --infographic --print
        """
    )


    parser.add_argument('--results-dir', default='results/',
                       help='Thư mục chứa kết quả')
    parser.add_argument('--prefix', default='P2P-project',
                       help='Prefix của files')
    parser.add_argument('--queue', choices=['DropTail', 'RED'],
                       help='Phân tích loại hàng đợi cụ thể')
    parser.add_argument('--compare', action='store_true',
                       help='So sánh DropTail vs RED')
    parser.add_argument('--dashboard', action='store_true',
                       help='Tạo dashboard trực quan')
    parser.add_argument('--timeline', action='store_true',
                       help='Tạo timeline chi tiết')
    parser.add_argument('--infographic', action='store_true',
                       help='Tạo infographic tổng hợp')
    parser.add_argument('--print', action='store_true',
                       help='In phân tích chi tiết ra terminal')

    args = parser.parse_args()

    # Create analyzer
    analyzer = EnhancedTCPAnalyzer(args.results_dir, args.prefix)

    print("\n" + "="*70)
    print("🎨 TCP RENO VISUAL ANALYZER - ENHANCED")
    print("="*70)

    try:
        if args.infographic:
            # Load both and create infographic
            print("\n📊 Đang tạo infographic tổng hợp...")
            analyzer.load_data('DropTail')
            analyzer.load_data('RED')
            analyzer.create_infographic()

        if args.compare:
            # Compare mode
            analyzer.load_data('DropTail')
            analyzer.load_data('RED')
            
            if args.print:
                print("\n📋 PHÂN TÍCH DROPTAIL:")
                analyzer.print_analysis('DropTail')
                print("\n📋 PHÂN TÍCH RED:")
                analyzer.print_analysis('RED')
            
            if args.dashboard:
                print("\n📊 Đang tạo comparison dashboard...")
                analyzer.create_comparison_dashboard()

        elif args.queue:
            # Single queue mode
            analyzer.load_data(args.queue)
            
            if args.print:
                analyzer.print_analysis(args.queue)
            
            if args.dashboard:
                print(f"\n📊 Đang tạo dashboard cho {args.queue}...")
                analyzer.create_dashboard(args.queue)
            
            if args.timeline:
                print(f"\n⏱️ Đang tạo timeline cho {args.queue}...")
                analyzer.create_animated_timeline(args.queue)
        
        else:
            print("\n❌ Lỗi: Phải chọn --queue <type> hoặc --compare hoặc --infographic")
            print("📖 Dùng --help để xem hướng dẫn")
            return 1

    except FileNotFoundError as e:
        print(f"\n❌ Lỗi: Không tìm thấy file - {e}")
        print("💡 Hãy chắc chắn bạn đã chạy simulation và có file kết quả")
        return 1
    except Exception as e:
        print(f"\n❌ Lỗi không mong đợi: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n" + "="*70)
    print("✅ Phân tích hoàn tất!")
    print("="*70 + "\n")

    return 0

if __name__ == '__main__':
    sys.exit(main())
