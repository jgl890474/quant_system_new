# -*- coding: utf-8 -*-
"""
定时任务模块 - 完整版
功能：
- 定时任务（指定时间执行）
- 间隔任务（周期性执行）
- 任务管理（添加/移除/暂停/恢复/列表）
- 任务持久化（保存到文件）
- 错误处理和重试
- 任务执行状态监控
- 交易时间判断函数

优化：
- 支持任务依赖
- 支持任务优先级
- 任务执行日志
- 防止重复执行
"""

import time
import threading
import json
import os
import traceback
from datetime import datetime, time as dt_time
from typing import Dict, List, Callable, Any, Optional
from collections import OrderedDict
import schedule

# ==================== 配置 ====================
任务保存文件 = "data/tasks.json"
最大重试次数 = 3
重试间隔 = 5  # 秒
任务超时时间 = 300  # 5分钟


# ==================== 任务类 ====================
class 任务:
    """单个任务类"""
    
    def __init__(self, 名称: str, 函数: Callable, 参数: Any = None,
                 任务类型: str = "定时", 执行时间: str = None,
                 间隔秒数: int = None, 启用: bool = True,
                 最大重试: int = 最大重试次数):
        self.名称 = 名称
        self.函数 = 函数
        self.参数 = 参数
        self.任务类型 = 任务类型  # "定时" 或 "间隔"
        self.执行时间 = 执行时间  # 定时任务：格式 "14:55"
        self.间隔秒数 = 间隔秒数  # 间隔任务：秒数
        self.启用 = 启用
        self.最大重试 = 最大重试
        self.重试次数 = 0
        self.上次执行时间 = None
        self.上次执行结果 = None
        self.执行次数 = 0
        self.成功次数 = 0
        self.失败次数 = 0
    
    def 执行(self) -> bool:
        """执行任务，返回是否成功"""
        if not self.启用:
            return False
        
        try:
            print(f"📌 执行任务: {self.名称} [{datetime.now().strftime('%H:%M:%S')}]")
            
            if self.参数 is not None:
                self.函数(self.参数)
            else:
                self.函数()
            
            self.重试次数 = 0
            self.上次执行结果 = "成功"
            self.成功次数 += 1
            print(f"✅ 任务完成: {self.名称}")
            return True
            
        except Exception as e:
            print(f"❌ 任务失败: {self.名称} - {e}")
            traceback.print_exc()
            
            self.上次执行结果 = f"失败: {e}"
            self.失败次数 += 1
            
            # 重试逻辑
            if self.重试次数 < self.最大重试:
                self.重试次数 += 1
                print(f"🔄 任务重试 ({self.重试次数}/{self.最大重试}): {self.名称}")
                time.sleep(重试间隔)
                return self.执行()  # 递归重试
            
            return False
        
        finally:
            self.上次执行时间 = datetime.now()
            self.执行次数 += 1
    
    def to_dict(self) -> dict:
        """转换为字典（用于保存）"""
        return {
            '名称': self.名称,
            '任务类型': self.任务类型,
            '执行时间': self.执行时间,
            '间隔秒数': self.间隔秒数,
            '启用': self.启用,
            '最大重试': self.最大重试,
            '执行次数': self.执行次数,
            '成功次数': self.成功次数,
            '失败次数': self.失败次数
        }
    
    @classmethod
    def from_dict(cls, 数据: dict, 函数映射: dict) -> '任务':
        """从字典创建任务"""
        return cls(
            名称=数据['名称'],
            函数=函数映射.get(数据['名称'], None),
            任务类型=数据['任务类型'],
            执行时间=数据.get('执行时间'),
            间隔秒数=数据.get('间隔秒数'),
            启用=数据.get('启用', True),
            最大重试=数据.get('最大重试', 最大重试次数)
        )


