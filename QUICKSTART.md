# TCP Reno Network Simulation Project

## Quick Start Guide

### 🚀 Chạy mô phỏng nhanh

```bash
# 1. Di chuyển project vào NS-3
cd ~/ns-allinone-3.43/ns-3.43/scratch
cp -r /path/to/TCP_Reno tcp_reno_project

# 2. Build và chạy
cd ~/ns-allinone-3.43/ns-3.43
./ns3 build
./ns3 run "scratch/tcp_reno_project/tcp_reno"

# 3. Phân tích kết quả
cd scratch/tcp_reno_project/analyze
python3 main.py --compare --dashboard
```

### 📊 Xem kết quả

Kết quả được lưu trong thư mục `results/`:
- `*_cwnd_trace_*.tr` - Dữ liệu CWND
- `*_summary_*.txt` - Thống kê tổng hợp
- `*_tcp_state_*.log` - Log FSM states

Xem README.md chính để biết hướng dẫn chi tiết!
