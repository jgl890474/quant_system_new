#!/bin/bash
# 文件位置: quant_system_v5/脚本/启动脚本.sh

cd "$(dirname "$0")/.."

echo "=================================="
echo "量化交易系统 v5.0 启动"
echo "=================================="

# 检查Python环境
if ! command -v python3 &> /dev/null; then
    echo "错误: 未找到 python3"
    exit 1
fi

# 安装依赖
echo "安装依赖..."
pip3 install -r requirements.txt

# 启动系统
echo "启动主程序..."
python3 main.py