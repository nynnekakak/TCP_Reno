@echo off
REM =============================================================
REM TCP Reno Simulation Runner for Windows
REM Chạy mô phỏng cho cả DropTail và RED queue
REM =============================================================

echo ========================================
echo TCP Reno Simulation Runner (Windows)
echo ========================================
echo.

REM Configuration
set NS3_DIR=%USERPROFILE%\ns-allinone-3.43\ns-3.43
set PROJECT_PATH=scratch/tcp_reno_project/tcp_reno
set DURATION=20
set NUM_FLOWS=3

REM Check if NS-3 directory exists
if not exist "%NS3_DIR%" (
    echo [ERROR] NS-3 directory not found at %NS3_DIR%
    echo Please update NS3_DIR in this script or install NS-3
    pause
    exit /b 1
)

cd /d "%NS3_DIR%"

REM Build project
echo [1/4] Building project...
call ns3 build
if errorlevel 1 (
    echo [ERROR] Build failed!
    pause
    exit /b 1
)
echo [OK] Build successful!
echo.

REM Run DropTail simulation
echo [2/4] Running DropTail simulation...
echo Queue Type: DropTail
echo Duration: %DURATION%s
echo Flows: %NUM_FLOWS%
echo.

call ns3 run "%PROJECT_PATH% --queueType=DropTail --duration=%DURATION% --numFlows=%NUM_FLOWS%"
if errorlevel 1 (
    echo [ERROR] DropTail simulation failed!
    pause
    exit /b 1
)
echo [OK] DropTail simulation completed!
echo.

REM Wait a bit
timeout /t 2 /nobreak >nul

REM Run RED simulation
echo [3/4] Running RED simulation...
echo Queue Type: RED
echo Duration: %DURATION%s
echo Flows: %NUM_FLOWS%
echo.

call ns3 run "%PROJECT_PATH% --queueType=RED --duration=%DURATION% --numFlows=%NUM_FLOWS%"
if errorlevel 1 (
    echo [ERROR] RED simulation failed!
    pause
    exit /b 1
)
echo [OK] RED simulation completed!
echo.

REM List results
echo [4/4] Results generated:
set RESULTS_DIR=scratch\tcp_reno_project\results
if exist "%RESULTS_DIR%" (
    echo Files in %RESULTS_DIR%:
    dir /b "%RESULTS_DIR%\*.tr" "%RESULTS_DIR%\*.txt" "%RESULTS_DIR%\*.log" 2>nul
) else (
    echo [WARNING] Results directory not found!
)

echo.
echo ========================================
echo All simulations completed successfully!
echo ========================================
echo.

echo Next steps:
echo 1. Analyze results with: cd analyze ^&^& python3 main.py --compare --dashboard
echo 2. View summary files in: %RESULTS_DIR%
echo 3. Generate comparison: cd analyze ^&^& python3 main.py --infographic
echo.

pause
