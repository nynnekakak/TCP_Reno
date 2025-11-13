"""
Cấu hình giao diện hiển thị cho matplotlib và seaborn.
Chỉ cần import file này là tự động áp dụng style cho toàn bộ biểu đồ.
"""

import matplotlib.pyplot as plt
from matplotlib import rcParams
import seaborn as sns

# Thiết lập font chữ
rcParams['font.family'] = 'sans-serif'
rcParams['font.sans-serif'] = ['DejaVu Sans', 'Symbola']

# Cấu hình style nền biểu đồ
plt.style.use('seaborn-v0_8-darkgrid')

# Thiết lập bảng màu mặc định
sns.set_palette("husl")

# (Tuỳ chọn) bạn có thể thêm các cấu hình mở rộng khác, ví dụ:
rcParams['figure.figsize'] = (10, 6)       # kích thước mặc định
rcParams['axes.titlesize'] = 14            # cỡ chữ tiêu đề
rcParams['axes.labelsize'] = 12            # cỡ chữ nhãn trục
rcParams['legend.fontsize'] = 10           # cỡ chữ chú thích
rcParams['xtick.labelsize'] = 10
rcParams['ytick.labelsize'] = 10

# Color scheme for TCP analysis
COLORS = {
    'DropTail': '#FF6B6B',      # Đỏ cam
    'RED': '#4ECDC4',            # Xanh ngọc
    'background': '#F7F7F7',
    'grid': '#E0E0E0',
    'text': '#2C3E50',
    'accent1': '#FFD93D',        # Vàng
    'accent2': '#6BCB77',        # Xanh lá
    'accent3': '#4D96FF',        # Xanh dương
    'danger': '#E63946',         # Đỏ
    'warning': '#F77F00',        # Cam
    'success': '#06FFA5'         # Xanh mint
}

