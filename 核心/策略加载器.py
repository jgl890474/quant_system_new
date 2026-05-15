# -*- coding: utf-8 -*-
"""
策略加载器 - 动态加载策略
"""

import os
import importlib
from pathlib import Path


class 策略加载器:
    """策略加载器"""
    
    def __init__(self):
        self.策略列表 = []
        self._加载策略()
    
    def _加载策略(self):
        """加载策略"""
        策略库路径 = Path(__file__).parent.parent / "策略库"
        
        if not 策略库路径.exists():
            print("策略库目录不存在")
            return
        
        for 子目录 in 策略库路径.iterdir():
            if 子目录.is_dir():
                for py文件 in 子目录.glob("*.py"):
                    if py文件.name.startswith("__"):
                        continue
                    try:
                        模块名 = f"策略库.{子目录.name}.{py文件.stem}"
                        模块 = importlib.import_module(模块名)
                        
                        for name, obj in module.__dict__.items():
                            if callable(obj) and name.endswith("Strategy"):
                                self.策略列表.append({
                                    "名称": name,
                                    "类别": 子目录.name,
                                    "类": obj,
                                    "品种": self._获取品种(子目录.name)
                                })
                                print(f"发现策略: {name}")
                    except Exception as e:
                        print(f"加载失败: {py文件.name} - {e}")
        
        print(f"共加载 {len(self.策略列表)} 个策略")
    
    def _获取品种(self, 类别):
        映射 = {"加密货币策略": "BTC-USD", "A股策略": "000001.SS", "美股策略": "AAPL"}
        return 映射.get(类别, "")
    
    def 获取策略(self, 名称=None):
        if 名称:
            for s in self.策略列表:
                if s.get("名称") == 名称:
                    return s
            return None
        return self.策略列表
    
    def 获取策略列表(self):
        return self.策略列表


def 获取策略加载器():
    return 策略加载器()
