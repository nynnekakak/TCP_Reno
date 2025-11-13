"""
Reporting utilities for analysis and infographic
Functions for creating reports and infographics
"""

import numpy as np
import datetime
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.widgets import Button
from .data_utils import count_events


def show_interactive_infographic(figures):
    """Show all pages in ONE window with proper scrolling
    
    Args:
        figures: List of (title, figure) tuples
    """
    import tkinter as tk
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
    from matplotlib.figure import Figure
    
    print("\n   📖 Creating scrollable infographic window...")
    
    total_pages = len(figures)
    
    # Close any existing matplotlib figures
    plt.close('all')
    
    # Create Tkinter window
    root = tk.Tk()
    root.title("TCP RENO INFOGRAPHIC - Complete Analysis")
    root.geometry("1400x800")
    
    # Create main frame with scrollbar
    main_frame = tk.Frame(root)
    main_frame.pack(fill=tk.BOTH, expand=1)
    
    # Create canvas for scrolling
    canvas = tk.Canvas(main_frame, bg='white')
    canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=1)
    
    # Add scrollbar
    scrollbar = tk.Scrollbar(main_frame, orient=tk.VERTICAL, command=canvas.yview)
    scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
    
    # Configure canvas
    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
    
    # Create frame inside canvas for content
    content_frame = tk.Frame(canvas, bg='white')
    canvas.create_window((0, 0), window=content_frame, anchor="nw")
    
    # Add title
    title_label = tk.Label(content_frame, 
                          text="TCP RENO INFOGRAPHIC - Complete Analysis",
                          font=('Arial', 24, 'bold'),
                          bg='white', fg='#2C3E50',
                          pady=15)
    title_label.pack(pady=(10, 20), padx=10)
    
    print(f"   Adding {total_pages} pages with full resolution...")
    
    # Add each page figure
    for i, (title, source_fig) in enumerate(figures):
        print(f"   ├─ Page {i+1}: {title}")
        
        # Page title with more spacing
        page_title = tk.Label(content_frame,
                             text=title,
                             font=('Arial', 18, 'bold'),
                             bg='#E3F2FD', fg='#2C3E50',
                             relief=tk.RAISED, bd=3,
                             pady=15)
        page_title.pack(pady=(30, 40), padx=20, fill=tk.X)
        
        # Create a frame for the figure with proper spacing
        fig_frame = tk.Frame(content_frame, bg='white', relief=tk.SOLID, bd=1)
        fig_frame.pack(pady=(0, 30), padx=20, fill=tk.BOTH)
        
        # Remove all text elements from figure (titles, suptitles)
        # Keep only the plots and charts
        for text_obj in source_fig.texts:
            text_obj.set_visible(False)
        
        # Adjust margins to use full space with more top padding
        source_fig.subplots_adjust(top=0.93, bottom=0.05)
        
        # Embed matplotlib figure
        canvas_fig = FigureCanvasTkAgg(source_fig, master=fig_frame)
        canvas_fig.draw()
        canvas_fig.get_tk_widget().pack(padx=10, pady=10, fill=tk.BOTH, expand=True)
        
        # Add divider (except last page)
        if i < total_pages - 1:
            divider = tk.Frame(content_frame, height=3, bg='#BDC3C7', relief=tk.SUNKEN)
            divider.pack(fill=tk.X, padx=20, pady=(10, 20))
    
    # Instructions at bottom
    instructions = tk.Label(content_frame,
                           text="📜 Scroll to view all pages | 💾 Right-click on charts to save | ❌ Close window when done",
                           font=('Arial', 10, 'italic'),
                           bg='#ECF0F1', fg='#7F8C8D',
                           pady=10)
    instructions.pack(pady=20, fill=tk.X)
    
    # Update scroll region
    content_frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox("all"))
    
    # Mouse wheel scrolling
    def _on_mousewheel(event):
        canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    canvas.bind_all("<MouseWheel>", _on_mousewheel)
    
    print("   └─ Complete! Opening scrollable window...")
    print("\n   ✅ Displaying in scrollable window...")
    print("   💡 Use mouse wheel or scrollbar to view all pages")
    print("   ⏳ Window will stay open until you close it...")
    
    # Start GUI loop
    root.mainloop()


