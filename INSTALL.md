# Hướng dẫn cài đặt chi tiết

## Mục lục
1. [Cài đặt NS-3 trên Ubuntu/Debian](#ubuntu-debian)
2. [Cài đặt NS-3 trên macOS](#macos)
3. [Cài đặt NS-3 trên Windows (WSL)](#windows-wsl)
4. [Cài đặt Python dependencies](#python-dependencies)
5. [Setup project](#setup-project)
6. [Xác minh cài đặt](#xác-minh-cài-đặt)

---

## Ubuntu/Debian

### Bước 1: Cài đặt dependencies

```bash
sudo apt-get update
sudo apt-get install -y \
    g++ \
    python3 \
    python3-pip \
    cmake \
    ninja-build \
    git \
    wget \
    tar
```

### Bước 2: Download và build NS-3

```bash
# Download NS-3
cd ~
wget https://www.nsnam.org/releases/ns-allinone-3.43.tar.bz2

# Extract
tar xjf ns-allinone-3.43.tar.bz2
cd ns-allinone-3.43/ns-3.43

# Configure
./ns3 configure --enable-examples --enable-tests

# Build (có thể mất 10-30 phút)
./ns3 build
```

### Bước 3: Test NS-3

```bash
# Chạy test đơn giản
./ns3 run first
```

Nếu thấy output tương tự:
```
At time +2s client sent 1024 bytes to 10.1.1.2 port 9
At time +2.00369s server received 1024 bytes from 10.1.1.1 port 49153
...
```
Thì cài đặt thành công! ✅

---

## macOS

### Bước 1: Cài đặt Homebrew (nếu chưa có)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### Bước 2: Cài đặt dependencies

```bash
brew install cmake python@3 wget
```

### Bước 3: Download và build NS-3

```bash
# Download
cd ~
wget https://www.nsnam.org/releases/ns-allinone-3.43.tar.bz2
tar xjf ns-allinone-3.43.tar.bz2
cd ns-allinone-3.43/ns-3.43

# Configure và build
./ns3 configure --enable-examples
./ns3 build
```

### Bước 4: Test

```bash
./ns3 run first
```

---

## Windows (WSL)

### Bước 1: Cài đặt WSL2

1. Mở PowerShell as Administrator:
```powershell
wsl --install
```

2. Restart máy tính

3. Mở Ubuntu từ Start Menu

### Bước 2: Update Ubuntu trong WSL

```bash
sudo apt-get update
sudo apt-get upgrade -y
```

### Bước 3: Follow hướng dẫn Ubuntu/Debian ở trên

---

## Python dependencies

### Cài đặt pip packages

```bash
# Cách 1: Sử dụng requirements.txt
cd /path/to/TCP_Reno
pip install -r requirements.txt

# Cách 2: Cài đặt từng package
pip install matplotlib numpy seaborn networkx pandas
```

### Verify Python packages

```bash
python -c "import matplotlib; import numpy; import seaborn; import networkx; print('✅ All packages installed!')"
```

---

## Setup project

### Bước 1: Clone repository

```bash
git clone https://github.com/nynnekakak/TCP_Reno.git
cd TCP_Reno
```

### Bước 2: Copy vào NS-3

```bash
# Tạo thư mục trong scratch/
mkdir -p ~/ns-allinone-3.43/ns-3.43/scratch/tcp_reno_project

# Copy files
cp tcp_reno.cc ~/ns-allinone-3.43/ns-3.43/scratch/tcp_reno_project/
cp CMakeLists.txt ~/ns-allinone-3.43/ns-3.43/scratch/tcp_reno_project/
cp plot_realtime.py ~/ns-allinone-3.43/ns-3.43/scratch/tcp_reno_project/

# Tạo thư mục results
mkdir -p ~/ns-allinone-3.43/ns-3.43/scratch/tcp_reno_project/results

# Copy analyzer tools
cp -r analyze ~/ns-allinone-3.43/ns-3.43/scratch/tcp_reno_project/
```

**Hoặc sử dụng symbolic link:**

```bash
cd ~/ns-allinone-3.43/ns-3.43/scratch
ln -s /path/to/TCP_Reno tcp_reno_project
```

### Bước 3: Build project

```bash
cd ~/ns-allinone-3.43/ns-3.43
./ns3 build
```

---

## Xác minh cài đặt

### Test 1: Chạy mô phỏng đơn giản

```bash
cd ~/ns-allinone-3.43/ns-3.43
./ns3 run "scratch/tcp_reno_project/tcp_reno --duration=5"
```

Kết quả mong đợi:
- Output hiển thị simulation progress
- Files được tạo trong `scratch/tcp_reno_project/results/`

### Test 2: Check results files

```bash
ls -lh scratch/tcp_reno_project/results/
```

Nên thấy:
```
P2P-project_cwnd_trace_DropTail.tr
P2P-project_tcp_state_DropTail.log
P2P-project_summary_DropTail.txt
```

### Test 3: Test analyzer

```bash
cd scratch/tcp_reno_project/analyze
python3 main.py --queue DropTail --print
```

Nên thấy output với phân tích và statistics.

### Test 4: Test visualization

```bash
python3 main.py --queue DropTail --dashboard
```

Nên tạo file PNG dashboard trong `results/`.

---

## Troubleshooting

### Lỗi: "ns3: command not found"

**Nguyên nhân**: Không ở đúng thư mục NS-3

**Giải pháp**:
```bash
cd ~/ns-allinone-3.43/ns-3.43
./ns3 --version
```

### Lỗi: "No module named 'matplotlib'"

**Nguyên nhân**: Chưa cài Python packages

**Giải pháp**:
```bash
pip install matplotlib numpy seaborn networkx
```

### Lỗi: Build failed với NS-3

**Nguyên nhân**: Thiếu dependencies

**Giải pháp**:
```bash
# Ubuntu/Debian
sudo apt-get install g++ python3 cmake

# macOS
brew install cmake python@3
```

### Lỗi: Permission denied khi chạy run.sh

**Giải pháp**:
```bash
chmod +x run.sh
./run.sh
```

### Lỗi: "Display not found" khi chạy plot_realtime.py

**Nguyên nhân**: Không có GUI environment (thường trên server/WSL)

**Giải pháp**:
- Sử dụng analyzer tool thay vì real-time plot:
```bash
cd analyze
python3 main.py --compare --dashboard
```

- Hoặc setup X11 forwarding cho WSL:
```bash
# Cài đặt VcXsrv hoặc X410 trên Windows
# Trong WSL:
export DISPLAY=:0
```

---

## Next Steps

Sau khi cài đặt thành công:

1. 📖 Đọc [README.md](README.md) để hiểu dự án
2. 🚀 Xem [QUICKSTART.md](QUICKSTART.md) để chạy nhanh
3. 📊 Chạy mô phỏng đầu tiên
4. 🎨 Khám phá analyzer tools

---

**Chúc bạn thành công! 🎉**

Nếu gặp vấn đề, tạo [Issue](https://github.com/nynnekakak/TCP_Reno/issues) trên GitHub.
