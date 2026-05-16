# -*- coding: utf-8 -*-

class 持仓对象:
    """持仓对象"""
    def __init__(self, 品种, 数量, 成本价):
        self.品种 = 品种
        self.数量 =数量
        self.平均成本 = 成本价
        self.当前价格 = 成本价
    
    def 更新价格(self, 当前价格):
        self.当前价格 = 当前价格


class 订单引擎:
    def __init__(self, 初始资金=1000000):
        self.初始资金 = 初始资金
        self.可用资金 = 初始资金
        self.持仓 = {}           # {品种: 持仓对象}
        self.交易记录 = []       # 交易记录列表
        self._历史持仓快照 = []   # 历史持仓快照
    
    def 买入(self, 品种, 价格, 数量, 策略名称=""):
        """执行买入"""
        try:
            if 价格 is None or 价格 <= 0:
                return {"success": False, "error": "价格无效"}
            
            if 数量 <= 0:
                return {"success": False, "error": "数量无效"}
            
            花费 = 价格 * 数量
            if 花费 > self.可用资金:
                return {"success": False, "error": f"资金不足，需要 ¥{花费:.2f}，可用 ¥{self.可用资金:.2f}"}
            
            # 处理已有持仓
            if 品种 in self.持仓:
                # 加仓：计算新的平均成本
                现有持仓 = self.持仓[品种]
                新数量 = 现有持仓.数量 + 数量
                新成本 = (现有持仓.平均成本 * 现有持仓.数量 + 价格 * 数量) / 新数量
                现有持仓.数量 = 新数量
                现有持仓.平均成本 = 新成本
            else:
                # 新建持仓
                self.持仓[品种] = 持仓对象(品种, 数量, 价格)
            
            self.可用资金 -= 花费
            
            # 记录交易
            交易 = {
                "时间": self._获取当前时间(),
                "品种": 品种,
                "动作": "买入",
                "价格": 价格,
                "数量": 数量,
                "金额": 花费,
                "策略名称": 策略名称,
                "盈亏": 0
            }
            self.交易记录.append(交易)
            
            print(f"✅ 买入: {品种} {数量} @ {价格} 花费 ¥{花费:.2f}")
            return {"success": True, "品种": 品种, "数量": 数量, "价格": 价格}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def 卖出(self, 品种, 价格, 数量, 策略名称=""):
        """执行卖出"""
        try:
            if 品种 not in self.持仓:
                return {"success": False, "error": f"没有持仓 {品种}"}
            
            if 价格 is None or 价格 <= 0:
                return {"success": False, "error": "价格无效"}
            
            if 数量 <= 0:
                return {"success": False, "error": "数量无效"}
            
            持仓对象 = self.持仓[品种]
            if 数量 > 持仓对象.数量:
                return {"success": False, "error": f"卖出数量超过持仓，可卖: {持仓对象.数量}"}
            
            # 计算盈亏
            收入 = 价格 * 数量
            成本 = 持仓对象.平均成本 * 数量
            盈亏 = 收入 - 成本
            
            # 更新持仓
            持仓对象.数量 -= 数量
            if 持仓对象.数量 <= 0:
                del self.持仓[品种]
            
            self.可用资金 += 收入
            
            # 记录交易
            交易 = {
                "时间": self._获取当前时间(),
                "品种": 品种,
                "动作": "卖出",
                "价格": 价格,
                "数量": 数量,
                "金额": 收入,
                "策略名称": 策略名称,
                "盈亏": 盈亏
            }
            self.交易记录.append(交易)
            
            print(f"✅ 卖出: {品种} {数量} @ {价格} 收入 ¥{收入:.2f} 盈亏 ¥{盈亏:.2f}")
            return {"success": True, "品种": 品种, "数量": 数量, "价格": 价格, "盈亏": 盈亏}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def 更新持仓价格(self, 品种, 当前价格):
        """更新持仓的当前价格"""
        if 品种 in self.持仓:
            self.持仓[品种].更新价格(当前价格)
    
    def 获取总资产(self):
        """获取总资产"""
        总市值 = 0
        for 品种, pos in self.持仓.items():
            总市值 += pos.数量 * pos.当前价格
        return self.可用资金 + 总市值
    
    def 获取可用资金(self):
        """获取可用资金"""
        return self.可用资金
    
    def 获取持仓品种列表(self):
        """获取持仓品种列表"""
        return list(self.持仓.keys())
    
    def 获取持仓信息(self, 品种):
        """获取单个持仓信息"""
        if 品种 in self.持仓:
            pos = self.持仓[品种]
            return {
                "品种": pos.品种,
                "数量": pos.数量,
                "平均成本": pos.平均成本,
                "当前价格": pos.当前价格,
                "市值": pos.数量 * pos.当前价格,
                "盈亏": (pos.当前价格 - pos.平均成本) * pos.数量,
                "盈亏率": ((pos.当前价格 - pos.平均成本) / pos.平均成本 * 100) if pos.平均成本 > 0 else 0
            }
        return None
    
    def 获取所有持仓(self):
        """获取所有持仓信息"""
        结果 = []
        for 品种, pos in self.持仓.items():
            结果.append({
                "品种": pos.品种,
                "数量": pos.数量,
                "平均成本": pos.平均成本,
                "当前价格": pos.当前价格,
                "市值": pos.数量 * pos.当前价格,
                "盈亏": (pos.当前价格 - pos.平均成本) * pos.数量,
                "盈亏率": ((pos.当前价格 - pos.平均成本) / pos.平均成本 * 100) if pos.平均成本 > 0 else 0
            })
        return 结果
    
    def 获取交易记录(self, 限制=100):
        """获取交易记录"""
        return self.交易记录[-限制:]
    
    def 清空所有持仓(self):
        """清空所有持仓"""
        self.持仓 = {}
        print("✅ 已清空所有持仓")
    
    def _获取当前时间(self):
        """获取当前时间字符串"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# 便捷函数
def 创建订单引擎(初始资金=1000000):
    return 订单引擎(初始资金)
