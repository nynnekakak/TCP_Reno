#!/bin/bash
# =============================================================
# TCP Reno Simulation Runner
# Chạy mô phỏng cho cả DropTail và RED queue
# =============================================================

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
NS3_DIR="$HOME/ns-allinone-3.43/ns-3.43"
PROJECT_PATH="scratch/tcp_reno_project/tcp_reno"
DURATION=20
NUM_FLOWS=3

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}TCP Reno Simulation Runner${NC}"
echo -e "${BLUE}========================================${NC}\n"

# Check if NS-3 directory exists
if [ ! -d "$NS3_DIR" ]; then
    echo -e "${RED}Error: NS-3 directory not found at $NS3_DIR${NC}"
    echo -e "${YELLOW}Please update NS3_DIR in this script${NC}"
    exit 1
fi

cd "$NS3_DIR"

# Build project
echo -e "${GREEN}[1/4] Building project...${NC}"
./ns3 build
if [ $? -ne 0 ]; then
    echo -e "${RED}Build failed!${NC}"
    exit 1
fi
echo -e "${GREEN}Build successful!${NC}\n"

# Run DropTail simulation
echo -e "${GREEN}[2/4] Running DropTail simulation...${NC}"
echo -e "${YELLOW}Queue Type: DropTail${NC}"
echo -e "${YELLOW}Duration: ${DURATION}s${NC}"
echo -e "${YELLOW}Flows: ${NUM_FLOWS}${NC}\n"

./ns3 run "${PROJECT_PATH} --queueType=DropTail --duration=${DURATION} --numFlows=${NUM_FLOWS}"
if [ $? -ne 0 ]; then
    echo -e "${RED}DropTail simulation failed!${NC}"
    exit 1
fi
echo -e "${GREEN}DropTail simulation completed!${NC}\n"

# Wait a bit
sleep 2

# Run RED simulation
echo -e "${GREEN}[3/4] Running RED simulation...${NC}"
echo -e "${YELLOW}Queue Type: RED${NC}"
echo -e "${YELLOW}Duration: ${DURATION}s${NC}"
echo -e "${YELLOW}Flows: ${NUM_FLOWS}${NC}\n"

./ns3 run "${PROJECT_PATH} --queueType=RED --duration=${DURATION} --numFlows=${NUM_FLOWS}"
if [ $? -ne 0 ]; then
    echo -e "${RED}RED simulation failed!${NC}"
    exit 1
fi
echo -e "${GREEN}RED simulation completed!${NC}\n"

# List results
echo -e "${GREEN}[4/4] Results generated:${NC}"
RESULTS_DIR="scratch/tcp_reno_project/results"
if [ -d "$RESULTS_DIR" ]; then
    echo -e "${BLUE}Files in ${RESULTS_DIR}:${NC}"
    ls -lh "$RESULTS_DIR"/*.tr "$RESULTS_DIR"/*.txt "$RESULTS_DIR"/*.log 2>/dev/null
else
    echo -e "${RED}Results directory not found!${NC}"
fi

echo -e "\n${BLUE}========================================${NC}"
echo -e "${GREEN}All simulations completed successfully!${NC}"
echo -e "${BLUE}========================================${NC}\n"

echo -e "${YELLOW}Next steps:${NC}"
echo -e "1. Analyze results with: ${GREEN}cd analyze && python3 main.py --compare --dashboard${NC}"
echo -e "2. View summary files in: ${GREEN}${RESULTS_DIR}${NC}"
echo -e "3. Generate comparison: ${GREEN}cd analyze && python3 main.py --infographic${NC}\n"