def print_analysis(analyzer, queue_type):
    """Print detailed analysis with emojis and colors"""
    data = analyzer.data[queue_type]
    summary = data['summary']
    
    print(f"\n{'='*70}")
    print(f"📊 DETAILED ANALYSIS: {queue_type} Queue")
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
            status = "Very stable"
        elif stability > 50:
            emoji = "⚠️"
            status = "Fairly stable"
        else:
            emoji = "❌"
            status = "Unstable"
        
        print(f"   {emoji} Stability:      {stability:>8.1f}% ({status})")
    
    # 2. Performance Metrics
    print(f"\n⚡ PERFORMANCE:")
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
    print(f"\n🔔 TCP EVENTS:")
    print(f"   {'─'*60}")
    event_counts = count_events(data['events'])
    
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
    print(f"\n💡 EVALUATION:")
    print(f"   {'─'*60}")
    
    if loss < 1 and timeouts < 3:
        print(f"   ✅ Connection performing very well with low packet loss")
        print(f"   ✅ Effective congestion control mechanism")
    elif loss < 5 and timeouts < 10:
        print(f"   ⚠️  Moderate congestion, TCP is adjusting")
        print(f"   ⚠️  Acceptable performance")
    else:
        print(f"   ❌ Severe congestion or overload")
        print(f"   ❌ Consider reviewing queue configuration")
    
    if queue_type == 'RED':
        print(f"\n   🎯 RED is working:")
        if delay < 30:
            print(f"   ✅ Keeping delay low through early dropping")
        if timeouts < 5:
            print(f"   ✅ Reducing timeouts via early warning")
    elif queue_type == 'DropTail':
        print(f"\n   🎯 DropTail is working:")
        if loss > 3:
            print(f"   ⚠️  Possible global synchronization")
        print(f"   ℹ️  Simple FIFO with tail drop")


