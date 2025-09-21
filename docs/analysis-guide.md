# Analysis Guide

This guide explains how to analyze TCP Reno simulation results using TraceMetrics and other tools.

## TraceMetrics Analysis

### Installing TraceMetrics

TraceMetrics is a network simulation analysis tool. Installation steps:

1. **Download TraceMetrics** (if available from your institution or research group)
2. **Install Java Runtime** (required for TraceMetrics):
   ```bash
   sudo apt install default-jre
   ```

### Importing Trace Files

1. **Launch TraceMetrics**
2. **Import Trace Data**:
   - Go to File → Import Traces
   - Select the generated `.dat` files from `results/` directory
   - Choose appropriate trace format (usually "Generic ASCII")

3. **Configure Data Columns**:
   - **cwnd-trace.dat**: Time, NodeId, OldCwnd, NewCwnd
   - **rtt-trace.dat**: Time, NodeId, OldRtt, NewRtt  
   - **throughput-trace.dat**: Time, Throughput

### Creating Visualizations

#### Congestion Window Analysis
1. Select cwnd-trace.dat
2. Create time-series plot:
   - X-axis: Time
   - Y-axis: NewCwnd
3. Observe TCP phases:
   - Slow start (exponential growth)
   - Congestion avoidance (linear growth)
   - Fast recovery (after packet loss)

#### Throughput Analysis
1. Import throughput-trace.dat
2. Create throughput vs time plot
3. Calculate statistics:
   - Average throughput
   - Peak throughput
   - Throughput variation

#### RTT Analysis
1. Use rtt-trace.dat for round-trip time analysis
2. Plot RTT evolution over time
3. Identify congestion indicators (RTT spikes)

## Alternative Analysis Tools

### Gnuplot Analysis

Create visualizations using Gnuplot:

```bash
# Install Gnuplot
sudo apt install gnuplot

# Create congestion window plot
gnuplot -e "
set terminal png size 800,600;
set output 'results/cwnd-plot.png';
set title 'TCP Reno Congestion Window';
set xlabel 'Time (s)';
set ylabel 'Congestion Window (bytes)';
plot 'results/cwnd-trace.dat' using 1:4 with lines title 'Cwnd'
"

# Create throughput plot  
gnuplot -e "
set terminal png size 800,600;
set output 'results/throughput-plot.png';
set title 'TCP Reno Throughput';
set xlabel 'Time (s)';
set ylabel 'Throughput (Mbps)';
plot 'results/throughput-trace.dat' using 1:2 with lines title 'Throughput'
"
```

### Python Analysis

Use Python for advanced analysis:

```python
import matplotlib.pyplot as plt
import numpy as np

# Load congestion window data
data = np.loadtxt('results/cwnd-trace.dat', comments='#')
time = data[:, 0]
cwnd = data[:, 3]

# Plot congestion window
plt.figure(figsize=(10, 6))
plt.plot(time, cwnd)
plt.title('TCP Reno Congestion Window Evolution')
plt.xlabel('Time (s)')
plt.ylabel('Congestion Window (bytes)')
plt.grid(True)
plt.savefig('results/cwnd-analysis.png')
plt.show()

# Calculate statistics
print(f"Average Cwnd: {np.mean(cwnd):.2f} bytes")
print(f"Max Cwnd: {np.max(cwnd):.2f} bytes")
print(f"Cwnd Std Dev: {np.std(cwnd):.2f} bytes")
```

### Wireshark Analysis

Analyze packet-level behavior:

1. **Open PCAP files**:
   ```bash
   wireshark results/reno-sim-1-0.pcap
   ```

2. **Filter TCP traffic**:
   - Filter: `tcp`
   - Focus on TCP segments and ACKs

3. **Analyze TCP behavior**:
   - Sequence number progression
   - Acknowledgment patterns
   - Retransmissions
   - Window advertisements

4. **TCP Stream Analysis**:
   - Statistics → Flow Graph
   - Statistics → TCP Stream Graphs
   - Analyze → Expert Information

## Key Metrics to Analyze

### Congestion Control Performance
- **Slow Start Threshold**: When does slow start end?
- **Congestion Avoidance**: Linear growth rate
- **Fast Recovery**: Response to packet loss
- **Utilization**: Link utilization efficiency

### Network Performance
- **Throughput**: Average and peak data rates
- **Latency**: Round-trip time evolution
- **Packet Loss**: Loss detection and recovery
- **Fairness**: If multiple flows, how fairly do they share bandwidth?

### Efficiency Metrics
- **Link Utilization**: (Throughput / Link Capacity) × 100%
- **Goodput**: Application-layer throughput
- **Protocol Overhead**: TCP vs application data ratio

## Comparative Analysis

### TCP Variant Comparison
Run simulations with different TCP variants:

```bash
# TCP Reno
./waf --run "scratch/reno-sim --tcpVariant=TcpReno"
mv results/cwnd-trace.dat results/cwnd-reno.dat

# TCP NewReno  
./waf --run "scratch/reno-sim --tcpVariant=TcpNewReno"
mv results/cwnd-trace.dat results/cwnd-newreno.dat

# Compare in TraceMetrics or create overlay plots
```

### Parameter Sensitivity Analysis
Test different network conditions:

```bash
# High bandwidth-delay product
# Modify link parameters in reno-sim.cc:
# DataRate: "100Mbps", Delay: "50ms"

# High loss scenario
# Add error model to introduce packet loss

# Buffer size effects
# Modify queue sizes
```

## Reporting Results

### Key Plots to Generate
1. **Congestion Window vs Time**
2. **Throughput vs Time** 
3. **RTT vs Time**
4. **Sequence Number vs Time**
5. **Comparative Performance Charts**

### Performance Summary Table
| Metric | Value | Unit |
|--------|-------|------|
| Average Throughput | X.XX | Mbps |
| Peak Throughput | X.XX | Mbps |
| Average RTT | X.XX | ms |
| Max Congestion Window | XXXX | bytes |
| Link Utilization | XX.X | % |
| Total Data Transferred | X.XX | MB |

### Analysis Insights
Document key observations:
- TCP behavior phases
- Performance bottlenecks
- Protocol efficiency
- Network utilization
- Recommendations for improvement

## Troubleshooting Analysis Issues

### Data Import Problems
- Verify file formats and delimiters
- Check for header lines and comments
- Ensure consistent time units

### Visualization Issues
- Check data ranges and scales
- Verify axis labels and units
- Ensure appropriate plot types for data

### Missing Data Points
- Confirm simulation completed successfully
- Check trace file generation settings
- Verify file write permissions