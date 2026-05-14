# -*- coding: utf-8 -*-
"""
自动交易模块 - 完整版
支持：多策略、多市场、止损止盈、飞书推送、定时调度

运行方式:
    python 脚本/自动交易.py                    # 手动运行一次
    python 脚本/自动交易.py --loop             # 循环运行
    python 脚本/自动交易.py --strategy 双均线   # 指定策略
"""

import sys
import os
import time
import json
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
        def __init__(self): self.持仓 = {}; self.可用资金 = 1000000
        def 买入(self, *args): return {"success": False}
        def 卖出(self, *args): return {"success": False}
        def 获取总资产(self): return 1000000
    
    订单引擎 = 简单订单引擎
    消息推送 = type('obj', (), {'发送飞书消息': lambda x,y=None: None, '发送交易信号': lambda **k: None})()
    数据库 = type('obj', (), {'保存交易记录': lambda x: None})()


# ==================== 配置 ====================
默认配置 = {
    "止损比例": 0.05,      # 止损 -5%
    "止盈比例": 0.10,      # 止盈 +10%
    "单笔风险": 0.02,      # 单笔风险2%
    "最大持仓数": 5,       # 最大持仓品种数
    "自动交易开关": False,  # 自动交易总开关
    "检查间隔": 60,        # 检查间隔（秒）
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
        self.今日已执行 = {}  # 记录今日已执行的策略
        self.今日日期 = date.today()
        self.今日交易次数 = 0
        self.今日盈亏 = 0.0
        
        # 策略实例缓存
        self.策略实例 = {}
        
        # 交易记录
        self.交易记录 = []
        
        print(f"✅ 自动交易机器人初始化完成")
        print(f"   初始资金: ¥{初始资金:,.0f}")
        print(f"   止损: {self.配置['止损比例']*100:.0f}%")
        print(f"   止盈: {self.配置['止盈比例']*100:.0f}%")
    
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
    
    def 获取策略(self, 策略名称: str, 品种: str):
        """获取或创建策略实例"""
        缓存key = f"{策略名称}_{品种}"
        if 缓存key in self.策略实例:
            return self.策略实例[缓存key]
        
        try:
            # 从策略库加载策略
            策略信息 = self.策略加载器.获取策略(策略名称)
            if 策略信息 and 策略信息.get("类"):
                策略实例 = 策略信息["类"](
                    名称=策略名称,
                    品种=品种,
                    初始资金=self.引擎.初始资金
                )
                self.策略实例[缓存key] = 策略实例
                print(f"   ✅ 策略实例化成功: {策略名称}")
                return 策略实例
        except Exception as e:
            print(f"   ❌ 策略实例化失败: {e}")
        
        return None
    
    def 尾盘买入检查(self, 策略配置: Dict = None):
        """
        尾盘买入检查
        
        参数:
            策略配置: {
                '策略名称': 'A股隔夜套利',
                '品种': '000001.SS',
                '买入时间': '14:55',
                '最小涨幅': 0.01,
                '最大涨幅': 0.05
            }
        """
        self.重置每日状态()
        
        if not self.配置["自动交易开关"]:
            return
        
        # 默认配置
        if 策略配置 is None:
            策略配置 = {
                '策略名称': 'A股隔夜套利',
                '品种': '000001.SS',
                '买入时间': '14:55'
            }
        
        策略名称 = 策略配置.get('策略名称', 'A股隔夜套利')
        品种 = 策略配置.get('品种', '000001.SS')
        买入时间 = 策略配置.get('买入时间', '14:55')
        
        # 检查是否已执行
        执行key = f"尾盘买入_{策略名称}_{品种}"
        if 执行key in self.今日已执行:
            return
        
        # 检查时间
        now = datetime.now()
        now_str = now.strftime("%H:%M")
        if now_str != 买入时间:
            return
        
        # 检查是否持仓
        if 品种 in self.引擎.持仓:
            print(f"   ⚪ 已有持仓 {品种}，跳过买入")
            return
        
        # 检查持仓数量
        if len(self.引擎.持仓) >= self.配置["最大持仓数"]:
            print(f"   ⚠️ 已达最大持仓数 {self.配置['最大持仓数']}，跳过买入")
            return
        
        print(f"\n📊 [{now.strftime('%H:%M:%S')}] 尾盘买入检查 - {策略名称}")
        
        try:
            # 获取行情
            行情结果 = self.行情.获取价格(品种)
            if not 行情结果 or not hasattr(行情结果, '价格'):
                print(f"   ❌ 无法获取 {品种} 行情")
                return
            
            价格 = 行情结果.价格
            
            # 获取策略信号
            策略实例 = self.获取策略(策略名称, 品种)
            if 策略实例:
                # 准备K线数据
                k线数据 = {
                    'close': 价格,
                    'volume': getattr(行情结果, '成交量', 0),
                    'high': getattr(行情结果, '最高', 价格),
                    'low': getattr(行情结果, '最低', 价格),
                    'open': getattr(行情结果, '开盘', 价格),
                    'date': now
                }
                
                信号 = 策略实例.处理行情(k线数据)
                
                if 信号 == 'buy':
                    print(f"   🟢 触发买入信号")
                    self._执行买入(品种, 价格, 策略名称)
                    self.今日已执行[执行key] = True
                else:
                    print(f"   ⚪ 无买入信号 (信号: {信号})")
            else:
                # 无策略实例，使用简单判断
                print(f"   ⚪ 策略实例不存在，跳过")
                
        except Exception as e:
            print(f"   ❌ 买入检查失败: {e}")
    
    def 早盘卖出检查(self, 策略配置: Dict = None):
        """
        早盘卖出检查（隔夜平仓）
        
        参数:
            策略配置: {
                '策略名称': 'A股隔夜套利',
                '品种': '000001.SS',
                '卖出时间': '09:30'
            }
        """
        self.重置每日状态()
        
        if not self.配置["自动交易开关"]:
            return
        
        if 策略配置 is None:
            策略配置 = {
                '策略名称': 'A股隔夜套利',
                '品种': '000001.SS',
                '卖出时间': '09:30'
            }
        
        策略名称 = 策略配置.get('策略名称', 'A股隔夜套利')
        品种 = 策略配置.get('品种', '000001.SS')
        卖出时间 = 策略配置.get('卖出时间', '09:30')
        
        # 检查时间
        now = datetime.now()
        now_str = now.strftime("%H:%M")
        if now_str != 卖出时间:
            return
        
        # 检查是否持仓
        if 品种 not in self.引擎.持仓:
            print(f"   ⚪ 无持仓 {品种}，跳过卖出")
            return
        
        print(f"\n💰 [{now.strftime('%H:%M:%S')}] 早盘卖出检查 - {策略名称}")
        
        try:
            行情结果 = self.行情.获取价格(品种)
            if not 行情结果 or not hasattr(行情结果, '价格'):
                print(f"   ❌ 无法获取 {品种} 价格")
                return
            
            价格 = 行情结果.价格
            pos = self.引擎.持仓[品种]
            
            self._执行卖出(品种, pos.数量, 价格, f"{策略名称}隔夜平仓")
            
        except Exception as e:
            print(f"   ❌ 卖出检查失败: {e}")
    
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
                    self._执行卖出(品种, 数量, 现价, f"止损触发 (亏损{盈亏率*100:.1f}%)")
                    self._发送止损通知(品种, 现价, 亏损金额)
                
                # 止盈检查
                elif 盈亏率 >= self.配置["止盈比例"]:
                    盈利金额 = (现价 - 成本) * 数量
                    # 部分止盈：卖出50%
                    卖出数量 = 数量 * 0.5
                    if 卖出数量 > 0:
                        print(f"   🎯 部分止盈: {品种} 盈利{盈利金额:.2f}")
                        self._执行卖出(品种, 卖出数量, 现价, f"部分止盈 (盈利{盈亏率*100:.1f}%)")
                        self._发送止盈通知(品种, 现价, 盈利金额, 数量 - 卖出数量)
                        
            except Exception as e:
                print(f"   止损止盈检查失败 {品种}: {e}")
    
    def AI信号检查(self, 市场: str = "A股", 策略类型: str = "量价策略"):
        """
        AI信号检查 - 根据AI推荐执行交易
        
        参数:
            市场: A股/美股/加密货币
            策略类型: 策略类型
        """
        if not self.配置["自动交易开关"]:
            return
        
        print(f"\n🤖 [{datetime.now().strftime('%H:%M:%S')}] AI信号检查")
        
        try:
            # 获取AI推荐
            ai结果 = self.AI引擎.AI推荐(市场, 策略类型, use_real_ai=False)
            
            if not ai结果 or not ai结果.get("推荐"):
                print(f"   ⚪ 无AI推荐")
                return
            
            for 推荐 in ai结果["推荐"][:3]:  # 最多处理3个推荐
                品种 = 推荐.get("代码")
                得分 = 推荐.get("得分", 0)
                理由 = 推荐.get("理由", "")
                
                if 得分 < 60:
                    continue
                
                # 检查是否已持仓
                if 品种 in self.引擎.持仓:
                    continue
                
                # 检查持仓数量
                if len(self.引擎.持仓) >= self.配置["最大持仓数"]:
                    break
                
                # 获取价格
                行情结果 = self.行情.获取价格(品种)
                if not 行情结果 or not hasattr(行情结果, '价格'):
                    continue
                
                价格 = 行情结果.价格
                
                # 执行买入
                print(f"   🟢 AI推荐买入: {品种} (得分{得分})")
                self._执行买入(品种, 价格, f"AI推荐_{策略类型}", 理由)
                
        except Exception as e:
            print(f"   ❌ AI信号检查失败: {e}")
    
    def _执行买入(self, 品种: str, 价格: float, 策略名称: str, 理由: str = ""):
        """执行买入操作"""
        try:
            # 计算买入数量
            可用资金 = self.引擎.获取可用资金() if hasattr(self.引擎, '获取可用资金') else self.引擎.可用资金
            买入金额 = 可用资金 * self.配置["单笔风险"]
            数量 = 买入金额 / 价格
            
            if 数量 <= 0:
                print(f"   ❌ 买入数量无效: {数量}")
                return
            
            # 执行买入
            if hasattr(self.引擎, '买入'):
                结果 = self.引擎.买入(品种, 价格, 数量)
                
                if 结果.get("success"):
                    self.今日交易次数 += 1
                    print(f"   ✅ 买入成功: {品种} {数量:.4f} @ {价格:.2f}")
                    
                    # 发送飞书通知
                    try:
                        消息推送.发送交易执行(品种, 'buy', 数量, 价格, 买入金额)
                    except:
                        pass
                    
                    # 记录交易
                    self.交易记录.append({
                        '时间': datetime.now().isoformat(),
                        '品种': 品种,
                        '动作': '买入',
                        '价格': 价格,
                        '数量': 数量,
                        '策略': 策略名称,
                        '理由': 理由
                    })
                else:
                    print(f"   ❌ 买入失败: {结果.get('error')}")
            else:
                print(f"   ❌ 引擎无买入方法")
                
        except Exception as e:
            print(f"   ❌ 买入执行异常: {e}")
    
    def _执行卖出(self, 品种: str, 数量: float, 价格: float, 理由: str = ""):
        """执行卖出操作"""
        try:
            if hasattr(self.引擎, '卖出'):
                结果 = self.引擎.卖出(品种, 价格, 数量)
                
                if 结果.get("success"):
                    # 计算盈亏
                    if 品种 in self.引擎.持仓:
                        pos = self.引擎.持仓[品种]
                        成本 = getattr(pos, '平均成本', 0)
                        盈亏 = (价格 - 成本) * 数量
                        self.今日盈亏 += 盈亏
                    
                    self.今日交易次数 += 1
                    print(f"   ✅ 卖出成功: {品种} {数量:.4f} @ {价格:.2f}")
                    
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
                        '理由': 理由,
                        '盈亏': 盈亏
                    })
                else:
                    print(f"   ❌ 卖出失败: {结果.get('error')}")
            else:
                print(f"   ❌ 引擎无卖出方法")
                
        except Exception as e:
            print(f"   ❌ 卖出执行异常: {e}")
    
    def _发送止损通知(self, 品种: str, 价格: float, 亏损金额: float):
        """发送止损通知"""
        try:
            消息推送.发送止损通知(品种, 价格 * 0.95, 价格, 亏损金额)
        except:
            print(f"   📢 止损: {品种} @ {价格:.2f} 亏损{亏损金额:.2f}")
    
    def _发送止盈通知(self, 品种: str, 价格: float, 盈利金额: float, 剩余数量: float):
        """发送止盈通知"""
        try:
            消息推送.发送止盈通知(品种, 价格 * 0.95, 价格, 盈利金额, 剩余数量)
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
                print(f"     - {品种}: {数量:.4f}股, 成本¥{成本:.2f}, 盈亏¥{盈亏:+.2f} ({盈亏率:+.1f}%)")
        
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
    
    def 运行一次(self, 策略配置: Dict = None):
        """运行一次完整流程（用于手动测试）"""
        print("\n" + "="*50)
        print("🚀 手动运行自动交易流程")
        print("="*50)
        
        self.重置每日状态()
        
        if 策略配置:
            self.尾盘买入检查(策略配置)
            self.早盘卖出检查(策略配置)
        else:
            # 默认策略：A股隔夜套利
            self.尾盘买入检查({
                '策略名称': 'A股隔夜套利',
                '品种': '000001.SS',
                '买入时间': self._获取当前时间窗口()
            })
        
        self.止损止盈检查()
        self.显示状态()
        
        print("="*50)
    
    def _获取当前时间窗口(self) -> str:
        """获取当前时间窗口"""
        now = datetime.now()
        if now.hour == 14 and now.minute >= 55:
            return now.strftime("%H:%M")
        return "14:55"
    
    def 运行循环(self, 策略配置列表: List[Dict] = None):
        """
        运行自动交易循环
        
        参数:
            策略配置列表: 多个策略配置
        """
        print("\n" + "="*50)
        print("🚀 自动交易机器人启动")
        print("="*50)
        print(f"   止损: {self.配置['止损比例']*100:.0f}%")
        print(f"   止盈: {self.配置['止盈比例']*100:.0f}%")
        print(f"   检查间隔: {self.配置['检查间隔']}秒")
        print("="*50)
        
        self.运行中 = True
        
        if 策略配置列表 is None:
            策略配置列表 = [
                {
                    '策略名称': 'A股隔夜套利',
                    '品种': '000001.SS',
                    '买入时间': '14:55',
                    '卖出时间': '09:30'
                }
            ]
        
        try:
            while self.运行中:
                # 1. 重置每日状态
                self.重置每日状态()
                
                # 2. 执行各策略的尾盘买入检查
                for 策略配置 in 策略配置列表:
                    self.尾盘买入检查(策略配置)
                
                # 3. 执行各策略的早盘卖出检查
                for 策略配置 in 策略配置列表:
                    self.早盘卖出检查(策略配置)
                
                # 4. 止损止盈检查
                self.止损止盈检查()
                
                # 5. 显示状态
                self.显示状态()
                
                # 等待下次检查
                time.sleep(self.配置["检查间隔"])
                
        except KeyboardInterrupt:
            print("\n👋 收到中断信号")
        finally:
            self.运行中 = False
            self.保存交易记录()
            print("🛑 自动交易机器人已停止")


