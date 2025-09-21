# Installation Guide

This guide walks you through setting up ns-3 on Ubuntu (VMware) for TCP Reno simulation.

## Prerequisites

- Ubuntu 18.04 or later (running in VMware)
- At least 2GB of free disk space
- Internet connection for downloading packages

## Step 1: Install Dependencies

```bash
# Update package list
sudo apt update

# Install essential build tools
sudo apt install -y build-essential

# Install ns-3 dependencies
sudo apt install -y gcc g++ python3 python3-dev python3-pip
sudo apt install -y cmake ninja-build
sudo apt install -y git mercurial

# Install optional but recommended packages
sudo apt install -y gdb valgrind
sudo apt install -y qt5-default
sudo apt install -y tcpdump wireshark
sudo apt install -y sqlite sqlite3 libsqlite3-dev
sudo apt install -y libxml2 libxml2-dev
sudo apt install -y libgtk-3-dev
sudo apt install -y vtun lxc
```

## Step 2: Download ns-3

```bash
# Create workspace directory
mkdir ~/ns3-workspace
cd ~/ns3-workspace

# Download ns-3 (using version 3.35 as example)
wget https://www.nsnam.org/release/ns-allinone-3.35.tar.bz2
tar -xjf ns-allinone-3.35.tar.bz2
cd ns-allinone-3.35
```

## Step 3: Build ns-3

```bash
# Build ns-3 (this may take 20-30 minutes)
./build.py --enable-examples --enable-tests

# Alternative: build only ns-3 core
cd ns-3.35
./waf configure --enable-examples --enable-tests
./waf
```

## Step 4: Verify Installation

```bash
# Test ns-3 installation
./waf --run hello-simulator

# Expected output: "Hello Simulator"
```

## Step 5: Set up Environment

Add to your `~/.bashrc`:

```bash
# ns-3 environment
export NS3_HOME=~/ns3-workspace/ns-allinone-3.35/ns-3.35
export PATH=$PATH:$NS3_HOME
```

Reload your environment:
```bash
source ~/.bashrc
```

## Troubleshooting

### Common Issues

1. **Missing Python packages**:
   ```bash
   pip3 install matplotlib numpy scipy
   ```

2. **Permission issues with Wireshark**:
   ```bash
   sudo usermod -a -G wireshark $USER
   # Log out and log back in
   ```

3. **Build errors**: Ensure all dependencies are installed and try:
   ```bash
   ./waf clean
   ./waf configure --enable-examples
   ./waf
   ```

## Next Steps

Once ns-3 is installed, you can:
1. Copy the simulation files to the ns-3 scratch directory
2. Follow the [Simulation Guide](simulation-guide.md) to run TCP Reno simulations
3. Use [Analysis Guide](analysis-guide.md) to analyze results with TraceMetrics