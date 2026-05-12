# -*- coding: utf-8 -*-
import time
from datetime import datetime
import 工具.数据库 as 数据库


class 订单引擎:
    def __init__(self, 初始资金=1000000, **kwargs):
        self.初始资金 = 初始资金
        self.手续费率 = 0.0003
        self.可用资金 = self.初始资金
        self.持仓市值 = 0
        self.总盈亏 = 0
        self.累积手续费 = 0
        self.持仓 = {}
        self.交易记录 = []
        # 记录已处理的价格，避免重复卖出
        self._last_price = {}
        self._恢复持仓()
    
    def 买入(self, 品种, 价格, 数量, 手续费率=None):
        """买入"""
        try:
            print(f"🔵 买入请求: 品种={品种}, 价格={价格}, 数量={数量}")
            
            if 价格 <= 0:
                return {"success": False, "error": f"价格无效: {价格}"}
            if 数量 <= 0:
                return {"success": False, "error": f"数量无效: {数量}"}
            
            使用手续费率 = 手续费率 if 手续费率 is not None else self.手续费率
            
            花费 = 价格 * 数量
            手续费 = 花费 * 使用手续费率
            总扣除 = 花费 + 手续费
            
            if 总扣除 > self.可用资金:
                return {
                    "success": False, 
                    "error": f"资金不足，需要 ¥{总扣除:.2f}，可用 ¥{self.可用资金:.2f}"
                }
            
            # 更新持仓
            if 品种 in self.持仓:
                原持仓 = self.持仓[品种]
                原数量 = 原持仓.数量
                原成本 = 原持仓.平均成本
                
                新数量 = 原数量 + 数量
                新平均成本 = (原成本 * 原数量 + 价格 * 数量) / 新数量
                
                self.持仓[品种].数量 = 新数量
                self.持仓[品种].平均成本 = 新平均成本
                print(f"📈 加仓: {品种}, 新数量={新数量}, 新成本={新平均成本:.2f}")
            else:
                from 核心.数据模型 import 持仓数据
                self.持仓[品种] = 持仓数据(品种, 数量, 价格)
                print(f"🆕 新持仓: {品种}, 数量={数量}, 成本={价格:.2f}")
            
            self.可用资金 -= 总扣除
            self.持仓市值 += 花费
            self.累积手续费 += 手续费
            
            self._记录交易("买入", 品种, 价格, 数量, 手续费=手续费)
            self._保存持仓()
            
            return {
                "success": True, 
                "message": f"成功买入 {品种} {数量}",
                "amount": 花费,
                "fee": 手续费
            }
            
        except Exception as e:
            print(f"❌ 买入异常: {e}")
            return {"success": False, "error": str(e)}
    
    def 卖出(self, 品种, 价格, 数量, 手续费率=None):
        """卖出 - 确保正确删除持仓"""
        try:
            print(f"🔴 卖出请求: 品种={品种}, 价格={价格}, 数量={数量}")
            
            # 先刷新持仓（从数据库恢复）
            self._恢复持仓()
            
            if 品种 not in self.持仓:
                return {"success": False, "error": f"无此持仓: {品种}"}
            
            if 价格 <= 0:
                return {"success": False, "error": f"价格无效: {价格}"}
            
            # 防止同一价格重复卖出
            price_key = f"{品种}_{价格}"
            if price_key in self._last_price:
                return {"success": False, "error": "请勿重复提交"}
            self._last_price[price_key] = time.time()
            
            使用手续费率 = 手续费率 if 手续费率 is not None else self.手续费率
            
            持仓 = self.持仓[品种]
            
            # 处理浮点数精度问题
            if abs(数量 - 持仓.数量) < 0.0001:
                数量 = 持仓.数量
            
            if 数量 > 持仓.数量:
                return {"success": False, "error": f"卖出数量({数量})超过持仓({持仓.数量})"}
            
            收入 = 价格 * 数量
            手续费 = 收入 * 使用手续费率
            净收入 = 收入 - 手续费
            成本 = 持仓.平均成本 * 数量
            盈亏 = 净收入 - 成本
            
            # 更新持仓数量
            持仓.数量 -= 数量
            
            # 如果数量为0，删除该持仓
            if 持仓.数量 <= 0.0001:
                del self.持仓[品种]
                print(f"🗑️ 已删除持仓: {品种}")
            
            # 更新资金
            self.可用资金 += 净收入
            self.持仓市值 -= 成本
            self.总盈亏 += 盈亏
            self.累积手续费 += 手续费
            
            # 记录交易
            self._记录交易("卖出", 品种, 价格, 数量, 盈亏, 手续费)
            
            # 关键：保存持仓到数据库
            self._保存持仓()
            
            print(f"✅ 卖出成功! 剩余持仓: {list(self.持仓.keys())}")
            
            return {
                "success": True, 
                "message": f"成功卖出 {品种} {数量}",
                "profit": 盈亏,
                "fee": 手续费,
                "remaining": len(self.持仓)
            }
            
        except Exception as e:
            print(f"❌ 卖出异常: {e}")
            return {"success": False, "error": str(e)}
    
    def 获取总资产(self):
        """获取总资产（需要实时计算持仓市值）"""
        # 重新计算持仓市值
        总持仓市值 = 0
        for 品种, 持仓 in self.持仓.items():
            当前价格 = getattr(持仓, '当前价格', 持仓.平均成本)
            总持仓市值 += 持仓.数量 * 当前价格
        return self.可用资金 + 总持仓市值
    
    def 获取可用资金(self):
        return self.可用资金
    
    def 获取持仓市值(self):
        """获取持仓市值"""
        总市值 = 0
        for 品种, 持仓 in self.持仓.items():
            当前价格 = getattr(持仓, '当前价格', 持仓.平均成本)
            总市值 += 持仓.数量 * 当前价格
        return 总市值
    
    def 获取总盈亏(self):
        return self.总盈亏
    
    def 获取持仓(self):
        return self.持仓
    
    def 获取持仓详情(self):
        详情 = []
        for 代码, 持仓 in self.持仓.items():
            现价 = getattr(持仓, '当前价格', 持仓.平均成本)
            市值 = 持仓.数量 * 现价
            成本 = 持仓.数量 * 持仓.平均成本
            浮动盈亏 = 市值 - 成本
            详情.append({
                "品种": 代码,
                "数量": 持仓.数量,
                "成本价": round(持仓.平均成本, 4),
                "现价": round(现价, 4),
                "市值": round(市值, 2),
                "成本总额": round(成本, 2),
                "浮动盈亏": round(浮动盈亏, 2),
            })
        return 详情
    
    def 获取交易记录(self):
        return self.交易记录[-100:]  # 只返回最近100条
    
    def 获取初始资金(self):
        return self.初始资金
    
    def 清空所有持仓(self):
        self.持仓 = {}
        self.可用资金 = self.初始资金
        self.持仓市值 = 0
        self.总盈亏 = 0
        self.累积手续费 = 0
        self.交易记录 = []
        数据库.清空所有持仓()
        return {"success": True}
    
    def 更新持仓价格(self, 品种, 当前价格):
        if 品种 in self.持仓:
            self.持仓[品种].当前价格 = 当前价格
    
    def 刷新持仓(self):
        """手动刷新持仓（从数据库恢复）"""
        self._恢复持仓()
        return {"success": True, "count": len(self.持仓)}
    
    def 同步到session(self):
        """返回自身，用于 session_state 更新"""
        return self
    
    def _记录交易(self, 动作, 品种, 价格, 数量, 盈亏=0, 手续费=0):
        交易 = {
            "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "品种": 品种,
            "动作": 动作,
            "价格": 价格,
            "数量": 数量,
            "盈亏": 盈亏,
            "手续费": 手续费,
            "策略名称": ""
        }
        self.交易记录.append(交易)
        数据库.保存交易记录(交易)
    
    def _保存持仓(self):
        """保存持仓到数据库"""
        try:
            数据库.保存持仓快照(self.持仓)
            print(f"💾 保存持仓快照, 共{len(self.持仓)}个持仓")
        except Exception as e:
            print(f"保存持仓失败: {e}")
    
    def _恢复持仓(self):
        """从数据库恢复持仓"""
        try:
            持仓数据字典 = 数据库.加载持仓快照()
            from 核心.数据模型 import 持仓数据
            self.持仓 = {}
            self.持仓市值 = 0
            self.可用资金 = self.初始资金
            
            for 品种, data in 持仓数据字典.items():
                数量 = data.get("数量", 0)
                成本 = data.get("平均成本", 0)
                if 数量 > 0:
                    self.持仓[品种] = 持仓数据(品种, 数量, 成本)
                    self.持仓市值 += 成本 * 数量
                    self.可用资金 -= 成本 * 数量
                    print(f"✅ 恢复持仓: {品种}, 数量={数量}, 成本={成本:.2f}")
            
            print(f"✅ 已恢复 {len(self.持仓)} 个持仓, 可用资金: {self.可用资金:.2f}")
        except Exception as e:
            print(f"恢复持仓失败: {e}")


def 创建订单引擎(初始资金=1000000):
    return 订单引擎(初始资金=初始资金)
