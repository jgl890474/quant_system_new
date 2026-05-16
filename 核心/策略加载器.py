# -*- coding: utf-8 -*-
import importlib
from pathlib import Path


class 策略加载器:
    def __init__(self):
        self.策略列表 = []
        self._加载策略()
    
    def _加载策略(self):
        策略库路径 = Path(__file__).parent.parent / "策略库"
        if not 策略库路径.exists():
            return
        
        for 子目录 in 策略库路径.iterdir():
            if 子目录.is_dir():
                for py文件 in 子目录.glob("*.py"):
                    if py文件.name.startswith("__"):
                        continue
                    try:
                        模块名 = f"策略库.{子目录.name}.{py文件.stem}"
                        模块 = importlib.import_module(模块名)
                        
                        for name, obj in 模块.__dict__.items():
                            if self._是策略类(obj):
                                self.策略列表.append({
                                    "名称": name,
                                    "类别": 子目录.name,
                                    "类": obj,
                                })
                    except:
                        pass
    
    def _是策略类(self, obj):
        try:
            from 核心.策略基类 import 策略基类
            return isinstance(obj, type) and issubclass(obj, 策略基类) and obj != 策略基类
        except:
            return False
    
    def 获取策略列表(self):
        return self.策略列表
    
    def 获取策略(self, 名称):
        for s in self.策略列表:
            if s.get("名称") == 名称:
                return s
        return None


def 获取策略加载器():
    return 策略加载器()
