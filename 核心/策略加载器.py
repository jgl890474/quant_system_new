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
            print(f"路径不存在: {路径}")
            return
        
        # 策略类别配置
        类别配置 = {
            "外汇策略": {"品种": "EURUSD", "显示": "💰 外汇"},
            "加密货币策略": {"品种": "BTC-USD", "显示": "₿ 加密货币"},
            "A股策略": {"品种": "000001.SS", "显示": "📈 A股"},
            "美股策略": {"品种": "AAPL", "显示": "🇺🇸 美股"},
        }
        
        for 文件夹名, 配置 in 类别配置.items():
            文件夹路径 = os.path.join(路径, 文件夹名)
            if not os.path.isdir(文件夹路径):
                print(f"⚠️ 文件夹不存在: {文件夹名}")
                continue
            
            print(f"📁 扫描: {文件夹名}")
            print(f"   品种配置: {配置['品种']}")
            
            for py文件 in glob.glob(os.path.join(文件夹路径, "*.py")):
                文件名 = os.path.basename(py文件)
                if 文件名 in ["__init__.py", "__pycache__"]:
                    continue
                
                策略名 = 文件名.replace(".py", "")
                print(f"   发现文件: {文件名}")
                
                try:
                    spec = importlib.util.spec_from_file_location(策略名, py文件)
                    模块 = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(模块)
                    
                    找到 = False
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
                                print(f"   ✅ 加载成功: {策略名} -> 品种: {配置['品种']}")
                                找到 = True
                                break
                    
                    if not 找到:
                        print(f"   ⚠️ 未找到策略类: {文件名}")
                        
                except Exception as e:
                    print(f"   ❌ 加载失败 {文件名}: {e}")
        
        # 打印加载结果
        print(f"\n📊 最终加载策略列表:")
        for s in self.策略列表:
            print(f"   {s['名称']} -> {s['品种']} ({s['类别']})")
        print(f"\n📊 共加载 {len(self.策略列表)} 个策略")
    
    def 获取策略(self):
        """获取所有策略列表"""
        return self.策略列表
    
    def 根据名称获取(self, 名称):
        """根据策略名称获取策略信息"""
        for s in self.策略列表:
            if s["名称"] == 名称:
                return s
        return None
