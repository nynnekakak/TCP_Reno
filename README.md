# TCP Reno TraceMetrics

A comprehensive TCP Reno simulation project using ns-3 on Ubuntu (VMware) with TraceMetrics analysis capabilities.

## Overview

This project provides a complete simulation environment for studying TCP Reno congestion control algorithm. It includes:

- **ns-3 based simulation** with realistic network topology
- **Comprehensive tracing** for congestion window, RTT, and throughput
- **TraceMetrics integration** for advanced analysis
- **Detailed documentation** with setup guides and analysis examples
- **Cross-platform support** optimized for Ubuntu in VMware environments

## Network Topology

```
   n0 ---------- n1 ---------- n2
      10 Mbps       1 Mbps
      1ms           10ms
      
   Source      Router      Sink
```

The simulation creates a bottleneck scenario where:
- High-speed access link (n0-n1): 10 Mbps, 1ms delay
- Bottleneck link (n1-n2): 1 Mbps, 10ms delay  
- TCP flow from n0 to n2 demonstrating congestion control behavior

## Quick Start

### Prerequisites

- Ubuntu 18.04+ (VMware environment recommended)
- ns-3.35 or later installed
- Build tools (gcc, g++, cmake)
- Optional: TraceMetrics, Wireshark, Gnuplot

### Installation

1. **Clone this repository:**
   ```bash
   git clone https://github.com/nynnekakak/TCP_Reno.git
   cd TCP_Reno
   ```

2. **Install ns-3** (see [Installation Guide](docs/installation-guide.md) for details):
   ```bash
   # Quick ns-3 installation
   sudo apt update
   sudo apt install -y build-essential gcc g++ python3 python3-dev cmake
   
   # Download and build ns-3
   mkdir ~/ns3-workspace && cd ~/ns3-workspace
   wget https://www.nsnam.org/release/ns-allinone-3.35.tar.bz2
   tar -xjf ns-allinone-3.35.tar.bz2
   cd ns-allinone-3.35 && ./build.py
   ```

3. **Copy simulation to ns-3:**
   ```bash
   export NS3_HOME=~/ns3-workspace/ns-allinone-3.35/ns-3.35
   cp src/reno-sim.cc $NS3_HOME/scratch/
   ```

### Running the Simulation

```bash
cd $NS3_HOME

# Basic simulation
./ns3 run scratch/reno-sim

# With custom parameters
./ns3 run "scratch/reno-sim --simTime=30 --tcpVariant=TcpReno"

# Alternative waf syntax
./waf --run "scratch/reno-sim --simTime=30"
```

### Example Output

```
Simulation completed successfully!
Total Bytes Received: 2458624
Average Throughput: 0.983 Mbps
```

## Generated Results

After running the simulation, check the `results/` directory for:

### Trace Files
- **cwnd-trace.dat**: Congestion window evolution over time
- **rtt-trace.dat**: Round-trip time measurements
- **throughput-trace.dat**: Instantaneous throughput data

### Network Captures  
- **reno-sim-*.pcap**: Packet capture files for Wireshark analysis

## Analysis with TraceMetrics

1. **Import trace files** into TraceMetrics
2. **Create visualizations** of TCP behavior:
   - Congestion window dynamics
   - Throughput variations  
   - RTT evolution
3. **Analyze TCP phases**:
   - Slow start exponential growth
   - Congestion avoidance linear growth
   - Fast recovery after packet loss

See the [Analysis Guide](docs/analysis-guide.md) for detailed instructions.

## Project Structure

```
TCP_Reno/
├── README.md              # This file
├── LICENSE                # MIT License
├── .gitignore             # Git ignore rules for C++/ns-3
├── src/
│   └── reno-sim.cc        # Main simulation source code
├── results/
│   └── README.md          # Results directory documentation  
└── docs/
    ├── README.md          # Documentation overview
    ├── installation-guide.md  # Step-by-step ns-3 setup
    ├── simulation-guide.md    # How to run simulations
    └── analysis-guide.md      # TraceMetrics analysis guide
```

## Simulation Parameters

Customize the simulation behavior using command-line arguments:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--simTime` | 20.0 | Simulation duration (seconds) |
| `--maxBytes` | 0 | Maximum bytes to send (0 = unlimited) |
| `--tcpVariant` | "TcpNewReno" | TCP congestion control variant |
| `--tracing` | true | Enable trace file generation |

## Example Usage Scenarios

### Basic TCP Reno Analysis
```bash
./ns3 run "scratch/reno-sim --tcpVariant=TcpReno --simTime=20"
```

### Long-term Behavior Study  
```bash
./ns3 run "scratch/reno-sim --simTime=60 --maxBytes=0"
```

### Limited Transfer Analysis
```bash
./ns3 run "scratch/reno-sim --maxBytes=1048576 --simTime=30"
```

### Performance Comparison
```bash
# Compare TCP variants
./ns3 run "scratch/reno-sim --tcpVariant=TcpReno"
./ns3 run "scratch/reno-sim --tcpVariant=TcpNewReno"  
./ns3 run "scratch/reno-sim --tcpVariant=TcpCubic"
```

## Documentation

- 📖 **[Installation Guide](docs/installation-guide.md)**: Complete ns-3 setup on Ubuntu
- 🚀 **[Simulation Guide](docs/simulation-guide.md)**: Running and customizing simulations  
- 📊 **[Analysis Guide](docs/analysis-guide.md)**: TraceMetrics and data analysis
- 📁 **[Results Documentation](results/README.md)**: Understanding output files

## Key Features

- ✅ **Realistic Network Topology**: Bottleneck scenario with configurable parameters
- ✅ **Comprehensive Tracing**: Congestion window, RTT, throughput, and packet captures
- ✅ **Multiple TCP Variants**: Support for TcpReno, TcpNewReno, TcpCubic, etc.
- ✅ **TraceMetrics Ready**: Output files formatted for direct import
- ✅ **Detailed Documentation**: Installation, simulation, and analysis guides
- ✅ **Cross-Platform**: Optimized for Ubuntu/VMware environments
- ✅ **Open Source**: MIT licensed for research and educational use

## Contributing

Contributions are welcome! Please feel free to:

1. **Report issues** with simulation setup or execution
2. **Submit improvements** to the simulation code  
3. **Add analysis examples** or visualization scripts
4. **Update documentation** for clarity or additional platforms

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- **ns-3 Network Simulator**: The foundation for our TCP simulations
- **TraceMetrics**: Advanced network simulation analysis capabilities  
- **TCP Research Community**: For continuous improvements to congestion control

## Citation

If you use this simulation in your research, please cite:

```bibtex
@misc{tcp-reno-tracemetrics,
  title={TCP Reno TraceMetrics: ns-3 Simulation with Analysis Tools},
  author={TCP Reno Project Contributors},
  year={2024},
  howpublished={\url{https://github.com/nynnekakak/TCP_Reno}}
}
```

## Support

For questions and support:
- 📖 Check the [documentation](docs/)
- 🐛 Report issues on GitHub  
- 💬 Join ns-3 community discussions
- 📧 Contact the maintainers

---

**Get started now**: Follow the [Installation Guide](docs/installation-guide.md) to set up your simulation environment!