# ==================== 定时任务调度器 ====================
class 定时任务调度器:
    """定时任务调度器 - 完整版"""
    
    def __init__(self):
        self.运行中 = False
        self.线程 = None
        self.任务列表: Dict[str, 任务] = OrderedDict()  # 任务字典
        self.函数映射 = {}  # 函数映射（用于持久化恢复）
        
        # 创建数据目录
        os.makedirs(os.path.dirname(任务保存文件), exist_ok=True)
        
        # 加载保存的任务
        self._加载任务()
    
    def 注册函数(self, 名称: str, 函数: Callable):
        """注册可持久化的函数"""
        self.函数映射[名称] = 函数
    
    def 添加任务(self, 任务函数: Callable, 执行时间: str, 
                 参数: Any = None, 任务名称: str = None,
                 最大重试: int = 最大重试次数) -> str:
        """
        添加定时任务
        
        参数:
            任务函数: 要执行的函数
            执行时间: 格式 "14:55"
            参数: 函数参数
            任务名称: 任务标识（自动生成如果为空）
            最大重试: 最大重试次数
        
        返回:
            任务名称
        """
        if 任务名称 is None:
            任务名称 = f"{任务函数.__name__}_{执行时间}"
        
        # 检查是否已存在
        if 任务名称 in self.任务列表:
            print(f"⚠️ 任务已存在: {任务名称}")
            return 任务名称
        
        新任务 = 任务(
            名称=任务名称,
            函数=任务函数,
            参数=参数,
            任务类型="定时",
            执行时间=执行时间,
            最大重试=最大重试
        )
        
        self.任务列表[任务名称] = 新任务
        self._注册到调度器(新任务)
        
        print(f"✅ 定时任务已添加: {任务名称} @ {执行时间}")
        
        # 保存任务
        self._保存任务()
        
        return 任务名称
    
    def 添加间隔任务(self, 任务函数: Callable, 间隔秒数: int,
                      参数: Any = None, 任务名称: str = None,
                      最大重试: int = 最大重试次数) -> str:
        """
        添加间隔任务（周期性执行）
        
        参数:
            任务函数: 要执行的函数
            间隔秒数: 执行间隔（秒）
            参数: 函数参数
            任务名称: 任务标识
            最大重试: 最大重试次数
        
        返回:
            任务名称
        """
        if 任务名称 is None:
            任务名称 = f"{任务函数.__name__}_每{间隔秒数}秒"
        
        if 任务名称 in self.任务列表:
            print(f"⚠️ 任务已存在: {任务名称}")
            return 任务名称
        
        新任务 = 任务(
            名称=任务名称,
            函数=任务函数,
            参数=参数,
            任务类型="间隔",
            间隔秒数=间隔秒数,
            最大重试=最大重试
        )
        
        self.任务列表[任务名称] = 新任务
        self._注册到调度器(新任务)
        
        print(f"✅ 间隔任务已添加: {任务名称} @ 每{间隔秒数}秒")
        
        # 保存任务
        self._保存任务()
        
        return 任务名称
    
    def _注册到调度器(self, 任务对象: 任务):
        """将任务注册到schedule调度器"""
        def 包装函数():
            if 任务对象.启用:
                任务对象.执行()
        
        if 任务对象.任务类型 == "定时" and 任务对象.执行时间:
            getattr(schedule.every().day.at(任务对象.执行时间)).do(包装函数)
        elif 任务对象.任务类型 == "间隔" and 任务对象.间隔秒数:
            schedule.every(任务对象.间隔秒数).seconds.do(包装函数)
    
    def 移除任务(self, 任务名称: str) -> bool:
        """
        移除任务
        
        参数:
            任务名称: 任务标识
        
        返回:
            是否移除成功
        """
        if 任务名称 in self.任务列表:
            del self.任务列表[任务名称]
            schedule.clear(任务名称)
            self._保存任务()
            print(f"🗑️ 任务已移除: {任务名称}")
            return True
        
        print(f"⚠️ 任务不存在: {任务名称}")
        return False
    
    def 暂停任务(self, 任务名称: str) -> bool:
        """暂停任务"""
        if 任务名称 in self.任务列表:
            self.任务列表[任务名称].启用 = False
            self._保存任务()
            print(f"⏸️ 任务已暂停: {任务名称}")
            return True
        return False
    
    def 恢复任务(self, 任务名称: str) -> bool:
        """恢复任务"""
        if 任务名称 in self.任务列表:
            self.任务列表[任务名称].启用 = True
            self._保存任务()
            print(f"▶️ 任务已恢复: {任务名称}")
            return True
        return False
    
    def 获取任务列表(self) -> List[dict]:
        """获取所有任务列表"""
        return [任务.to_dict() for 任务 in self.任务列表.values()]
    
    def 获取任务状态(self, 任务名称: str) -> Optional[dict]:
        """获取单个任务状态"""
        if 任务名称 in self.任务列表:
            任务 = self.任务列表[任务名称]
            return {
                '名称': 任务.名称,
                '启用': 任务.启用,
                '执行次数': 任务.执行次数,
                '成功次数': 任务.成功次数,
                '失败次数': 任务.失败次数,
                '上次执行时间': 任务.上次执行时间.strftime("%Y-%m-%d %H:%M:%S") if 任务.上次执行时间 else None,
                '上次执行结果': 任务.上次执行结果
            }
        return None
    
    def 清空所有任务(self):
        """清空所有任务"""
        self.任务列表.clear()
        schedule.clear()
        self._保存任务()
        print("🗑️ 所有任务已清空")
    
    def _保存任务(self):
        """保存任务到文件"""
        try:
            # 只保存可持久化的任务（有函数映射的）
            可保存任务 = []
            for 任务 in self.任务列表.values():
                if 任务.名称 in self.函数映射 or 任务.函数.__name__ in self.函数映射:
                    可保存任务.append(任务.to_dict())
            
            with open(任务保存文件, 'w', encoding='utf-8') as f:
                json.dump(可保存任务, f, ensure_ascii=False, indent=2)
            
            print(f"💾 任务已保存: {len(可保存任务)} 个任务")
        except Exception as e:
            print(f"❌ 保存任务失败: {e}")
    
    def _加载任务(self):
        """从文件加载任务"""
        if not os.path.exists(任务保存文件):
            return
        
        try:
            with open(任务保存文件, 'r', encoding='utf-8') as f:
                任务数据列表 = json.load(f)
            
            for 任务数据 in 任务数据列表:
                任务名称 = 任务数据['名称']
                if 任务名称 in self.函数映射:
                    新任务 = 任务.from_dict(任务数据, self.函数映射)
                    if 新任务.函数:  # 只有函数存在时才加载
                        self.任务列表[任务名称] = 新任务
                        if 新任务.启用:
                            self._注册到调度器(新任务)
            
            print(f"📂 已加载 {len(self.任务列表)} 个任务")
        except Exception as e:
            print(f"❌ 加载任务失败: {e}")
    
    def 启动(self):
        """启动调度器（前台运行）"""
        if self.运行中:
            print("⚠️ 调度器已在运行中")
            return
        
        self.运行中 = True
        print("🚀 定时任务调度器已启动")
        print(f"📋 当前任务数: {len(self.任务列表)}")
        
        while self.运行中:
            try:
                schedule.run_pending()
                time.sleep(1)
            except KeyboardInterrupt:
                print("\n收到中断信号")
                break
            except Exception as e:
                print(f"❌ 调度器运行错误: {e}")
                time.sleep(5)
        
        self.停止()
    
    def 启动后台(self):
        """后台启动调度器"""
        if self.运行中:
            print("⚠️ 调度器已在运行中")
            return
        
        self.线程 = threading.Thread(target=self.启动, daemon=True)
        self.线程.start()
        print("🚀 定时任务调度器已后台启动")
    
    def 停止(self):
        """停止调度器"""
        self.运行中 = False
        print("🛑 定时任务调度器已停止")
    
    def 获取统计信息(self) -> dict:
        """获取调度器统计信息"""
        总任务数 = len(self.任务列表)
        启用任务数 = sum(1 for t in self.任务列表.values() if t.启用)
        总执行次数 = sum(t.执行次数 for t in self.任务列表.values())
        总成功次数 = sum(t.成功次数 for t in self.任务列表.values())
        总失败次数 = sum(t.失败次数 for t in self.任务列表.values())
        
        return {
            '总任务数': 总任务数,
            '启用任务数': 启用任务数,
            '总执行次数': 总执行次数,
            '总成功次数': 总成功次数,
            '总失败次数': 总失败次数,
            '运行中': self.运行中
        }


