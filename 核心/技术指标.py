# -*- coding: utf-8 -*-
"""
技术指标计算模块 - 完整版
包含：MACD、布林带、RSI、KDJ、成交量指标、趋势指标等
"""

import pandas as pd
import numpy as np
from typing import Dict


class 技术指标计算器:
    """完整技术指标计算器"""
    
    @staticmethod
    def 计算MACD(df: pd.DataFrame, fast=12, slow=26, signal=9) -> Dict:
        """计算MACD指标"""
        if df.empty or len(df) < slow + signal:
            return {'MACD': 0, '信号线': 0, '柱状图': 0, '金叉': False, '死叉': False, '状态': '中性'}
        
        close = df['收盘'] if '收盘' in df.columns else df['Close']
        
        ema_fast = close.ewm(span=fast, adjust=False).mean()
        ema_slow = close.ewm(span=slow, adjust=False).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        
        golden_cross = False
        death_cross = False
        
        if len(macd_line) >= 2:
            if macd_line.iloc[-1] > signal_line.iloc[-1] and macd_line.iloc[-2] <= signal_line.iloc[-2]:
                golden_cross = True
            elif macd_line.iloc[-1] < signal_line.iloc[-1] and macd_line.iloc[-2] >= signal_line.iloc[-2]:
                death_cross = True
        
        return {
            'MACD': round(macd_line.iloc[-1], 4),
            '信号线': round(signal_line.iloc[-1], 4),
            '柱状图': round(histogram.iloc[-1], 4),
            '金叉': golden_cross,
            '死叉': death_cross,
            '状态': '多头' if macd_line.iloc[-1] > signal_line.iloc[-1] else '空头'
        }
    
    @staticmethod
    def 计算布林带(df: pd.DataFrame, period=20, std_dev=2) -> Dict:
        """计算布林带指标"""
        if df.empty or len(df) < period:
            return {'上轨': 0, '中轨': 0, '下轨': 0, '带宽': 0, '位置': 0.5, '信号': '未知'}
        
        close = df['收盘'] if '收盘' in df.columns else df['Close']
        
        middle = close.rolling(window=period).mean()
        std = close.rolling(window=period).std()
        
        upper = middle + (std * std_dev)
        lower = middle - (std * std_dev)
        
        current_price = close.iloc[-1]
        band_width = (upper.iloc[-1] - lower.iloc[-1]) / middle.iloc[-1] * 100 if middle.iloc[-1] > 0 else 0
        
        if current_price <= lower.iloc[-1]:
            position = 0
            signal = "触及下轨-超卖"
        elif current_price >= upper.iloc[-1]:
            position = 1
            signal = "触及上轨-超买"
        else:
            position = (current_price - lower.iloc[-1]) / (upper.iloc[-1] - lower.iloc[-1]) if (upper.iloc[-1] - lower.iloc[-1]) > 0 else 0.5
            signal = "正常区间"
        
        return {
            '上轨': round(upper.iloc[-1], 2),
            '中轨': round(middle.iloc[-1], 2),
            '下轨': round(lower.iloc[-1], 2),
            '带宽': round(band_width, 2),
            '位置': round(position, 2),
            '信号': signal
        }
    
    @staticmethod
    def 计算RSI(df: pd.DataFrame, period=14) -> Dict:
        """计算RSI指标"""
        if df.empty or len(df) < period + 1:
            return {'RSI': 50, '状态': '中性', '信号': '观望'}
        
        close = df['收盘'] if '收盘' in df.columns else df['Close']
        
        delta = close.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        current_rsi = rsi.iloc[-1]
        
        if current_rsi < 30:
            status = "超卖"
            signal = "买入信号"
        elif current_rsi > 70:
            status = "超买"
            signal = "卖出信号"
        elif 40 <= current_rsi <= 60:
            status = "中性"
            signal = "观望"
        else:
            status = "正常"
            signal = "持有"
        
        return {
            'RSI': round(current_rsi, 2),
            '状态': status,
            '信号': signal
        }
    
    @staticmethod
    def 计算KDJ(df: pd.DataFrame, n=9, m1=3, m2=3) -> Dict:
        """计算KDJ指标"""
        if df.empty or len(df) < n:
            return {'K': 50, 'D': 50, 'J': 50, '信号': '中性'}
        
        low = df['最低'] if '最低' in df.columns else df['Low']
        high = df['最高'] if '最高' in df.columns else df['High']
        close = df['收盘'] if '收盘' in df.columns else df['Close']
        
        low_list = low.rolling(window=n).min()
        high_list = high.rolling(window=n).max()
        
        rsv = (close - low_list) / (high_list - low_list) * 100
        rsv = rsv.fillna(50)
        
        k = rsv.ewm(span=m1, adjust=False).mean()
        d = k.ewm(span=m2, adjust=False).mean()
        j = 3 * k - 2 * d
        
        if k.iloc[-1] < 20 and d.iloc[-1] < 20:
            signal = "买入"
        elif k.iloc[-1] > 80 and d.iloc[-1] > 80:
            signal = "卖出"
        else:
            signal = "中性"
        
        return {
            'K': round(k.iloc[-1], 2),
            'D': round(d.iloc[-1], 2),
            'J': round(j.iloc[-1], 2),
            '信号': signal
        }
    
    @staticmethod
    def 计算成交量指标(df: pd.DataFrame) -> Dict:
        """计算成交量相关指标"""
        if df.empty:
            return {'成交量': 0, '5日均量': 0, '20日均量': 0, '成交量比率': 1, '放量状态': '正常', 'OBV趋势': '平缓'}
        
        volume = df['成交量'] if '成交量' in df.columns else df['Volume']
        close = df['收盘'] if '收盘' in df.columns else df['Close']
        
        vol_ma5 = volume.rolling(5).mean()
        vol_ma20 = volume.rolling(20).mean()
        
        vol_ratio = volume.iloc[-1] / vol_ma20.iloc[-1] if vol_ma20.iloc[-1] > 0 else 1
        
        # OBV简化计算
        obv = [0]
        for i in range(1, len(df)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.append(obv[-1] + volume.iloc[i])
            elif close.iloc[i] < close.iloc[i-1]:
                obv.append(obv[-1] - volume.iloc[i])
            else:
                obv.append(obv[-1])
        
        if len(obv) > 20:
            obv_trend = "上涨" if obv[-1] > obv[-20] else "下跌"
        else:
            obv_trend = "平缓"
        
        if vol_ratio > 1.2:
            vol_status = "放量"
        elif vol_ratio < 0.8:
            vol_status = "缩量"
        else:
            vol_status = "正常"
        
        return {
            '成交量': int(volume.iloc[-1]),
            '5日均量': int(vol_ma5.iloc[-1]),
            '20日均量': int(vol_ma20.iloc[-1]),
            '成交量比率': round(vol_ratio, 2),
            '放量状态': vol_status,
            'OBV趋势': obv_trend
        }
    
    @staticmethod
    def 计算趋势指标(df: pd.DataFrame) -> Dict:
        """计算趋势相关指标"""
        if df.empty or len(df) < 20:
            return {'MA5': 0, 'MA10': 0, 'MA20': 0, 'MA60': 0, '趋势': '未知', '趋势得分': 20, '趋势强度': '未知'}
        
        close = df['收盘'] if '收盘' in df.columns else df['Close']
        high = df['最高'] if '最高' in df.columns else df['High']
        low = df['最低'] if '最低' in df.columns else df['Low']
        
        ma5 = close.rolling(5).mean()
        ma10 = close.rolling(10).mean()
        ma20 = close.rolling(20).mean()
        ma60 = close.rolling(60).mean()
        
        # 趋势判断
        if not pd.isna(ma5.iloc[-1]) and not pd.isna(ma20.iloc[-1]) and not pd.isna(ma60.iloc[-1]):
            if ma5.iloc[-1] > ma20.iloc[-1] > ma60.iloc[-1]:
                trend = "强势上涨"
                trend_score = 40
            elif ma5.iloc[-1] > ma20.iloc[-1]:
                trend = "上涨"
                trend_score = 30
            elif ma5.iloc[-1] < ma20.iloc[-1] < ma60.iloc[-1]:
                trend = "强势下跌"
                trend_score = 5
            elif ma5.iloc[-1] < ma20.iloc[-1]:
                trend = "下跌"
                trend_score = 10
            else:
                trend = "震荡"
                trend_score = 20
        else:
            trend = "未知"
            trend_score = 20
        
        # ADX简化计算
        try:
            plus_dm = high.diff()
            minus_dm = low.diff()
            plus_dm[plus_dm < 0] = 0
            minus_dm[minus_dm > 0] = 0
            
            tr = pd.concat([high - low, abs(high - close.shift()), abs(low - close.shift())], axis=1).max(axis=1)
            atr = tr.rolling(14).mean()
            
            plus_di = 100 * (plus_dm.rolling(14).mean() / atr)
            minus_di = 100 * (abs(minus_dm).rolling(14).mean() / atr)
            dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
            adx = dx.rolling(14).mean()
            
            if not pd.isna(adx.iloc[-1]):
                if adx.iloc[-1] > 25:
                    trend_strength = "强趋势"
                elif adx.iloc[-1] > 20:
                    trend_strength = "中等趋势"
                else:
                    trend_strength = "弱趋势/震荡"
            else:
                trend_strength = "未知"
        except:
            trend_strength = "未知"
        
        return {
            'MA5': round(ma5.iloc[-1], 2) if not pd.isna(ma5.iloc[-1]) else 0,
            'MA10': round(ma10.iloc[-1], 2) if not pd.isna(ma10.iloc[-1]) else 0,
            'MA20': round(ma20.iloc[-1], 2) if not pd.isna(ma20.iloc[-1]) else 0,
            'MA60': round(ma60.iloc[-1], 2) if not pd.isna(ma60.iloc[-1]) else 0,
            '趋势': trend,
            '趋势得分': trend_score,
            '趋势强度': trend_strength
        }


# 全局实例
_指标计算器 = None

def 获取指标计算器():
    global _指标计算器
    if _指标计算器 is None:
        _指标计算器 = 技术指标计算器()
    return _指标计算器
