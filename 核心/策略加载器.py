# -*- coding: utf-8 -*-
"""
策略加载器 - 动态加载策略库中的所有策略
"""

import os
import sys
import importlib
import inspect
from pathlib import Path


class 策略加载器:
    """策略加载器 - 动态加载策略库中的策略"""
    
    def __init__(self):
        self.策略列表 = []
        self._加载所有策略()
    
    def _加载所有策略(self):
        """加载所有策略"""
        策略库路径 = Path(__file__).parent.parent / "策略库"
        
        if not 策略库路径.exists():
            print(f"⚠️ 策略库目录不存在: {策略库路径}")
            return
        
        print("📁 扫描策略库...")
        
        # 遍历所有子目录
        for 子目录 in 策略库路径.iterdir():
            if 子目录.is_dir():
                self._加载目录中的策略(子目录)
        
        print(f"✅ 共加载 {len(self.策略列表)} 个策略")
    
    def _加载目录中的策略(self, 目录):
        """加载目录中的策略"""
        for py文件 in 目录.glob("*.py"):
            if py文件.name.startswith("__"):
                continue
            
            try:
                # 动态导入模块
                模块名 = f"策略库.{目录.name}.{py文件.stem}"
                模块 = importlib.import_module(模块名)
                
                # 查找策略类
                for name, obj in inspect.getmembers(模块, inspect.isclass):
                    if self._是策略类(obj):
                        策略信息 = {
                            "名称": name,
                            "类别": 目录.name,
                            "类": obj,
                            "文件": str(py文件),
                            "模块": 模块名,
                            "品种": self._获取默认品种(目录.name),
                            "描述": getattr(obj, '__doc__', '')
                        }
                        self.策略列表.append(策略信息)
                        print(f"   ✅ 发现策略: {name}")
                        
            except Exception as e:
                print(f"   ⚠️ 加载失败 {py文件.name}: {e}")
    
    def _是策略类(self, cls):
        """判断是否是策略类"""
        try:
            from 核心.策略基类 import 策略基类
            return issubclass(cls, 策略基类) and cls != 策略基类
        except:
            return False
    
    def _获取默认品种(self, 类别):
        """根据类别获取默认品种"""
        品种映射 = {
            "加密货币策略": "BTC-USD",
            "A股策略": "000001.SS",
            "美股策略": "AAPL",
            "外汇策略": "EURUSD",
            "期货策略": "GC=F"
        }
        return 品种映射.get(类别, "")
    
    def 获取策略(self, 名称=None):
        """获取策略"""
        if 名称:
            for s in self.策略列表:
                if s.get("名称") == 名称:
                    return s
            return None
        return self.策略列表
    
    def 获取策略列表(self):
        """获取所有策略列表"""
        return self.策略列表
    
    def 刷新(self):
        """刷新策略列表"""
        self.策略列表 = []
        self._加载所有策略()


# 全局实例
_加载器 = None

def 获取策略加载器():
    global _加载器
    if _加载器 is None:
        _加载器 = 策略加载器()
    return _加载器
