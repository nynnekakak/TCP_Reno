# 🚀 TCP Reno Network Simulation Project

## 📋 Tổng quan

Dự án mô phỏng và phân tích giao thức TCP Reno sử dụng **NS-3 (Network Simulator 3)** với so sánh hiệu năng giữa hai cơ chế quản lý hàng đợi: **DropTail** và **RED (Random Early Detection)**.

Dự án bao gồm:
- ✅ Mô phỏng TCP Reno trên mạng P2P với topology 7 nodes
- ✅ Theo dõi chi tiết Finite State Machine (FSM) của TCP
- ✅ Trực quan hóa real-time với đồ thị CWND và FSM
- ✅ Công cụ phân tích kết quả với dashboard đẹp mắt
- ✅ So sánh hiệu năng giữa DropTail và RED queue

---

## 🌳 Cấu trúc dự án

```
TCP_Reno/
│
├── README.md                          # File này - Hướng dẫn chính
├── tcp_reno.cc                        # File mô phỏng NS-3 chính
├── CMakeLists.txt                     # File build cho NS-3
├── plot_realtime.py                   # Trực quan hóa real-time
├── run.sh                             # Script chạy mô phỏng (Linux/Mac)
│
├── analyze/                           # Công cụ phân tích kết quả
│   ├── README.md                      # Hướng dẫn sử dụng analyzer
│   ├── main.py                        # Entry point cho analyzer
│   ├── gui.py                         # GUI interface (nếu có)
│   ├── PROJECT_STRUCTURE.md           # Cấu trúc analyzer
│   │
│   ├── analyzer/                      # Module analyzer
│   │   ├── __init__.py
│   │   ├── enhanced_tcp_analyzer.py   # Lớp analyzer chính
│   │   ├── data_utils.py              # Xử lý dữ liệu
│   │   ├── dashboard_utils.py         # Tạo dashboard
│   │   └── report_utils.py            # Tạo báo cáo
│   │
│   └── config/                        # Cấu hình màu sắc và style
│       └── plot_config.py
│
└── results/                           # Thư mục chứa kết quả mô phỏng
    ├── P2P-project_cwnd_trace_DropTail.tr
    ├── P2P-project_cwnd_trace_RED.tr
    ├── P2P-project_summary_DropTail.txt
    └── P2P-project_summary_RED.txt
```

---

## 🎯 Tính năng chính

### 1. 🔬 Mô phỏng NS-3 (`tcp_reno.cc`)

#### Topology mạng:
```
   Senders (n0, n1, n2)  →  Router n3  →  Router n4 (Bottleneck)  →  Receivers (n5, n6)
   
   3 Senders              Aggregation      Bottleneck             2 Receivers
   @ 10Mbps              Router           @ 5Mbps                 @ 10Mbps
```

#### Các tính năng mô phỏng:
- ✅ **TCP Reno Implementation**: Mô phỏng đầy đủ thuật toán TCP Reno
- ✅ **FSM Tracking**: Theo dõi chi tiết các trạng thái: SlowStart, CongestionAvoidance, FastRecovery
- ✅ **Queue Disciplines**: So sánh DropTail và RED queue
- ✅ **Multi-flow Support**: Hỗ trợ 1-3 flows đồng thời
- ✅ **Detailed Logging**: Ghi lại mọi sự kiện TCP (state changes, dup ACKs, timeouts, etc.)
- ✅ **Flow Monitor**: Thống kê throughput, packet loss, delay

#### Các sự kiện được theo dõi:
- 📊 **Congestion Window (CWND)** evolution
- 🔄 **State transitions** (SlowStart ↔ CongestionAvoidance ↔ FastRecovery)
- 📦 **Packet transmission/reception**
- ⚠️ **Duplicate ACKs** và **Triple Duplicate ACK** detection
- ⏱️ **Timeout events** và **RTO backoff**
- 🚀 **Fast Retransmit** và **Fast Recovery** mechanisms

