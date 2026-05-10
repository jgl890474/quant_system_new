# -*- coding: utf-8 -*-
import sqlite3
import os
from datetime import datetime


DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "quant_system.db")


def 获取连接():
    """获取数据库连接"""
    return sqlite3.connect(DB_PATH)


def 初始化数据库():
    """初始化数据库表"""
    conn = 获取连接()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS 交易记录 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            时间 TEXT,
            品种 TEXT,
            动作 TEXT,
            价格 REAL,
            数量 REAL,
            盈亏 REAL,
            策略名称 TEXT
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS 持仓快照 (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            时间 TEXT,
            品种 TEXT,
            数量 REAL,
            平均成本 REAL,
            当前价格 REAL,
            盈亏 REAL
        )
    ''')
    
    cursor.execute('''
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
    ''')
    
    conn.commit()
    conn.close()
    print("✅ 数据库初始化完成")


def 保存交易记录(交易):
    """保存交易记录"""
    try:
        conn = 获取连接()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO 交易记录 (时间, 品种, 动作, 价格, 数量, 盈亏, 策略名称)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            交易.get("时间", datetime.now().strftime("%Y-%m-%d %H:%M:%S")),
            交易.get("品种", ""),
            交易.get("动作", ""),
            交易.get("价格", 0),
            交易.get("数量", 0),
            交易.get("盈亏", 0),
            交易.get("策略名称", "")
        ))
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"保存交易记录失败: {e}")
        return False


def 获取交易记录(限制数量=100):
    """获取交易记录"""
    try:
        conn = 获取连接()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT 时间, 品种, 动作, 价格, 数量, 盈亏, 策略名称
            FROM 交易记录
            ORDER BY 时间 DESC
            LIMIT ?
        ''', (限制数量,))
        rows = cursor.fetchall()
        conn.close()
        
        记录 = []
        for row in rows:
            记录.append({
                "时间": row[0],
                "品种": row[1],
                "动作": row[2],
                "价格": row[3],
                "数量": row[4],
                "盈亏": row[5],
                "策略名称": row[6]
            })
        return 记录
    except Exception as e:
        print(f"获取交易记录失败: {e}")
        return []


def 保存持仓快照(持仓):
    """保存持仓快照"""
    try:
        conn = 获取连接()
        cursor = conn.cursor()
        当前时间 = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        for 品种, pos in 持仓.items():
            # 兼容持仓数据对象和字典两种格式
            if hasattr(pos, '数量'):
                number = pos.数量
                avg_cost = pos.平均成本
            else:
                number = pos.get("数量", 0)
                avg_cost = pos.get("平均成本", 0)
                
            cursor.execute('''
                INSERT INTO 持仓快照 (时间, 品种, 数量, 平均成本, 当前价格, 盈亏)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                当前时间,
                品种,
                number,
                avg_cost,
                0,
                0
            ))
        
        conn.commit()
        conn.close()
        return True
    except Exception as e:
        print(f"保存持仓快照失败: {e}")
        return False


def 加载持仓快照():
    """加载最新的持仓快照"""
    try:
        conn = 获取连接()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT t1.品种, t1.数量, t1.平均成本
            FROM 持仓快照 t1
            INNER JOIN (
                SELECT 品种, MAX(时间) as 最新时间
                FROM 持仓快照
                GROUP BY 品种
            ) t2 ON t1.品种 = t2.品种 AND t1.时间 = t2.最新时间
        ''')
        rows = cursor.fetchall()
        conn.close()
        
        持仓 = {}
        for row in rows:
            持仓[row[0]] = {
                "数量": row[1],
                "平均成本": row[2]
            }
        return 持仓
    except Exception as e:
        print(f"加载持仓快照失败: {e}")
        return {}


def 清空所有持仓():
    """清空所有持仓数据"""
    try:
        conn = 获取连接()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM 持仓快照")
        conn.commit()
        conn.close()
        print("✅ 已清空所有持仓数据")
        return True
    except Exception as e:
        print(f"清空持仓数据失败: {e}")
        return False


def 获取当前时间():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# ==================== 数据库类（兼容订单引擎的调用方式） ====================
class 数据库:
    """数据库操作类 - 兼容订单引擎的调用方式"""
    
    @staticmethod
    def 保存交易记录(交易):
        return 保存交易记录(交易)
    
    @staticmethod
    def 保存持仓快照(持仓):
        return 保存持仓快照(持仓)
    
    @staticmethod
    def 加载持仓快照():
        return 加载持仓快照()
    
    @staticmethod
    def 获取交易记录(限制数量=100):
        return 获取交易记录(限制数量)
    
    @staticmethod
    def 清空所有持仓():
        return 清空所有持仓()
    
    @staticmethod
    def 初始化数据库():
        return 初始化数据库()


# 测试入口
if __name__ == "__main__":
    初始化数据库()
    print("数据库模块测试完成")
