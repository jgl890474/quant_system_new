# -*- coding: utf-8 -*-
import os
import glob
import importlib.util


class 策略加载器:
    def __init__(self, 策略路径="策略库"):
        self.策略列表 = []
        self._加载所有(策略路径)
        self._打印加载结果()
    
    def _加载所有(self, 路径):
        """加载所有策略文件夹中的策略"""
        if not os.path.exists(路径):
            print(f"❌ 策略路径不存在: {路径}")
            return
        
        # 类别配置（文件夹名 → 显示名称和品种）
        类别配置 = {
            "外汇策略": {"品种": "EURUSD", "显示": "💰 外汇"},
            "期货策略": {"品种": "GC=F", "显示": "📊 期货"},
            "加密货币策略": {"品种": "BTC-USD", "显示": "₿ 加密货币"},
            "A股策略": {"品种": "000001.SS", "显示": "📈 A股"},
            "港股策略": {"品种": "00700.HK", "显示": "🇭🇰 港股"},
            "美股策略": {"品种": "AAPL", "显示": "🇺🇸 美股"},
        }
        
        # 扫描每个类别文件夹
        for 文件夹名, 配置 in 类别配置.items():
            文件夹路径 = os.path.join(路径, 文件夹名)
            
            if not os.path.isdir(文件夹路径):
                print(f"⚠️ 文件夹不存在: {文件夹名}，跳过")
                continue
            
            print(f"📁 扫描文件夹: {文件夹名}")
            
            # 扫描该文件夹下的所有 .py 文件
            py文件列表 = glob.glob(os.path.join(文件夹路径, "*.py"))
            
            if not py文件列表:
                print(f"   ⚠️ 没有找到策略文件")
                continue
            
            for py文件 in py文件列表:
                文件名 = os.path.basename(py文件)
                
                # 跳过特殊文件
                if 文件名 in ["__init__.py", "__pycache__"]:
                    continue
                
                if 文件名.endswith(".txt"):
                    continue
                
                策略名 = 文件名.replace(".py", "")
                
                try:
                    # 动态加载模块
                    spec = importlib.util.spec_from_file_location(策略名, py文件)
                    模块 = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(模块)
                    
                    # 查找模块中的策略类（类名包含 Strategy 或以 Strategy 结尾）
                    找到策略 = False
                    for 属性名 in dir(模块):
                        属性 = getattr(模块, 属性名)
                        
                        # 检查是否为类
                        if not isinstance(属性, type):
                            continue
                        
                        # 检查是否为策略类（类名包含 Strategy 或 继承了策略基类）
                        类名 = 属性.__name__
                        if "Strategy" in 类名 or 类名.endswith("策略"):
                            
                            self.策略列表.append({
                                "名称": 策略名,
                                "类": 属性,
                                "品种": 配置["品种"],
                                "类别": 配置["显示"],
                                "文件名": 文件名
                            })
                            print(f"   ✅ 加载成功: {策略名} → {配置['显示']}")
                            找到策略 = True
                            break
                    
                    if not 找到策略:
                        print(f"   ⚠️ 未找到策略类: {文件名} (需要类名包含 'Strategy')")
                        
                except Exception as e:
                    print(f"   ❌ 加载失败 {文件名}: {e}")
        
        # 额外扫描：如果某个文件夹有文件但没有被上述规则匹配，尝试通用加载
        self._通用加载(路径)
    
    def _通用加载(self, 路径):
        """通用加载：扫描所有子文件夹，尝试加载所有策略"""
        所有策略文件夹 = ["外汇策略", "期货策略", "加密货币策略", "A股策略", "港股策略", "美股策略"]
        
        for 文件夹名 in 所有策略文件夹:
            文件夹路径 = os.path.join(路径, 文件夹名)
            if not os.path.isdir(文件夹路径):
                continue
            
            for py文件 in glob.glob(os.path.join(文件夹路径, "*.py")):
                文件名 = os.path.basename(py文件)
                if 文件名 in ["__init__.py", "__pycache__"]:
                    continue
                
                策略名 = 文件名.replace(".py", "")
                
                # 检查是否已加载
                已存在 = any(s["名称"] == 策略名 for s in self.策略列表)
                if 已存在:
                    continue
                
                try:
                    spec = importlib.util.spec_from_file_location(策略名, py文件)
                    模块 = importlib.util.module_from_spec(spec)
                    spec.loader.exec_module(模块)
                    
                    for 属性名 in dir(模块):
                        属性 = getattr(模块, 属性名)
                        if isinstance(属性, type):
                            # 默认品种和类别
                            默认配置 = {
                                "外汇策略": {"品种": "EURUSD", "显示": "💰 外汇"},
                                "期货策略": {"品种": "GC=F", "显示": "📊 期货"},
                                "加密货币策略": {"品种": "BTC-USD", "显示": "₿ 加密货币"},
                                "A股策略": {"品种": "000001.SS", "显示": "📈 A股"},
                                "港股策略": {"品种": "00700.HK", "显示": "🇭🇰 港股"},
                                "美股策略": {"品种": "AAPL", "显示": "🇺🇸 美股"},
                            }
                            配置 = 默认配置.get(文件夹名, {"品种": "AAPL", "显示": "📈 股票"})
                            
                            self.策略列表.append({
                                "名称": 策略名,
                                "类": 属性,
                                "品种": 配置["品种"],
                                "类别": 配置["显示"],
                                "文件名": 文件名
                            })
                            print(f"   ✅ [通用] 加载成功: {策略名}")
                            break
                except:
                    pass
    
    def _打印加载结果(self):
        """打印加载结果汇总"""
        print("\n" + "="*50)
        print("📊 策略加载完成汇总")
        print("="*50)
        
        if not self.策略列表:
            print("⚠️ 没有加载到任何策略！")
            return
        
        # 按类别分组
        分组 = {}
        for s in self.策略列表:
            类别 = s["类别"]
            if 类别 not in 分组:
                分组[类别] = []
            分组[类别].append(s["名称"])
        
        for 类别, 策略名列表 in 分组.items():
            print(f"  {类别}: {len(策略名列表)} 个策略")
            for 名 in 策略名列表:
                print(f"    - {名}")
        
        print(f"\n✅ 总计: {len(self.策略列表)} 个策略")
        print("="*50)
    
    def 获取策略(self):
        """获取所有策略列表"""
        return self.策略列表
    
    def 根据名称获取(self, 名称):
        """根据策略名获取策略信息"""
        for s in self.策略列表:
            if s["名称"] == 名称:
                return s
        return None
    
    def 刷新(self):
        """重新加载策略"""
        self.策略列表 = []
        self._加载所有("策略库")
        self._打印加载结果()
