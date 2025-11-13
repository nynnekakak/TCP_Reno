#!/usr/bin/env python3
"""
TCP Reno Visual Analysis Tool - GUI Version
Giao diện đồ họa cho phân tích TCP Reno
"""

import sys
import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
from pathlib import Path
import threading
from analyzer.enhanced_tcp_analyzer import EnhancedTCPAnalyzer


class TCPAnalyzerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 TCP Reno Analyzer - Giao diện Phân tích")
        self.root.geometry("900x700")
        self.root.configure(bg='#f0f0f0')
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Title.TLabel', font=('Arial', 16, 'bold'), background='#f0f0f0')
        style.configure('Header.TLabel', font=('Arial', 11, 'bold'), background='#f0f0f0')
        style.configure('Action.TButton', font=('Arial', 10, 'bold'), padding=10)
        
        # Variables
        self.results_dir = tk.StringVar(value="results/")
        self.prefix = tk.StringVar(value="P2P-project")
        self.queue_type = tk.StringVar(value="DropTail")
        self.analyzer = None
        
        self.create_widgets()
        
    def create_widgets(self):
        # Title
        title_frame = tk.Frame(self.root, bg='#2c3e50', height=80)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="🎯 TCP Reno Performance Analyzer",
            font=('Arial', 20, 'bold'),
            bg='#2c3e50',
            fg='white'
        )
        title_label.pack(pady=20)
        
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill='both', expand=True)
        
        # Configuration Section
        config_frame = ttk.LabelFrame(main_frame, text="⚙️ Cấu hình", padding="15")
        config_frame.pack(fill='x', pady=(0, 10))
        
        # Results Directory
        ttk.Label(config_frame, text="📁 Thư mục kết quả:", font=('Arial', 10, 'bold')).grid(
            row=0, column=0, sticky='w', pady=5
        )
        dir_frame = ttk.Frame(config_frame)
        dir_frame.grid(row=0, column=1, sticky='ew', pady=5, padx=(10, 0))
        ttk.Entry(dir_frame, textvariable=self.results_dir, width=40).pack(side='left', fill='x', expand=True)
        ttk.Button(dir_frame, text="📂 Chọn", command=self.browse_directory, width=10).pack(side='left', padx=(5, 0))
        
        # Prefix
        ttk.Label(config_frame, text="🏷️ Prefix:", font=('Arial', 10, 'bold')).grid(
            row=1, column=0, sticky='w', pady=5
        )
        ttk.Entry(config_frame, textvariable=self.prefix, width=30).grid(
            row=1, column=1, sticky='w', pady=5, padx=(10, 0)
        )
        
        config_frame.columnconfigure(1, weight=1)
        
        # Analysis Options Section
        options_frame = ttk.LabelFrame(main_frame, text="📊 Tùy chọn Phân tích", padding="15")
        options_frame.pack(fill='x', pady=(0, 10))
        
        # Queue Type Selection
        queue_frame = ttk.Frame(options_frame)
        queue_frame.pack(fill='x', pady=5)
        
        ttk.Label(queue_frame, text="🔄 Loại hàng đợi:", font=('Arial', 10, 'bold')).pack(side='left')
        ttk.Radiobutton(queue_frame, text="DropTail", variable=self.queue_type, 
                       value="DropTail").pack(side='left', padx=(10, 5))
        ttk.Radiobutton(queue_frame, text="RED", variable=self.queue_type, 
                       value="RED").pack(side='left', padx=5)
        
        # Action Buttons
        action_frame = ttk.LabelFrame(main_frame, text="🚀 Hành động", padding="15")
        action_frame.pack(fill='x', pady=(0, 10))
        
        # Create button grid
        btn_frame = ttk.Frame(action_frame)
        btn_frame.pack(fill='x')
        
        # Row 1
        row1 = ttk.Frame(btn_frame)
        row1.pack(fill='x', pady=5)
        
        self.btn_dashboard = ttk.Button(
            row1, text="📊 Dashboard đơn", 
            command=self.create_single_dashboard,
            style='Action.TButton'
        )
        self.btn_dashboard.pack(side='left', padx=5, fill='x', expand=True)
        
        self.btn_compare = ttk.Button(
            row1, text="⚖️ So sánh DT vs RED", 
            command=self.create_comparison,
            style='Action.TButton'
        )
        self.btn_compare.pack(side='left', padx=5, fill='x', expand=True)
        
        # Row 2
        row2 = ttk.Frame(btn_frame)
        row2.pack(fill='x', pady=5)
        
        self.btn_timeline = ttk.Button(
            row2, text="⏱️ Timeline", 
            command=self.create_timeline,
            style='Action.TButton'
        )
        self.btn_timeline.pack(side='left', padx=5, fill='x', expand=True)
        
        self.btn_infographic = ttk.Button(
            row2, text="📄 Infographic PDF", 
            command=self.create_infographic,
            style='Action.TButton'
        )
        self.btn_infographic.pack(side='left', padx=5, fill='x', expand=True)
        
        # Row 3
        row3 = ttk.Frame(btn_frame)
        row3.pack(fill='x', pady=5)
        
        self.btn_analysis = ttk.Button(
            row3, text="📝 In phân tích", 
            command=self.print_analysis,
            style='Action.TButton'
        )
        self.btn_analysis.pack(side='left', padx=5, fill='x', expand=True)
        
        self.btn_full = ttk.Button(
            row3, text="🎯 Phân tích đầy đủ", 
            command=self.full_analysis,
            style='Action.TButton'
        )
        self.btn_full.pack(side='left', padx=5, fill='x', expand=True)
        
        # Output Console
        output_frame = ttk.LabelFrame(main_frame, text="📟 Kết quả", padding="10")
        output_frame.pack(fill='both', expand=True)
        
        self.output_text = scrolledtext.ScrolledText(
            output_frame, 
            height=15, 
            width=80,
            font=('Courier', 9),
            bg='#1e1e1e',
            fg='#00ff00',
            insertbackground='white'
        )
        self.output_text.pack(fill='both', expand=True)
        
        # Status Bar
        self.status_bar = tk.Label(
            self.root, 
            text="✅ Sẵn sàng",
            bd=1, 
            relief=tk.SUNKEN, 
            anchor=tk.W,
            bg='#2c3e50',
            fg='white',
            font=('Arial', 9)
        )
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def browse_directory(self):
        directory = filedialog.askdirectory(title="Chọn thư mục kết quả")
        if directory:
            self.results_dir.set(directory)
            self.log(f"📁 Đã chọn thư mục: {directory}")
    
    def log(self, message):
        self.output_text.insert(tk.END, message + "\n")
        self.output_text.see(tk.END)
        self.root.update_idletasks()
    
    def update_status(self, message):
        self.status_bar.config(text=message)
        self.root.update_idletasks()
    
    def disable_buttons(self):
        for btn in [self.btn_dashboard, self.btn_compare, self.btn_timeline, 
                   self.btn_infographic, self.btn_analysis, self.btn_full]:
            btn.config(state='disabled')
    
    def enable_buttons(self):
        for btn in [self.btn_dashboard, self.btn_compare, self.btn_timeline, 
                   self.btn_infographic, self.btn_analysis, self.btn_full]:
            btn.config(state='normal')
    
    def run_in_thread(self, target):
        """Run function in separate thread to avoid freezing GUI"""
        thread = threading.Thread(target=target, daemon=True)
        thread.start()
    
    def create_analyzer(self):
        """Create analyzer instance"""
        try:
            results_dir = self.results_dir.get()
            prefix = self.prefix.get()
            
            if not results_dir or not prefix:
                messagebox.showerror("Lỗi", "Vui lòng nhập đầy đủ thông tin!")
                return None
            
            self.log("\n" + "="*70)
            self.log("🎨 TCP RENO VISUAL ANALYZER - GUI VERSION")
            self.log("="*70)
            
            self.analyzer = EnhancedTCPAnalyzer(results_dir, prefix)
            return self.analyzer
            
        except Exception as e:
            self.log(f"\n❌ Lỗi tạo analyzer: {e}")
            messagebox.showerror("Lỗi", f"Không thể tạo analyzer:\n{e}")
            return None
    
    def create_single_dashboard(self):
        def task():
            try:
                self.disable_buttons()
                self.update_status("⏳ Đang tạo dashboard...")
                
                analyzer = self.create_analyzer()
                if not analyzer:
                    return
                
                queue = self.queue_type.get()
                self.log(f"\n📊 Đang tạo dashboard cho {queue}...")
                
                analyzer.load_data(queue)
                analyzer.create_dashboard(queue)
                
                self.log(f"✅ Dashboard {queue} đã hoàn thành!")
                self.update_status("✅ Hoàn thành!")
                messagebox.showinfo("Thành công", f"Dashboard {queue} đã được tạo!")
                
            except FileNotFoundError as e:
                self.log(f"\n❌ Lỗi: Không tìm thấy file - {e}")
                messagebox.showerror("Lỗi", f"Không tìm thấy file dữ liệu:\n{e}")
            except Exception as e:
                self.log(f"\n❌ Lỗi: {e}")
                messagebox.showerror("Lỗi", str(e))
            finally:
                self.enable_buttons()
                self.update_status("✅ Sẵn sàng")
        
        self.run_in_thread(task)
    
    def create_comparison(self):
        def task():
            try:
                self.disable_buttons()
                self.update_status("⏳ Đang so sánh...")
                
                analyzer = self.create_analyzer()
                if not analyzer:
                    return
                
                self.log("\n⚖️ Đang tải dữ liệu cả DropTail và RED...")
                analyzer.load_data('DropTail')
                analyzer.load_data('RED')
                
                self.log("📊 Đang tạo comparison dashboard...")
                analyzer.create_comparison_dashboard()
                
                self.log("✅ Comparison dashboard đã hoàn thành!")
                self.update_status("✅ Hoàn thành!")
                messagebox.showinfo("Thành công", "Comparison dashboard đã được tạo!")
                
            except FileNotFoundError as e:
                self.log(f"\n❌ Lỗi: Không tìm thấy file - {e}")
                messagebox.showerror("Lỗi", f"Không tìm thấy file dữ liệu:\n{e}")
            except Exception as e:
                self.log(f"\n❌ Lỗi: {e}")
                messagebox.showerror("Lỗi", str(e))
            finally:
                self.enable_buttons()
                self.update_status("✅ Sẵn sàng")
        
        self.run_in_thread(task)
    
    def create_timeline(self):
        def task():
            try:
                self.disable_buttons()
                self.update_status("⏳ Đang tạo timeline...")
                
                analyzer = self.create_analyzer()
                if not analyzer:
                    return
                
                queue = self.queue_type.get()
                self.log(f"\n⏱️ Đang tạo timeline cho {queue}...")
                
                analyzer.load_data(queue)
                analyzer.create_animated_timeline(queue)
                
                self.log(f"✅ Timeline {queue} đã hoàn thành!")
                self.update_status("✅ Hoàn thành!")
                messagebox.showinfo("Thành công", f"Timeline {queue} đã được tạo!")
                
            except FileNotFoundError as e:
                self.log(f"\n❌ Lỗi: Không tìm thấy file - {e}")
                messagebox.showerror("Lỗi", f"Không tìm thấy file dữ liệu:\n{e}")
            except Exception as e:
                self.log(f"\n❌ Lỗi: {e}")
                messagebox.showerror("Lỗi", str(e))
            finally:
                self.enable_buttons()
                self.update_status("✅ Sẵn sàng")
        
        self.run_in_thread(task)
    
    def create_infographic(self):
        def task():
            try:
                self.disable_buttons()
                self.update_status("⏳ Đang tạo infographic PDF...")
                
                analyzer = self.create_analyzer()
                if not analyzer:
                    return
                
                self.log("\n📄 Đang tải dữ liệu cả DropTail và RED...")
                analyzer.load_data('DropTail')
                analyzer.load_data('RED')
                
                self.log("📊 Đang tạo infographic PDF...")
                analyzer.create_infographic()
                
                self.log("✅ Infographic PDF đã hoàn thành!")
                self.update_status("✅ Hoàn thành!")
                messagebox.showinfo("Thành công", "Infographic PDF đã được tạo!")
                
            except FileNotFoundError as e:
                self.log(f"\n❌ Lỗi: Không tìm thấy file - {e}")
                messagebox.showerror("Lỗi", f"Không tìm thấy file dữ liệu:\n{e}")
            except Exception as e:
                self.log(f"\n❌ Lỗi: {e}")
                messagebox.showerror("Lỗi", str(e))
            finally:
                self.enable_buttons()
                self.update_status("✅ Sẵn sàng")
        
        self.run_in_thread(task)
    
    def print_analysis(self):
        def task():
            try:
                self.disable_buttons()
                self.update_status("⏳ Đang phân tích...")
                
                analyzer = self.create_analyzer()
                if not analyzer:
                    return
                
                queue = self.queue_type.get()
                self.log(f"\n📝 Đang phân tích {queue}...")
                
                analyzer.load_data(queue)
                
                # Capture print output
                import io
                from contextlib import redirect_stdout
                
                f = io.StringIO()
                with redirect_stdout(f):
                    analyzer.print_analysis(queue)
                
                output = f.getvalue()
                self.log(output)
                
                self.log(f"\n✅ Phân tích {queue} hoàn thành!")
                self.update_status("✅ Hoàn thành!")
                
            except FileNotFoundError as e:
                self.log(f"\n❌ Lỗi: Không tìm thấy file - {e}")
                messagebox.showerror("Lỗi", f"Không tìm thấy file dữ liệu:\n{e}")
            except Exception as e:
                self.log(f"\n❌ Lỗi: {e}")
                messagebox.showerror("Lỗi", str(e))
            finally:
                self.enable_buttons()
                self.update_status("✅ Sẵn sàng")
        
        self.run_in_thread(task)
    
    def full_analysis(self):
        def task():
            try:
                self.disable_buttons()
                self.update_status("⏳ Đang thực hiện phân tích đầy đủ...")
                
                analyzer = self.create_analyzer()
                if not analyzer:
                    return
                
                self.log("\n🎯 BẮT ĐẦU PHÂN TÍCH ĐẦY ĐỦ")
                self.log("="*70)
                
                # Load data
                self.log("\n1️⃣ Đang tải dữ liệu...")
                analyzer.load_data('DropTail')
                analyzer.load_data('RED')
                
                # Print analysis
                self.log("\n2️⃣ Đang phân tích DropTail...")
                import io
                from contextlib import redirect_stdout
                
                f = io.StringIO()
                with redirect_stdout(f):
                    analyzer.print_analysis('DropTail')
                self.log(f.getvalue())
                
                self.log("\n3️⃣ Đang phân tích RED...")
                f = io.StringIO()
                with redirect_stdout(f):
                    analyzer.print_analysis('RED')
                self.log(f.getvalue())
                
                # Create visualizations
                self.log("\n4️⃣ Đang tạo comparison dashboard...")
                analyzer.create_comparison_dashboard()
                
                self.log("\n5️⃣ Đang tạo infographic PDF...")
                analyzer.create_infographic()
                
                self.log("\n" + "="*70)
                self.log("✅ PHÂN TÍCH ĐẦY ĐỦ HOÀN THÀNH!")
                self.log("="*70)
                
                self.update_status("✅ Hoàn thành!")
                messagebox.showinfo("Thành công", "Phân tích đầy đủ đã hoàn thành!")
                
            except FileNotFoundError as e:
                self.log(f"\n❌ Lỗi: Không tìm thấy file - {e}")
                messagebox.showerror("Lỗi", f"Không tìm thấy file dữ liệu:\n{e}")
            except Exception as e:
                self.log(f"\n❌ Lỗi: {e}")
                messagebox.showerror("Lỗi", str(e))
            finally:
                self.enable_buttons()
                self.update_status("✅ Sẵn sàng")
        
        self.run_in_thread(task)


def main():
    """Main function to run GUI"""
    root = tk.Tk()
    app = TCPAnalyzerGUI(root)
    
    # Center window
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()


if __name__ == '__main__':
    main()