def create_page1_overview(analyzer):
    """Page 1: Overview and Queue Explanation"""
    colors = analyzer.colors
    dt_summary = analyzer.data['DropTail']['summary']
    red_summary = analyzer.data['RED']['summary']
    
    fig = plt.figure(figsize=(16, 11))
    fig.patch.set_facecolor('#FFFFFF')
    
    # Title
    fig.text(0.5, 0.96, 'TCP RENO PERFORMANCE ANALYSIS', 
            ha='center', va='top', fontsize=32, fontweight='bold',
            color='#2C3E50')
    fig.text(0.5, 0.92, 'Comparison: DropTail vs RED Queue Management',
            ha='center', va='top', fontsize=16, style='italic',
            color='#7F8C8D')
    
    gs = GridSpec(3, 1, figure=fig, 
                  hspace=0.4, left=0.08, right=0.92, 
                  top=0.88, bottom=0.06,
                  height_ratios=[1.2, 1.5, 1.3])
    
    # Section 1: Queue Explanation
    ax1 = fig.add_subplot(gs[0])
    ax1.axis('off')
    
    explanation = """QUEUE MANAGEMENT MECHANISMS

DropTail (Tail Drop)                                           RED (Random Early Detection)
───────────────────────────────────────────────────────────────────────────────────────────────
• Accepts packets until buffer is full                         • Monitors average queue length continuously
• Drops new packets when buffer reaches capacity               • Randomly drops packets BEFORE queue is full
• Simple FIFO (First In First Out) implementation              • Provides early congestion warning to TCP
• May cause "global synchronization" problem                   • Prevents global synchronization effectively"""
    
    ax1.text(0.5, 0.5, explanation, ha='center', va='center',
            fontsize=13, family='monospace', linespacing=2.2,
            bbox=dict(boxstyle='round,pad=2', 
                     facecolor='#FFF9E6', 
                     edgecolor='#F39C12',
                     linewidth=3, alpha=0.9))
    
    # Section 2: Key Metrics Table
    ax2 = fig.add_subplot(gs[1])
    ax2.axis('off')
    
    ax2.text(0.5, 0.95, 'KEY PERFORMANCE METRICS', 
            ha='center', va='top', fontsize=18, fontweight='bold',
            transform=ax2.transAxes, color='#2C3E50')
    
    metrics_data = [
        ['Metric', 'DropTail', 'RED', 'Winner'],
        ['Throughput (Mbps)', 
         f"{dt_summary.get('avg_throughput', 0):.3f}", 
         f"{red_summary.get('avg_throughput', 0):.3f}",
         '[*] DT' if dt_summary.get('avg_throughput', 0) > red_summary.get('avg_throughput', 0) else '[*] RED'],
        ['Packet Loss Rate (%)', 
         f"{dt_summary.get('loss_rate', 0):.2f}", 
         f"{red_summary.get('loss_rate', 0):.2f}",
         '[*] DT' if dt_summary.get('loss_rate', 0) < red_summary.get('loss_rate', 0) else '[*] RED'],
        ['Average Delay (ms)', 
         f"{dt_summary.get('avg_delay', 0):.2f}", 
         f"{red_summary.get('avg_delay', 0):.2f}",
         '[*] DT' if dt_summary.get('avg_delay', 0) < red_summary.get('avg_delay', 0) else '[*] RED'],
        ['Timeout Events', 
         f"{int(dt_summary.get('timeouts', 0))}", 
         f"{int(red_summary.get('timeouts', 0))}",
         '[*] DT' if dt_summary.get('timeouts', 0) < red_summary.get('timeouts', 0) else '[*] RED'],
        ['Fast Retransmits', 
         f"{int(dt_summary.get('fast_retransmits', 0))}", 
         f"{int(red_summary.get('fast_retransmits', 0))}",
         '[*] DT' if dt_summary.get('fast_retransmits', 0) < red_summary.get('fast_retransmits', 0) else '[*] RED'],
    ]
    
    table = ax2.table(cellText=metrics_data, 
                     cellLoc='center', loc='center',
                     colWidths=[0.38, 0.20, 0.20, 0.18],
                     bbox=[0.05, 0.05, 0.9, 0.8])
    
    table.auto_set_font_size(False)
    table.set_fontsize(14)
    
    for i in range(4):
        cell = table[(0, i)]
        cell.set_facecolor('#3498DB')
        cell.set_text_props(weight='bold', color='white', size=15)
        cell.set_height(0.15)
        cell.set_edgecolor('#2C3E50')
        cell.set_linewidth(2)
    
    for i in range(1, len(metrics_data)):
        for j in range(4):
            cell = table[(i, j)]
            cell.set_facecolor('#FFFFFF' if i % 2 == 0 else '#F8F9FA')
            cell.set_height(0.13)
            cell.set_edgecolor('#BDC3C7')
            cell.set_linewidth(1)
    
    # Section 3: Pros and Cons
    ax3 = fig.add_subplot(gs[2])
    ax3.axis('off')
    
    pros_cons = """ADVANTAGES & DISADVANTAGES

DropTail PROS                                 DropTail CONS                                 RED PROS                                      RED CONS
────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────────
✓ Simple implementation                       ✗ Global synchronization                      ✓ Prevents global sync                        ✗ Complex configuration
✓ Minimal CPU overhead                        ✗ Buffer bloat issues                         ✓ Lower average delay                         ✗ Parameter sensitivity
✓ Predictable behavior                        ✗ Higher latency spikes                       ✓ Better flow fairness                        ✗ Higher CPU overhead"""
    
    ax3.text(0.5, 0.5, pros_cons, ha='center', va='center',
            fontsize=13, family='monospace', linespacing=2.4,
            bbox=dict(boxstyle='round,pad=2', 
                     facecolor='#E8F5E9',
                     edgecolor='#27AE60',
                     linewidth=3, alpha=0.9))
    
    return fig


