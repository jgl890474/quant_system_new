# -*- coding: utf-8 -*-
import time
from 工具.数据库 import 数据库
from 核心.数据模型 import 持仓数据


class 订单引擎:
    def __init__(self, 初始资金=1000000):
        self.初始资金 = 初始资金
        self.可用资金 = 初始资金
        self.持仓市值 = 0
        self.总盈亏 = 0
        self.持仓 = {}
        self.交易记录 = []
        
        # 从数据库恢复持仓
        self._恢复持仓()
    
    def 买入(self, 品种, 价格, 数量):
        """买入 - 支持多品种持仓"""
        try:
            花费 = 价格 * 数量
            
            if 花费 > self.可用资金:
                return {"success": False, "error": f"资金不足，需要 ¥{花费:.2f}，可用 ¥{self.可用资金:.2f}"}
            
            if 品种 in self.持仓:
                # 加仓
                原持仓 = self.持仓[品种]
                原数量 = 原持仓.数量
                原成本 = 原持仓.平均成本
                
                新数量 = int(原数量 + 数量)
                新平均成本 = (原成本 * 原数量 + 价格 * 数量) / 新数量
                
                self.持仓[品种].数量 = 新数量
                self.持仓[品种].平均成本 = 新平均成本
            else:
                # 新持仓
                self.持仓[品种] = 持仓数据(品种, int(数量), 价格)
            
            self.可用资金 -= 花费
            self.持仓市值 += 花费
            
            self._记录交易("买入", 品种, 价格, 数量)
            self._保存持仓()
            
            return {"success": True, "message": f"成功买入 {品种} {数量} 股"}
            
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
            
            收入 = 价格 * 数量
            成本 = 持仓.平均成本 * 数量
            盈亏 = 收入 - 成本
            
            持仓.数量 -= int(数量)
            if 持仓.数量 <= 0:
                del self.持仓[品种]
            
            self.可用资金 += 收入
            self.持仓市值 -= 成本
            self.总盈亏 += 盈亏
            
            self._记录交易("卖出", 品种, 价格, 数量, 盈亏)
            self._保存持仓()
            
            return {"success": True, "message": f"成功卖出 {品种} {数量} 股", "profit": 盈亏}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def 获取总资产(self):
        return self.可用资金 + self.持仓市值
    
    def 获取可用资金(self):
        return self.可用资金
    
    def 获取持仓市值(self):
        return self.持仓市值
    
    def 获取总盈亏(self):
        return self.总盈亏
    
    def _记录交易(self, 动作, 品种, 价格, 数量, 盈亏=0):
        交易 = {
            "时间": time.strftime("%Y-%m-%d %H:%M:%S"),
            "品种": 品种,
            "动作": 动作,
            "价格": 价格,
            "数量": 数量,
            "盈亏": 盈亏,
            "策略名称": ""
        }
        self.交易记录.append(交易)
        数据库.保存交易记录(交易)
    
    def _保存持仓(self):
        数据库.保存持仓快照(self.持仓)
    
    def _恢复持仓(self):
        """从数据库恢复持仓"""
        try:
            持仓数据字典 = 数据库.加载持仓快照()
            for 品种, data in 持仓数据字典.items():
                self.持仓[品种] = 持仓数据(
                    品种, 
                    data.get("数量", 0), 
                    data.get("平均成本", 0)
                )
        except Exception as e:
            print(f"恢复持仓失败: {e}")
