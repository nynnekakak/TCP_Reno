# Simulation Guide

This guide explains how to run and customize the TCP Reno simulation.

## Quick Start

1. Copy the simulation file to ns-3:
   ```bash
   cp src/reno-sim.cc $NS3_HOME/scratch/
   ```

2. Build and run:
   ```bash
   cd $NS3_HOME
   ./waf
   ./waf --run scratch/reno-sim
   ```

## Simulation Parameters

The simulation accepts several command-line parameters:

### Basic Parameters

```bash
# Run simulation for 30 seconds
./waf --run "scratch/reno-sim --simTime=30"

# Limit data transfer to 1MB
./waf --run "scratch/reno-sim --maxBytes=1048576"

# Use different TCP variant
./waf --run "scratch/reno-sim --tcpVariant=TcpReno"

# Disable tracing for faster execution
./waf --run "scratch/reno-sim --tracing=false"
```

### Advanced Configuration

You can modify the simulation by editing `reno-sim.cc`:

#### Network Topology
```cpp
// Modify link characteristics
p2p1.SetDeviceAttribute ("DataRate", StringValue ("100Mbps"));
p2p1.SetChannelAttribute ("Delay", StringValue ("5ms"));

p2p2.SetDeviceAttribute ("DataRate", StringValue ("10Mbps"));
p2p2.SetChannelAttribute ("Delay", StringValue ("20ms"));
```

#### Buffer Sizes
```cpp
// Add buffer size configuration
p2p2.SetQueue ("ns3::DropTailQueue",
               "MaxSize", StringValue ("10p"));
```

#### Multiple Flows
```cpp
// Create additional TCP flows
for (uint32_t i = 0; i < numFlows; ++i)
  {
    BulkSendHelper source ("ns3::TcpSocketFactory",
                          InetSocketAddress (interfaces2.GetAddress (1), port + i));
    ApplicationContainer app = source.Install (nodes.Get (0));
    app.Start (Seconds (1.0 + i * 0.1));
    app.Stop (Seconds (simulationTime));
  }
```

## Output Files

The simulation generates several output files in the `results/` directory:

### Trace Files
- **cwnd-trace.dat**: Congestion window evolution
  - Format: `Time NodeId OldCwnd NewCwnd`
- **rtt-trace.dat**: Round-trip time measurements  
  - Format: `Time NodeId OldRtt NewRtt`
- **throughput-trace.dat**: Throughput over time
  - Format: `Time Throughput(Mbps)`

### PCAP Files
- **reno-sim-0-0.pcap**: Packets on link n0-n1
- **reno-sim-1-0.pcap**: Packets on link n1-n2

## Performance Monitoring

### Real-time Monitoring
While the simulation runs, you can monitor progress:

```bash
# In another terminal, watch trace files being generated
tail -f results/cwnd-trace.dat
tail -f results/throughput-trace.dat
```

### Quick Analysis
```bash
# Average throughput
awk 'NR>1 {sum+=$2; count++} END {print "Average throughput:", sum/count, "Mbps"}' results/throughput-trace.dat

# Maximum congestion window
awk 'NR>1 {if($4>max) max=$4} END {print "Max congestion window:", max, "bytes"}' results/cwnd-trace.dat
```

## Simulation Scenarios

### Scenario 1: Basic TCP Reno
```bash
./waf --run "scratch/reno-sim --tcpVariant=TcpReno --simTime=20"
```

### Scenario 2: Long-running Transfer
```bash
./waf --run "scratch/reno-sim --simTime=60 --maxBytes=0"
```

### Scenario 3: Limited Transfer
```bash
./waf --run "scratch/reno-sim --maxBytes=5242880 --simTime=30"
```

## Troubleshooting

### Build Issues
```bash
# Clean and rebuild
./waf clean
./waf configure --enable-examples
./waf
```

### No Output Files
- Check that the `results/` directory exists
- Verify write permissions
- Ensure tracing is enabled (`--tracing=true`)

### Simulation Crashes
- Check ns-3 logs: `export NS_LOG=TcpRenoSimulation=level_all`
- Verify TCP variant name spelling
- Check parameter values (positive numbers, reasonable simulation time)

## Next Steps

After running simulations:
1. Analyze results with the [Analysis Guide](analysis-guide.md)
2. Import trace files into TraceMetrics
3. Create custom plots and visualizations
4. Compare different TCP variants and parameters