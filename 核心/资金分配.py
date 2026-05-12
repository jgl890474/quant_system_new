# -*- coding: utf-8 -*-

class 资金分配器:
    def __init__(self, 总资金):
        self.总资金 = 总资金
        print(f"💰 资金分配器初始化，总资金: ¥{总资金:,.2f}")
    
    def 分配(self, 策略列表):
        """将总资金平均分配给策略列表中的每个策略"""
        if not 策略列表:
            print("⚠️ 策略列表为空，无法分配资金")
            return
        
        策略数量 = len(策略列表)
        per = self.总资金 / 策略数量  # 使用 / 而不是 //
        
        for s in 策略列表:
            s.初始资金 = per
            s.资金 = per
        
        print(f"✅ 资金分配完成: {策略数量} 个策略，每个策略 ¥{per:,.2f}")
        return {"策略数量": 策略数量, "每策略资金": per}
    
    def 获取分配详情(self, 策略列表):
        """获取分配详情（不实际分配）"""
        if not 策略列表:
            return []
        
        per = self.总资金 / len(策略列表)
        return [{"策略": s, "资金": per} for s in 策略列表]
