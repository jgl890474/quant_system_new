# -*- coding: utf-8 -*-

class 策略运行器:
    """策略运行器 - 支持策略启停控制和参数传递"""
    
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
    
    @classmethod
    def 运行(cls, 策略信息, 行情数据, 策略参数=None):
        """
        运行策略，返回交易信号
        
        参数:
            策略信息: 策略字典，包含名称、品种、类等
            行情数据: 行情数据对象，包含价格、成交量等
            策略参数: 可选，策略的参数配置
        
        返回:
            'buy' / 'sell' / 'hold'
        """
        try:
            if not 策略信息:
                return 'hold'
            
            策略名称 = 策略信息.get("名称", "")
            
            # 检查策略是否已停止
            if not cls.获取策略状态(策略名称):
                return 'hold'
            
            策略类 = 策略信息.get("类")
            品种 = 策略信息.get("品种", "未知")
            
            if 策略类 is not None:
                # 创建策略实例
                实例 = 策略类(策略名称, 品种, 10000)
                
                # 应用策略参数（如果提供）
                if 策略参数 and hasattr(实例, '批量设置参数'):
                    实例.批量设置参数(策略参数)
                    print(f"   📊 应用策略参数: {策略名称}")
                
                # 处理行情数据
                if 行情数据 and hasattr(行情数据, '价格'):
                    行情字典 = {
                        'close': 行情数据.价格,
                        'volume': getattr(行情数据, '成交量', 0),
                        'high': getattr(行情数据, '最高', 行情数据.价格),
                        'low': getattr(行情数据, '最低', 行情数据.价格),
                        'open': getattr(行情数据, '开盘', 行情数据.价格),
                        'date': getattr(行情数据, '时间戳', None)
                    }
                elif isinstance(行情数据, dict):
                    行情字典 = 行情数据
                else:
                    行情字典 = {'close': 0, 'volume': 0, 'high': 0, 'low': 0, 'open': 0}
                
                # 调用策略
                信号 = 实例.处理行情(行情字典)
                
                # 如果没有有效信号，尝试检查止损止盈
                if 信号 == 'hold' and hasattr(实例, '持仓') and 实例.持仓 > 0:
                    if hasattr(实例, '检查止损止盈'):
                        止损信号 = 实例.检查止损止盈(行情字典['close'])
                        if 止损信号 != 'hold':
                            信号 = 止损信号
                
                return 信号
            else:
                # 策略类不存在，使用模拟信号
                return cls._模拟信号(策略信息, 行情数据)
                
        except Exception as e:
            print(f"❌ 策略运行失败 {策略信息.get('名称', '未知')}: {e}")
            return 'hold'
    
    @classmethod
    def 运行带仓位(cls, 策略信息, 行情数据, 总资金, 策略参数=None):
        """
        运行策略并返回交易信号和仓位数量
        
        返回:
            dict: {'信号': 'buy/sell/hold', '数量': 数量, '理由': 理由}
        """
        try:
            信号 = cls.运行(策略信息, 行情数据, 策略参数)
            
            if 信号 == 'hold':
                return {'信号': 'hold', '数量': 0, '理由': '无信号'}
            
            # 获取价格
            if 行情数据 and hasattr(行情数据, '价格'):
                价格 = 行情数据.价格
            elif isinstance(行情数据, dict):
                价格 = 行情数据.get('close', 0)
            else:
                价格 = 0
            
            if 价格 <= 0:
                return {'信号': 'hold', '数量': 0, '理由': '价格无效'}
            
            # 获取策略实例计算仓位
            策略类 = 策略信息.get("类")
            品种 = 策略信息.get("品种", "未知")
            
            数量 = 0
            if 策略类 is not None:
                实例 = 策略类(策略信息.get("名称", ""), 品种, 总资金)
                if 策略参数 and hasattr(实例, '批量设置参数'):
                    实例.批量设置参数(策略参数)
                
                if hasattr(实例, '计算仓位'):
                    数量 = 实例.计算仓位(总资金, 价格)
                else:
                    # 默认仓位计算（1%资金）
                    数量 = 总资金 * 0.01 / 价格
            else:
                # 默认仓位计算
                数量 = 总资金 * 0.01 / 价格
            
            数量 = round(数量, 4)
            
            return {
                '信号': 信号,
                '数量': 数量,
                '价格': 价格,
                '理由': f"{策略信息.get('名称', '')}策略信号"
            }
            
        except Exception as e:
            print(f"❌ 策略运行失败: {e}")
            return {'信号': 'hold', '数量': 0, '理由': f'运行异常: {e}'}
    
    @staticmethod
    def _模拟信号(策略信息, 行情数据):
        """为默认策略生成模拟信号"""
        try:
            品种 = 策略信息.get("品种", "")
            策略名称 = 策略信息.get("名称", "")
            
            # 获取价格
            if 行情数据 and hasattr(行情数据, '价格'):
                价格 = 行情数据.价格
            elif isinstance(行情数据, dict):
                价格 = 行情数据.get('close', 0)
            else:
                价格 = 0
            
            if 价格 <= 0:
                return 'hold'
            
            import random
            random.seed(hash(品种) % 10000)
            
            if "双均线" in 策略名称:
                return random.choice(['buy', 'hold', 'hold'])
            
            if "加密" in 策略名称:
                return 'buy' if 价格 > 0 else 'hold'
            
            if "隔夜" in 策略名称:
                from datetime import datetime
                now = datetime.now()
                return 'buy' if 14 <= now.hour <= 15 else 'hold'
            
            if "动量" in 策略名称:
                return random.choice(['buy', 'sell', 'hold'])
            
            return 'hold'
        except Exception:
            return 'hold'
    
    @staticmethod
    def 获取策略帮助(策略信息):
        """获取策略帮助信息"""
        try:
            策略类 = 策略信息.get("类")
            if 策略类 is not None:
                名称 = 策略信息.get("名称", "未知")
                文档 = 策略类.__doc__ or "无文档说明"
                return f"**{名称}**\n\n{文档}"
            return "暂无帮助信息"
        except Exception:
            return "无法获取帮助信息"


# 便捷函数
def 获取策略运行器():
    """获取策略运行器实例"""
    return 策略运行器
    
