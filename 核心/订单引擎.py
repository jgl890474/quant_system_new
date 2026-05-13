# -*- coding: utf-8 -*-
import time
from datetime import datetime
import pytz
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
        self._last_price = {}
        
        self._恢复持仓()
        print(f"✅ 订单引擎初始化完成，初始资金: {self.初始资金:,.0f}")
    
    def _获取当前时间(self, 品种):
        """根据品种类型获取对应的时区时间"""
        try:
            if 品种 and (str(品种).isdigit() or str(品种).endswith('.SS') or str(品种).endswith('.SZ')):
                tz = pytz.timezone('Asia/Shanghai')
                now_utc = datetime.now(pytz.UTC)
                now_local = now_utc.astimezone(tz)
                return now_local.strftime("%Y-%m-%d %H:%M:%S")
            else:
                now_utc = datetime.now(pytz.UTC)
                return now_utc.strftime("%Y-%m-%d %H:%M:%S")
        except Exception:
            return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    def _获取实时价格(self, 品种):
        """获取实时价格 - 增强版"""
        try:
            from 核心 import 行情获取
            结果 = 行情获取.获取价格(品种)
            if 结果 and hasattr(结果, '价格') and 结果.价格 > 0:
                print(f"✅ 获取实时价格成功: {品种} = {结果.价格}")
                return 结果.价格
            else:
                print(f"⚠️ 获取实时价格失败: {品种} 返回空值")
        except Exception as e:
            print(f"❌ 获取实时价格异常: {品种} - {e}")
        return None
    
    def 买入(self, 品种, 价格=None, 数量=None, 手续费率=None):
        """买入 - 自动获取实时价格作为成本"""
        try:
            # 如果没有传价格，从行情获取
            if 价格 is None or 价格 <= 0:
                价格 = self._获取实时价格(品种)
                if 价格 is None or 价格 <= 0:
                    return {"success": False, "error": f"无法获取 {品种} 的实时价格，请稍后再试"}
                print(f"📊 自动获取实时价格: {品种} = {价格}")
            
            print(f"🔵 买入: {品种}, 价格={价格}, 数量={数量}")
            
            if isinstance(数量, str):
                数量 = float(数量)
            if isinstance(价格, str):
                价格 = float(价格)
            
            if 价格 <= 0:
                return {"success": False, "error": f"价格无效: {价格}"}
            if 数量 <= 0:
                return {"success": False, "error": f"数量无效: {数量}"}
            
            # ========== 关键修复：加密货币数量归一化 ==========
            # 对于市值较小的币种，数量保持原样，不进行任何转换
            # 所有加密货币的数量都直接存储，不做倍数转换
            
            使用手续费率 = 手续费率 if 手续费率 is not None else self.手续费率
            
            花费 = 价格 * 数量
            手续费 = 花费 * 使用手续费率
            总扣除 = 花费 + 手续费
            
            if 总扣除 > self.可用资金:
                return {"success": False, "error": f"资金不足，需要 ¥{总扣除:.2f}，可用 ¥{self.可用资金:.2f}"}
            
            # 更新持仓
            from 核心.数据模型 import 持仓数据
            if 品种 in self.持仓:
                原持仓 = self.持仓[品种]
                新数量 = 原持仓.数量 + 数量
                新平均成本 = (原持仓.平均成本 * 原持仓.数量 + 价格 * 数量) / 新数量
                self.持仓[品种].数量 = 新数量
                self.持仓[品种].平均成本 = 新平均成本
                print(f"📈 加仓: {品种}, 新数量={新数量}, 新成本={新平均成本:.2f}")
            else:
                self.持仓[品种] = 持仓数据(品种, 数量, 价格)
                print(f"🆕 新持仓: {品种}, 数量={数量}, 成本={价格:.2f}")
            
            self.可用资金 -= 总扣除
            self.持仓市值 += 花费
            self.累积手续费 += 手续费
            
            self._记录交易("买入", 品种, 价格, 数量, 手续费=手续费)
            self._保存持仓()
            
            return {"success": True, "message": f"成功买入 {品种} {数量} @ {价格}", "数量": 数量}
            
        except Exception as e:
            print(f"❌ 买入异常: {e}")
            return {"success": False, "error": str(e)}
    
    def 卖出(self, 品种, 价格=None, 数量=None, 手续费率=None):
        """卖出 - 自动获取实时价格"""
        try:
            # 如果没有传价格，从行情获取
            if 价格 is None or 价格 <= 0:
                价格 = self._获取实时价格(品种)
                if 价格 is None or 价格 <= 0:
                    return {"success": False, "error": f"无法获取 {品种} 的实时价格"}
                print(f"📊 自动获取实时价格: {品种} = {价格}")
            
            print(f"🔴 卖出: {品种}, 价格={价格}, 数量={数量}")
            
            if isinstance(数量, str):
                数量 = float(数量)
            if isinstance(价格, str):
                价格 = float(价格)
            
            self._恢复持仓()
            
            if 品种 not in self.持仓:
                return {"success": False, "error": f"无此持仓: {品种}"}
            
            if 价格 <= 0:
                return {"success": False, "error": f"价格无效"}
            
            持仓 = self.持仓[品种]
            if 数量 > 持仓.数量:
                return {"success": False, "error": f"卖出数量({数量})超过持仓({持仓.数量})"}
            
            收入 = 价格 * 数量
            手续费 = 收入 * 0.0003
            净收入 = 收入 - 手续费
            成本 = 持仓.平均成本 * 数量
            盈亏 = 净收入 - 成本
            
            持仓.数量 -= 数量
            if 持仓.数量 <= 0:
                del self.持仓[品种]
                print(f"🗑️ 已清空持仓: {品种}")
            
            self.可用资金 += 净收入
            self.持仓市值 -= 成本
            self.总盈亏 += 盈亏
            
            self._记录交易("卖出", 品种, 价格, 数量, 盈亏, 手续费)
            self._保存持仓()
            
            print(f"✅ 卖出成功: {品种} {数量} @ {价格}, 盈亏: {盈亏:.2f}")
            
            return {"success": True, "message": f"成功卖出 {品种} {数量} @ {价格}"}
            
        except Exception as e:
            print(f"❌ 卖出异常: {e}")
            return {"success": False, "error": str(e)}
    
    def 获取实时持仓市值(self):
        """获取实时持仓市值"""
        总市值 = 0
        for 品种, 持仓 in self.持仓.items():
            现价 = getattr(持仓, '当前价格', 持仓.平均成本)
            总市值 += 持仓.数量 * 现价
        return 总市值
    
    def 获取总资产(self):
        """获取总资产"""
        return self.可用资金 + self.获取实时持仓市值()
    
    def 获取可用资金(self):
        return self.可用资金
    
    def 获取持仓市值(self):
        return self.获取实时持仓市值()
    
    def 获取总盈亏(self):
        return self.总盈亏
    
    def 获取持仓(self):
        return self.持仓
    
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
        print("✅ 已清空所有持仓")
        return {"success": True}
    
    def 刷新持仓(self):
        self._恢复持仓()
        return {"success": True}
    
    def _记录交易(self, 动作, 品种, 价格, 数量, 盈亏=0, 手续费=0):
        交易 = {
            "时间": self._获取当前时间(品种),
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
        try:
            数据库.保存持仓快照(self.持仓)
            print(f"💾 保存持仓: {len(self.持仓)} 个品种")
        except Exception as e:
            print(f"保存持仓失败: {e}")
    
    def _恢复持仓(self):
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
                    # 直接使用数据库中的数量，不进行任何转换
                    self.持仓[品种] = 持仓数据(品种, float(数量), float(成本))
                    self.持仓市值 += 成本 * 数量
                    self.可用资金 -= 成本 * 数量
                    print(f"✅ 恢复持仓: {品种}, 数量={数量}, 成本={成本:.2f}")
            
            print(f"✅ 恢复完成，共 {len(self.持仓)} 个持仓，可用资金: {self.可用资金:.2f}")
        except Exception as e:
            print(f"恢复持仓失败: {e}")
    
    # ========== 新增：诊断工具 ==========
    def 打印持仓详情(self):
        """打印当前持仓详情（用于调试）"""
        print("\n" + "="*50)
        print("当前持仓详情")
        print("="*50)
        for 品种, pos in self.持仓.items():
            print(f"{品种}: 数量={pos.数量}, 成本={pos.平均成本:.4f}")
        print("="*50)
    
    def 修复数量单位(self, 品种, 正确数量):
        """手动修复品种的数量（用于纠正单位错误）"""
        if 品种 in self.持仓:
            self.持仓[品种].数量 = 正确数量
            self._保存持仓()
            print(f"✅ 已修复 {品种} 数量为 {正确数量}")
            return {"success": True}
        return {"success": False, "error": "品种不存在"}


def 创建订单引擎(初始资金=1000000):
    return 订单引擎(初始资金=初始资金)
