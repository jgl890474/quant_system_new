# -*- coding: utf-8 -*-
"""
策略加载器 - 动态从策略库加载策略
"""

import os
import importlib
from pathlib import Path


class 策略加载器:
    def __init__(self):
        self.策略列表 = []
        self.策略路径 = Path(__file__).parent.parent / "策略库"
        self._加载策略()
    
    def _加载策略(self):
        """动态从策略库加载策略"""
        if not self.策略路径.exists():
            print(f"⚠️ 策略库路径不存在: {self.策略路径}")
            self._使用默认策略()
            return
        
        # 类别映射
        类别映射 = {
            "加密货币策略": "₿ 加密货币",
            "A股策略": "📈 A股",
            "美股策略": "🇺🇸 美股",
        }
        
        品种映射 = {
            "加密货币策略": "BTC-USD",
            "A股策略": "000001.SS",
            "美股策略": "AAPL",
        }
        
        for 类别文件夹 in self.策略路径.iterdir():
            if not 类别文件夹.is_dir():
                continue
            
            文件夹名 = 类别文件夹.name
            显示类别 = 类别映射.get(文件夹名, 文件夹名)
            默认品种 = 品种映射.get(文件夹名, "")
            
            for 策略文件 in 类别文件夹.glob("*.py"):
                if 策略文件.name.startswith("__"):
                    continue
                
                策略名 = 策略文件.stem
                
                # 尝试导入策略类
                策略类 = None
                try:
                    模块名 = f"策略库.{文件夹名}.{策略名}"
                    模块 = importlib.import_module(模块名)
                    
                    # 查找策略类
                    for 属性名 in dir(模块):
                        属性 = getattr(模块, 属性名)
                        if isinstance(属性, type):
                            if "Strategy" in 属性.__name__ or "策略" in 属性.__name__:
                                策略类 = 属性
                                break
                except Exception as e:
                    print(f"⚠️ 导入策略类失败 {策略名}: {e}")
                
                self.策略列表.append({
                    "名称": 策略名,
                    "类别": 显示类别,
                    "品种": 默认品种,
                    "类": 策略类,
                    "参数": {
                        "短期均线": 5,
                        "长期均线": 20,
                        "止损比例": 0.05,
                        "止盈比例": 0.10,
                        "仓位比例": 0.3,
                    }
                })
                print(f"✅ 发现策略: {策略名} ({显示类别})")
        
        if not self.策略列表:
            print("⚠️ 未发现策略，使用默认策略")
            self._使用默认策略()
        
        print(f"📊 策略加载器初始化完成，共 {len(self.策略列表)} 个策略")
    
    def _使用默认策略(self):
        """使用默认策略列表"""
        self.策略列表 = [
            {"名称": "加密双均线1", "类别": "₿ 加密货币", "品种": "BTC-USD", "类": None, "参数": {}},
            {"名称": "加密风控策略", "类别": "₿ 加密货币", "品种": "BTC-USD", "类": None, "参数": {}},
            {"名称": "A股双均线1", "类别": "📈 A股", "品种": "000001.SS", "类": None, "参数": {}},
            {"名称": "A股量价策略2", "类别": "📈 A股", "品种": "000001.SS", "类": None, "参数": {}},
            {"名称": "A股隔夜套利策略3", "类别": "📈 A股", "品种": "000001.SS", "类": None, "参数": {}},
            {"名称": "美股简单策略1", "类别": "🇺🇸 美股", "品种": "AAPL", "类": None, "参数": {}},
            {"名称": "美股动量策略", "类别": "🇺🇸 美股", "品种": "AAPL", "类": None, "参数": {}},
        ]
    
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
        """获取带状态的策略列表（兼容策略中心）"""
        return [{"名称": s["名称"], "类别": s["类别"], "品种": s["品种"], "启用": True} for s in self.策略列表]
    
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
    
    # ========== 策略参数管理 ==========
    def 获取策略参数(self, 策略名称: str) -> dict:
        """获取策略参数"""
        for s in self.策略列表:
            if s.get("名称") == 策略名称:
                return s.get("参数", {})
        return {}
    
    def 更新策略参数(self, 策略名称: str, 参数更新: dict) -> bool:
        """更新策略参数"""
        for s in self.策略列表:
            if s.get("名称") == 策略名称:
                if "参数" not in s:
                    s["参数"] = {}
                s["参数"].update(参数更新)
                print(f"✅ 更新策略参数: {策略名称} = {参数更新}")
                return True
        return False
    
    def 设置策略参数(self, 策略名称: str, 参数名: str, 值) -> bool:
        """设置单个策略参数"""
        for s in self.策略列表:
            if s.get("名称") == 策略名称:
                if "参数" not in s:
                    s["参数"] = {}
                s["参数"][参数名] = 值
                print(f"✅ 设置策略参数: {策略名称}.{参数名} = {值}")
                return True
        return False


def 获取策略加载器():
    """获取策略加载器实例"""
    return 策略加载器()