def create_page2_cwnd(analyzer):
    """Page 2: CWND Evolution Charts"""
    colors = analyzer.colors
    dt_data = analyzer.data['DropTail']
    red_data = analyzer.data['RED']
    
    fig = plt.figure(figsize=(16, 11))
    fig.patch.set_facecolor('#FFFFFF')
    
    fig.text(0.5, 0.96, 'CONGESTION WINDOW EVOLUTION', 
            ha='center', va='top', fontsize=32, fontweight='bold',
            color='#2C3E50')
    
    gs = GridSpec(2, 1, figure=fig, 
                  hspace=0.3, left=0.08, right=0.92, 
                  top=0.90, bottom=0.06)
    
    # DropTail CWND
    ax1 = fig.add_subplot(gs[0])
    if dt_data['cwnd']:
        times = np.array(dt_data['time'])
        cwnd = np.array(dt_data['cwnd'])
        ax1.plot(times, cwnd, color=colors['DropTail'], linewidth=3, alpha=0.9, label='CWND')
        ax1.fill_between(times, cwnd, alpha=0.25, color=colors['DropTail'])
        ax1.set_title('DropTail - Congestion Window Evolution', 
                     fontsize=20, fontweight='bold', pad=20, color='#2C3E50')
        ax1.set_xlabel('Time (seconds)', fontsize=16, fontweight='600')
        ax1.set_ylabel('CWND (KB)', fontsize=16, fontweight='600')
        ax1.grid(True, alpha=0.35, linestyle='--', linewidth=1)
        ax1.set_facecolor('#FAFBFC')
        ax1.legend(loc='upper right', fontsize=14)
        ax1.tick_params(labelsize=12)
    
    # RED CWND
    ax2 = fig.add_subplot(gs[1])
    if red_data['cwnd']:
        times = np.array(red_data['time'])
        cwnd = np.array(red_data['cwnd'])
        ax2.plot(times, cwnd, color=colors['RED'], linewidth=3, alpha=0.9, label='CWND')
        ax2.fill_between(times, cwnd, alpha=0.25, color=colors['RED'])
        ax2.set_title('RED - Congestion Window Evolution', 
                     fontsize=20, fontweight='bold', pad=20, color='#2C3E50')
        ax2.set_xlabel('Time (seconds)', fontsize=16, fontweight='600')
        ax2.set_ylabel('CWND (KB)', fontsize=16, fontweight='600')
        ax2.grid(True, alpha=0.35, linestyle='--', linewidth=1)
        ax2.set_facecolor('#FAFBFC')
        ax2.legend(loc='upper right', fontsize=14)
        ax2.tick_params(labelsize=12)
    
    return fig


