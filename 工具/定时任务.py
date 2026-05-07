# -*- coding: utf-8 -*-
import time
import threading
from datetime import datetime, time as dt_time
import schedule


class 定时任务:
    """定时任务调度器"""
    
    def __init__(self):
        self.运行中 = False
        self.线程 = None
    
    def 添加任务(self, 任务函数, 执行时间, 参数=None):
        """添加定时任务，执行时间格式: '14:55'"""
        print(f"⏰ 添加定时任务: {执行时间}")
        
        def 包装函数():
            if 参数:
                任务函数(参数)
            else:
                任务函数()
        
        getattr(schedule.every().day.at(执行时间)).do(包装函数)
    
    def 添加间隔任务(self, 任务函数, 间隔秒数, 参数=None):
        """添加间隔任务（秒级）"""
        print(f"⏰ 添加间隔任务: 每 {间隔秒数} 秒")
        
        def 包装函数():
            if 参数:
                任务函数(参数)
            else:
                任务函数()
        
        schedule.every(间隔秒数).seconds.do(包装函数)
    
    def 启动(self):
        """启动调度器"""
        self.运行中 = True
        print("⏰ 定时任务调度器已启动")
        
        while self.运行中:
            schedule.run_pending()
            time.sleep(1)
    
    def 停止(self):
        """停止调度器"""
        self.运行中 = False
        print("⏰ 定时任务调度器已停止")
    
    def 启动后台(self):
        """后台启动"""
        self.线程 = threading.Thread(target=self.启动, daemon=True)
        self.线程.start()


# ========== 交易时间判断函数 ==========
def 是交易时间():
    """判断当前是否在交易时间内"""
    now = datetime.now()
    当前时间 = now.time()
    
    上午开始 = dt_time(9, 30)
    上午结束 = dt_time(11, 30)
    下午开始 = dt_time(13, 0)
    下午结束 = dt_time(15, 0)
    
    if 上午开始 <= 当前时间 <= 上午结束:
        return True
    if 下午开始 <= 当前时间 <= 下午结束:
        return True
    return False


def 是尾盘时间():
    """判断是否尾盘时间 (14:50-15:00)"""
    now = datetime.now()
    当前时间 = now.time()
    return 当前时间 >= dt_time(14, 50) and 当前时间 <= dt_time(15, 0)


def 是早盘时间():
    """判断是否早盘时间 (9:30-9:35)"""
    now = datetime.now()
    当前时间 = now.time()
    return 当前时间 >= dt_time(9, 30) and 当前时间 <= dt_time(9, 35)


def 获取交易状态():
    """获取当前交易状态"""
    now = datetime.now()
    当前时间 = now.time()
    
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
