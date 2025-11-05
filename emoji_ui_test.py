#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Hiển thị emoji màu trong Matplotlib bằng cách chèn ảnh PNG
"""

import os
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
from io import BytesIO
import requests

# =============================
# TẢI HOẶC DÙNG ẢNH EMOJI MÀU
# =============================
# Mình dùng emoji từ Twemoji (của Twitter) — ảnh PNG màu, nhẹ
EMOJI_URLS = {
    "clock": "https://github.com/twitter/twemoji/raw/master/assets/72x72/23f1.png",  # ⏱️
    "chart": "https://github.com/twitter/twemoji/raw/master/assets/72x72/1f4ca.png",  # 📊
    "refresh": "https://github.com/twitter/twemoji/raw/master/assets/72x72/1f501.png",  # 🔄
    "rocket": "https://github.com/twitter/twemoji/raw/master/assets/72x72/1f680.png",  # 🚀
}

def load_emoji(url):
    """Tải emoji PNG từ URL và trả về ảnh dạng numpy"""
    response = requests.get(url)
    return np.array(Image.open(BytesIO(response.content)))

# Tải ảnh emoji
emoji_imgs = {k: load_emoji(v) for k, v in EMOJI_URLS.items()}

# =============================
# DỮ LIỆU TEST
# =============================
queue_type = "RED"
time = np.linspace(0, 10, 100)
cwnd = 100 * np.sin(time) + 200

# =============================
# VẼ BIỂU ĐỒ
# =============================
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

fig, ax = plt.subplots(figsize=(9, 5))
ax.plot(time, cwnd, linewidth=2.5, label='TCP Reno Window', color='#0077b6')
ax.fill_between(time, cwnd, 0, alpha=0.15, color='#0077b6')

# =============================
# HIỂN THỊ TIÊU ĐỀ + TRỤC + EMOJI ẢNH
# =============================
ax.set_xlabel("Thời gian (giây)", fontsize=14, fontweight='bold')
ax.set_ylabel("Congestion Window (KB)", fontsize=14, fontweight='bold')
ax.set_title(f"Diễn biến Congestion Window - {queue_type}",
             fontsize=18, fontweight='bold', pad=20)

# =============================
# CHÈN ẢNH EMOJI VÀO BIỂU ĐỒ
# =============================
# Hàm chèn emoji ảnh vào vị trí xác định (theo tọa độ trục figure)
def insert_emoji(fig, emoji_img, xy, zoom=0.12):
    ax_emoji = fig.add_axes([xy[0], xy[1], zoom, zoom])
    ax_emoji.imshow(emoji_img)
    ax_emoji.axis('off')

# Chèn một vài emoji vui mắt
insert_emoji(fig, emoji_imgs["rocket"], (0.08, 0.88), zoom=0.08)
insert_emoji(fig, emoji_imgs["refresh"], (0.48, 0.88), zoom=0.08)
insert_emoji(fig, emoji_imgs["chart"], (0.88, 0.88), zoom=0.08)

ax.legend(loc='upper right', fontsize=11, framealpha=0.9)
ax.grid(True, alpha=0.3, linestyle=':', linewidth=1)
ax.set_facecolor('white')

plt.tight_layout()
plt.show()

