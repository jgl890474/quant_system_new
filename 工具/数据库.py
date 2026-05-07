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
