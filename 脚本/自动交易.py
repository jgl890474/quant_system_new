# -*- coding: utf-8 -*-
"""
自动交易模块 - 完整版
支持：AI策略信号自动买入卖出、多策略、多市场、止损止盈、飞书推送、定时调度

运行方式:
    python 脚本/自动交易.py                    # 手动运行一次
    python 脚本/自动交易.py --loop             # 循环运行
    python 脚本/自动交易.py --strategy 加密风控策略2 --symbol BTC-USD --loop
"""

import sys
import os
import time
import json
import threading
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional, Any

# 添加项目根目录到路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==================== 导入模块 ====================
try:
    from 核心 import 订单引擎, 策略加载器, AI引擎, 行情获取
    from 工具 import 消息推送, 数据库
    from 工具 import 定时任务 as 定时任务模块
except ImportError as e:
    print(f"⚠️ 模块导入失败: {e}")
    # 创建兼容模块
    class 简单订单引擎:
        def __init__(self, 初始资金=1000000): 
            self.持仓 = {}; self.可用资金 = 初始资金; self.初始资金 = 初始资金
        def 买入(self, *args, **kwargs): return {"success": False, "error": "引擎未初始化"}
        def 卖出(self, *args, **kwargs): return {"success": False, "error": "引擎未初始化"}
        def 获取总资产(self): return self.可用资金
        def 获取可用资金(self): return self.可用资金
    
    订单引擎 = 简单订单引擎
    消息推送 = type('obj', (), {'发送飞书消息': lambda x,y=None: None, '发送交易信号': lambda **k: None, '发送交易执行': lambda **k: None})()
    数据库 = type('obj', (), {'保存交易记录': lambda x: None})()
    行情获取 = type('obj', (), {'获取价格': lambda x: None})()


# ==================== 配置 ====================
默认配置 = {
    "止损比例": 0.05,      # 止损 -5%
    "止盈比例": 0.10,      # 止盈 +10%
    "单笔风险": 0.02,      # 单笔风险2%
    "最大持仓数": 5,       # 最大持仓品种数
    "自动交易开关": False,  # 自动交易总开关
    "检查间隔": 60,        # 检查间隔（秒）
    "AI检查间隔": 300,     # AI信号检查间隔（秒）
}


# ==================== 策略配置模板 ====================
策略配置模板 = {
    "加密货币": [
        {"名称": "加密双均线1", "品种": "BTC-USD", "执行间隔": 60, "资金分配": 0.30},
        {"名称": "加密风控策略", "品种": "BTC-USD", "执行间隔": 60, "资金分配": 0.30},
    ],
    "A股": [
        {"名称": "A股双均线1", "品种": "000001.SS", "执行间隔": 3600, "资金分配": 0.25},
        {"名称": "A股量价策略2", "品种": "000001.SS", "执行间隔": 3600, "资金分配": 0.25},
        {"名称": "A股隔夜套利策略3", "品种": "000001.SS", "执行间隔": 3600, "资金分配": 0.25},
    ],
    "美股": [
        {"名称": "美股简单策略1", "品种": "AAPL", "执行间隔": 1800, "资金分配": 0.25},
        {"名称": "美股动量策略", "品种": "AAPL", "执行间隔": 1800, "资金分配": 0.25},
    ],
}