### 2. 📈 Trực quan hóa Real-time (`plot_realtime.py`)

- **Live CWND plot**: Biểu đồ congestion window real-time
- **FSM visualization**: Hiển thị trạng thái FSM hiện tại
- **Statistics panel**: Thống kê chi tiết (state changes, dup ACKs, timeouts, etc.)
- **Auto-detection**: Tự động phát hiện và theo dõi file kết quả mới
- **Screenshot capture**: Tự động lưu screenshot khi simulation kết thúc

### 3. 🎨 Phân tích nâng cao (`analyze/`)

Xem chi tiết trong [analyze/README.md](analyze/README.md)

- 📊 **Dashboard**: Visualize CWND, metrics, events, distributions
- 🔄 **Comparison**: So sánh DropTail vs RED side-by-side
- 📈 **Timeline**: Timeline chi tiết với event annotations
- 📋 **Infographic**: Tổng hợp toàn diện với recommendations
- 🖨️ **Reports**: In phân tích chi tiết với emoji và format đẹp

---

## 🔧 Yêu cầu hệ thống

### Cho mô phỏng NS-3:
- **NS-3** (version 3.43 trở lên) - [Download NS-3](https://www.nsnam.org/releases/)
- **C++ compiler** (g++ >= 7.0)
- **CMake** >= 3.10
- **Python 3** (cho build system của NS-3)

### Cho phân tích và visualization:
- **Python 3.7+**
- **matplotlib** >= 3.3.0
- **numpy** >= 1.19.0
- **seaborn** >= 0.11.0
- **networkx** >= 2.5 (cho FSM visualization)

---

## 📥 Cài đặt

### Bước 1: Clone repository

```bash
git clone https://github.com/nynnekakak/TCP_Reno.git
cd TCP_Reno
```

### Bước 2: Cài đặt NS-3

#### Trên Ubuntu/Debian:
```bash
# Cài đặt dependencies
sudo apt-get update
sudo apt-get install g++ python3 cmake ninja-build git

# Download và build NS-3
cd ~
wget https://www.nsnam.org/releases/ns-allinone-3.43.tar.bz2
tar xjf ns-allinone-3.43.tar.bz2
cd ns-allinone-3.43/ns-3.43

# Build NS-3
./ns3 configure --enable-examples --enable-tests
./ns3 build
```

#### Trên Windows (WSL):
Sử dụng Windows Subsystem for Linux (WSL) và làm theo hướng dẫn Ubuntu/Debian ở trên.

### Bước 3: Copy project vào NS-3

```bash
# Tạo thư mục project trong scratch/
cd ~/ns-allinone-3.43/ns-3.43/scratch
mkdir tcp_reno_project
cd tcp_reno_project

# Copy các file từ repo
cp /path/to/TCP_Reno/tcp_reno.cc ./
cp /path/to/TCP_Reno/CMakeLists.txt ./
cp /path/to/TCP_Reno/plot_realtime.py ./

# Tạo thư mục results
mkdir -p results
```

**Hoặc sử dụng symbolic link:**
```bash
cd ~/ns-allinone-3.43/ns-3.43/scratch
ln -s /path/to/TCP_Reno tcp_reno_project
```

### Bước 4: Cài đặt Python dependencies

```bash
# Cho visualization
pip install matplotlib numpy seaborn networkx

# Hoặc dùng requirements.txt (nếu có)
pip install -r requirements.txt
```

---

## 🚀 Sử dụng

### Chạy mô phỏng

#### Cách 1: Sử dụng NS-3 command line

```bash
# Từ thư mục ns-3.43/
cd ~/ns-allinone-3.43/ns-3.43

# Build project
./ns3 build

# Chạy với DropTail queue (mặc định)
./ns3 run "scratch/tcp_reno_project/tcp_reno"

# Chạy với RED queue
./ns3 run "scratch/tcp_reno_project/tcp_reno --queueType=RED"

# Chạy với nhiều parameters
./ns3 run "scratch/tcp_reno_project/tcp_reno --queueType=RED --duration=30 --numFlows=3"
```

#### Cách 2: Sử dụng script (Linux/Mac)

```bash
# Từ thư mục dự án
cd ~/ns-allinone-3.43/ns-3.43/scratch/tcp_reno_project

# Chạy cả hai simulations
./run.sh
```

### Các tham số mô phỏng

| Tham số | Mặc định | Mô tả |
|---------|----------|-------|
| `--queueType` | `DropTail` | Loại queue: `DropTail` hoặc `RED` |
| `--duration` | `20.0` | Thời gian mô phỏng (giây) |
| `--numFlows` | `3` | Số lượng flows (1-3) |
| `--cwnd` | `1` | Initial congestion window (segments) |
| `--ssthresh` | `65535` | Initial slow start threshold (segments) |
| `--mtu` | `1500` | MTU size (bytes) |
| `--sack` | `true` | Bật/tắt SACK |
| `--error_p` | `0.0` | Packet error rate |
| `--bottleneck_bandwidth` | `5Mbps` | Băng thông bottleneck |
| `--tcp_queue_size` | `25` | Kích thước queue (packets) |

### Ví dụ sử dụng:

```bash
# Mô phỏng 30s với RED queue và 2 flows
./ns3 run "scratch/tcp_reno_project/tcp_reno --queueType=RED --duration=30 --numFlows=2"

# Mô phỏng với error rate 1%
./ns3 run "scratch/tcp_reno_project/tcp_reno --error_p=0.01"

# Mô phỏng với bottleneck 2Mbps và queue size 50
./ns3 run "scratch/tcp_reno_project/tcp_reno --bottleneck_bandwidth=2Mbps --tcp_queue_size=50"
```

---

## 📊 Phân tích kết quả

### Sử dụng công cụ analyzer

```bash
cd analyze

# Dashboard cho một loại queue
python main.py --queue DropTail --dashboard

# So sánh cả hai
python main.py --compare --dashboard

# Tạo infographic tổng hợp
python main.py --infographic

# Full analysis
python main.py --compare --dashboard --infographic --print
```

Chi tiết xem [analyze/README.md](analyze/README.md)

### Files kết quả được tạo ra:

#### Từ mô phỏng NS-3:
- `P2P-project_cwnd_trace_<QueueType>.tr` - Dữ liệu CWND theo thời gian
- `P2P-project_tcp_state_<QueueType>.log` - Log FSM state transitions
- `P2P-project_summary_<QueueType>.txt` - Tổng hợp thống kê

#### Từ analyzer:
- `P2P-project_dashboard_<QueueType>.png` - Dashboard trực quan
- `P2P-project_comparison_dashboard.png` - So sánh DropTail vs RED
- `P2P-project_infographic.png` - Infographic tổng hợp
- `P2P-project_timeline_<QueueType>.png` - Timeline chi tiết

---

## 📖 Giải thích thuật toán

### TCP Reno States:

#### 1. **Slow Start** 🚀
- **Mục đích**: Tăng cwnd nhanh để khám phá băng thông
- **Hành vi**: cwnd tăng gấp đôi mỗi RTT (exponential growth)
- **Điều kiện**: cwnd < ssthresh
- **Chuyển sang CA**: Khi cwnd >= ssthresh
- **Chuyển sang FR**: Khi nhận 3 duplicate ACKs

#### 2. **Congestion Avoidance** 📈
- **Mục đích**: Tăng cwnd cẩn thận khi gần capacity
- **Hành vi**: cwnd += 1/cwnd mỗi ACK (linear growth)
- **Điều kiện**: cwnd >= ssthresh
- **Chuyển sang FR**: Khi nhận 3 duplicate ACKs
- **Chuyển sang SS**: Khi timeout xảy ra

#### 3. **Fast Recovery** 🔄
- **Mục đích**: Phục hồi nhanh từ packet loss
- **Hành vi**: 
  - ssthresh = cwnd / 2
  - cwnd = ssthresh + 3
  - Tăng cwnd khi nhận thêm duplicate ACKs
- **Trigger**: 3 duplicate ACKs (Fast Retransmit)
- **Exit**: Khi nhận new ACK → về CA

#### 4. **Timeout** ⏱️
- **Hành vi**:
  - ssthresh = cwnd / 2
  - cwnd = 1
  - RTO backoff (exponential)
- **Trở về**: Slow Start

### Queue Disciplines:

#### DropTail 📦
- **Cơ chế**: Tail-drop - drop packets khi queue đầy
- **Ưu điểm**: Đơn giản, overhead thấp
- **Nhược điểm**: 
  - Global synchronization
  - Bursty packet losses
  - Queueing delay cao

#### RED (Random Early Detection) 🎲
- **Cơ chế**: Probabilistic early drops dựa trên average queue length
- **Parameters**:
  - MinTh = 20% queue size
  - MaxTh = 60% queue size
- **Ưu điểm**:
  - Tránh global synchronization
  - Giảm queueing delay
  - Fair giữa các flows
- **Nhược điểm**: 
  - Cấu hình phức tạp
  - Overhead tính toán cao hơn

---

## 🔍 Troubleshooting

### NS-3 build errors

```bash
# Rebuild từ đầu
./ns3 clean
./ns3 configure --enable-examples
./ns3 build
```

### File not found errors

```bash
# Kiểm tra đường dẫn
ls scratch/tcp_reno_project/
ls scratch/tcp_reno_project/results/

# Đảm bảo permissions
chmod +x run.sh
chmod +x plot_realtime.py
```

### Python import errors

```bash
# Reinstall dependencies
pip install --upgrade matplotlib numpy seaborn networkx
```

### Real-time plot không hiển thị

```bash
# Kiểm tra Python có GUI backend
python -c "import matplotlib; print(matplotlib.get_backend())"

# Nếu không, cài đặt
# Ubuntu/Debian:
sudo apt-get install python3-tk

# macOS:
brew install python-tk
```

---

## 📚 Tài liệu tham khảo

1. **TCP Reno**:
   - RFC 2581: TCP Congestion Control
   - RFC 2582: The NewReno Modification to TCP's Fast Recovery Algorithm

2. **RED Queue**:
   - Floyd, S., & Jacobson, V. (1993). Random early detection gateways for congestion avoidance

3. **NS-3 Documentation**:
   - [NS-3 Tutorial](https://www.nsnam.org/docs/tutorial/html/)
   - [NS-3 Manual](https://www.nsnam.org/docs/manual/html/)
   - [NS-3 API Documentation](https://www.nsnam.org/docs/doxygen/)

---

## 🤝 Đóng góp

Nếu bạn muốn đóng góp vào dự án:

1. Fork repository
2. Tạo branch mới (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Tạo Pull Request

---

## 📝 License

Dự án này được phát hành dưới MIT License - xem file [LICENSE](LICENSE) để biết thêm chi tiết.

---

## 👥 Tác giả

- **Nhóm PBL** - Đại học [Tên trường của bạn]
- GitHub: [@nynnekakak](https://github.com/nynnekakak)

---

## 🙏 Lời cảm ơn

- NS-3 development team
- Matplotlib và Seaborn communities
- Các tài liệu tham khảo về TCP/IP networking

---

## 📞 Liên hệ

Nếu có câu hỏi hoặc vấn đề, vui lòng:
- Tạo [Issue](https://github.com/nynnekakak/TCP_Reno/issues) trên GitHub
- Email: [your-email@example.com]

---

## 🎓 Sử dụng cho mục đích học tập

Dự án này phù hợp cho:
- 📚 Môn học Computer Networks
- 🔬 Đồ án môn học (PBL)
- 📊 Research về TCP performance
- 🎯 Học về network simulation với NS-3

---

**Happy Simulating! 🚀**
