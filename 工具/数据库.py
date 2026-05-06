# -*- coding: utf-8 -*-
import sqlite3
import json
from datetime import datetime

数据库路径 = "quant_system.db"

def 初始化数据库():
    conn = sqlite3.connect(数据库路径, check_same_thread=False)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS 交易记录 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            时间 TEXT,
            动作 TEXT,
            品种 TEXT,
            价格 REAL,
            数量 REAL,
            盈亏 REAL DEFAULT 0,
            策略名称 TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def 保存交易记录(动作, 品种, 价格, 数量, 盈亏=0, 策略名称=""):
    try:
        conn = sqlite3.connect(数据库路径, check_same_thread=False)
        cursor = conn.cursor()
        # 使用 ISO 格式时间
        时间 = datetime.now().isoformat()
        cursor.execute("""
            INSERT INTO 交易记录 (时间, 动作, 品种, 价格, 数量, 盈亏, 策略名称)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (时间, 动作, 品种, 价格, 数量, 盈亏, 策略名称))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"保存交易记录失败: {e}")
        return False

def 获取交易记录(限制数量=100):
    try:
        conn = sqlite3.connect(数据库路径, check_same_thread=False)
        query = f"SELECT * FROM 交易记录 ORDER BY 时间 DESC LIMIT {限制数量}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()