# ==================== 自动交易机器人 ====================
class 自动交易机器人:
    """自动交易机器人 - 完整版"""
    
    def __init__(self, 初始资金: float = 1000000):
        self.引擎 = 订单引擎(初始资金=初始资金)
        self.策略加载器 = 策略加载器()
        self.AI引擎 = AI引擎()
        self.行情 = 行情获取
        
        # 配置
        self.配置 = 默认配置.copy()
        
        # 状态
        self.运行中 = False
        self.今日已执行 = {}
        self.今日日期 = date.today()
        self.今日交易次数 = 0
        self.今日盈亏 = 0.0
        
        # 策略实例缓存
        self.策略实例 = {}
        self.策略配置列表 = []
        
        # 上次检查时间
        self.上次AI检查时间 = 0
        self.上次止损检查时间 = 0
        
        # 交易记录
        self.交易记录 = []
        
        # 加载策略配置
        self._加载策略配置()
        
        print(f"✅ 自动交易机器人初始化完成")
        print(f"   初始资金: ¥{初始资金:,.0f}")
        print(f"   止损: {self.配置['止损比例']*100:.0f}%")
        print(f"   止盈: {self.配置['止盈比例']*100:.0f}%")
        print(f"   加载策略数量: {len(self.策略配置列表)}")
    
    def _加载策略配置(self):
        """加载策略配置 - 优先从策略加载器获取"""
        self.策略配置列表 = []
        
        # 首先尝试从策略加载器获取实际存在的策略
        实际策略列表 = []
        if hasattr(self.策略加载器, '获取策略'):
            try:
                实际策略列表 = self.策略加载器.获取策略()
                print(f"📊 从策略加载器获取到 {len(实际策略列表)} 个策略")
            except Exception as e:
                print(f"⚠️ 从策略加载器获取策略失败: {e}")
        
        # 使用实际存在的策略构建配置
        if 实际策略列表:
            for s in 实际策略列表:
                策略名称 = s.get("名称", "")
                类别 = s.get("类别", "")
                品种 = s.get("品种", "")
                
                # 判断类别
                if "外汇" in 类别:
                    市场类别 = "外汇"
                elif "加密" in 类别 or "₿" in 类别:
                    市场类别 = "加密货币"
                elif "A股" in 类别 or "📈" in 类别:
                    市场类别 = "A股"
                elif "美股" in 类别 or "🇺🇸" in 类别:
                    市场类别 = "美股"
                else:
                    市场类别 = "其他"
                
                # 获取策略参数（如果有）
                策略参数 = {}
                if hasattr(self.策略加载器, '获取策略参数'):
                    try:
                        策略参数 = self.策略加载器.获取策略参数(策略名称)
                    except:
                        pass
                
                self.策略配置列表.append({
                    "名称": 策略名称,
                    "类别": 市场类别,
                    "启用": True,
                    "品种": [品种],
                    "执行间隔": 60,
                    "资金分配": 0.25,
                    "最大持仓": 3,
                    "参数": 策略参数  # 保存策略参数
                })
            print(f"✅ 从策略加载器构建 {len(self.策略配置列表)} 个策略配置")
            return
        
        # 如果策略加载器没有策略，使用默认配置模板
        print("⚠️ 策略加载器无策略，使用默认配置模板")
        for 市场, 策略列表 in 策略配置模板.items():
            for 策略 in 策略列表:
                self.策略配置列表.append({
                    "名称": 策略["名称"],
                    "类别": 市场,
                    "启用": True,
                    "品种": [策略["品种"]],
                    "执行间隔": 策略.get("执行间隔", 60),
                    "资金分配": 策略.get("资金分配", 0.25),
                    "最大持仓": 3,
                    "参数": {}
                })
        print(f"✅ 使用默认策略配置，共 {len(self.策略配置列表)} 个策略")
    
    def 重置每日状态(self):
        """重置每日状态"""
        today = date.today()
        if today != self.今日日期:
            # 发送昨日报告
            if self.今日交易次数 > 0:
                self._发送每日报告()
            
            self.今日日期 = today
            self.今日已执行 = {}
            self.今日交易次数 = 0
            self.今日盈亏 = 0.0
            print(f"\n📅 进入新的一天 ({today.strftime('%Y-%m-%d')})，重置状态")
    
    def 获取策略实例(self, 策略名称: str, 品种: str):
        """获取或创建策略实例"""
        缓存key = f"{策略名称}_{品种}"
        if 缓存key in self.策略实例:
            return self.策略实例[缓存key]
        
        # 获取策略参数
        策略参数 = {}
        for config in self.策略配置列表:
            if config.get("名称") == 策略名称:
                策略参数 = config.get("参数", {})
                break
        
        try:
            # 从策略库加载策略
            if hasattr(self.策略加载器, '获取策略'):
                策略信息 = self.策略加载器.获取策略(策略名称)
            else:
                策略信息 = None
            
            if 策略信息 and 策略信息.get("类"):
                策略类 = 策略信息["类"]
                策略实例 = 策略类(
                    名称=策略名称,
                    品种=品种,
                    初始资金=self.引擎.初始资金
                )
                # 应用策略参数
                if 策略参数 and hasattr(策略实例, '批量设置参数'):
                    策略实例.批量设置参数(策略参数)
                    print(f"   📊 应用策略参数: {策略名称}")
                
                self.策略实例[缓存key] = 策略实例
                print(f"   ✅ 策略实例化成功: {策略名称} - {品种}")
                return 策略实例
            else:
                # 尝试直接导入策略类
                策略文件映射 = {
                    "加密风控策略": "策略库.加密货币策略.加密风控策略",
                    "加密双均线1": "策略库.加密货币策略.加密双均线1",
                    "A股双均线1": "策略库.A股策略.A股双均线1",
                    "美股简单策略1": "策略库.美股策略.美股简单策略1",
                }
                if 策略名称 in 策略文件映射:
                    try:
                        模块 = __import__(策略文件映射[策略名称], fromlist=[策略名称])
                        策略类 = getattr(模块, 策略名称)
                        策略实例 = 策略类(策略名称, 品种, self.引擎.初始资金)
                        # 应用策略参数
                        if 策略参数 and hasattr(策略实例, '批量设置参数'):
                            策略实例.批量设置参数(策略参数)
                        self.策略实例[缓存key] = 策略实例
                        print(f"   ✅ 直接导入策略成功: {策略名称} - {品种}")
                        return 策略实例
                    except Exception as e2:
                        print(f"   ❌ 直接导入失败: {e2}")
        except Exception as e:
            print(f"   ❌ 策略实例化失败 {策略名称}: {e}")
        
        return None
    
    def 策略信号检查(self):
        """检查所有策略的买入卖出信号"""
        if not self.配置["自动交易开关"]:
            return
        
        for 策略配置 in self.策略配置列表:
            if not 策略配置.get("启用", True):
                continue
            
            策略名称 = 策略配置.get("名称", "")
            品种列表 = 策略配置.get("品种", [])
            策略参数 = 策略配置.get("参数", {})
            
            for 品种 in 品种列表:
                try:
                    # 获取策略实例
                    策略实例 = self.获取策略实例(策略名称, 品种)
                    if not 策略实例:
                        continue
                    
                    # 获取行情
                    行情 = self._获取行情数据(品种)
                    if not 行情:
                        continue
                    
                    # 应用参数到实例（确保参数最新）
                    if 策略参数 and hasattr(策略实例, '批量设置参数'):
                        策略实例.批量设置参数(策略参数)
                    
                    # 调用策略处理行情
                    信号 = 策略实例.处理行情(行情)
                    
                    if 信号 == 'buy':
                        print(f"   🟢 [{策略名称}] 买入信号: {品种}")
                        self._执行AI买入(品种, 策略实例, 行情)
                    
                    elif 信号 == 'sell':
                        print(f"   🔴 [{策略名称}] 卖出信号: {品种}")
                        self._执行AI卖出(品种, 策略实例, 行情)
                    
                except Exception as e:
                    print(f"   ❌ 策略检查失败 {策略名称} {品种}: {e}")
    
    def _获取行情数据(self, 品种):
        """获取行情数据"""
        try:
            价格结果 = self.行情.获取价格(品种)
            if not 价格结果 or not hasattr(价格结果, '价格'):
                return None
            
            return {
                'close': 价格结果.价格,
                'volume': getattr(价格结果, '成交量', 0),
                'high': getattr(价格结果, '最高', 价格结果.价格),
                'low': getattr(价格结果, '最低', 价格结果.价格),
                'open': getattr(价格结果, '开盘', 价格结果.价格),
                'date': datetime.now()
            }
        except Exception as e:
            print(f"获取行情失败 {品种}: {e}")
            return None
    
    def _执行AI买入(self, 品种, 策略实例, 行情):
        """执行AI策略买入"""
        价格 = 行情['close']
        
        # 检查是否已有持仓
        if 品种 in self.引擎.持仓:
            print(f"   ⚪ 已有持仓 {品种}，跳过买入")
            return
        
        # 检查持仓数量上限
        if len(self.引擎.持仓) >= self.配置["最大持仓数"]:
            print(f"   ⚠️ 已达最大持仓数 {self.配置['最大持仓数']}，跳过买入")
            return
        
        # 使用策略的仓位计算
        if hasattr(策略实例, '计算仓位'):
            总资金 = self.引擎.获取总资产()
            数量 = 策略实例.计算仓位(总资金, 价格)
            print(f"   📊 [策略仓位] 总资金={总资金:.0f}, 价格={价格:.2f}, 建议数量={数量:.4f}")
        else:
            # 默认计算（1%资金）
            可用资金 = self.引擎.获取可用资金()
            数量 = 可用资金 * 0.01 / 价格
            print(f"   📊 [默认计算] 可用资金={可用资金:.0f}, 建议数量={数量:.4f}")
        
        if 数量 <= 0:
            print(f"   ❌ 买入数量无效: {数量}")
            return
        
        # 执行买入
        结果 = self.引擎.买入(品种, 价格, 数量, 策略名称=策略实例.名称)
        
        if 结果.get("success"):
            self.今日交易次数 += 1
            print(f"   ✅ AI买入成功: {品种} {数量:.4f} @ {价格:.2f}")
            print(f"   📊 买入金额: {价格 * 数量:.2f}")
            
            # 发送飞书通知
            try:
                消息推送.发送交易执行(品种, 'buy', 数量, 价格, 价格 * 数量)
            except:
                pass
            
            # 记录交易
            self.交易记录.append({
                '时间': datetime.now().isoformat(),
                '品种': 品种,
                '动作': '买入',
                '价格': 价格,
                '数量': 数量,
                '策略': 策略实例.名称,
                '理由': f"{策略实例.名称}策略信号"
            })
        else:
            print(f"   ❌ AI买入失败: {结果.get('error')}")
    
    def _执行AI卖出(self, 品种, 策略实例, 行情):
        """执行AI策略卖出"""
        价格 = 行情['close']
        
        if 品种 not in self.引擎.持仓:
            print(f"   ⚪ 无持仓 {品种}，跳过卖出")
            return
        
        pos = self.引擎.持仓[品种]
        数量 = pos.数量
        
        # 执行卖出
        结果 = self.引擎.卖出(品种, 价格, 数量, 策略名称=策略实例.名称)
        
        if 结果.get("success"):
            # 计算盈亏
            成本 = getattr(pos, '平均成本', 0)
            盈亏 = (价格 - 成本) * 数量
            self.今日盈亏 += 盈亏
            self.今日交易次数 += 1
            
            print(f"   ✅ AI卖出成功: {品种} {数量:.4f} @ {价格:.2f} 盈亏:{盈亏:.2f}")
            
            # 发送飞书通知
            try:
                消息推送.发送交易执行(品种, 'sell', 数量, 价格, 价格 * 数量)
            except:
                pass
            
            # 记录交易
            self.交易记录.append({
                '时间': datetime.now().isoformat(),
                '品种': 品种,
                '动作': '卖出',
                '价格': 价格,
                '数量': 数量,
                '策略': 策略实例.名称,
                '理由': f"{策略实例.名称}策略信号",
                '盈亏': 盈亏
            })
        else:
            print(f"   ❌ AI卖出失败: {结果.get('error')}")
    
    def 止损止盈检查(self):
        """检查所有持仓的止损止盈"""
        if not self.配置["自动交易开关"]:
            return
        
        for 品种, pos in list(self.引擎.持仓.items()):
            try:
                成本 = getattr(pos, '平均成本', 0)
                数量 = getattr(pos, '数量', 0)
                
                if 成本 <= 0 or 数量 <= 0:
                    continue
                
                # 获取实时价格
                行情结果 = self.行情.获取价格(品种)
                if not 行情结果 or not hasattr(行情结果, '价格'):
                    continue
                
                现价 = 行情结果.价格
                盈亏率 = (现价 - 成本) / 成本
                
                # 止损检查
                if 盈亏率 <= -self.配置["止损比例"]:
                    亏损金额 = (成本 - 现价) * 数量
                    print(f"   🛑 止损触发: {品种} 亏损{亏损金额:.2f}")
                    self._执行风控卖出(品种, 数量, 现价, f"止损触发 (亏损{盈亏率*100:.1f}%)")
                    self._发送止损通知(品种, 现价, 亏损金额)
                
                # 止盈检查
                elif 盈亏率 >= self.配置["止盈比例"]:
                    盈利金额 = (现价 - 成本) * 数量
                    print(f"   🎯 止盈触发: {品种} 盈利{盈利金额:.2f}")
                    self._执行风控卖出(品种, 数量, 现价, f"止盈触发 (盈利{盈亏率*100:.1f}%)")
                    self._发送止盈通知(品种, 现价, 盈利金额, 0)
                        
            except Exception as e:
                print(f"   止损止盈检查失败 {品种}: {e}")
    
    def _执行风控卖出(self, 品种, 数量, 价格, 理由):
        """执行风控卖出"""
        try:
            结果 = self.引擎.卖出(品种, 价格, 数量, 策略名称="风控")
            
            if 结果.get("success"):
                # 计算盈亏
                if 品种 in self.引擎.持仓:
                    pos = self.引擎.持仓[品种]
                    成本 = getattr(pos, '平均成本', 0)
                    盈亏 = (价格 - 成本) * 数量
                    self.今日盈亏 += 盈亏
                
                self.今日交易次数 += 1
                print(f"   ✅ 风控卖出成功: {品种} {数量:.4f} @ {价格:.2f}")
                
                self.交易记录.append({
                    '时间': datetime.now().isoformat(),
                    '品种': 品种,
                    '动作': '卖出',
                    '价格': 价格,
                    '数量': 数量,
                    '策略': '风控',
                    '理由': 理由,
                    '盈亏': 盈亏
                })
            else:
                print(f"   ❌ 风控卖出失败: {结果.get('error')}")
        except Exception as e:
            print(f"   ❌ 风控卖出异常: {e}")
    
    def _发送止损通知(self, 品种, 价格, 亏损金额):
        """发送止损通知"""
        try:
            消息推送.发送止损通知(品种, 价格, 价格, 亏损金额)
        except:
            print(f"   📢 止损: {品种} @ {价格:.2f} 亏损{亏损金额:.2f}")
    
    def _发送止盈通知(self, 品种, 价格, 盈利金额, 剩余数量):
        """发送止盈通知"""
        try:
            消息推送.发送止盈通知(品种, 价格, 价格, 盈利金额, 剩余数量)
        except:
            print(f"   📢 止盈: {品种} @ {价格:.2f} 盈利{盈利金额:.2f}")
    
    def _发送每日报告(self):
        """发送每日报告"""
        try:
            总资产 = self.引擎.获取总资产() if hasattr(self.引擎, '获取总资产') else 1000000
            消息推送.发送每日报告(
                总资产=总资产,
                今日盈亏=self.今日盈亏,
                今日交易次数=self.今日交易次数,
                持仓数量=len(self.引擎.持仓)
            )
        except:
            print(f"\n📊 每日报告: 交易{self.今日交易次数}次, 盈亏{self.今日盈亏:+.2f}")
    
    def 显示状态(self):
        """显示当前状态"""
        交易状态 = self._获取交易状态()
        总资产 = self.引擎.获取总资产() if hasattr(self.引擎, '获取总资产') else 0
        可用资金 = self.引擎.获取可用资金() if hasattr(self.引擎, '获取可用资金') else 0
        
        print(f"\n📊 [{datetime.now().strftime('%H:%M:%S')}] 交易状态")
        print(f"   {'='*40}")
        print(f"   市场状态: {交易状态}")
        print(f"   自动交易: {'🟢开启' if self.配置['自动交易开关'] else '🔴关闭'}")
        print(f"   总资产: ¥{总资产:,.0f}")
        print(f"   可用资金: ¥{可用资金:,.0f}")
        print(f"   持仓数量: {len(self.引擎.持仓)} 个")
        print(f"   今日交易: {self.今日交易次数} 次")
        print(f"   今日盈亏: ¥{self.今日盈亏:+,.2f}")
        
        if self.引擎.持仓:
            print(f"\n   📦 持仓明细:")
            for 品种, pos in self.引擎.持仓.items():
                成本 = getattr(pos, '平均成本', 0)
                数量 = getattr(pos, '数量', 0)
                现价 = getattr(pos, '当前价格', 成本)
                盈亏 = (现价 - 成本) * 数量
                盈亏率 = (盈亏 / (成本 * 数量)) * 100 if 成本 > 0 and 数量 > 0 else 0
                print(f"     - {品种}: {数量:.4f}个, 成本¥{成本:.2f}, 盈亏¥{盈亏:+.2f} ({盈亏率:+.1f}%)")
        
        print(f"   {'='*40}")
    
    def _获取交易状态(self) -> str:
        """获取交易状态"""
        now = datetime.now()
        if now.weekday() >= 5:
            return "非交易日"
        
        now_str = now.strftime("%H:%M")
        if now_str < "09:30":
            return "未开盘"
        elif now_str <= "11:30":
            return "上午交易中"
        elif now_str < "13:00":
            return "午间休市"
        elif now_str <= "15:00":
            return "下午交易中"
        else:
            return "已收盘"
    
    def 设置自动交易(self, 开启: bool):
        """设置自动交易开关"""
        self.配置["自动交易开关"] = 开启
        status = "开启" if 开启 else "关闭"
        print(f"🎛️ 自动交易已{status}")
        
        try:
            消息推送.发送飞书消息(f"自动交易已{status}", "info")
        except:
            pass
    
    def 更新配置(self, 新配置: dict):
        """更新配置"""
        self.配置.update(新配置)
        print(f"⚙️ 配置已更新: {self.配置}")
    
    def 保存交易记录(self):
        """保存交易记录到数据库"""
        try:
            for 记录 in self.交易记录:
                数据库.保存交易记录(记录)
            print(f"💾 已保存 {len(self.交易记录)} 条交易记录")
        except Exception as e:
            print(f"保存交易记录失败: {e}")
    
    def 运行一次(self):
        """运行一次完整流程（用于手动测试）"""
        print("\n" + "="*50)
        print("🚀 手动运行自动交易流程")
        print("="*50)
        
        self.重置每日状态()
        
        # 执行一次策略检查
        self.策略信号检查()
        
        # 执行一次止损止盈检查
        self.止损止盈检查()
        
        self.显示状态()
        
        print("="*50)
    
    def 运行循环(self):
        """运行自动交易循环"""
        print("\n" + "="*50)
        print("🚀 自动交易机器人启动")
        print("="*50)
        print(f"   止损: {self.配置['止损比例']*100:.0f}%")
        print(f"   止盈: {self.配置['止盈比例']*100:.0f}%")
        print(f"   策略检查间隔: {self.配置['检查间隔']}秒")
        print(f"   加载策略数量: {len(self.策略配置列表)}")
        print("="*50)
        
        self.运行中 = True
        
        try:
            while self.运行中:
                # 1. 重置每日状态
                self.重置每日状态()
                
                # 2. 策略信号检查（AI自动买入卖出）
                self.策略信号检查()
                
                # 3. 止损止盈检查
                self.止损止盈检查()
                
                # 4. 显示状态
                self.显示状态()
                
                # 等待下次检查
                time.sleep(self.配置["检查间隔"])
                
        except KeyboardInterrupt:
            print("\n👋 收到中断信号")
        finally:
            self.运行中 = False
            self.保存交易记录()
            print("🛑 自动交易机器人已停止")
    
    def 获取状态(self) -> dict:
        """获取机器人状态"""
        return {
            "运行中": self.运行中,
            "自动交易开关": self.配置["自动交易开关"],
            "今日交易次数": self.今日交易次数,
            "今日盈亏": self.今日盈亏,
            "持仓数量": len(self.引擎.持仓),
            "策略数量": len(self.策略配置列表)
        }
    
    def 设置引擎(self, 引擎):
        """设置订单引擎"""
        self.引擎 = 引擎


