# -*- coding: utf-8 -*-
import os
import glob
import importlib.util

class 策略加载器:
    def __init__(self, 策略路径="策略库"):
        self.策略列表 = []
        self._加载所有(策略路径)
    
    def _加载所有(self, 路径):
        if not os.path.exists(路径):
            return
        
        类别配置 = {
            "外汇策略": {"品种": "EURUSD", "显示": "外汇"},
            "期货策略": {"品种": "GC=F", "显示": "期货"},
            "加密货币策略": {"品种": "BTC-USD", "显示": "加密货币"},
            "A股策略": {"品种": "000001.SS", "显示": "A股"},
            "港股策略": {"品种": "00700.HK", "显示": "港股"},
            "美股策略": {"品种": "AAPL", "显示": "美股"},
        }
        
        for 文件夹, 配置 in 类别配置.items():
            文件夹路径 = os.path.join(路径, 文件夹)
            if not os.path.isdir(文件夹路径):
                continue
            
            for py文件 in glob.glob(os.path.join(文件夹路径, "*.py")):
                文件名 = os.path.basename(py文件)
                if 文件名 in ["__init__.py", "__pycache__"] or 文件名.endswith(".txt"):
                    continue
                
                策略名 = 文件名.replace(".py", "")
                
                try:
                    spec = importlib.util.spec_from_file_location(策略名, py文件)
                    模块 = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(模块)
                    
                    for 属性名 in dir(模块):
                        属性 = getattr(模块, 属性名)
                        if isinstance(属性, type) and 属性名.endswith("Strategy"):
                            self.策略列表.append({
                                "名称": 策略名,
                                "类": 属性,
                                "品种": 配置["品种"],
                                "类别": 配置["显示"],
                            })
                except:
                    pass
    
    def 获取策略(self):
        return self.策略列表
    
    def 根据名称获取(self, 名称):
        for s in self.策略列表:
            if s["名称"] == 名称:
                return s
        return None