def create_page3_performance(analyzer):
    """Page 3: Performance Comparison"""
    colors = analyzer.colors
    dt_summary = analyzer.data['DropTail']['summary']
    red_summary = analyzer.data['RED']['summary']
    
    fig = plt.figure(figsize=(16, 11))
    fig.patch.set_facecolor('#FFFFFF')
    
    fig.text(0.5, 0.96, 'PERFORMANCE COMPARISON', 
            ha='center', va='top', fontsize=32, fontweight='bold',
            color='#2C3E50')
    
    gs = GridSpec(2, 2, figure=fig, 
                  hspace=0.35, wspace=0.35,
                  left=0.08, right=0.92, 
                  top=0.90, bottom=0.06)
    
    queues = ['DropTail', 'RED']
    
    # Throughput
    ax1 = fig.add_subplot(gs[0, 0])
    throughputs = [dt_summary.get('avg_throughput', 0), 
                   red_summary.get('avg_throughput', 0)]
    bars1 = ax1.bar(queues, throughputs, 
                    color=[colors['DropTail'], colors['RED']],
                    width=0.5, alpha=0.85, edgecolor='#2C3E50', linewidth=2)
    ax1.set_title('Throughput Comparison', 
                  fontsize=18, fontweight='bold', pad=20, color='#2C3E50')
    ax1.set_ylabel('Throughput (Mbps)', fontsize=14, fontweight='600')
    ax1.grid(True, alpha=0.3, axis='y', linestyle='--', linewidth=1)
    ax1.set_facecolor('#FAFBFC')
    ax1.set_ylim(0, max(throughputs) * 1.3)
    ax1.tick_params(labelsize=12)
    
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height + max(throughputs)*0.03,
                f'{height:.3f}', ha='center', va='bottom',
                fontsize=14, fontweight='bold', color='#2C3E50')
    
    # Loss Rate
    ax2 = fig.add_subplot(gs[0, 1])
    loss_rates = [dt_summary.get('loss_rate', 0), 
                  red_summary.get('loss_rate', 0)]
    bars2 = ax2.bar(queues, loss_rates, 
                    color=[colors['DropTail'], colors['RED']],
                    width=0.5, alpha=0.85, edgecolor='#2C3E50', linewidth=2)
    ax2.set_title('Packet Loss Rate', 
                  fontsize=18, fontweight='bold', pad=20, color='#2C3E50')
    ax2.set_ylabel('Loss Rate (%)', fontsize=14, fontweight='600')
    ax2.grid(True, alpha=0.3, axis='y', linestyle='--', linewidth=1)
    ax2.set_facecolor('#FAFBFC')
    ax2.set_ylim(0, max(loss_rates) * 1.3 if max(loss_rates) > 0 else 1)
    ax2.tick_params(labelsize=12)
    
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., 
                height + (max(loss_rates)*0.03 if max(loss_rates) > 0 else 0.02),
                f'{height:.2f}%', ha='center', va='bottom',
                fontsize=14, fontweight='bold', color='#2C3E50')
    
    # Delay
    ax3 = fig.add_subplot(gs[1, 0])
    delays = [dt_summary.get('avg_delay', 0), 
              red_summary.get('avg_delay', 0)]
    bars3 = ax3.bar(queues, delays, 
                    color=[colors['DropTail'], colors['RED']],
                    width=0.5, alpha=0.85, edgecolor='#2C3E50', linewidth=2)
    ax3.set_title('Average Delay', 
                  fontsize=18, fontweight='bold', pad=20, color='#2C3E50')
    ax3.set_ylabel('Delay (milliseconds)', fontsize=14, fontweight='600')
    ax3.grid(True, alpha=0.3, axis='y', linestyle='--', linewidth=1)
    ax3.set_facecolor('#FAFBFC')
    ax3.set_ylim(0, max(delays) * 1.3 if max(delays) > 0 else 1)
    ax3.tick_params(labelsize=12)
    
    for bar in bars3:
        height = bar.get_height()
        ax3.text(bar.get_x() + bar.get_width()/2., 
                height + (max(delays)*0.03 if max(delays) > 0 else 0.02),
                f'{height:.2f}', ha='center', va='bottom',
                fontsize=14, fontweight='bold', color='#2C3E50')
    
    # Timeouts
    ax4 = fig.add_subplot(gs[1, 1])
    timeouts = [int(dt_summary.get('timeouts', 0)), 
                int(red_summary.get('timeouts', 0))]
    bars4 = ax4.bar(queues, timeouts, 
                    color=[colors['DropTail'], colors['RED']],
                    width=0.5, alpha=0.85, edgecolor='#2C3E50', linewidth=2)
    ax4.set_title('Timeout Events', 
                  fontsize=18, fontweight='bold', pad=20, color='#2C3E50')
    ax4.set_ylabel('Number of Timeouts', fontsize=14, fontweight='600')
    ax4.grid(True, alpha=0.3, axis='y', linestyle='--', linewidth=1)
    ax4.set_facecolor('#FAFBFC')
    ax4.set_ylim(0, max(timeouts) * 1.3 if max(timeouts) > 0 else 1)
    ax4.tick_params(labelsize=12)
    
    for bar in bars4:
        height = bar.get_height()
        ax4.text(bar.get_x() + bar.get_width()/2., 
                height + (max(timeouts)*0.03 if max(timeouts) > 0 else 0.02),
                f'{int(height)}', ha='center', va='bottom',
                fontsize=14, fontweight='bold', color='#2C3E50')
    
    return fig


