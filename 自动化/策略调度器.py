# -*- coding: utf-8 -*-
"""
通用策略调度器 - 自动执行所有启用的策略
"""

import json
import time
import threading
from datetime import datetime
from pathlib import Path
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from 核心.策略发现器 import 获取策略发现器
from 核心 import 行情获取


class 通用策略执行器:
    """通用策略执行器 - 调度所有策略"""
    
    def __init__(self, 引擎):
        self.引擎 = 引擎
        self.运行中 = False
        self.策略实例 = {}
        self.策略配置 = []
        self.线程 = None
        
        # 加载配置
        self._加载配置()
        
        # 加载策略类
        self._加载策略类()
    
    def _加载配置(self):
        """加载策略调度配置"""
        配置文件 = Path(__file__).parent.parent / "配置" / "策略调度配置.json"
        
        if 配置文件.exists():
            try:
                with open(配置文件, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.策略配置 = data.get("策略调度", [])
                    print(f"✅ 已加载 {len(self.策略配置)} 个策略配置")
            except Exception as e:
                print(f"⚠️ 读取配置文件失败: {e}")
                self.策略配置 = []
        else:
            print(f"⚠️ 配置文件不存在: {配置文件}")
            self.策略配置 = []
    
    def _加载策略类(self):
        """加载策略类"""
        发现器 = 获取策略发现器()
        
        if not 发现器 or len(发现器.策略列表) == 0:
            print("⚠️ 未发现任何策略，请检查策略库目录")
            return
        
        for 配置 in self.策略配置:
            if not 配置.get("启用", False):
                continue
            
            策略名称 = 配置.get("名称", "")
            if not 策略名称:
                continue
            
            策略信息 = 发现器.获取策略(名称=策略名称)
            
            if 策略信息:
                # 为每个品种创建策略实例
                for 品种 in 配置.get("品种", []):
                    try:
                        实例 = 策略信息["类"](
                            名称=f"{策略名称}_{品种}",
                            品种=品种,
                            初始资金=self.引擎.初始资金
                        )
                        
                        # 覆盖策略参数（从配置）
                        if "参数" in 配置:
                            for key, value in 配置["参数"].items():
                                if hasattr(实例, key):
                                    setattr(实例, key, value)
                        
                        实例.执行间隔 = 配置.get("执行间隔", 60)
                        实例.最大持仓 = 配置.get("最大持仓", 3)
                        实例.资金分配 = 配置.get("资金分配", 0.1)
                        
                        self.策略实例[f"{策略名称}_{品种}"] = {
                            "实例": 实例,
                            "配置": 配置,
                            "品种": 品种,
                            "最后执行": 0
                        }
                        
                        print(f"✅ 策略已加载: {策略名称} - {品种}")
                    except Exception as e:
                        print(f"❌ 策略加载失败 {策略名称} - {品种}: {e}")
            else:
                print(f"⚠️ 策略不存在: {策略名称}")
        
        print(f"📊 共加载 {len(self.策略实例)} 个策略实例")
    
    def 启动(self):
        """启动调度器"""
        if self.运行中:
            print("⚠️ 调度器已在运行中")
            return
        
        if len(self.策略实例) == 0:
            print("⚠️ 没有启用的策略实例，调度器无法启动")
            print("   请检查: 1) 配置文件 2) 策略是否存在 3) 策略是否启用")
            return
        
        self.运行中 = True
        self.线程 = threading.Thread(target=self._运行循环, daemon=True)
        self.线程.start()
        print(f"🚀 通用策略调度器已启动，共 {len(self.策略实例)} 个策略实例")
    
    def 停止(self):
        """停止调度器"""
        self.运行中 = False
        print(f"🛑 通用策略调度器已停止")
    
    def 获取状态(self):
        """获取调度器状态"""
        return {
            "运行中": self.运行中,
            "策略数量": len(self.策略实例),
            "策略列表": list(self.策略实例.keys())
        }
    
    def _运行循环(self):
        """主循环"""
        print("🔄 策略调度循环已启动")
        while self.运行中:
            try:
                self._检查所有策略()
            except Exception as e:
                print(f"❌ 策略调度错误: {e}")
            
            time.sleep(5)  # 每5秒检查一次
    
    def _检查所有策略(self):
        """检查所有策略"""
        当前时间 = time.time()
        
        for key, item in self.策略实例.items():
            try:
                策略 = item["实例"]
                配置 = item["配置"]
                品种 = item["品种"]
                最后执行 = item["最后执行"]
                
                # 检查执行间隔
                if 当前时间 - 最后执行 < getattr(策略, '执行间隔', 60):
                    continue
                
                # 更新最后执行时间
                item["最后执行"] = 当前时间
                
                # 执行策略
                self._执行策略(策略, 配置, 品种)
                
            except Exception as e:
                print(f"❌ 检查策略失败 {key}: {e}")
    
    def _执行策略(self, 策略, 配置, 品种):
        """执行单个策略"""
        try:
            # 获取行情
            行情 = self._获取行情(品种)
            if not 行情:
                return
            
            # 推送行情给策略
            信号 = 策略.处理行情(行情)
            
            # 处理信号
            if 信号 == 'buy':
                self._处理买入信号(策略, 配置, 品种, 行情)
            elif 信号 == 'sell':
                self._处理卖出信号(策略, 配置, 品种, 行情)
            
        except Exception as e:
            print(f"❌ 策略执行失败 {品种}: {e}")
    
    def _获取行情(self, 品种):
        """获取行情数据"""
        try:
            价格结果 = 行情获取.获取价格(品种)
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
    
    def _处理买入信号(self, 策略, 配置, 品种, 行情):
        """处理买入信号"""
        当前价格 = 行情['close']
        
        # 检查是否已有持仓
        if 品种 in self.引擎.持仓:
            return
        
        # 检查持仓数量上限
        if len(self.引擎.持仓) >= getattr(策略, '最大持仓', 3):
            return
        
        # 计算买入数量
        if hasattr(策略, '计算仓位'):
            总资金 = self.引擎.获取总资产() if hasattr(self.引擎, '获取总资产') else self.引擎.初始资金
            数量 = 策略.计算仓位(总资金, 当前价格)
        else:
            # 默认计算
            可用资金 = self.引擎.获取可用资金() if hasattr(self.引擎, '获取可用资金') else self.引擎.可用资金
            买入金额 = 可用资金 * getattr(策略, '资金分配', 0.1)
            数量 = 买入金额 / 当前价格
        
        if 数量 <= 0:
            print(f"   ⚠️ 买入数量无效: {数量}")
            return
        
        # 执行买入，传入策略名称
        结果 = self.引擎.买入(品种, 当前价格, 数量, 策略名称=配置["名称"])
        
        if 结果.get("success"):
            print(f"✅ [{配置['名称']}] 买入 {品种} {数量:.4f} @ {当前价格:.2f}")
            
            # 更新策略状态
            if hasattr(策略, '持仓'):
                策略.持仓 = 1
            if hasattr(策略, '入场价'):
                策略.入场价 = 当前价格
            if hasattr(策略, '入场时间'):
                策略.入场时间 = datetime.now()
        else:
            print(f"   ❌ 买入失败: {结果.get('error')}")
    
    def _处理卖出信号(self, 策略, 配置, 品种, 行情):
        """处理卖出信号（策略主动卖出）"""
        当前价格 = 行情['close']
        
        if 品种 not in self.引擎.持仓:
            return
        
        pos = self.引擎.持仓[品种]
        数量 = pos.数量
        
        # 执行卖出，传入策略名称
        结果 = self.引擎.卖出(品种, 当前价格, 数量, 策略名称=配置["名称"])
        
        if 结果.get("success"):
            # 计算盈亏
            成本 = getattr(pos, '平均成本', 0)
            盈亏 = (当前价格 - 成本) * 数量
            
            print(f"✅ [{配置['名称']}] 卖出 {品种} {数量:.4f} @ {当前价格:.2f} 盈亏:{盈亏:.2f}")
            
            # 更新策略状态
            if hasattr(策略, '持仓'):
                策略.持仓 = 0
            if hasattr(策略, '入场价'):
                策略.入场价 = 0
            if hasattr(策略, '持仓最高盈利'):
                策略.持仓最高盈利 = 0
        else:
            print(f"   ❌ 卖出失败: {结果.get('error')}")


# 全局实例
_调度器 = None

def 获取策略调度器(引擎=None):
    """获取全局策略调度器实例"""
    global _调度器
    if _调度器 is None and 引擎:
        _调度器 = 通用策略执行器(引擎)
    return _调度器


def 启动策略调度器(引擎):
    """便捷函数：启动策略调度器"""
    调度器 = 获取策略调度器(引擎)
    if 调度器:
        调度器.启动()
    return 调度器
