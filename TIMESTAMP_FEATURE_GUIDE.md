# 📋 HƯỚNG DẪN SỬ DỤNG HỆ THỐNG MỚI VỚI TIMESTAMP

## 🎯 Tính năng mới

### ✅ Đã thêm vào hệ thống:

1. **Tên file tự động có timestamp**
   - Mỗi lần chạy simulation sẽ tạo file với timestamp duy nhất
   - Format: `P2P-project_YYYYMMDD_HHMMSS_[type]_[queue].ext`
   - Ví dụ: `P2P-project_20241118_143052_cwnd_trace_RED.tr`

2. **Quản lý nhiều runs trong Results tab**
   - Lọc file theo từng lần chạy (run)
   - Hiển thị timestamp dễ đọc: "2024-11-18 14:30:52"
   - Xem tất cả hoặc chọn run cụ thể
   - Cột Queue Type để dễ dàng phân biệt DropTail/RED

3. **Xóa file theo run**
   - Xóa toàn bộ results (Clear All Results)
   - Xóa một run cụ thể (Delete Selected Run)
   - Giữ lại các run khác để so sánh

4. **Phân tích theo run trong Analysis tab**
   - Chọn run cụ thể để phân tích
   - "Latest Run" - phân tích run mới nhất
   - Hỗ trợ file legacy (không có timestamp)

## 📖 Cách sử dụng

### 🚀 1. Chạy Simulation

Như trước, chạy simulation với các thông số:
- Chọn queue type (DropTail, RED, hoặc cả hai)
- Cấu hình thông số (Duration, Error Rate, v.v.)
- Click "▶️ Run Simulation"

**Kết quả:** File sẽ được tạo với timestamp tự động, VD:
```
P2P-project_20241118_143052_cwnd_trace_DropTail.tr
P2P-project_20241118_143052_summary_DropTail.txt
P2P-project_20241118_143052_cwnd_trace_RED.tr
P2P-project_20241118_143052_summary_RED.txt
```

### 📊 2. Xem Results

Vào tab **Results**:

1. **Lọc theo Run:**
   - Dropdown "Filter by Run" hiển thị danh sách các lần chạy
   - Chọn "All Runs" để xem tất cả
   - Chọn timestamp cụ thể để xem một run

2. **Xem thông tin file:**
   - File Name: Tên file đầy đủ
   - Type: Loại file (Trace, Summary, State Log)
   - Queue Type: DropTail hoặc RED
   - Size: Kích thước file
   - Modified: Thời gian sửa đổi

3. **Quản lý file:**
   - 📂 Open Results Folder: Mở thư mục results
   - 🗑️ Clear All Results: Xóa TẤT CẢ file
   - 🗑️ Delete Selected Run: Xóa chỉ run đang chọn

### 📈 3. Phân tích Results

Vào tab **Analysis**:

1. **Chọn Run:**
   - Dropdown "Select Run to Analyze"
   - "Latest Run": Tự động chọn run mới nhất
   - Hoặc chọn timestamp cụ thể
   - Click 🔄 để refresh danh sách

2. **Chạy phân tích:**
   - Single Queue Analysis: Dashboard, Timeline, Print Analysis
   - Comparison Analysis: So sánh DropTail vs RED
   - Infographic: Báo cáo PDF hoặc GUI

## 💡 Ví dụ thực tế

### Ví dụ 1: So sánh các cấu hình Error Rate

```
Run 1: Duration=20s, Error_Rate=0
→ File: P2P-project_20241118_140000_*_RED.tr

Run 2: Duration=20s, Error_Rate=0.01
→ File: P2P-project_20241118_140500_*_RED.tr

Run 3: Duration=20s, Error_Rate=0.02
→ File: P2P-project_20241118_141000_*_RED.tr
```

Bây giờ bạn có 3 sets file riêng biệt, có thể:
- Xem từng run trong Results tab
- Phân tích từng run riêng trong Analysis tab
- So sánh kết quả bằng cách chạy analysis nhiều lần với các run khác nhau

### Ví dụ 2: So sánh Duration

```
Run 1: Duration=10s, Queue=Both
→ P2P-project_20241118_150000_*

Run 2: Duration=30s, Queue=Both
→ P2P-project_20241118_150300_*

Run 3: Duration=60s, Queue=Both
→ P2P-project_20241118_150600_*
```

Chọn từng run và tạo Comparison Dashboard để thấy:
- Ảnh hưởng của thời gian simulation
- Sự khác biệt giữa DropTail và RED ở mỗi duration

## 🔧 Build NS-3 lần đầu

**QUAN TRỌNG:** Phải build lại NS-3 để áp dụng thay đổi timestamp!

### Windows (PowerShell):
```powershell
cd "C:\path\to\ns-allinone-3.43\ns-3.43"
./ns3 clean
./ns3 configure --enable-examples --enable-tests
./ns3 build
```

### Linux/Mac:
```bash
cd ~/ns-allinone-3.43/ns-3.43
./ns3 clean
./ns3 configure --enable-examples --enable-tests
./ns3 build
```

## 🎓 Tips sử dụng

1. **Đặt tên có ý nghĩa trong notes:**
   - Ghi chú các thông số quan trọng của mỗi run
   - Ví dụ: "Test high error rate 2%"

2. **Xóa file không cần:**
   - Dùng "Delete Selected Run" để xóa các run thất bại
   - Giữ lại các run quan trọng để so sánh

3. **Legacy files:**
   - File cũ không có timestamp vẫn hoạt động
   - Có thể chọn "Legacy Files" trong filter
   - Khuyến nghị: Xóa và chạy lại với hệ thống mới

4. **Phân tích nhiều run:**
   - Chạy analysis cho run 1 → save plot
   - Chạy analysis cho run 2 → save plot  
   - So sánh các plot bằng mắt

## 🐛 Troubleshooting

### Vấn đề 1: Không thấy timestamp mới
- **Nguyên nhân:** Chưa build lại NS-3
- **Giải pháp:** Build lại NS-3 theo hướng dẫn trên

### Vấn đề 2: Dropdown "Select Run" trống
- **Nguyên nhân:** Chưa có file với timestamp
- **Giải pháp:** Chạy simulation mới sau khi build NS-3

### Vấn đề 3: Analysis không tìm thấy file
- **Nguyên nhân:** Chọn run không có đủ file cần thiết
- **Giải pháp:** Kiểm tra trong Results tab xem run đó có đủ file không

## 📝 Technical Details

### File naming pattern:
```
{prefix}_{timestamp}_{type}_{queue}.{ext}

prefix: P2P-project
timestamp: YYYYMMDD_HHMMSS
type: cwnd_trace | tcp_state | summary | ascii | pcap
queue: DropTail | RED
ext: .tr | .log | .txt
```

### Timestamp format:
```
20241118_143052
└─┬──┘ └─┬──┘ └─┬──┘
 Year   Month Day
         Hour  Min Sec
```

### Python code changes:
- `analyze/analyzer/data_utils.py`: Thêm `find_latest_file()` function
- `tcp_reno_gui.py`: Thêm run filtering và management

### NS-3 code changes:
- `tcp_reno.cc`: Thêm timestamp generation với `<ctime>` và `<sstream>`
- Unique prefix: `prefix_file_name + "_" + timestamp`

## 🎉 Kết luận

Hệ thống mới cho phép:
✅ Thử nghiệm nhiều cấu hình khác nhau
✅ Lưu trữ và so sánh kết quả
✅ Quản lý file dễ dàng hơn
✅ Tránh mất dữ liệu do ghi đè

**Hãy thử ngay!** Chạy simulation với các thông số khác nhau và so sánh kết quả! 🚀
