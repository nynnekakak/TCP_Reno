"""
Dashboard utilities for visualization
Các hàm tạo dashboard và biểu đồ
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.patches import Rectangle
from .data_utils import count_events


def create_dashboard(analyzer, queue_type, show_gui=False):
    """Tạo dashboard trực quan đẹp mắt cho 1 loại hàng đợi"""
    data = analyzer.data[queue_type]
    summary = data['summary']
    colors = analyzer.colors
    
    # Tạo figure với kích thước lớn
    fig = plt.figure(figsize=(20, 12))
    fig.patch.set_facecolor(colors['background'])
    
    # Tạo layout phức tạp hơn
    gs = GridSpec(4, 3, figure=fig, hspace=0.5, wspace=0.35,
                 left=0.06, right=0.96, top=0.90, bottom=0.06)

    # ===== 1. CWND Evolution =====
    ax1 = fig.add_subplot(gs[0:2, :])
    time = np.array(data['time'])
    cwnd = np.array(data['cwnd'])
    
    ax1.plot(time, cwnd, linewidth=3, color=colors[queue_type], 
            label=f'{queue_type} CWND', alpha=0.9, zorder=3)
    ax1.plot(time, cwnd, linewidth=6, color=colors[queue_type], 
            alpha=0.2, zorder=2)
    ax1.fill_between(time, 0, cwnd, color=colors[queue_type], 
                    alpha=0.15, zorder=1)
    
    # Đánh dấu events
    timeouts = [e for e in data['events'] if e['event'] == 'TIMEOUT_EVENT']
    fast_retx = [e for e in data['events'] if e['event'] == 'TRIPLE_DUP_ACK']
    
    for event in timeouts[:10]:
        t = event['time']
        if t < max(time):
            idx = np.argmin(np.abs(time - t))
            ax1.axvline(x=t, color=colors['danger'], linestyle='--', 
                      linewidth=2, alpha=0.6, zorder=4)
            ax1.scatter([t], [cwnd[idx]], color=colors['danger'], 
                      s=150, marker='X', edgecolors='white', linewidths=2, 
                      zorder=5, label='Timeout' if event == timeouts[0] else '')
    
    for event in fast_retx[:10]:
        t = event['time']
        if t < max(time):
            idx = np.argmin(np.abs(time - t))
            ax1.scatter([t], [cwnd[idx]], color=colors['warning'], 
                      s=100, marker='v', edgecolors='white', linewidths=2, 
                      zorder=5, label='Fast Retransmit' if event == fast_retx[0] else '')
    
    ax1.set_xlabel('Time (seconds)', fontsize=13, fontweight='bold')
    ax1.set_ylabel('Congestion Window (KB)', fontsize=13, fontweight='bold')
    ax1.set_title(f'Congestion Window Evolution - {queue_type}', 
                 fontsize=16, fontweight='bold', pad=15)
    ax1.legend(loc='upper right', fontsize=10, framealpha=0.9)
    ax1.grid(True, alpha=0.3, linestyle=':', linewidth=1)
    ax1.set_facecolor('white')
    
    stats_text = f'Max: {np.max(cwnd):.1f} KB\nAvg: {np.mean(cwnd):.1f} KB\nMin: {np.min(cwnd):.1f} KB'
    ax1.text(0.02, 0.98, stats_text, transform=ax1.transAxes,
            fontsize=10, verticalalignment='top',
            bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.8))

    # ===== 2. Performance Metrics Cards =====
    metrics_data = [
        ('Throughput', f"{summary.get('avg_throughput', 0):.2f}", 'Mbps', colors['success']),
        ('Packet Loss', f"{summary.get('loss_rate', 0):.2f}", '%', colors['danger']),
        ('Avg Delay', f"{summary.get('avg_delay', 0):.2f}", 'ms', colors['accent3'])
    ]
    
    for i, (title, value, unit, color) in enumerate(metrics_data):
        ax = fig.add_subplot(gs[2, i])
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.axis('off')
        
        rect = Rectangle((0.05, 0.15), 0.9, 0.75, facecolor=color, alpha=0.2, 
                       edgecolor=color, linewidth=3)
        ax.add_patch(rect)
        
        ax.text(0.5, 0.72, title, ha='center', va='center',
               fontsize=12, fontweight='bold', color=colors['text'])
        ax.text(0.5, 0.48, value, ha='center', va='center',
               fontsize=24, fontweight='bold', color=color)
        ax.text(0.5, 0.28, unit, ha='center', va='center',
               fontsize=11, color=colors['text'], alpha=0.7)

    # ===== 3. Events Bar Chart =====
    ax4 = fig.add_subplot(gs[3, 0])
    event_counts = count_events(data['events'])
    
    events_to_plot = ['DUP_ACK', 'TRIPLE_DUP_ACK', 'TIMEOUT_EVENT', 'NEW_ACK']
    event_labels = ['Dup ACKs', 'Fast Retx', 'Timeouts', 'New ACKs']
    event_values = [event_counts.get(e, 0) for e in events_to_plot]
    event_colors = [colors['accent1'], colors['warning'], 
                   colors['danger'], colors['success']]
    
    bars = ax4.barh(event_labels, event_values, color=event_colors, 
                   alpha=0.8, edgecolor='white', linewidth=2)
    
    for bar, val in zip(bars, event_values):
        width = bar.get_width()
        ax4.text(width + max(event_values)*0.02, bar.get_y() + bar.get_height()/2,
                f'{int(val)}', ha='left', va='center', 
                fontsize=11, fontweight='bold')
    
    ax4.set_xlabel('Count', fontsize=11, fontweight='bold')
    ax4.set_title('TCP Events Statistics', fontsize=13, fontweight='bold', pad=12)
    ax4.grid(True, axis='x', alpha=0.3)
    ax4.set_facecolor('white')
    ax4.tick_params(labelsize=10)

    # ===== 4. CWND Distribution Histogram =====
    ax5 = fig.add_subplot(gs[3, 1])
    n, bins, patches = ax5.hist(cwnd, bins=30, color=colors[queue_type], 
                                alpha=0.7, edgecolor='white', linewidth=1.5)
    
    cm = plt.cm.get_cmap('RdYlGn')
    bin_centers = 0.5 * (bins[:-1] + bins[1:])
    col = bin_centers - min(bin_centers)
    col /= max(col)
    for c, p in zip(col, patches):
        plt.setp(p, 'facecolor', cm(c))
    
    ax5.axvline(np.mean(cwnd), color='red', linestyle='--', 
               linewidth=2.5, label=f'Mean: {np.mean(cwnd):.1f}', alpha=0.8)
    ax5.axvline(np.median(cwnd), color='blue', linestyle='--', 
               linewidth=2.5, label=f'Median: {np.median(cwnd):.1f}', alpha=0.8)
    
    ax5.set_xlabel('CWND (KB)', fontsize=11, fontweight='bold')
    ax5.set_ylabel('Frequency', fontsize=11, fontweight='bold')
    ax5.set_title('CWND Distribution', fontsize=13, fontweight='bold', pad=12)
    ax5.legend(fontsize=9)
    ax5.grid(True, alpha=0.3, axis='y')
    ax5.set_facecolor('white')
    ax5.tick_params(labelsize=10)

    # ===== 5. Summary Table =====
    ax6 = fig.add_subplot(gs[3, 2])
    ax6.axis('off')
    
    table_data = [
        ['Packets Sent', f"{int(summary.get('total_tx', 0)):,}"],
        ['Packets Received', f"{int(summary.get('total_rx', 0)):,}"],
        ['Packets Lost', f"{int(summary.get('total_lost', 0)):,}"],
        ['State Changes', f"{int(summary.get('state_changes', 0)):,}"],
        ['Timeouts', f"{int(summary.get('timeouts', 0)):,}"],
        ['Fast Retransmits', f"{int(summary.get('fast_retransmits', 0)):,}"]
    ]
    
    table = ax6.table(cellText=table_data, cellLoc='left', loc='center',
                     colWidths=[0.58, 0.42])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.2)
    
    for i in range(len(table_data)):
        for j in range(2):
            cell = table[(i, j)]
            if i % 2 == 0:
                cell.set_facecolor('#F0F0F0')
            else:
                cell.set_facecolor('white')
            cell.set_edgecolor(colors['grid'])
            cell.set_linewidth(2)
            if j == 1:
                cell.set_text_props(weight='bold', color=colors[queue_type])
    
    ax6.set_title('Summary Statistics', fontsize=13, fontweight='bold', pad=15)

    if not show_gui:
        fig.suptitle(f'TCP Reno Performance Dashboard - {queue_type} Queue', 
                    fontsize=20, fontweight='bold', y=0.96)

    output_file = analyzer.results_dir / f"{analyzer.prefix}_dashboard_{queue_type}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight', 
               facecolor=colors['background'])
    print(f"\nDashboard saved: {output_file}")
    if not show_gui:
        plt.show()
    return fig


def create_comparison_dashboard(analyzer, show_gui=False):
    """Tạo dashboard so sánh DropTail vs RED"""
    colors = analyzer.colors
    dt_data = analyzer.data['DropTail']
    red_data = analyzer.data['RED']
    
    fig = plt.figure(figsize=(24, 14))
    fig.patch.set_facecolor(colors['background'])
    
    gs = GridSpec(3, 3, figure=fig, hspace=0.4, wspace=0.3,
                 left=0.05, right=0.95, top=0.91, bottom=0.06)

    # ===== 1. CWND Comparison =====
    ax1 = fig.add_subplot(gs[0, :])
    
    ax1.plot(dt_data['time'], dt_data['cwnd'], linewidth=3, 
            color=colors['DropTail'], label='DropTail', alpha=0.85, zorder=3)
    ax1.fill_between(dt_data['time'], 0, dt_data['cwnd'],
                    color=colors['DropTail'], alpha=0.15, zorder=1)
    
    ax1.plot(red_data['time'], red_data['cwnd'], linewidth=3, 
            color=colors['RED'], label='RED', alpha=0.85, zorder=3)
    ax1.fill_between(red_data['time'], 0, red_data['cwnd'],
                    color=colors['RED'], alpha=0.15, zorder=1)
    
    ax1.set_xlabel('Time (seconds)', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Congestion Window (KB)', fontsize=14, fontweight='bold')
    ax1.set_title('CWND Evolution Comparison: DropTail vs RED', 
                 fontsize=18, fontweight='bold', pad=18)
    ax1.legend(loc='upper right', fontsize=13, framealpha=0.95)
    ax1.grid(True, alpha=0.3, linestyle=':', linewidth=1.5)
    ax1.set_facecolor('white')
    ax1.tick_params(labelsize=12)

    # ===== 2. Performance Metrics Comparison =====
    metrics = ['avg_throughput', 'loss_rate', 'avg_delay']
    metric_labels = ['Throughput (Mbps)', 'Loss Rate (%)', 'Avg Delay (ms)']
    metric_colors = [colors['success'], colors['danger'], colors['accent3']]
    
    for idx, (metric, label, color) in enumerate(zip(metrics, metric_labels, metric_colors)):
        ax = fig.add_subplot(gs[1, idx])
        
        dt_val = dt_data['summary'].get(metric, 0)
        red_val = red_data['summary'].get(metric, 0)
        
        bars = ax.bar(['DropTail', 'RED'], [dt_val, red_val],
                     color=[colors['DropTail'], colors['RED']], 
                     alpha=0.7, edgecolor='white', linewidth=2.5)
        
        for bar, val in zip(bars, [dt_val, red_val]):
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{val:.2f}', ha='center', va='bottom',
                   fontsize=13, fontweight='bold')
        
        ax.set_ylabel(label, fontsize=12, fontweight='bold')
        ax.set_title(label.split('(')[0].strip(), fontsize=14, fontweight='bold', pad=12)
        ax.grid(True, alpha=0.3, axis='y')
        ax.set_facecolor('white')
        ax.tick_params(labelsize=11)

    # ===== 3. Event Comparison =====
    ax4 = fig.add_subplot(gs[2, 0])
    
    dt_events = count_events(dt_data['events'])
    red_events = count_events(red_data['events'])
    
    events = ['TIMEOUT_EVENT', 'TRIPLE_DUP_ACK', 'DUP_ACK']
    event_labels = ['Timeouts', 'Fast Retransmits', 'Dup ACKs']
    
    x = np.arange(len(events))
    width = 0.35
    
    dt_values = [dt_events.get(e, 0) for e in events]
    red_values = [red_events.get(e, 0) for e in events]
    
    ax4.bar(x - width/2, dt_values, width, label='DropTail',
           color=colors['DropTail'], alpha=0.8, edgecolor='white', linewidth=2)
    ax4.bar(x + width/2, red_values, width, label='RED',
           color=colors['RED'], alpha=0.8, edgecolor='white', linewidth=2)
    
    ax4.set_xlabel('Event Type', fontsize=12, fontweight='bold')
    ax4.set_ylabel('Count', fontsize=12, fontweight='bold')
    ax4.set_title('TCP Events Comparison', fontsize=14, fontweight='bold', pad=12)
    ax4.set_xticks(x)
    ax4.set_xticklabels(event_labels, fontsize=10)
    ax4.legend(fontsize=11)
    ax4.grid(True, alpha=0.3, axis='y')
    ax4.set_facecolor('white')
    ax4.tick_params(labelsize=10)

    # ===== 4. CWND Distribution Comparison =====
    ax5 = fig.add_subplot(gs[2, 1])
    
    ax5.hist(dt_data['cwnd'], bins=30, alpha=0.6, label='DropTail',
            color=colors['DropTail'], edgecolor='white', linewidth=1)
    ax5.hist(red_data['cwnd'], bins=30, alpha=0.6, label='RED',
            color=colors['RED'], edgecolor='white', linewidth=1)
    
    ax5.axvline(np.mean(dt_data['cwnd']), color=colors['DropTail'], 
               linestyle='--', linewidth=2.5, alpha=0.8,
               label=f'DT Mean: {np.mean(dt_data["cwnd"]):.1f}')
    ax5.axvline(np.mean(red_data['cwnd']), color=colors['RED'], 
               linestyle='--', linewidth=2.5, alpha=0.8,
               label=f'RED Mean: {np.mean(red_data["cwnd"]):.1f}')
    
    ax5.set_xlabel('CWND (KB)', fontsize=12, fontweight='bold')
    ax5.set_ylabel('Frequency', fontsize=12, fontweight='bold')
    ax5.set_title('CWND Distribution Comparison', fontsize=14, fontweight='bold', pad=12)
    ax5.legend(fontsize=9)
    ax5.grid(True, alpha=0.3, axis='y')
    ax5.set_facecolor('white')
    ax5.tick_params(labelsize=10)

    # ===== 5. Summary Comparison Table =====
    ax6 = fig.add_subplot(gs[2, 2])
    ax6.axis('off')
    
    table_data = [
        ['Metric', 'DropTail', 'RED'],
        ['Throughput (Mbps)', 
         f"{dt_data['summary'].get('avg_throughput', 0):.2f}",
         f"{red_data['summary'].get('avg_throughput', 0):.2f}"],
        ['Loss Rate (%)', 
         f"{dt_data['summary'].get('loss_rate', 0):.2f}",
         f"{red_data['summary'].get('loss_rate', 0):.2f}"],
        ['Avg Delay (ms)', 
         f"{dt_data['summary'].get('avg_delay', 0):.2f}",
         f"{red_data['summary'].get('avg_delay', 0):.2f}"],
        ['Timeouts', 
         f"{int(dt_data['summary'].get('timeouts', 0)):,}",
         f"{int(red_data['summary'].get('timeouts', 0)):,}"],
        ['Fast Retransmits', 
         f"{int(dt_data['summary'].get('fast_retransmits', 0)):,}",
         f"{int(red_data['summary'].get('fast_retransmits', 0)):,}"]
    ]
    
    table = ax6.table(cellText=table_data, cellLoc='center', loc='center',
                     colWidths=[0.4, 0.3, 0.3])
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 2.0)
    
    for i in range(len(table_data)):
        for j in range(3):
            cell = table[(i, j)]
            if i == 0:
                cell.set_facecolor(colors['accent1'])
                cell.set_text_props(weight='bold', color='white')
            elif i % 2 == 1:
                cell.set_facecolor('#F0F0F0')
            else:
                cell.set_facecolor('white')
            cell.set_edgecolor(colors['grid'])
            cell.set_linewidth(2)
            if j > 0 and i > 0:
                cell.set_text_props(weight='bold')
    
    ax6.set_title('Performance Summary', fontsize=14, fontweight='bold', pad=15)
    
    if not show_gui:
        fig.suptitle('TCP Reno: DropTail vs RED Queue Comparison', 
                    fontsize=22, fontweight='bold', y=0.97)

    output_file = analyzer.results_dir / f"{analyzer.prefix}_comparison_dashboard.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight',
               facecolor=colors['background'])
    print(f"\nComparison Dashboard saved: {output_file}")
    if not show_gui:
        plt.show()
    return fig


def create_animated_timeline(analyzer, queue_type, show_gui=False):
    """Tạo timeline view với annotations"""
    data = analyzer.data[queue_type]
    colors = analyzer.colors
    
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(18, 10), 
                                    gridspec_kw={'height_ratios': [3, 1]})
    fig.patch.set_facecolor(colors['background'])
    
    time = np.array(data['time'])
    cwnd = np.array(data['cwnd'])
    
    ax1.plot(time, cwnd, linewidth=2.5, color=colors[queue_type], 
            alpha=0.9, label='CWND')
    ax1.fill_between(time, 0, cwnd, color=colors[queue_type], alpha=0.2)
    
    # Mark events
    timeouts = [e for e in data['events'] if e['event'] == 'TIMEOUT_EVENT']
    fast_retx = [e for e in data['events'] if e['event'] == 'TRIPLE_DUP_ACK']
    
    for event in timeouts:
        t = event['time']
        if t < max(time):
            idx = np.argmin(np.abs(time - t))
            ax1.scatter([t], [cwnd[idx]], s=200, marker='X', 
                      color=colors['danger'], edgecolors='white',
                      linewidths=2, zorder=10, 
                      label='Timeout' if event == timeouts[0] else '')
            ax1.axvline(x=t, color=colors['danger'], 
                      linestyle='--', alpha=0.3, linewidth=2)
    
    for event in fast_retx:
        t = event['time']
        if t < max(time):
            idx = np.argmin(np.abs(time - t))
            ax1.scatter([t], [cwnd[idx]], s=150, marker='v',
                      color=colors['warning'], edgecolors='white',
                      linewidths=2, zorder=10, 
                      label='Fast Retx' if event == fast_retx[0] else '')
    
    ax1.set_ylabel('CWND (KB)', fontsize=13, fontweight='bold')
    ax1.set_title(f'Detailed Timeline - {queue_type}', 
                 fontsize=16, fontweight='bold', pad=15)
    ax1.legend(loc='upper right', fontsize=10, framealpha=0.95)
    ax1.grid(True, alpha=0.3, linestyle=':')
    ax1.set_facecolor('white')
    ax1.tick_params(labelsize=11)
    
    # Event density heatmap
    event_times = [e['time'] for e in data['events']]
    if event_times:
        hist, bins = np.histogram(event_times, bins=50, range=(0, max(time)))
        colors_map = plt.cm.YlOrRd(hist / max(hist) if max(hist) > 0 else hist)
        
        for i in range(len(bins)-1):
            ax2.add_patch(Rectangle((bins[i], 0), bins[i+1]-bins[i], 1,
                                   facecolor=colors_map[i], edgecolor='none'))
    
    ax2.set_xlabel('Time (seconds)', fontsize=13, fontweight='bold')
    ax2.set_ylabel('Event\nDensity', fontsize=10, fontweight='bold')
    ax2.set_xlim(0, max(time))
    ax2.set_ylim(0, 1)
    ax2.set_yticks([])
    ax2.set_facecolor('white')
    ax2.tick_params(labelsize=11)
    
    plt.tight_layout()
    
    output_file = analyzer.results_dir / f"{analyzer.prefix}_timeline_{queue_type}.png"
    plt.savefig(output_file, dpi=300, bbox_inches='tight',
               facecolor=colors['background'])
    print(f"\nTimeline saved: {output_file}")
    if not show_gui:
        plt.show()
    return fig