def create_page4_packets(analyzer):
    """Page 4: Packet Statistics"""
    colors = analyzer.colors
    dt_summary = analyzer.data['DropTail']['summary']
    red_summary = analyzer.data['RED']['summary']
    
    fig = plt.figure(figsize=(16, 11))
    fig.patch.set_facecolor('#FFFFFF')
    
    fig.text(0.5, 0.96, 'PACKET STATISTICS', 
            ha='center', va='top', fontsize=32, fontweight='bold',
            color='#2C3E50')
    
    gs = GridSpec(2, 1, figure=fig, 
                  hspace=0.3, left=0.1, right=0.9, 
                  top=0.90, bottom=0.06)
    
    # DropTail packets
    ax1 = fig.add_subplot(gs[0])
    dt_packets = ['Sent', 'Received', 'Lost']
    dt_values = [dt_summary.get('total_tx', 0), 
                 dt_summary.get('total_rx', 0), 
                 dt_summary.get('total_lost', 0)]
    bars1 = ax1.bar(dt_packets, dt_values, 
                    color=['#3498DB', '#27AE60', '#E74C3C'],
                    width=0.5, alpha=0.85, edgecolor='#2C3E50', linewidth=2)
    ax1.set_title('DropTail - Packet Statistics', 
                  fontsize=20, fontweight='bold', pad=20, color='#2C3E50')
    ax1.set_ylabel('Number of Packets', fontsize=16, fontweight='600')
    ax1.grid(True, alpha=0.3, axis='y', linestyle='--', linewidth=1)
    ax1.set_facecolor('#FAFBFC')
    ax1.tick_params(labelsize=14)
    
    for bar in bars1:
        height = bar.get_height()
        ax1.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}', ha='center', va='bottom',
                fontsize=14, fontweight='bold', color='#2C3E50')
    
    # RED packets
    ax2 = fig.add_subplot(gs[1])
    red_packets = ['Sent', 'Received', 'Lost']
    red_values = [red_summary.get('total_tx', 0), 
                  red_summary.get('total_rx', 0), 
                  red_summary.get('total_lost', 0)]
    bars2 = ax2.bar(red_packets, red_values, 
                    color=['#3498DB', '#27AE60', '#E74C3C'],
                    width=0.5, alpha=0.85, edgecolor='#2C3E50', linewidth=2)
    ax2.set_title('RED - Packet Statistics', 
                  fontsize=20, fontweight='bold', pad=20, color='#2C3E50')
    ax2.set_ylabel('Number of Packets', fontsize=16, fontweight='600')
    ax2.grid(True, alpha=0.3, axis='y', linestyle='--', linewidth=1)
    ax2.set_facecolor('#FAFBFC')
    ax2.tick_params(labelsize=14)
    
    for bar in bars2:
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{int(height):,}', ha='center', va='bottom',
                fontsize=14, fontweight='bold', color='#2C3E50')
    
    return fig


def create_page5_recommendation(analyzer):
    """Page 5: Final Recommendation"""
    dt_summary = analyzer.data['DropTail']['summary']
    red_summary = analyzer.data['RED']['summary']
    
    fig = plt.figure(figsize=(16, 11))
    fig.patch.set_facecolor('#FFFFFF')
    
    fig.text(0.5, 0.96, 'FINAL RECOMMENDATION', 
            ha='center', va='top', fontsize=32, fontweight='bold',
            color='#2C3E50')
    
    ax = fig.add_subplot(111)
    ax.axis('off')
    
    delay_winner = "RED" if red_summary.get('avg_delay', 0) < dt_summary.get('avg_delay', 0) else "DropTail"
    loss_winner = "RED" if red_summary.get('loss_rate', 0) < dt_summary.get('loss_rate', 0) else "DropTail"
    
    # Get actual values for display
    dt_delay = dt_summary.get('avg_delay', 0)
    red_delay = red_summary.get('avg_delay', 0)
    dt_loss = dt_summary.get('loss_rate', 0)
    red_loss = red_summary.get('loss_rate', 0)
    
    recommendation = f"""PERFORMANCE SUMMARY

Winners:
    [DELAY]  Lower Delay:  {delay_winner} ({red_delay:.2f} ms vs {dt_delay:.2f} ms)
    [LOSS]   Lower Loss:   {loss_winner} ({red_loss:.2f}% vs {dt_loss:.2f}%)

────────────────────────────────────────────────────────────────────────────────────────────────────

Choose DropTail When:                                    Choose RED When:

* Simplicity and ease of implementation                  * Minimizing latency is critical
  are top priorities                                       for applications

* CPU and memory resources are limited                   * Handling high traffic with multiple
                                                           concurrent flows

* Network load is light to moderate                      * Preventing global synchronization
                                                           is important

* Basic queue management is sufficient                   * Better fairness among flows
                                                           is required

* Low maintenance overhead is needed                     * Advanced congestion control
                                                           is beneficial"""
    
    ax.text(0.5, 0.5, recommendation, ha='center', va='center',
            fontsize=16, family='monospace', linespacing=2.5,
            bbox=dict(boxstyle='round,pad=3', 
                     facecolor='#E3F2FD',
                     edgecolor='#2196F3',
                     linewidth=3, alpha=0.9))
    
    return fig


