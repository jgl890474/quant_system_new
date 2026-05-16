# -*- coding: utf-8 -*-
import os
import glob
import importlib.util
from pathlib import Path

class 策略加载器:
    def __init__(self):
        self.策略列表 = []
        self._加载策略()
        
        if not self.策略列表:
            self._使用默认策略()
    
    def _加载策略(self):
        """从策略库文件夹加载策略"""
        策略库路径 = Path(__file__).parent.parent / "策略库"
        
        # 策略类别映射
        类别映射 = {
            "外汇策略": "💰 外汇",
            "加密货币策略": "₿ 加密货币",
            "A股策略": "📈 A股",
            "美股策略": "🇺🇸 美股",
        }
        
        品种映射 = {
            "外汇策略": "EURUSD",
            "加密货币策略": "BTC-USD",
            "A股策略": "000001.SS",
            "美股策略": "AAPL",
        }
        
        if not 策略库路径.exists():
            print(f"策略库目录不存在: {策略库路径}")
            return
        
        for 子目录 in 策略库路径.iterdir():
            if not 子目录.is_dir():
                continue
            
            目录名 = 子目录.name
            类别 = 类别映射.get(目录名, 目录名)
            品种 = 品种映射.get(目录名, "")
            
            for py文件 in 子目录.glob("*.py"):
                if py文件.name.startswith("__"):
                    continue
                
                策略名 = py文件.stem
                
                # 尝试加载策略类
                策略类 = None
                try:
                    spec = importlib.util.spec_from_file_location(策略名, py文件)
                    模块 = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(模块)
                    
                    # 查找策略类
                    for attr_name in dir(模块):
                        attr = getattr(模块, attr_name)
                        if isinstance(attr, type):
                            if "Strategy" in attr.__name__ or "策略" in attr.__name__:
                                策略类 = attr
                                break
                except Exception as e:
                    print(f"加载策略类失败 {策略名}: {e}")
                
                self.策略列表.append({
                    "名称": 策略名,
                    "类别": 类别,
                    "品种": 品种,
                    "类": 策略类,
                    "文件路径": str(py文件),
                })
                print(f"✅ 发现策略: {策略名} ({类别})")
        
        print(f"📊 共加载 {len(self.策略列表)} 个策略")
    
    def _使用默认策略(self):
        """使用默认策略"""
        默认策略 = [
            {"名称": "外汇利差策略", "类别": "💰 外汇", "品种": "EURUSD", "类": None},
            {"名称": "加密双均线", "类别": "₿ 加密货币", "品种": "BTC-USD", "类": None},
            {"名称": "A股双均线", "类别": "📈 A股", "品种": "000001.SS", "类": None},
            {"名称": "美股动量策略", "类别": "🇺🇸 美股", "品种": "AAPL", "类": None},
        ]
        self.策略列表 = 默认策略
        print(f"📊 使用默认策略，共 {len(self.策略列表)} 个")
    
    def 获取策略(self, 名称=None):
        if 名称:
            for s in self.策略列表:
                if s.get("名称") == 名称:
                    return s
            return None
        return self.策略列表
    
    def 获取策略列表(self):
        return self.策略列表
    
    def 获取策略列表_带状态(self):
        return [{"名称": s["名称"], "类别": s["类别"], "品种": s["品种"], "启用": True} for s in self.策略列表]
    
    def 根据名称获取(self, 名称):
        for s in self.策略列表:
            if s["名称"] == 名称:
                return s
        return None
    
    def 刷新(self):
        self.策略列表 = []
        self._加载策略()


def 获取策略加载器():
    return 策略加载器()
