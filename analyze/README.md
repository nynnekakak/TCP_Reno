# 🎯 TCP Reno Visual Analyzer

## 📋 Mô tả

Công cụ phân tích và trực quan hóa kết quả mô phỏng TCP Reno với giao diện đẹp mắt, hỗ trợ so sánh giữa các cơ chế quản lý hàng đợi **DropTail** và **RED** (Random Early Detection).

## 🌳 Cấu trúc Project

```
analyze/
│
├── main.py                          # Entry point chính
│
├── config/
│   └── plot_config.py              # Cấu hình màu sắc và style
│
└── analyzer/
    ├── __init__.py                 # Package initialization
    ├── enhanced_tcp_analyzer.py    # Lớp chính EnhancedTCPAnalyzer
    ├── data_utils.py               # Load & parse dữ liệu
    ├── dashboard_utils.py          # Tạo dashboard & biểu đồ
    └── report_utils.py             # In báo cáo & infographic
```

## ✨ Tính năng

### 📊 Dashboard
- **Single Queue Dashboard**: Phân tích chi tiết cho một loại hàng đợi (DropTail hoặc RED)
  - Biểu đồ CWND evolution với event markers
  - Performance metrics cards (Throughput, Loss Rate, Delay)
  - Events bar chart
  - CWND distribution histogram
  - Summary table

- **Comparison Dashboard**: So sánh DropTail vs RED
  - CWND comparison overlay
  - Performance metrics side-by-side
  - Events comparison
  - CWND statistics comparison
  - Winner summary table

### 📈 Visualization
- **Animated Timeline**: Timeline chi tiết với event annotations
- **Infographic**: Tổng hợp toàn diện với recommendations

### 📝 Analysis Report
- In phân tích chi tiết ra terminal với emoji và format đẹp
- Đánh giá hiệu năng và đưa ra nhận xét

## 🚀 Cài đặt

### Yêu cầu

```bash
Python 3.7+
matplotlib
numpy
seaborn
pathlib
```

### Cài đặt dependencies

```bash
pip install matplotlib numpy seaborn
```

## 💻 Sử dụng

### Cú pháp cơ bản

```bash
python main.py [OPTIONS]
```

### Options

| Option | Mô tả |
|--------|-------|
| `--results-dir DIR` | Thư mục chứa kết quả (mặc định: `results/`) |
| `--prefix PREFIX` | Prefix của files (mặc định: `P2P-project`) |
| `--queue {DropTail,RED}` | Phân tích loại hàng đợi cụ thể |
| `--compare` | So sánh DropTail vs RED |
| `--dashboard` | Tạo dashboard trực quan |
| `--timeline` | Tạo timeline chi tiết |
| `--infographic` | Tạo infographic tổng hợp |
| `--print` | In phân tích chi tiết ra terminal |

### 📌 Ví dụ

#### 1. Dashboard cho một loại hàng đợi

```bash
# Phân tích DropTail
python main.py --queue DropTail --dashboard

# Phân tích RED
python main.py --queue RED --dashboard
```

#### 2. So sánh DropTail vs RED

```bash
python main.py --compare --dashboard
```

#### 3. Tạo infographic tổng hợp

```bash
python main.py --infographic
```

#### 4. Timeline chi tiết

```bash
python main.py --queue RED --timeline
```

#### 5. In phân tích ra terminal

```bash
python main.py --queue DropTail --print
```

#### 6. Full analysis (tất cả)

```bash
python main.py --compare --dashboard --infographic --print
```

#### 7. Với custom results directory

```bash
python main.py --results-dir ./my_results --prefix my_sim --compare --dashboard
```

## 📁 Dữ liệu đầu vào

Tool cần các file sau trong thư mục results:

```
results/
├── {prefix}_cwnd_trace_DropTail.tr
├── {prefix}_cwnd_trace_RED.tr
├── {prefix}_tcp_state_DropTail.log
├── {prefix}_tcp_state_RED.log
├── {prefix}_summary_DropTail.txt
└── {prefix}_summary_RED.txt
```

