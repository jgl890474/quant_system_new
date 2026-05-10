# -*- coding: utf-8 -*-
from 工具.数据库 import 数据库
from 核心.数据模型 import 持仓数据
import time


class 订单引擎:
    def __init__(self, 初始资金=1000000):
        self.初始资金 = 初始资金
        self.可用资金 = 初始资金
        self.持仓市值 = 0
        self.总盈亏 = 0
        self.持仓 = {}  # 品种 -> 持仓数据
        self.交易记录 = []
        
        # 从数据库恢复持仓
        self._恢复持仓()
    
    def 买入(self, 品种, 价格, 数量):
        """买入 - 支持多品种持仓"""
        try:
            花费 = 价格 * 数量
            
            # 检查可用资金
            if 花费 > self.可用资金:
                return {"success": False, "error": f"资金不足"}
            
            # 处理持仓
            if 品种 in self.持仓:
                # 已有持仓：加仓
                原持仓 = self.持仓[品种]
                原数量 = 原持仓.数量
                原成本 = 原持仓.平均成本
                
                新数量 = 原数量 + 数量
                新平均成本 = (原成本 * 原数量 + 价格 * 数量) / 新数量
                
                self.持仓[品种].数量 = 新数量
                self.持仓[品种].平均成本 = 新平均成本
            else:
                # 新持仓
                self.持仓[品种] = 持仓数据(品种, 数量, 价格)
            
            # 更新资金
            self.可用资金 -= 花费
            self.持仓市值 += 花费
            
            # 记录交易
            self.记录交易("买入", 品种, 价格, 数量)
            
            # 保存到数据库
            self._保存持仓()
            
            return {"success": True, "message": f"买入成功"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def 卖出(self, 品种, 价格, 数量):
        """卖出"""
        try:
            if 品种 not in self.持仓:
                return {"success": False, "error": "无此持仓"}
            
            持仓 = self.持仓[品种]
            if 数量 > 持仓.数量:
                return {"success": False, "error": "卖出数量超过持仓"}
            
            # 计算盈亏
            收入 = 价格 * 数量
            成本 = 持仓.平均成本 * 数量
            盈亏 = 收入 - 成本
            
            # 更新持仓
            持仓.数量 -= 数量
            if 持仓.数量 <= 0:
                del self.持仓[品种]
            
            # 更新资金
            self.可用资金 += 收入
            self.持仓市值 -= 成本
            
            # 记录交易
            self.记录交易("卖出", 品种, 价格, 数量, 盈亏)
            
            # 保存到数据库
            self._保存持仓()
            
            return {"success": True, "message": f"卖出成功", "profit": 盈亏}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def 获取总资产(self):
        """计算总资产"""
        当前持仓市值 = 0
        for 品种, pos in self.持仓.items():
            # 这里可以调用行情获取当前价格
            当前持仓市值 += pos.数量 * pos.平均成本
        return self.可用资金 + 当前持仓市值
    
    def 记录交易(self, 动作, 品种, 价格, 数量, 盈亏=0):
        """记录交易"""
        交易 = {
            "时间": time.strftime("%Y-%m-%d %H:%M:%S"),
            "品种": 品种,
            "动作": 动作,
            "价格": 价格,
            "数量": 数量,
            "盈亏": 盈亏
        }
        self.交易记录.append(交易)
        数据库.保存交易记录(交易)
    
    def _保存持仓(self):
        """保存持仓到数据库"""
        数据库.保存持仓快照(self.持仓)
    
    def _恢复持仓(self):
        """从数据库恢复持仓"""
        try:
            持仓数据 = 数据库.加载持仓快照()
            for 品种, data in 持仓数据.items():
                self.持仓[品种] = 持仓数据(
                    品种, 
                    data.get("数量", 0), 
                    data.get("平均成本", 0)
                )
        except:
            pass
