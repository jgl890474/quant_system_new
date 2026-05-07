# -*- coding: utf-8 -*-
import sqlite3
import json
import pandas as pd
from datetime import datetime

# 设置北京时间
def 获取当前时间():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def 获取当前日期():
    return datetime.now().strftime("%Y-%m-%d")

数据库路径 = "quant_system.db"

def 获取连接():
    return sqlite3.connect(数据库路径, check_same_thread=False)

def 初始化数据库():
    """初始化所有数据表"""
    conn = 获取连接()
    cursor = conn.cursor()
    
    # 交易记录表
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
    
    # 持仓表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS 持仓 (
            品种 TEXT PRIMARY KEY,
            数量 REAL,
            平均成本 REAL,
            已实现盈亏 REAL DEFAULT 0,
            更新时间 TEXT
        )
    """)
    
    # 资金曲线表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS 资金曲线 (
            日期 TEXT PRIMARY KEY,
            总资产 REAL,
            总盈亏 REAL,
            持仓市值 REAL,
            可用资金 REAL
        )
    """)
    
    # 持仓历史表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS 持仓历史 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            时间 TEXT,
            品种 TEXT,
            数量 REAL,
            成本 REAL,
            现价 REAL,
            盈亏 REAL,
            市值 REAL
        )
    """)
    
    # 回测结果表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS 回测结果 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            时间 TEXT,
            品种 TEXT,
            策略类型 TEXT,
            开始日期 TEXT,
            结束日期 TEXT,
            初始资金 REAL,
            最终资金 REAL,
            总收益率 REAL,
            年化收益 REAL,
            最大回撤 REAL,
            胜率 REAL,
            交易次数 INTEGER,
            参数 TEXT
        )
    """)
    
    # AI决策记录表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS AI决策记录 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            时间 TEXT,
            品种 TEXT,
            价格 REAL,
            策略信号 TEXT,
            AI信号 TEXT,
            置信度 INTEGER,
            理由 TEXT
        )
    """)
    
    # 系统参数表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS 系统参数 (
            参数名 TEXT PRIMARY KEY,
            参数值 TEXT,
            更新时间 TEXT
        )
    """)
    
    conn.commit()
    conn.close()

def 清空所有持仓():
    """清空持仓表（修复错误数据）"""
    try:
        conn = 获取连接()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM 持仓")
        cursor.execute("DELETE FROM 资金曲线")
        cursor.execute("DELETE FROM 持仓历史")
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"清空持仓失败: {e}")
        return False

# ========== 交易记录 ==========
def 保存交易记录(动作, 品种, 价格, 数量, 盈亏=0, 策略名称=""):
    try:
        conn = 获取连接()
        cursor = conn.cursor()
        时间 = 获取当前时间()
        cursor.execute("""
            INSERT INTO 交易记录 (时间, 动作, 品种, 价格, 数量, 盈亏, 策略名称)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (时间, 动作, 品种, 价格, 数量, 盈亏, 策略名称))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def 获取交易记录(限制数量=100):
    try:
        conn = 获取连接()
        query = f"SELECT * FROM 交易记录 ORDER BY 时间 DESC LIMIT {限制数量}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

# ========== 持仓管理 ==========
def 保存持仓(品种, 数量, 平均成本, 已实现盈亏=0):
    try:
        conn = 获取连接()
        cursor = conn.cursor()
        更新时间 = 获取当前时间()
        cursor.execute("""
            INSERT OR REPLACE INTO 持仓 (品种, 数量, 平均成本, 已实现盈亏, 更新时间)
            VALUES (?, ?, ?, ?, ?)
        """, (品种, 数量, 平均成本, 已实现盈亏, 更新时间))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def 删除持仓(品种):
    try:
        conn = 获取连接()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM 持仓 WHERE 品种 = ?", (品种,))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def 获取所有持仓():
    try:
        conn = 获取连接()
        df = pd.read_sql_query("SELECT * FROM 持仓", conn)
        conn.close()
        持仓字典 = {}
        for _, row in df.iterrows():
            持仓字典[row['品种']] = {
                '数量': row['数量'],
                '平均成本': row['平均成本'],
                '已实现盈亏': row['已实现盈亏']
            }
        return 持仓字典
    except:
        return {}

# ========== 资金曲线 ==========
def 保存资金快照(总资产, 总盈亏, 持仓市值, 可用资金):
    try:
        conn = 获取连接()
        cursor = conn.cursor()
        日期 = 获取当前日期()
        cursor.execute("""
            INSERT OR REPLACE INTO 资金曲线 (日期, 总资产, 总盈亏, 持仓市值, 可用资金)
            VALUES (?, ?, ?, ?, ?)
        """, (日期, 总资产, 总盈亏, 持仓市值, 可用资金))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def 获取资金曲线(天数=90):
    try:
        conn = 获取连接()
        query = f"SELECT * FROM 资金曲线 ORDER BY 日期 DESC LIMIT {天数}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df.sort_values('日期')
    except:
        return pd.DataFrame()

# ========== 持仓历史 ==========
def 保存持仓历史(品种, 数量, 成本, 现价, 盈亏, 市值):
    try:
        conn = 获取连接()
        cursor = conn.cursor()
        时间 = 获取当前时间()
        cursor.execute("""
            INSERT INTO 持仓历史 (时间, 品种, 数量, 成本, 现价, 盈亏, 市值)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (时间, 品种, 数量, 成本, 现价, 盈亏, 市值))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def 获取持仓历史(品种=None, 天数=30):
    try:
        conn = 获取连接()
        if 品种:
            query = f"SELECT * FROM 持仓历史 WHERE 品种 = '{品种}' ORDER BY 时间 DESC LIMIT {天数}"
        else:
            query = f"SELECT * FROM 持仓历史 ORDER BY 时间 DESC LIMIT {天数 * 10}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