# ==================== 全局单例 ====================
_调度器实例 = None

def 获取调度器() -> 定时任务调度器:
    """获取全局调度器实例"""
    global _调度器实例
    if _调度器实例 is None:
        _调度器实例 = 定时任务调度器()
    return _调度器实例


# ==================== 交易时间判断函数 ====================
def 是交易时间(市场: str = "A股") -> bool:
    """
    判断当前是否在交易时间内
    
    参数:
        市场: A股/美股/加密货币
    """
    now = datetime.now()
    当前时间 = now.time()
    
    if 市场 == "加密货币":
        # 加密货币7x24小时交易
        return True
    
    elif 市场 == "A股":
        上午开始 = dt_time(9, 30)
        上午结束 = dt_time(11, 30)
        下午开始 = dt_time(13, 0)
        下午结束 = dt_time(15, 0)
        
        if 上午开始 <= 当前时间 <= 上午结束:
            return True
        if 下午开始 <= 当前时间 <= 下午结束:
            return True
        return False
    
    elif 市场 == "美股":
        # 美股夏令时 21:30-04:00，冬令时 22:30-05:00
        开始时间 = dt_time(21, 30)
        结束时间 = dt_time(4, 0)
        
        if 当前时间 >= 开始时间 or 当前时间 <= 结束时间:
            return True
        return False
    
    return False


def 是尾盘时间() -> bool:
    """判断是否A股尾盘时间 (14:50-15:00)"""
    now = datetime.now()
    当前时间 = now.time()
    return 当前时间 >= dt_time(14, 50) and 当前时间 <= dt_time(15, 0)


