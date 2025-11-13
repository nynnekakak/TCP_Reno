"""
Enhanced TCP Analyzer - Main Class
Lớp chính cho phân tích TCP Reno
"""

from pathlib import Path
from config.plot_config import COLORS
from .data_utils import load_data, count_events
from .dashboard_utils import (
    create_dashboard,
    create_comparison_dashboard,
    create_animated_timeline
)
from .report_utils import print_analysis, create_infographic


class EnhancedTCPAnalyzer:
    """
    Lớp phân tích TCP Reno với visualization đẹp mắt
    """
    
    def __init__(self, results_dir, prefix):
        """
        Khởi tạo analyzer
        
        Args:
            results_dir (str): Thư mục chứa kết quả
            prefix (str): Prefix của files
        """
        self.results_dir = Path(results_dir)
        self.prefix = prefix
        self.data = {}
        self.colors = COLORS
    
    def load_data(self, queue_type):
        """
        Load dữ liệu cho một loại hàng đợi
        
        Args:
            queue_type (str): Loại hàng đợi (DropTail/RED)
        
        Returns:
            dict: Dữ liệu đã load
        """
        data = load_data(self.results_dir, self.prefix, queue_type)
        self.data[queue_type] = data
        return data
    
    def create_dashboard(self, queue_type):
        """
        Tạo dashboard cho một loại hàng đợi
        
        Args:
            queue_type (str): Loại hàng đợi
        """
        if queue_type not in self.data:
            self.load_data(queue_type)
        
        create_dashboard(self, queue_type)
    
    def create_comparison_dashboard(self):
        """Tạo dashboard so sánh DropTail vs RED"""
        if 'DropTail' not in self.data or 'RED' not in self.data:
            print("❌ Cần dữ liệu cả DropTail và RED để so sánh")
            return
        
        create_comparison_dashboard(self)
    
    def create_animated_timeline(self, queue_type):
        """
        Tạo timeline view với annotations
        
        Args:
            queue_type (str): Loại hàng đợi
        """
        if queue_type not in self.data:
            self.load_data(queue_type)
        
        create_animated_timeline(self, queue_type)
    
    def print_analysis(self, queue_type):
        """
        In phân tích chi tiết ra terminal
        
        Args:
            queue_type (str): Loại hàng đợi
        """
        if queue_type not in self.data:
            self.load_data(queue_type)
        
        print_analysis(self, queue_type)
    
    def create_infographic(self):
        """Tạo infographic tổng hợp"""
        if 'DropTail' not in self.data or 'RED' not in self.data:
            print("❌ Cần dữ liệu cả hai loại hàng đợi")
            return
        
        create_infographic(self)
