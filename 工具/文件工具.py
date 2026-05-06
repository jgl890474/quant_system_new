# -*- coding: utf-8 -*-
import json
import os

def 保存JSON(数据, 文件路径):
    with open(文件路径, 'w', encoding='utf-8') as f:
        json.dump(数据, f, ensure_ascii=False, indent=2)

def 读取JSON(文件路径):
    if not os.path.exists(文件路径):
        return None
    with open(文件路径, 'r', encoding='utf-8') as f:
        return json.load(f)

