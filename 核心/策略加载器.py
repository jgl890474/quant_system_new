# -*- coding: utf-8 -*-
import os
import glob
import importlib.util

class 策略加载器:
    def __init__(self, 策略路径="策略库"):
        self.策略路径 = 策略路径
        self.策略列表 = []
        self._加载所有(策略路径)
        
        if not self.策略列表:
            self._使用默认策略()
    
    def _使用默认策略(self):
        """使用默认策略"""
        默认策略 = [
            {"名称": "双均线策略", "类别": "📈 A股", "品种": "000001"},
            {"名称": "量价策略", "类别": "📈 A股", "品种": "000002"},
            {"名称": "隔夜套利策略", "类别": "📈 A股", "品种": "000858"},
            {"名称": "加密双均线", "类别": "₿ 加密货币", "品种": "BTC-USD"},
            {"名称": "动量策略", "类别": "🇺🇸 美股", "品种": "AAPL"},
            {"名称": "外汇利差策略", "类别": "💰 外汇", "品种": "EURUSD"},
            {"名称": "期货趋势策略", "类别": "📊 期货", "品种": "GC=F"},
        ]
        
        for 策略 in 默认策略:
            self.策略列表.append({
                "名称": 策略["名称"],
                "类": None,
                "品种": 策略["品种"],
                "类别": 策略["类别"],
            })
    
    def _加载所有(self, 路径):
        if not os.path.exists(路径):
            return
        
        类别配置 = {
            "外汇策略": {"品种": "EURUSD", "显示": "💰 外汇"},
            "加密货币策略": {"品种": "BTC-USD", "显示": "₿ 加密货币"},
            "A股策略": {"品种": "000001.SS", "显示": "📈 A股"},
            "美股策略": {"品种": "AAPL", "显示": "🇺🇸 美股"},
        }
        
        for 文件夹名, 配置 in 类别配置.items():
            文件夹路径 = os.path.join(路径, 文件夹名)
            if not os.path.isdir(文件夹路径):
                continue
            
            for py文件 in glob.glob(os.path.join(文件夹路径, "*.py")):
                文件名 = os.path.basename(py文件)
                if 文件名 in ["__init__.py", "__pycache__"]:
                    continue
                
                策略名 = 文件名.replace(".py", "")
                
                try:
                    spec = importlib.util.spec_from_file_location(策略名, py文件)
                    模块 = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(模块)
                    
                    for 属性名 in dir(模块):
                        属性 = getattr(模块, 属性名)
                        if isinstance(属性, type):
                            if "Strategy" in 属性.__name__ or "策略" in 属性.__name__:
                                self.策略列表.append({
                                    "名称": 策略名,
                                    "类": 属性,
                                    "品种": 配置["品种"],
                                    "类别": 配置["显示"],
                                })
                                break
                except Exception:
                    pass
    
    def 获取策略(self):
        return self.策略列表
    
    def 获取策略列表(self):
        return self.策略列表
    
    def 获取策略列表_带状态(self):
        """策略中心需要的格式"""
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
        for s in self.策略列表:
            if s["名称"] == 名称:
                return s
        return None
    
    def 刷新(self):
        self.策略列表 = []
        self._加载所有(self.策略路径)
        if not self.策略列表:
            self._使用默认策略()
