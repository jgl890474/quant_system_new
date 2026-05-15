# -*- coding: utf-8 -*-
"""
策略加载器 - 简化版，不依赖策略基类
"""
import os
from pathlib import Path


class 策略加载器:
    def __init__(self):
        self.策略列表 = []
        self._加载策略()
    
    def _加载策略(self):
        """加载策略 - 直接扫描文件，不导入类"""
        策略库路径 = Path(__file__).parent.parent / "策略库"
        
        # 策略类别映射
        类别映射 = {
            "外汇策略": "💰 外汇",
            "加密货币策略": "₿ 加密货币",
            "A股策略": "📈 A股",
            "美股策略": "🇺🇸 美股",
        }
        
        # 品种映射
        品种映射 = {
            "外汇策略": "EURUSD",
            "加密货币策略": "BTC-USD",
            "A股策略": "000001.SS",
            "美股策略": "AAPL",
        }
        
        if not 策略库路径.exists():
            print(f"策略库目录不存在: {策略库路径}")
            self._使用默认策略()
            return
        
        for 子目录 in 策略库_path.iterdir():
            if not 子目录.is_dir():
                continue
            
            类别名称 = 子目录.name
            显示类别 = 类别映射.get(类别名称, 类别名称)
            品种 = 品种映射.get(类别名称, "")
            
            for py文件 in 子目录.glob("*.py"):
                if py文件.name.startswith("__"):
                    continue
                
                策略名 = py文件.stem
                self.策略列表.append({
                    "名称": 策略名,
                    "类别": 显示类别,
                    "品种": 品种,
                    "类": None,
                })
                print(f"✅ 发现策略: {策略名} ({显示类别})")
        
        if not self.策略列表:
            print("未找到策略文件，使用默认策略")
            self._使用默认策略()
        else:
            print(f"📊 共加载 {len(self.策略列表)} 个策略")
    
    def _使用默认策略(self):
        """使用默认策略列表"""
        默认策略 = [
            {"名称": "外汇利差策略", "类别": "💰 外汇", "品种": "EURUSD"},
            {"名称": "加密双均线", "类别": "₿ 加密货币", "品种": "BTC-USD"},
            {"名称": "加密风控策略", "类别": "₿ 加密货币", "品种": "BTC-USD"},
            {"名称": "A股双均线", "类别": "📈 A股", "品种": "000001.SS"},
            {"名称": "A股量价策略", "类别": "📈 A股", "品种": "000001.SS"},
            {"名称": "A股隔夜套利策略", "类别": "📈 A股", "品种": "000001.SS"},
            {"名称": "美股动量策略", "类别": "🇺🇸 美股", "品种": "AAPL"},
            {"名称": "美股简单策略", "类别": "🇺🇸 美股", "品种": "AAPL"},
        ]
        
        for 策略 in 默认策略:
            self.策略列表.append({
                "名称": 策略["名称"],
                "类别": 策略["类别"],
                "品种": 策略["品种"],
                "类": None,
            })
        
        print(f"📊 已加载 {len(self.策略列表)} 个默认策略")
    
    def 获取策略(self, 名称=None):
        """获取策略列表或单个策略"""
        if 名称:
            for s in self.策略列表:
                if s.get("名称") == 名称:
                    return s
            return None
        return self.策略列表
    
    def 获取策略列表(self):
        """获取策略列表"""
        return self.策略列表
    
    def 获取策略列表_带状态(self):
        """获取带状态的策略列表"""
        结果 = []
        for s in self.策略列表:
            结果.append({
                "名称": s.get("名称", ""),
                "类别": s.get("类别", ""),
                "品种": s.get("品种", ""),
                "启用": True,
            })
        return 结果
    
    def 根据名称获取(self, 名称):
        """根据名称获取策略"""
        for s in self.策略列表:
            if s["名称"] == 名称:
                return s
        return None
    
    def 刷新(self):
        """刷新策略列表"""
        self.策略列表 = []
        self._加载策略()


def 获取策略加载器():
    return 策略加载器()
