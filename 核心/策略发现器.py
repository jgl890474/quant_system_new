# -*- coding: utf-8 -*-
"""
策略发现器 - 自动扫描并加载策略库中的所有策略
"""

import os
import importlib
import inspect
from pathlib import Path


class 策略发现器:
    """自动发现策略库中的所有策略"""
    
    def __init__(self):
        self.策略列表 = []
        self._扫描策略()
    
    def _扫描策略(self):
        """扫描策略库目录"""
        策略库路径 = Path(__file__).parent.parent / "策略库"
        
        if not 策略库路径.exists():
            print(f"⚠️ 策略库目录不存在: {策略库路径}")
            return
        
        # 遍历所有子目录
        for 子目录 in 策略库_path.iterdir():
            if 子目录.is_dir():
                self._扫描目录(子目录)
    
    def _扫描目录(self, 目录):
        """扫描单个目录"""
        for py文件 in 目录.glob("*.py"):
            if py文件.name.startswith("__"):
                continue
            
            try:
                # 动态导入模块
                模块名 = f"策略库.{目录.name}.{py文件.stem}"
                模块 = importlib.import_module(模块名)
                
                # 查找策略类（继承自策略基类）
                for name, obj in inspect.getmembers(模块, inspect.isclass):
                    if self._是策略类(obj):
                        # 获取策略元数据
                        策略信息 = {
                            "名称": getattr(obj, '策略名称', py文件.stem),
                            "类别": getattr(obj, '策略类别', 目录.name),
                            "类": obj,
                            "文件": str(py文件),
                            "模块": 模块名,
                            "参数": getattr(obj, '策略参数', {})
                        }
                        self.策略列表.append(策略信息)
                        print(f"✅ 发现策略: {策略信息['名称']} ({策略信息['类别']})")
                        
            except Exception as e:
                print(f"⚠️ 加载策略失败 {py文件.name}: {e}")
    
    def _是策略类(self, cls):
        """判断是否是策略类"""
        try:
            from 核心.策略基类 import 策略基类
            return issubclass(cls, 策略基类) and cls != 策略基类
        except:
            return False
    
    def 获取策略(self, 名称=None, 类别=None):
        """获取策略列表"""
        if 名称:
            for s in self.策略列表:
                if s["名称"] == 名称:
                    return s
            return None
        
        if 类别:
            return [s for s in self.策略列表 if s["类别"] == 类别]
        
        return self.策略列表
    
    def 刷新(self):
        """刷新策略列表"""
        self.策略列表 = []
        self._扫描策略()


# 全局实例
_发现器 = None

def 获取策略发现器():
    global _发现器
    if _发现器 is None:
        _发现器 = 策略发现器()
    return _发现器
