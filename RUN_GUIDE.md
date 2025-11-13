# 🚀 HƯỚNG DẪN CHẠY NHANH

## Cú pháp chạy ĐÚNG:

```bash
./ns3 run "scratch/tcp_reno_project/tcp_reno [OPTIONS]"
```

## ✅ Các ví dụ:

### 1. Chạy cơ bản với DropTail (5 giây)
```bash
./ns3 run "scratch/tcp_reno_project/tcp_reno --duration=5"
```

### 2. Chạy với RED queue (5 giây, 3 flows)
```bash
./ns3 run "scratch/tcp_reno_project/tcp_reno --queueType=RED --duration=5 --numFlows=3"
```

### 3. Chạy mô phỏng đầy đủ 20 giây
```bash
# DropTail
./ns3 run "scratch/tcp_reno_project/tcp_reno --queueType=DropTail --duration=20 --numFlows=3"

# RED
./ns3 run "scratch/tcp_reno_project/tcp_reno --queueType=RED --duration=20 --numFlows=3"
```

### 4. Chạy với các tham số tùy chỉnh
```bash
./ns3 run "scratch/tcp_reno_project/tcp_reno --queueType=RED --duration=30 --numFlows=2 --bottleneck_bandwidth=2Mbps --tcp_queue_size=50"
```

## 📋 Workflow hoàn chỉnh:

```bash
# Bước 1: Di chuyển đến thư mục NS-3
cd ~/ns-allinone-3.43/ns-3.43

# Bước 2: Build project (chỉ cần làm 1 lần hoặc khi có thay đổi code)
./ns3 build

# Bước 3: Chạy simulation
./ns3 run "scratch/tcp_reno_project/tcp_reno --queueType=RED --duration=5 --numFlows=3"

# Bước 4: Xem kết quả
ls -lh scratch/tcp_reno_project/results/

# Bước 5: Phân tích
cd scratch/tcp_reno_project/analyze
python3 main.py --queue RED --dashboard
```

## 🎯 Tham số quan trọng:

| Tham số | Mặc định | Ý nghĩa |
|---------|----------|---------|
| `--queueType` | `DropTail` | `DropTail` hoặc `RED` |
| `--duration` | `20` | Thời gian mô phỏng (giây) |
| `--numFlows` | `3` | Số flows (1-3) |
| `--bottleneck_bandwidth` | `5Mbps` | Băng thông bottleneck |
| `--tcp_queue_size` | `25` | Kích thước queue (packets) |
| `--mtu` | `1500` | MTU size (bytes) |
| `--error_p` | `0.0` | Packet error rate |

## 🔧 Sử dụng script tự động:

### Linux/Mac:
```bash
cd ~/ns-allinone-3.43/ns-3.43/scratch/tcp_reno_project
chmod +x run.sh
./run.sh
```

### Windows (WSL):
```bash
cd ~/ns-allinone-3.43/ns-3.43/scratch/tcp_reno_project
bash run.sh
```

Script sẽ tự động:
1. Build project
2. Chạy simulation với DropTail
3. Chạy simulation với RED
4. Hiển thị kết quả

## 📊 Xem kết quả:

```bash
# Xem file summary
cat scratch/tcp_reno_project/results/P2P-project_summary_RED.txt

# Phân tích với tool
cd scratch/tcp_reno_project/analyze
python3 main.py --compare --dashboard --infographic
```

## ⚠️ Lưu ý:

1. **Phải ở thư mục NS-3 root** (`ns-3.43/`) khi chạy lệnh `./ns3`
2. **Build trước** khi chạy lần đầu: `./ns3 build`
3. **Đường dẫn đầy đủ**: `scratch/tcp_reno_project/tcp_reno` (không phải chỉ `tcp_reno_project`)
4. **Kết quả** sẽ ở: `scratch/tcp_reno_project/results/`

---

**Chúc bạn thành công! 🎉**
