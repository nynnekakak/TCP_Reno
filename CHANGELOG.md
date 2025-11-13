# CHANGELOG

## [1.0.0] - 2025-01-13

### Added
- ✅ Full TCP Reno simulation với NS-3.43
- ✅ So sánh DropTail vs RED queue disciplines
- ✅ Detailed FSM state tracking (SlowStart, CongestionAvoidance, FastRecovery)
- ✅ Real-time visualization với plot_realtime.py
- ✅ Enhanced analyzer với dashboard và infographic
- ✅ Multi-flow support (1-3 concurrent flows)
- ✅ Comprehensive documentation (README.md, QUICKSTART.md)
- ✅ Automated build và run scripts

### Features
- **Simulation**:
  - 7-node topology (3 senders, 2 routers, 2 receivers)
  - Configurable parameters (duration, bandwidth, queue size, etc.)
  - Flow monitor với throughput, packet loss, delay statistics
  - Error model support
  - SACK và Nagle algorithm options

- **Visualization**:
  - Real-time CWND plotting
  - FSM state diagram với highlighting
  - Animated timeline
  - Comparison dashboards

- **Analysis Tools**:
  - Enhanced TCP Analyzer với multiple views
  - Dashboard creation (single queue và comparison)
  - Infographic generation
  - Terminal reports với emoji formatting

### Documentation
- Complete README.md với Vietnamese
- Quick start guide
- Detailed usage instructions
- Troubleshooting section
- API documentation for analyzer

### Files Structure
```
TCP_Reno/
├── README.md
├── QUICKSTART.md
├── LICENSE
├── CHANGELOG.md
├── requirements.txt
├── .gitignore
├── tcp_reno.cc
├── CMakeLists.txt
├── plot_realtime.py
├── run.sh
├── analyze/
└── results/
```

---

## Future Enhancements (Planned)

### Version 1.1.0 (Planned)
- [ ] GUI interface cho simulation control
- [ ] Web-based dashboard
- [ ] Additional queue disciplines (CoDel, FQ-CoDel)
- [ ] TCP variants comparison (Reno, NewReno, CUBIC)
- [ ] Performance optimization
- [ ] Docker containerization

### Version 1.2.0 (Planned)
- [ ] Automated testing suite
- [ ] CI/CD pipeline
- [ ] More complex topologies
- [ ] Wireless network support
- [ ] Cloud deployment scripts

---

## Known Issues

### Current Limitations
1. Real-time plotter requires X11/display server
2. NS-3 path hardcoded trong run.sh (cần customize)
3. Python 2 compatibility chưa test
4. Windows native support limited (cần WSL)

### Workarounds
1. Sử dụng analyzer tool cho visualization nếu không có display
2. Update NS3_DIR trong run.sh
3. Khuyến nghị Python 3.7+
4. Sử dụng WSL hoặc VM cho Windows users

---

## Contributors
- Nhóm PBL - Initial release và documentation

## References
- NS-3 Network Simulator (https://www.nsnam.org/)
- TCP RFC 2581, 2582
- RED Queue paper (Floyd & Jacobson, 1993)
