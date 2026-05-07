# 在初始化数据库函数中添加持仓历史表
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

# 新增：保存持仓历史快照
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

# 获取持仓历史（按品种分组）
def 获取持仓历史(品种=None, 天数=90):
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
