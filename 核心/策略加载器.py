# -*- coding: utf-8 -*-
"""
策略加载器 - 动态扫描策略库
"""

import importlib
import os
import sys
from pathlib import Path


class 策略加载器:
    def __init__(self):
        self.策略列表 = []
        self._扫描并加载策略()
    
    def _扫描并加载策略(self):
        """扫描策略库目录并加载所有策略"""
        策略库路径 = Path(__file__).parent.parent / "策略库"
        
        if not 策略库路径.exists():
            print(f"⚠️ 策略库目录不存在: {策略库路径}")
            return
        
        print(f"📁 扫描策略库: {策略库路径}")
        
        # 遍历所有子目录
        for 子目录 in 策略库_path.iterdir():
            if not 子目录.is_dir():
                continue
            
            print(f"   扫描目录: {子目录.name}")
            
            for py文件 in 子目录.glob("*.py"):
                if py文件.name.startswith("__"):
                    continue
                
                try:
                    # 动态导入模块
                    模块名 = f"策略库.{子目录.name}.{py文件.stem}"
                    
                    # 清除旧模块缓存
                    if 模块名 in sys.modules:
                        del sys.modules[模块名]
                    
                    模块 = importlib.import_module(模块名)
                    
                    # 查找策略类
                    for name, obj in 模块.__dict__.items():
                        if self._是策略类(obj):
                            策略信息 = {
                                "名称": name,
                                "类别": 子目录.name,
                                "类": obj,
                                "文件": str(py文件),
                                "品种": self._获取默认品种(子目录.name),
                                "模块": 模块名
                            }
                            self.策略列表.append(策略信息)
                            print(f"      ✅ 加载策略: {name}")
                            
                except Exception as e:
                    print(f"      ❌ 加载失败 {py文件.name}: {e}")
        
        print(f"📊 共加载 {len(self.策略列表)} 个策略")
    
    def _是策略类(self, obj):
        """判断是否是策略类"""
        try:
            from 核心.策略基类 import 策略基类
            return (isinstance(obj, type) and 
                    issubclass(obj, 策略基类) and 
                    obj != 策略基类)
        except:
            return False
    
    def _获取默认品种(self, 类别):
        """根据类别返回默认品种"""
        映射 = {
            "加密货币策略": "BTC-USD",
            "A股策略": "000001.SS",
            "美股策略": "AAPL",
            "外汇策略": "EURUSD",
            "期货策略": "GC=F"
        }
        return 映射.get(类别, "")
    
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
        self._扫描并加载策略()
        return self.策略列表


# 全局单例
_策略加载器实例 = None

def 获取策略加载器():
    global _策略加载器实例
    if _策略加载器实例 is None:
        _策略加载器实例 = 策略加载器()
    return _策略加载器实例


# 便捷函数
def 刷新策略列表():
    """刷新策略列表"""
    loader = 获取策略加载器()
    return loader.刷新()
