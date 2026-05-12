# -*- coding: utf-8 -*-
"""
A股隔夜套利策略 - 自动执行脚本
运行方式: python 脚本/自动交易.py
或在 Streamlit Cloud 上通过定时任务触发
"""
import sys
import os
import time
from datetime import datetime, date

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心 import 订单引擎, 策略加载器, AI引擎, 行情获取
from 策略库.A股策略.A股隔夜套利策略 import AStockOvernightStrategy


# ==================== 辅助函数 ====================
def 获取当前时间():
    return datetime.now()


def 是尾盘时间():
    """检查是否是尾盘时间 (14:55-15:00)"""
    now = datetime.now()
    return now.hour == 14 and now.minute >= 55


def 是早盘时间():
    """检查是否是早盘时间 (09:30-09:35)"""
    now = datetime.now()
    return now.hour == 9 and now.minute >= 30 and now.minute <= 35


def 是交易时间():
    """检查是否是交易时间"""
    now = datetime.now()
    now_str = now.strftime("%H:%M")
    return now_str >= "09:30" and now_str <= "15:00" and now.weekday() < 5


def 获取交易状态():
    """获取当前交易状态"""
    now = datetime.now()
    if now.weekday() >= 5:
        return "非交易日"
    if 是早盘时间():
        return "早盘交易中"
    if 是尾盘时间():
        return "尾盘交易中"
    if now.hour >= 9 and now.hour < 15:
        return "盘中"
    return "盘后"


class 定时任务:
    """简单的定时任务调度器"""
    
    def __init__(self):
        self.任务列表 = []
        self.运行中 = True
    
    def 添加任务(self, 函数, 时间字符串):
        """添加定时任务，如 添加任务(函数, '14:55')"""
        self.任务列表.append({"函数": 函数, "时间": 时间字符串, "最后执行": None})
        print(f"⏰ 已添加定时任务: {时间字符串}")
        return self
    
    def 添加间隔任务(self, 函数, 间隔秒):
        """添加间隔任务"""
        self.任务列表.append({"函数": 函数, "间隔": 间隔秒, "最后执行": None})
        print(f"⏰ 已添加间隔任务: 每{间隔秒}秒")
        return self
    
    def 执行一次任务(self):
        """执行一次所有任务"""
        for 任务 in self.任务列表:
            if "时间" in 任务:
                # 定时任务
                now = datetime.now().strftime("%H:%M")
                目标时间 = 任务["时间"]
                
                if now == 目标时间:
                    if 任务["最后执行"] != date.today():
                        try:
                            任务["函数"]()
                            任务["最后执行"] = date.today()
                            print(f"✅ 执行定时任务: {目标时间}")
                        except Exception as e:
                            print(f"❌ 定时任务失败: {e}")
            elif "间隔" in 任务:
                # 间隔任务
                now = time.time()
                if 任务["最后执行"] is None or now - 任务["最后执行"] >= 任务["间隔"]:
                    try:
                        任务["函数"]()
                        任务["最后执行"] = now
                    except Exception as e:
                        print(f"❌ 间隔任务失败: {e}")
    
    def 启动(self):
        """启动调度器"""
        print("🚀 定时调度器启动...")
        try:
            while self.运行中:
                self.执行一次任务()
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n👋 调度器已停止")
            self.运行中 = False