### Format file CWND trace (.tr)
```
<time> <cwnd_value>
0.0 10.0
0.1 12.5
...
```

### Format file TCP state (.log)
```
<time>s: <EVENT_TYPE> <details>
1.5s: TIMEOUT_EVENT cwnd=10
2.3s: TRIPLE_DUP_ACK cwnd=15
...
```

### Format file summary (.txt)
```
Total Throughput: 8.5 Mbps
Average Throughput per Flow: 4.25 Mbps
Total Packets Sent: 10000
Total Packets Received: 9500
Total Lost Packets: 500 (5.00%)
Average Delay: 25.5 ms
Total State Changes: 45
Total Duplicate ACKs: 120
Total Fast Retransmits: 15
Total Fast Recoveries: 12
Total Timeouts: 3
```

## 🎨 Output

Tool tạo ra các file PNG trong thư mục results:

- `{prefix}_dashboard_DropTail.png` - Dashboard cho DropTail
- `{prefix}_dashboard_RED.png` - Dashboard cho RED
- `{prefix}_comparison_dashboard.png` - So sánh DropTail vs RED
- `{prefix}_timeline_DropTail.png` - Timeline DropTail
- `{prefix}_timeline_RED.png` - Timeline RED
- `{prefix}_infographic.png` - Infographic tổng hợp

## 🔧 Cấu hình

### Tùy chỉnh màu sắc

Edit file `config/plot_config.py`:

```python
COLORS = {
    'DropTail': '#FF6B6B',    # Màu cho DropTail
    'RED': '#4ECDC4',          # Màu cho RED
    'background': '#F7F7F7',   # Màu nền
    # ... thêm các màu khác
}
```

## 📚 Architecture

### Modules

#### `main.py`
- Entry point của application
- Parse command line arguments
- Orchestrate analysis workflow

#### `analyzer/enhanced_tcp_analyzer.py`
- Lớp chính `EnhancedTCPAnalyzer`
- Quản lý dữ liệu và điều phối các module khác

#### `analyzer/data_utils.py`
- `load_data()`: Load dữ liệu từ files
- `parse_summary()`: Parse summary file
- `count_events()`: Đếm số lượng events

#### `analyzer/dashboard_utils.py`
- `create_dashboard()`: Tạo dashboard cho 1 queue
- `create_comparison_dashboard()`: So sánh 2 queues
- `create_animated_timeline()`: Tạo timeline

#### `analyzer/report_utils.py`
- `print_analysis()`: In phân tích ra terminal
- `create_infographic()`: Tạo infographic

#### `config/plot_config.py`
- Cấu hình matplotlib style
- Định nghĩa color scheme

## 🎯 Use Cases

### 1. Network Research
Phân tích hiệu năng của các cơ chế quản lý hàng đợi trong mạng

### 2. Education
Minh họa trực quan cho sinh viên về TCP congestion control

### 3. Performance Tuning
So sánh và đánh giá các configuration khác nhau

### 4. Documentation
Tạo báo cáo với visualization chất lượng cao

## 🐛 Troubleshooting

### Lỗi: File not found
```
❌ Không tìm thấy file CWND
```
**Giải pháp**: Kiểm tra lại đường dẫn `--results-dir` và `--prefix`

### Lỗi: Import error
```
ImportError: No module named 'matplotlib'
```
**Giải pháp**: 
```bash
pip install matplotlib numpy seaborn
```

### Lỗi: Empty data
```
❌ Cần dữ liệu cả DropTail và RED
```
**Giải pháp**: Đảm bảo có đủ file dữ liệu cho cả hai loại queue

## 📄 License

MIT License - Free to use and modify

## 👥 Contributors

- Nhóm PBL - Đại học [Tên trường]

## 📞 Contact

- Email: [your-email@example.com]
- GitHub: [your-github-url]

## 🙏 Acknowledgments

- NS-3 Network Simulator
- Matplotlib & Seaborn communities
- TCP Reno RFC 2581

---

**Happy Analyzing! 🎉**