# ==================== 便捷函数 ====================
_机器人实例 = None

def 获取机器人() -> 自动交易机器人:
    """获取全局机器人实例"""
    global _机器人实例
    if _机器人实例 is None:
        _机器人实例 = 自动交易机器人()
    return _机器人实例


def 启动自动交易(策略配置列表: List[Dict] = None):
    """启动自动交易"""
    机器人 = 获取机器人()
    机器人.设置自动交易(True)
    机器人.运行循环(策略配置列表)


def 停止自动交易():
    """停止自动交易"""
    机器人 = 获取机器人()
    机器人.运行中 = False


# ==================== 命令行入口 ====================
if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description='自动交易机器人')
    parser.add_argument('--loop', action='store_true', help='循环运行')
    parser.add_argument('--strategy', type=str, default='A股隔夜套利', help='策略名称')
    parser.add_argument('--symbol', type=str, default='000001.SS', help='品种代码')
    parser.add_argument('--stop-loss', type=float, default=0.05, help='止损比例')
    parser.add_argument('--take-profit', type=float, default=0.10, help='止盈比例')
    
    args = parser.parse_args()
    
    机器人 = 获取机器人()
    
    # 更新配置
    if args.stop_loss:
        机器人.更新配置({"止损比例": args.stop_loss})
    if args.take_profit:
        机器人.更新配置({"止盈比例": args.take_profit})
    
    if args.loop:
        # 循环运行
        策略配置 = {
            '策略名称': args.strategy,
            '品种': args.symbol,
            '买入时间': '14:55',
            '卖出时间': '09:30'
        }
        机器人.设置自动交易(True)
        机器人.运行循环([策略配置])
    else:
        # 手动运行一次
        策略配置 = {
            '策略名称': args.strategy,
            '品种': args.symbol,
            '买入时间': '14:55'
        }
        机器人.运行一次(策略配置)
