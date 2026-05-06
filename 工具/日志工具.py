
# -*- coding: utf-8 -*-
import logging

def 获取日志(名称="量化系统"):
    logger = logging.getLogger(名称)
    logger.setLevel(logging.INFO)
    if not logger.handlers:
        handler = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
