import os
import importlib

class 策略加载器:
    """自动扫描加载策略"""
    
    def __init__(self):
        self.策略目录 = os.path.dirname(__file__)
        self.所有策略 = {}
    
    def 加载所有策略(self):
        for 目录 in os.listdir(self.策略目录):
            if not 目录.startswith("策略_"):
                continue
            类目 = 目录[3:]
            self.所有策略[类目] = self._加载目录策略(目录)
        return self.所有策略
    
    def _加载目录策略(self, 目录):
        策略组 = {}
        目录路径 = os.path.join(self.策略目录, 目录)
        for 文件 in os.listdir(目录路径):
            if not 文件.endswith(".py") or 文件 == "__init__.py":
                continue
            模块 = importlib.import_module(f"策略引擎.{目录}.{文件[:-3]}")
            for attr in dir(模块):
                if attr.endswith("策略") and attr != "策略基类":
                    策略组[文件] = {"实例": getattr(模块, attr)(), "名称": attr}
        return 策略组