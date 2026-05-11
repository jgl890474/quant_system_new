# -*- coding: utf-8 -*-

class 策略运行器:
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
            # 检查策略信息是否有效
            if not 策略信息:
                return 'hold'
            
            # 检查是否有策略类（从文件加载的才有类，默认策略没有）
            策略类 = 策略信息.get("类")
            if 策略类 is not None:
                # 有策略类，使用策略类处理
                实例 = 策略类(策略信息["名称"], 策略信息.get("品种", "未知"), 10000)
                
                # 构建行情数据
                if 行情数据 and hasattr(行情数据, '价格'):
                    行情字典 = {'close': 行情数据.价格}
                else:
                    行情字典 = {'close': 0}
                
                return 实例.处理行情(行情字典)
            else:
                # 没有策略类（默认策略），返回模拟信号
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
            
            # 根据不同策略返回不同信号（演示用）
            策略名称 = 策略信息.get("名称", "")
            
            if "双均线" in 策略名称:
                # 模拟：价格波动产生随机信号
                import random
                random.seed(hash(品种) % 10000)
                return random.choice(['buy', 'hold', 'hold'])  # 20%买入概率
            
            if "量价" in 策略名称:
                return 'hold'
            
            if "隔夜" in 策略名称:
                # 尾盘买入信号
                from datetime import datetime
                now = datetime.now()
                if 14 <= now.hour <= 15:
                    return 'buy'
                return 'hold'
            
            if "加密" in 策略名称:
                return 'buy' if 价格 > 0 else 'hold'
            
            if "动量" in 策略名称:
                return 'hold'
            
            if "利差" in 策略名称:
                return 'hold'
            
            return 'hold'
        except:
            return 'hold'rn 'hold'
