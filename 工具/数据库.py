# -*- coding: utf-8 -*-
import sqlite3
import json
import pandas as pd
from datetime import datetime
import streamlit as st

数据库路径 = "quant_system.db"


def 获取连接():
    """获取数据库连接"""
    conn = sqlite3.connect(数据库路径, check_same_thread=False)
    return conn


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

    # 持仓快照表（历史）
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS 持仓快照 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            时间 TEXT,
            品种 TEXT,
            数量 REAL,
            平均成本 REAL,
            当前价格 REAL,
            盈亏 REAL
        )
    """)

    # 策略配置表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS 策略配置 (
            策略名称 TEXT PRIMARY KEY,
            参数 TEXT,
            启用 INTEGER DEFAULT 1,
            更新时间 TEXT
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

    # AI 决策历史表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS AI决策历史 (
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

    conn.commit()
    conn.close()


def 保存交易记录(动作, 品种, 价格, 数量, 盈亏=0, 策略名称=""):
    """保存单条交易记录"""
    try:
        conn = 获取连接()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO 交易记录 (时间, 动作, 品种, 价格, 数量, 盈亏, 策略名称)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), 动作, 品种, 价格, 数量, 盈亏, 策略名称))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"保存交易记录失败: {e}")
        return False


def 获取交易记录(限制数量=100):
    """获取最近的交易记录"""
    try:
        conn = 获取连接()
        df = pd.read_sql_query(f"SELECT * FROM 交易记录 ORDER BY 时间 DESC LIMIT {限制数量}", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()


def 保存持仓快照(持仓字典, 总资产):
    """保存当前持仓快照"""
    try:
        conn = 获取连接()
        cursor = conn.cursor()
        时间 = datetime.now().isoformat()

        for 品种, 持仓 in 持仓字典.items():
            cursor.execute("""
                INSERT INTO 持仓快照 (时间, 品种, 数量, 平均成本, 当前价格, 盈亏)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (时间, 品种, 持仓.数量, 持仓.平均成本, 持仓.当前价格,
                  持仓.数量 * (持仓.当前价格 - 持仓.平均成本)))

        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"保存持仓快照失败: {e}")
        return False


def 保存策略配置(策略名称, 参数字典):
    """保存策略参数配置"""
    try:
        conn = 获取连接()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO 策略配置 (策略名称, 参数, 更新时间)
            VALUES (?, ?, ?)
        """, (策略名称, json.dumps(参数字典, ensure_ascii=False), datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"保存策略配置失败: {e}")
        return False


def 获取策略配置(策略名称):
    """获取策略参数配置"""
    try:
        conn = 获取连接()
        cursor = conn.cursor()
        cursor.execute("SELECT 参数 FROM 策略配置 WHERE 策略名称 = ?", (策略名称,))
        row = cursor.fetchone()
        conn.close()
        if row:
            return json.loads(row[0])
        return None
    except:
        return None


def 保存AI决策(品种, 价格, 策略信号, AI信号, 置信度, 理由):
    """保存AI决策历史"""
    try:
        conn = 获取连接()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO AI决策历史 (时间, 品种, 价格, 策略信号, AI信号, 置信度, 理由)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (datetime.now().isoformat(), 品种, 价格, 策略信号, AI信号, 置信度, 理由))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"保存AI决策失败: {e}")
        return False


def 获取AI决策历史(限制数量=50):
    """获取AI决策历史"""
    try:
        conn = 获取连接()
        df = pd.read_sql_query(f"SELECT * FROM AI决策历史 ORDER BY 时间 DESC LIMIT {限制数量}", conn)
        conn.close()
        return df
    except:
        return pd.DataFrame()


def 保存系统参数(参数名, 参数值):
    """保存系统参数"""
    try:
        conn = 获取连接()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO 系统参数 (参数名, 参数值, 更新时间)
            VALUES (?, ?, ?)
        """, (参数名, json.dumps(参数值, ensure_ascii=False), datetime.now().isoformat()))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"保存系统参数失败: {e}")
        return False


def 获取系统参数(参数名):
    """获取系统参数"""
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


def 导出交易记录CSV():
    """导出交易记录为CSV"""
    df = 获取交易记录(10000)
    if not df.empty:
        csv = df.to_csv(index=False)
        return csv
    return None