def create_infographic(analyzer, show_gui=False):
    """Create multi-page infographic PDF or display interactively
    
    Args:
        analyzer: EnhancedTCPAnalyzer instance
        show_gui: If True, display figures interactively instead of saving to PDF
    """
    
    if show_gui:
        # Interactive mode - hiển thị tất cả trong 1 cửa sổ
        print(f"\n📊 Creating integrated infographic view...")
        print("💡 All 5 pages in one scrollable window!\n")
        
        pages = [
            ("Page 1: Overview", create_page1_overview),
            ("Page 2: CWND Evolution", create_page2_cwnd),
            ("Page 3: Performance Comparison", create_page3_performance),
            ("Page 4: Packet Statistics", create_page4_packets),
            ("Page 5: Final Recommendation", create_page5_recommendation)
        ]
        
        # CRITICAL: Turn off interactive mode to prevent individual figure windows
        was_interactive = plt.isinteractive()
        plt.ioff()
        
        # Create all figures in background (no display)
        print("   Rendering all pages...")
        figures = []
        for i, (title, create_func) in enumerate(pages, 1):
            print(f"   ├─ Page {i}: {title.split(':')[1].strip()}")
            fig = create_func(analyzer)
            fig.canvas.draw()  # Force render without showing
            figures.append((title, fig))
        
        print("   └─ Integrating pages into single view...")
        
        # Show with navigation - THIS WILL BE THE ONLY WINDOW
        show_interactive_infographic(figures)
        
        # Clean up background figures AFTER showing the integrated view
        for _, fig in figures:
            plt.close(fig)
        
        # Restore previous interactive state
        if was_interactive:
            plt.ion()
        
        print("\n✅ Infographic displayed in ONE window!")
        print("📜 Scroll down to see all pages in one continuous view")
        print("💾 Tip: Use --infographic without --gui to save as PDF file")
        
    else:
        # PDF mode - lưu file như cũ
        output_file = analyzer.results_dir / f"{analyzer.prefix}_infographic.pdf"
        
        print(f"\n📊 Creating multi-page infographic PDF...")
        
        with PdfPages(output_file) as pdf:
            # Page 1: Overview
            print("   Creating Page 1: Overview...")
            fig1 = create_page1_overview(analyzer)
            pdf.savefig(fig1, bbox_inches='tight', dpi=300)
            plt.close(fig1)
            
            # Page 2: CWND Evolution
            print("   Creating Page 2: CWND Evolution...")
            fig2 = create_page2_cwnd(analyzer)
            pdf.savefig(fig2, bbox_inches='tight', dpi=300)
            plt.close(fig2)
            
            # Page 3: Performance Comparison
            print("   Creating Page 3: Performance Comparison...")
            fig3 = create_page3_performance(analyzer)
            pdf.savefig(fig3, bbox_inches='tight', dpi=300)
            plt.close(fig3)
            
            # Page 4: Packet Statistics
            print("   Creating Page 4: Packet Statistics...")
            fig4 = create_page4_packets(analyzer)
            pdf.savefig(fig4, bbox_inches='tight', dpi=300)
            plt.close(fig4)
            
            # Page 5: Recommendation
            print("   Creating Page 5: Final Recommendation...")
            fig5 = create_page5_recommendation(analyzer)
            pdf.savefig(fig5, bbox_inches='tight', dpi=300)
            plt.close(fig5)
            
            # Set PDF metadata
            d = pdf.infodict()
            d['Title'] = 'TCP Reno Performance Analysis'
            d['Author'] = 'Network Analyzer'
            d['Subject'] = 'DropTail vs RED Queue Management Comparison'
            d['Keywords'] = 'TCP, Reno, DropTail, RED, Queue Management'
            d['CreationDate'] = datetime.datetime.today()
        
        print(f"\n✅ Multi-page infographic saved: {output_file}")
        print(f"   📄 Total pages: 5")
        print(f"   📁 File size: {output_file.stat().st_size / 1024:.1f} KB")
        print(f"\n💡 Open the PDF file to view all pages!")