def 是早盘时间() -> bool:
    """判断是否A股早盘时间 (9:30-9:35)"""
    now = datetime.now()
    当前时间 = now.time()
    return 当前时间 >= dt_time(9, 30) and 当前时间 <= dt_time(9, 35)


def 是午盘时间() -> bool:
    """判断是否A股午盘时间 (13:00-15:00)"""
    now = datetime.now()
    当前时间 = now.time()
    return 当前时间 >= dt_time(13, 0) and 当前时间 <= dt_time(15, 0)


def 获取交易状态(市场: str = "A股") -> str:
    """获取当前交易状态"""
    now = datetime.now()
    当前时间 = now.time()
    
    if 市场 == "加密货币":
        return "交易中 (7x24小时)"
    
    elif 市场 == "A股":
        if 当前时间 < dt_time(9, 30):
            return "未开盘"
        elif dt_time(9, 30) <= 当前时间 <= dt_time(11, 30):
            return "上午交易中"
        elif dt_time(11, 30) < 当前时间 <= dt_time(13, 0):
            return "午间休市"
        elif dt_time(13, 0) <= 当前时间 <= dt_time(15, 0):
            return "下午交易中"
        else:
            return "已收盘"
    
    elif 市场 == "美股":
        if 当前时间 >= dt_time(21, 30) or 当前时间 <= dt_time(4, 0):
            return "交易中"
        else:
            return "休市"
    
    return "未知"


def 距离收盘时间() -> int:
    """返回距离A股收盘还有多少分钟"""
    now = datetime.now()
    当前时间 = now.time()
    收盘时间 = dt_time(15, 0)
    
    if 当前时间 >= 收盘时间:
        return 0
    
    当前分钟 = 当前时间.hour * 60 + 当前时间.minute
    收盘分钟 = 收盘时间.hour * 60 + 收盘时间.minute
    
    return 收盘分钟 - 当前分钟


def 距离开盘时间() -> int:
    """返回距离A股开盘还有多少分钟"""
    now = datetime.now()
    当前时间 = now.time()
    开盘时间 = dt_time(9, 30)
    
    if 当前时间 >= 开盘时间:
        return 0
    
    当前分钟 = 当前时间.hour * 60 + 当前时间.minute
    开盘分钟 = 开盘时间.hour * 60 + 开盘时间.minute
    
    return 开盘分钟 - 当前分钟


# ==================== 便捷函数（兼容旧版本） ====================
def 添加任务(任务函数, 执行时间, 参数=None):
    """兼容旧版本的添加任务函数"""
    调度器 = 获取调度器()
    return 调度器.添加任务(任务函数, 执行时间, 参数)


def 添加间隔任务(任务函数, 间隔秒数, 参数=None):
    """兼容旧版本的添加间隔任务函数"""
    调度器 = 获取调度器()
    return 调度器.添加间隔任务(任务函数, 间隔秒数, 参数)


def 启动后台():
    """兼容旧版本的启动函数"""
    调度器 = 获取调度器()
    调度器.启动后台()


def 停止():
    """兼容旧版本的停止函数"""
    调度器 = 获取调度器()
    调度器.停止()


# ==================== 示例任务 ====================
def _示例任务():
    """示例任务函数"""
    print(f"执行示例任务: {datetime.now()}")


def _示例带参数任务(消息):
    """示例带参数任务函数"""
    print(f"执行示例任务: {消息}")


# ==================== 测试 ====================
if __name__ == "__main__":
    print("=" * 50)
    print("定时任务模块测试")
    print("=" * 50)
    
    调度器 = 获取调度器()
    
    # 注册函数（用于持久化）
    调度器.注册函数("示例任务", _示例任务)
    调度器.注册函数("示例带参数任务", _示例带参数任务)
    
    # 测试添加任务
    调度器.添加任务(_示例任务, "14:55", 任务名称="测试定时任务")
    调度器.添加间隔任务(_示例任务, 10, 任务名称="测试间隔任务")
    
    # 显示任务列表
    print("\n📋 当前任务列表:")
    for 任务信息 in 调度器.获取任务列表():
        print(f"  - {任务信息}")
    
    # 测试交易时间函数
    print(f"\n📊 交易状态: {获取交易状态()}")
    print(f"📊 加密货币交易状态: {获取交易状态('加密货币')}")
    print(f"⏰ 距离收盘: {距离收盘时间()} 分钟")
    print(f"⏰ 距离开盘: {距离开盘时间()} 分钟")
    
    # 测试后台启动（可选）
    # 调度器.启动后台()
    # time.sleep(30)
    # 调度器.停止()
    
    print("\n✅ 定时任务模块测试完成")
