# -*- coding: utf-8 -*-
import time
import pytz
from datetime import datetime
import 工具.数据库 as 数据库
from 核心.数据模型 import 持仓数据


def 获取市场类型(品种):
    """根据品种代码判断市场类型"""
    品种_upper = str(品种).upper()
    
    # A股判断
    if str(品种).endswith('.SS') or str(品种).endswith('.SZ'):
        return "A股"
    if str(品种).isdigit() and len(str(品种)) == 6:
        return "A股"
    
    # 美股判断
    美股列表 = ['AAPL', 'GOOGL', 'MSFT', 'AMZN', 'TSLA', 'META', 'NVDA', 'NFLX', 'AMD', 'INTC', 'IBM', 'ORCL', 'CSCO', 'ADBE', 'CRM', 'PYPL', 'DIS', 'UBER', 'COIN']
    if 品种_upper in 美股列表 or (品种_upper.isalpha() and len(品种_upper) <= 5):
        return "美股"
    
    # 加密货币判断
    加密货币列表 = ['BTC', 'ETH', 'BNB', 'SOL', 'XRP', 'DOGE', 'ADA', 'AVAX', 'USDT']
    if any(crypto in 品种_upper for crypto in 加密货币列表) or '-' in 品种:
        return "加密货币"
    
    return "其他"


def 获取交易时间(品种):
    """根据品种获取正确的交易时间"""
    now = datetime.now()
    市场 = 获取市场类型(品种)
    
    try:
        if 市场 == "A股":
            # A股使用北京时间（东八区）
            tz = pytz.timezone('Asia/Shanghai')
            beijing_time = now.astimezone(tz)
            return beijing_time.strftime("%Y-%m-%d %H:%M:%S")
        elif 市场 == "美股":
            # 美股使用美东时间
            tz = pytz.timezone('America/New_York')
            us_time = now.astimezone(tz)
            return us_time.strftime("%Y-%m-%d %H:%M:%S")
        else:
            # 加密货币等使用UTC
            return now.strftime("%Y-%m-%d %H:%M:%S")
    except:
        # 如果没有安装pytz，使用本地时间
        return now.strftime("%Y-%m-%d %H:%M:%S")


