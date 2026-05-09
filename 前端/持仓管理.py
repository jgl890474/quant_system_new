# 持仓显示部分（替换原有代码）
if 引擎.持仓:
    数据 = []
    for 品种, pos in 引擎.持仓.items():
        try:
            # 获取价格（兼容不同返回格式）
            价格结果 = 行情获取.获取价格(品种)
            if hasattr(价格结果, '价格'):
                现价 = float(价格结果.价格)
            elif hasattr(价格结果, 'price'):
                现价 = float(价格结果.price)
            elif isinstance(价格结果, (int, float)):
                现价 = float(价格结果)
            else:
                现价 = float(pos.平均成本)

            成本 = float(pos.平均成本)
            数量 = float(pos.数量)

            盈亏 = 数量 * (现价 - 成本)
            盈亏率 = (现价 / 成本 - 1) * 100 if 成本 > 0 else 0.0

            数据.append({
                "品种": 品种,
                "数量": f"{数量:.0f}",
                "成本": f"{成本:.2f}",
                "现价": f"{现价:.2f}",
                "盈亏": f"¥{盈亏:+,.2f}",
                "盈亏率": f"{盈亏率:+.2f}%"
            })
        except Exception as e:
            数据.append({
                "品种": 品种,
                "数量": f"{pos.数量:.0f}",
                "成本": f"{pos.平均成本:.2f}",
                "现价": "获取失败",
                "盈亏": "---",
                "盈亏率": "---"
            })

    st.dataframe(pd.DataFrame(数据), use_container_width=True, hide_index=True)

    # 底部显示总盈亏
    总盈亏 = 0.0
    for d in 数据:
        if d["盈亏"] != "---":
            总盈亏 += float(d["盈亏"].replace("¥", "").replace(",", ""))
    st.caption(f"📊 持仓总盈亏：¥{总盈亏:+,.2f}")

else:
    st.caption("暂无持仓")
