#!/usr/bin/env python3
"""
TCP Reno Visual Analysis Tool - Enhanced Version with Emoji Support
Phân tích kết quả mô phỏng TCP Reno với đồ họa đẹp mắt

Main entry point for the application
"""

import sys
import argparse
from analyzer.enhanced_tcp_analyzer import EnhancedTCPAnalyzer


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description='TCP Reno Visual Analyzer - Enhanced Version',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
🎨 Examples:
  # Dashboard cho 1 loại hàng đợi
  python3 main.py --queue DropTail --dashboard
  
  # So sánh cả hai
  python3 main.py --compare --dashboard
  
  # Tạo infographic tổng hợp
  python3 main.py --infographic
  
  # Timeline chi tiết
  python3 main.py --queue RED --timeline
  
  # Full analysis
  python3 main.py --compare --dashboard --infographic --print
        """
    )

    parser.add_argument('--results-dir', default='../results/',
                       help='Thư mục chứa kết quả')
    parser.add_argument('--prefix', default='P2P-project',
                       help='Prefix của files')
    parser.add_argument('--queue', choices=['DropTail', 'RED'],
                       help='Phân tích loại hàng đợi cụ thể')
    parser.add_argument('--compare', action='store_true',
                       help='So sánh DropTail vs RED')
    parser.add_argument('--dashboard', action='store_true',
                       help='Tạo dashboard trực quan')
    parser.add_argument('--timeline', action='store_true',
                       help='Tạo timeline chi tiết')
    parser.add_argument('--infographic', action='store_true',
                       help='Tạo infographic tổng hợp')
    parser.add_argument('--print', action='store_true',
                       help='In phân tích chi tiết ra terminal')

    args = parser.parse_args()

    # Create analyzer
    analyzer = EnhancedTCPAnalyzer(args.results_dir, args.prefix)

    print("\n" + "="*70)
    print("🎨 TCP RENO VISUAL ANALYZER - ENHANCED")
    print("="*70)

    try:
        if args.infographic:
            # Load both and create infographic
            print("\n📊 Đang tạo infographic tổng hợp...")
            analyzer.load_data('DropTail')
            analyzer.load_data('RED')
            analyzer.create_infographic()

        if args.compare:
            # Compare mode
            analyzer.load_data('DropTail')
            analyzer.load_data('RED')
            
            if args.print:
                print("\n📋 PHÂN TÍCH DROPTAIL:")
                analyzer.print_analysis('DropTail')
                print("\n📋 PHÂN TÍCH RED:")
                analyzer.print_analysis('RED')
            
            if args.dashboard:
                print("\n📊 Đang tạo comparison dashboard...")
                analyzer.create_comparison_dashboard()

        elif args.queue:
            # Single queue mode
            analyzer.load_data(args.queue)
            
            if args.print:
                analyzer.print_analysis(args.queue)
            
            if args.dashboard:
                print(f"\n📊 Đang tạo dashboard cho {args.queue}...")
                analyzer.create_dashboard(args.queue)
            
            if args.timeline:
                print(f"\n⏱️ Đang tạo timeline cho {args.queue}...")
                analyzer.create_animated_timeline(args.queue)
        
        else:
            print("\n❌ Lỗi: Phải chọn --queue <type> hoặc --compare hoặc --infographic")
            print("📖 Dùng --help để xem hướng dẫn")
            return 1

    except FileNotFoundError as e:
        print(f"\n❌ Lỗi: Không tìm thấy file - {e}")
        print("💡 Hãy chắc chắn bạn đã chạy simulation và có file kết quả")
        return 1
    except Exception as e:
        print(f"\n❌ Lỗi không mong đợi: {e}")
        import traceback
        traceback.print_exc()
        return 1

    print("\n" + "="*70)
    print("✅ Phân tích hoàn tất!")
    print("="*70 + "\n")

    return 0


if __name__ == '__main__':
    sys.exit(main())