class 订单引擎:
    def __init__(self, 初始资金=1000000, 手续费率=0.0003, **kwargs):
        """
        初始化订单引擎
        参数:
            初始资金: 初始资金金额（默认100万）
            手续费率: 默认手续费率（默认万分之三 = 0.0003）
            **kwargs: 兼容其他参数（如 INITIAL_CAPITAL）
        """
        # 兼容英文参数名
        if 'initial_capital' in kwargs:
            self.初始资金 = kwargs['initial_capital']
        elif 'INITIAL_CAPITAL' in kwargs:
            self.初始资金 = kwargs['INITIAL_CAPITAL']
        else:
            self.初始资金 = 初始资金
        
        self.手续费率 = 手续费率
        self.可用资金 = self.初始资金
        self.持仓市值 = 0
        self.总盈亏 = 0
        self.累积手续费 = 0
        self.持仓 = {}
        self.交易记录 = []
        
        # 从数据库恢复持仓
        self._恢复持仓()
    
    def 买入(self, 品种, 价格, 数量, 手续费率=None):
        """
        买入 - 支持多品种持仓
        参数:
            品种: 品种代码
            价格: 买入价格
            数量: 买入数量
            手续费率: 可选，覆盖默认手续费率
        """
        try:
            使用手续费率 = 手续费率 if 手续费率 is not None else self.手续费率
            
            花费 = 价格 * 数量
            手续费 = 花费 * 使用手续费率
            总扣除 = 花费 + 手续费
            
            if 总扣除 > self.可用资金:
                return {
                    "success": False, 
                    "error": f"资金不足，需要 ¥{总扣除:.2f}（含手续费 ¥{手续费:.2f}），可用 ¥{self.可用资金:.2f}"
                }
            
            if 品种 in self.持仓:
                # 加仓
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
            
            self.可用资金 -= 总扣除
            self.持仓市值 += 花费
            self.累积手续费 += 手续费
            
            self._记录交易("买入", 品种, 价格, 数量, 手续费=手续费)
            self._保存持仓()
            
            return {
                "success": True, 
                "message": f"成功买入 {品种} {数量} 股",
                "amount": 花费,
                "fee": 手续费,
                "total_cost": 总扣除
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def 卖出(self, 品种, 价格, 数量, 手续费率=None):
        """
        卖出
        参数:
            品种: 品种代码
            价格: 卖出价格
            数量: 卖出数量
            手续费率: 可选，覆盖默认手续费率
        """
        try:
            if 品种 not in self.持仓:
                return {"success": False, "error": "无此持仓"}
            
            使用手续费率 = 手续费率 if 手续费率 is not None else self.手续费率
            
            持仓 = self.持仓[品种]
            if 数量 > 持仓.数量:
                return {"success": False, "error": f"卖出数量超过持仓，当前持仓 {持仓.数量} 股"}
            
            收入 = 价格 * 数量
            手续费 = 收入 * 使用手续费率
            净收入 = 收入 - 手续费
            成本 = 持仓.平均成本 * 数量
            盈亏 = 净收入 - 成本
            
            # 更新持仓数量
            持仓.数量 -= 数量
            if 持仓.数量 <= 0:
                del self.持仓[品种]
            
            self.可用资金 += 净收入
            self.持仓市值 -= 成本
            self.总盈亏 += 盈亏
            self.累积手续费 += 手续费
            
            self._记录交易("卖出", 品种, 价格, 数量, 盈亏, 手续费)
            self._保存持仓()
            
            return {
                "success": True, 
                "message": f"成功卖出 {品种} {数量} 股",
                "profit": 盈亏,
                "fee": 手续费,
                "net_income": 净收入
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def 获取总资产(self):
        """获取总资产（可用资金 + 持仓市值）"""
        return self.可用资金 + self.持仓市值
    
    def 获取可用资金(self):
        """获取可用资金"""
        return self.可用资金
    
    def 获取持仓市值(self):
        """获取持仓市值"""
        return self.持仓市值
    
    def 获取总盈亏(self):
        """获取已实现总盈亏"""
        return self.总盈亏
    
    def 获取浮动盈亏(self, 品种=None, 当前价格=None):
        """
        获取浮动盈亏
        参数:
            品种: 指定品种，不传则计算全部
            当前价格: 指定品种的当前价格
        """
        if 品种:
            if 品种 in self.持仓:
                持仓 = self.持仓[品种]
                if 当前价格 is not None:
                    持仓.当前价格 = 当前价格
                return (持仓.当前价格 - 持仓.平均成本) * 持仓.数量
            return 0
        else:
            总浮动盈亏 = 0
            for 代码, 持仓 in self.持仓.items():
                总浮动盈亏 += (持仓.当前价格 - 持仓.平均成本) * 持仓.数量
            return 总浮动盈亏
    
    def 获取总资产含浮动盈亏(self):
        """获取总资产（含浮动盈亏）"""
        return self.可用资金 + self.持仓市值
    
    def 获取总收益率(self):
        """获取总收益率（含浮动盈亏）"""
        总资产 = self.获取总资产含浮动盈亏()
        return (总资产 - self.初始资金) / self.初始资金 * 100
    
    def 获取累积手续费(self):
        """获取累积手续费"""
        return self.累积手续费
    
    def 获取持仓(self):
        """获取所有持仓"""
        return self.持仓
    
    def 获取持仓详情(self):
        """获取持仓详情（含浮动盈亏）"""
        详情 = []
        for 代码, 持仓 in self.持仓.items():
            现价 = getattr(持仓, '当前价格', 持仓.平均成本)
            市值 = 持仓.数量 * 现价
            成本 = 持仓.数量 * 持仓.平均成本
            浮动盈亏 = 市值 - 成本
            浮动盈亏率 = (浮动盈亏 / 成本 * 100) if 成本 > 0 else 0
            详情.append({
                "品种": 代码,
                "数量": int(持仓.数量),
                "成本价": round(持仓.平均成本, 4),
                "现价": round(现价, 4),
                "市值": round(市值, 2),
                "成本总额": round(成本, 2),
                "浮动盈亏": round(浮动盈亏, 2),
                "浮动盈亏率": round(浮动盈亏率, 2)
            })
        return 详情
    
    def 获取交易记录(self):
        """获取交易记录"""
        return self.交易记录
    
    def 获取初始资金(self):
        """获取初始资金"""
        return self.初始资金
    
    def 获取手续费率(self):
        """获取手续费率"""
        return self.手续费率
    
    def 设置手续费率(self, 手续费率):
        """设置默认手续费率"""
        self.手续费率 = 手续费率
        return {"success": True, "message": f"手续费率已设置为 {手续费率*100:.3f}%"}
    
    def 清空所有持仓(self):
        """清空所有持仓"""
        self.持仓 = {}
        self.可用资金 = self.初始资金
        self.持仓市值 = 0
        self.总盈亏 = 0
        self.累积手续费 = 0
        self.交易记录 = []
        数据库.清空所有持仓()
        print("✅ 已清空所有持仓")
        return {"success": True, "message": "已清空所有持仓"}
    
    def 重置引擎(self, 初始资金=None, 手续费率=None):
        """重置订单引擎"""
        if 初始资金 is not None:
            self.初始资金 = 初始资金
        if 手续费率 is not None:
            self.手续费率 = 手续费率
        
        self.可用资金 = self.初始资金
        self.持仓市值 = 0
        self.总盈亏 = 0
        self.累积手续费 = 0
        self.持仓 = {}
        self.交易记录 = []
        self._保存持仓()
        print("✅ 订单引擎已重置")
        return {"success": True, "message": "引擎已重置"}
    
    def 更新持仓价格(self, 品种, 当前价格):
        """更新持仓的当前价格"""
        if 品种 in self.持仓:
            self.持仓[品种].当前价格 = 当前价格
    
    def 批量更新价格(self, 价格字典):
        """批量更新持仓价格"""
        for 品种, 价格 in 价格字典.items():
            self.更新持仓价格(品种, 价格)
    
    def 获取账户摘要(self):
        """获取账户摘要信息"""
        总资产 = self.获取总资产()
        总收益率 = self.获取总收益率()
        浮动盈亏 = self.获取浮动盈亏()
        
        return {
            "初始资金": self.初始资金,
            "可用资金": self.可用资金,
            "持仓市值": self.持仓市值,
            "总资产": 总资产,
            "总收益率": 总收益率,
            "浮动盈亏": 浮动盈亏,
            "已实现盈亏": self.总盈亏,
            "累积手续费": self.累积手续费,
            "持仓数量": len(self.持仓)
        }
    
    def _记录交易(self, 动作, 品种, 价格, 数量, 盈亏=0, 手续费=0):
        """记录交易 - 使用正确的市场时间"""
        交易 = {
            "时间": 获取交易时间(品种),  # 使用修正后的时间
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
                # 更新持仓市值
                self.持仓市值 += data.get("平均成本", 0) * data.get("数量", 0)
                # 更新可用资金（减去持仓成本）
                self.可用资金 -= data.get("平均成本", 0) * data.get("数量", 0)
            print(f"✅ 已恢复 {len(self.持仓)} 个持仓")
        except Exception as e:
            print(f"恢复持仓失败: {e}")


# 兼容性函数 - 供其他模块导入
def 创建订单引擎(初始资金=1000000, 手续费率=0.0003):
    """创建订单引擎实例"""
    return 订单引擎(初始资金=初始资金, 手续费率=手续费率)
Traceback:
File "/mount/src/quant_system_new/启动入口.py", line 28, in <module>
    st.session_state.订单引擎 = 订单引擎()
                                ~~~~~~~~^^