class 自动交易机器人:
    """自动交易机器人"""
    
    def __init__(self):
        self.引擎 = 订单引擎(初始资金=1000000)
        self.策略加载器 = 策略加载器()
        self.AI引擎 = AI引擎()
        self.策略 = None
        self.今日已买入 = False
        self.今日日期 = date.today()
        self.品种 = "000001.SS"  # 可以改为具体股票代码
        
    def 重置每日状态(self):
        """重置每日状态"""
        today = date.today()
        if today != self.今日日期:
            self.今日日期 = today
            self.今日已买入 = False
            print(f"📅 进入新的一天，重置状态")
    
    def 初始化策略(self):
        """初始化隔夜套利策略"""
        self.策略 = AStockOvernightStrategy(
            名称="A股隔夜套利",
            品种=self.品种,
            初始资金=self.引擎.初始资金,
            买入时=14,      # 14:55
            买入分=55,
            卖出时=9,       # 09:30
            卖出分=30,
            最小涨幅=0.01,
            最大涨幅=0.05,
            成交量倍数=1.5,
            止损=0.03,
            止盈=0.05
        )
        print(f"✅ 策略初始化完成")
        print(f"   品种: {self.品种}")
        print(f"   买入窗口: 14:55-15:00")
        print(f"   卖出窗口: 09:30-09:35")
        print(f"   止损/止盈: 3% / 5%")
    
    def 尾盘买入检查(self):
        """尾盘买入检查"""
        self.重置每日状态()
        
        if self.今日已买入:
            return
        
        if not 是尾盘时间():
            return
        
        if not 是交易时间():
            return
        
        print(f"\n📊 [{datetime.now().strftime('%H:%M:%S')}] 尾盘买入检查")
        
        try:
            行情结果 = 行情获取.获取价格(self.品种)
            if not 行情结果 or not hasattr(行情结果, '价格'):
                print(f"   ❌ 无法获取 {self.品种} 行情")
                return
            
            # 准备K线数据
            k线 = {
                'close': 行情结果.价格,
                'volume': getattr(行情结果, '成交量', 0),
                'high': getattr(行情结果, '最高', 行情结果.价格),
                'low': getattr(行情结果, '最低', 行情结果.价格),
                'open': getattr(行情结果, '开盘', 行情结果.价格)
            }
            
            # 运行策略
            信号 = self.策略.处理行情(k线)
            
            if 信号 == 'buy':
                print(f"   🟢 触发买入信号")
                价格 = 行情结果.价格
                结果 = self.引擎.买入(self.品种, 价格, 1000)  # 买入1000股
                if 结果.get("success"):
                    self.今日已买入 = True
                    print(f"   ✅ 已买入 {self.品种} @ {价格:.2f}")
                else:
                    print(f"   ❌ 买入失败: {结果.get('error')}")
            else:
                print(f"   ⚪ 无买入信号 (信号: {信号})")
                
        except Exception as e:
            print(f"   ❌ 买入检查失败: {e}")
    
    def 早盘卖出检查(self):
        """早盘卖出检查"""
        self.重置每日状态()
        
        if not 是早盘时间():
            return
        
        if not 是交易时间():
            return
        
        print(f"\n💰 [{datetime.now().strftime('%H:%M:%S')}] 早盘卖出检查")
        
        try:
            if self.品种 in self.引擎.持仓:
                print(f"   🟡 发现隔夜持仓")
                
                行情结果 = 行情获取.获取价格(self.品种)
                if not 行情结果 or not hasattr(行情结果, '价格'):
                    print(f"   ❌ 无法获取价格")
                    return
                
                价格 = 行情结果.价格
                pos = self.引擎.持仓[self.品种]
                
                结果 = self.引擎.卖出(self.品种, 价格, pos.数量)
                if 结果.get("success"):
                    self.今日已买入 = False
                    print(f"   ✅ 已卖出 {self.品种} @ {价格:.2f}")
                else:
                    print(f"   ❌ 卖出失败: {结果.get('error')}")
            else:
                print(f"   ⚪ 无隔夜持仓")
                
        except Exception as e:
            print(f"   ❌ 卖出检查失败: {e}")
    
    def 实时监控(self):
        """实时监控持仓（止损止盈）"""
        if not self.策略:
            return
        
        try:
            for 品种, pos in list(self.引擎.持仓.items()):
                行情结果 = 行情获取.获取价格(品种)
                if not 行情结果 or not hasattr(行情结果, '价格'):
                    continue
                
                k线 = {
                    'close': 行情结果.价格,
                    'volume': getattr(行情结果, '成交量', 0)
                }
                
                信号 = self.策略.处理行情(k线)
                
                if 信号 == 'sell':
                    print(f"   🛑 止损/止盈触发: {品种}")
                    结果 = self.引擎.卖出(品种, 行情结果.价格, self.引擎.持仓[品种].数量)
                    if 结果.get("success"):
                        print(f"   ✅ 已止损/止盈平仓: {品种}")
                    
        except Exception as e:
            pass
    
    def 显示状态(self):
        """显示当前状态"""
        状态 = 获取交易状态()
        print(f"\n📊 [{datetime.now().strftime('%H:%M:%S')}] 交易状态: {状态}")
        print(f"   总资产: ¥{self.引擎.获取总资产():,.0f}")
        print(f"   持仓: {len(self.引擎.持仓)} 个品种")
        if self.引擎.持仓:
            for 品种, pos in self.引擎.持仓.items():
                现价 = getattr(pos, '当前价格', pos.平均成本)
                盈亏 = (现价 - pos.平均成本) * pos.数量
                print(f"     - {品种}: {int(pos.数量)}股, 成本¥{pos.平均成本:.2f}, 盈亏¥{盈亏:+.2f}")
    
    def 运行一次(self):
        """运行一次完整流程（用于手动测试）"""
        print("🚀 手动运行一次自动交易流程")
        print("="*50)
        
        self.初始化策略()
        self.重置每日状态()
        self.尾盘买入检查()
        self.早盘卖出检查()
        self.实时监控()
        self.显示状态()
        print("="*50)
    
    def 运行循环(self):
        """运行自动交易循环"""
        print("🚀 A股隔夜套利策略 - 自动交易机器人启动")
        print("="*50)
        
        self.初始化策略()
        
        # 创建定时任务调度器
        调度器 = 定时任务()
        
        # 添加定时任务
        调度器.添加任务(self.尾盘买入检查, "14:55")
        调度器.添加任务(self.早盘卖出检查, "09:30")
        调度器.添加间隔任务(self.实时监控, 60)   # 每分钟监控一次
        调度器.添加间隔任务(self.显示状态, 300)  # 每5分钟显示一次状态
        
        # 立即显示一次状态
        self.显示状态()
        
        # 启动调度器
        调度器.启动()


if __name__ == "__main__":
    机器人 = 自动交易机器人()
    
    # 判断是否传入参数
    if len(sys.argv) > 1 and sys.argv[1] == "--loop":
        机器人.运行循环()
    else:
        机器人.运行一次()
