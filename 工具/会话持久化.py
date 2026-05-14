# -*- coding: utf-8 -*-
"""
会话状态持久化工具
解决频繁重启导致的配置丢失问题
"""

import streamlit as st
import pickle
import os
import hashlib
from datetime import datetime, timedelta
from typing import Any

class SessionPersistence:
    """会话持久化管理器"""
    
    def __init__(self, cache_dir=".session_cache"):
        self.cache_dir = cache_dir
        self._init_cache_dir()
    
    def _init_cache_dir(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
    
    def _get_key_hash(self, key: str) -> str:
        return hashlib.md5(key.encode()).hexdigest()
    
    def save(self, key: str, value: Any, ttl_hours: int = 24):
        file_path = os.path.join(self.cache_dir, self._get_key_hash(key))
        data = {
            'value': value,
            'expire_at': datetime.now() + timedelta(hours=ttl_hours)
        }
        try:
            with open(file_path, 'wb') as f:
                pickle.dump(data, f)
            return True
        except Exception as e:
            print(f"保存失败 {key}: {e}")
            return False
    
    def load(self, key: str, default: Any = None) -> Any:
        file_path = os.path.join(self.cache_dir, self._get_key_hash(key))
        if not os.path.exists(file_path):
            return default
        try:
            with open(file_path, 'rb') as f:
                data = pickle.load(f)
            if datetime.now() < data['expire_at']:
                return data['value']
            else:
                os.remove(file_path)
                return default
        except:
            return default


_persistence = None

def get_persistence():
    global _persistence
    if _persistence is None:
        _persistence = SessionPersistence()
    return _persistence


def auto_restore_session():
    """自动恢复会话状态"""
    persistence = get_persistence()
    critical_keys = [
        'selected_market',
        'selected_strategy_ids',
        'risk_config',
        'auto_trade_enabled',
        'user_positions'
    ]
    restored_count = 0
    for key in critical_keys:
        if key not in st.session_state:
            saved_value = persistence.load(key)
            if saved_value is not None:
                st.session_state[key] = saved_value
                restored_count += 1
    if restored_count > 0:
        st.toast(f"✅ 已恢复 {restored_count} 项会话配置", icon="🔄")
    return restored_count


def auto_save_session():
    """自动保存会话状态"""
    persistence = get_persistence()
    critical_keys = [
        'selected_market',
        'selected_strategy_ids',
        'risk_config',
        'auto_trade_enabled',
        'user_positions'
    ]
    for key in critical_keys:
        if key in st.session_state:
            persistence.save(key, st.session_state[key])
