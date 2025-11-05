#!/bin/bash

echo "=========================================="
echo "TCP Reno Enhanced Simulation"
echo "=========================================="

# Navigate to ns-3 root directory
cd ../..

echo -e "\n[1/2] Running simulation with DropTail queue..."
./ns3 run "tcp-reno-project --queueType=DropTail --duration=20 --numFlows=3"

echo -e "\n[2/2] Running simulation with RED queue..."
./ns3 run "tcp-reno-project --queueType=RED --duration=20 --numFlows=3"

echo -e "\n=========================================="
echo "Simulation completed!"
echo "=========================================="
echo "Results location:"
echo "  scratch/tcp-reno-project/results/"
echo ""
echo "Generated files:"
ls -lh scratch/tcp-reno-project/results/
echo "=========================================="