# ========== 回测结果 ==========
def 保存回测结果(品种, 策略类型, 开始日期, 结束日期, 初始资金, 最终资金, 
                  总收益率, 年化收益, 最大回撤, 胜率, 交易次数, 参数):
    try:
        conn = 获取连接()
        cursor = conn.cursor()
        时间 = 获取当前时间()
        cursor.execute("""
            INSERT INTO 回测结果 
            (时间, 品种, 策略类型, 开始日期, 结束日期, 初始资金, 最终资金, 
             总收益率, 年化收益, 最大回撤, 胜率, 交易次数, 参数)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            时间, 品种, 策略类型, 
            开始日期, 结束日期, 初始资金, 最终资金,
            总收益率, 年化收益, 最大回撤, 胜率, 交易次数, 
            json.dumps(参数, ensure_ascii=False)
        ))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def 获取回测历史(限制数量=20):
    try:
        conn = 获取连接()
        query = f"SELECT * FROM 回测结果 ORDER BY 时间 DESC LIMIT {限制数量}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

# ========== AI决策记录 ==========
def 保存AI决策(品种, 价格, 策略信号, AI信号, 置信度, 理由):
    try:
        conn = 获取连接()
        cursor = conn.cursor()
        时间 = 获取当前时间()
        cursor.execute("""
            INSERT INTO AI决策记录 (时间, 品种, 价格, 策略信号, AI信号, 置信度, 理由)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (时间, 品种, 价格, 策略信号, AI信号, 置信度, 理由))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def 获取AI决策历史(限制数量=50):
    try:
        conn = 获取连接()
        query = f"SELECT * FROM AI决策记录 ORDER BY 时间 DESC LIMIT {限制数量}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()

# ========== 系统参数 ==========
def 保存系统参数(参数名, 参数值):
    try:
        conn = 获取连接()
        cursor = conn.cursor()
        更新时间 = 获取当前时间()
        cursor.execute("""
            INSERT OR REPLACE INTO 系统参数 (参数名, 参数值, 更新时间)
            VALUES (?, ?, ?)
        """, (参数名, json.dumps(参数值, ensure_ascii=False), 更新时间))
        conn.commit()
        conn.close()
        return True
    except:
        return False

def 获取系统参数(参数名):
    try:
        conn = 获取连接()
        cursor = conn.cursor()
        cursor.execute("SELECT 参数值 FROM 系统参数 WHERE 参数名 = ?", (参数名,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return json.loads(row[0])
        return None
    except:
        return None
