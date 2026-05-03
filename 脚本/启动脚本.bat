@echo off
REM 文件位置: quant_system_v5/脚本/启动脚本.bat

cd /d %~dp0..

echo ==================================
echo 量化交易系统 v5.0 启动
echo ==================================

REM 安装依赖
echo 安装依赖...
pip install -r requirements.txt

REM 启动系统
echo 启动主程序...
python main.py

pause