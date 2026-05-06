#!/bin/bash
cd "$(dirname "$0")/.."
streamlit run 启动入口.py --server.port 8501 --server.address 0.0.0.0