# ==================== 便捷函数 ====================
_机器人实例 = None

def 获取机器人() -> 自动交易机器人:
    """获取全局机器人实例"""
    global _机器人实例
    if _机器人实例 is None:
        _机器人实例 = 自动交易机器人()
    return _机器人实例


def 启动自动交易():
    """启动自动交易"""
    机器人 = 获取机器人()
    机器人.设置自动交易(True)
    机器人.运行循环()


def 停止自动交易():
    """停止自动交易"""
    机器人 = 获取机器人()
    机器人.运行中 = False


# ==================== 命令行入口 ====================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='自动交易机器人')
    parser.add_argument('--loop', action='store_true', help='循环运行')
    parser.add_argument('--strategy', type=str, default=None, help='策略名称')
    parser.add_argument('--symbol', type=str, default=None, help='品种代码')
    parser.add_argument('--stop-loss', type=float, default=0.05, help='止损比例')
    parser.add_argument('--take-profit', type=float, default=0.10, help='止盈比例')
    
    args = parser.parse_args()
    
    机器人 = 获取机器人()
    
    # 更新配置
    if args.stop_loss:
        机器人.更新配置({"止损比例": args.stop_loss})
    if args.take_profit:
        机器人.更新配置({"止盈比例": args.take_profit})
    
    # 如果指定了策略，添加自定义策略配置
    if args.strategy and args.symbol:
        机器人.策略配置列表 = [{
            "名称": args.strategy,
            "类别": "自定义",
            "启用": True,
            "品种": [args.symbol],
            "执行间隔": 60,
            "资金分配": 0.30,
            "最大持仓": 1,
            "参数": {}
        }]
        print(f"✅ 使用自定义策略: {args.strategy} - {args.symbol}")
    
    if args.loop:
        机器人.设置自动交易(True)
        机器人.运行循环()
    else:
        机器人.运行一次()
