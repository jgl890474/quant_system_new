# -*- coding: utf-8 -*-

class 策略运行器:
    """策略运行器 - 支持策略启停控制"""
    
    # 全局策略状态存储
    _策略状态 = {}
    
    @classmethod
    def 设置策略状态(cls, 策略名称, 是否启用):
        """设置策略的启用/停止状态"""
        cls._策略状态[策略名称] = 是否启用
        print(f"📊 策略 [{策略名称}] 已{'启用' if 是否启用 else '停止'}")
    
    @classmethod
    def 获取策略状态(cls, 策略名称):
        """获取策略的启用状态"""
        return cls._策略状态.get(策略名称, True)  # 默认启用
    
    @classmethod
    def 获取所有策略状态(cls):
        """获取所有策略状态"""
        return cls._策略状态.copy()
    
    @classmethod
    def 是否运行中(cls, 策略名称):
        """判断策略是否运行中（用于AI交易过滤）"""
        return cls._策略状态.get(策略名称, True)
    
    @staticmethod
    def 运行(策略信息, 行情数据):
        """
        运行策略，返回交易信号
        参数:
            策略信息: 包含策略名称、类别、品种、类等信息的字典
            行情数据: 行情数据对象，应包含价格属性
        返回:
            'buy' - 买入信号
            'sell' - 卖出信号
            'hold' - 持有/无操作
        """
        try:
            if not 策略信息:
                return 'hold'
            
            策略名称 = 策略信息.get("名称", "")
            
            # 检查策略是否已停止（只在策略信号区域生效）
            if not 策略运行器.获取策略状态(策略名称):
                return 'hold'
            
            策略类 = 策略信息.get("类")
            if 策略类 is not None:
                实例 = 策略类(策略信息["名称"], 策略信息.get("品种", "未知"), 10000)
                
                if 行情数据 and hasattr(行情数据, '价格'):
                    行情字典 = {'close': 行情数据.价格}
                else:
                    行情字典 = {'close': 0}
                
                return 实例.处理行情(行情字典)
            else:
                return 策略运行器._模拟信号(策略信息, 行情数据)
                
        except Exception as e:
            print(f"策略运行失败: {e}")
            return 'hold'
    
    @staticmethod
    def _模拟信号(策略信息, 行情数据):
        """为默认策略生成模拟信号"""
        try:
            品种 = 策略信息.get("品种", "")
            价格 = 行情数据.价格 if 行情数据 and hasattr(行情数据, '价格') else 0
            
            if 价格 <= 0:
                return 'hold'
            
            策略名称 = 策略信息.get("名称", "")
            
            if "双均线" in 策略名称:
                import random
                random.seed(hash(品种) % 10000)
                return random.choice(['buy', 'hold', 'hold'])
            
            if "加密" in 策略名称:
                return 'buy' if 价格 > 0 else 'hold'
            
            if "隔夜" in 策略名称:
                from datetime import datetime
                now = datetime.now()
                return 'buy' if 14 <= now.hour <= 15 else 'hold'
            
            return 'hold'
        except:
            return 'hold'
