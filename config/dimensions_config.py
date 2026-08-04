"""
维度定义与配置
所有数据结构化定义，支持动态加载
"""

# ==================== 商家情绪定义 ====================
MERCHANT_SENTIMENT_VALUES = [
    "正向情绪",
    "中性情绪", 
    "负向情绪",
    "强烈负向情绪"
]

# ==================== 用户诉求定义 ====================
USER_REQUEST_VALUES = [
    "refund_only",
    "return_refund",
    "exchange",
    "repair",
    "resend",
    "partial_return",
    "installation",
    "cancel_order"
]

# ==================== 达成一致方案定义 ====================
CONSENSUS_SOLUTION_VALUES = [
    "cancel_order",
    "refund_only",
    "return_refund",
    "exchange",
    "repair",
    "resend",
    "free_shipping",
    "partial_return",
    "installation"
]

# ==================== 介入类型定义 ====================
INTERVENTION_TYPE_VALUES = [
    "escalate_to_agent",
    "multiple_rejections",
    "no_viable_solution",
    "abuse_or_threat"
]

# ==================== 是否达成一致的标准 ====================
CONSENSUS_STANDARDS = {
    "yes": {
        "scenarios": [
            "商家提方案+用户明示接受（'好的'、'可以'、'没问题了'）",
            "商家提方案+用户被动接受（'好吧'、'就这样'、'只能这样了'）",
            "用户提诉求+商家明确表达同意"
        ]
    },
    "no": {
        "scenarios": [
            "用户明确拒绝（'不行'、'不同意'、'我投诉'）",
            "商家明确拒绝（'赔不了'、'开不了'）"
        ]
    },
    "unclear": {
        "scenarios": [
            "排障/解答阶段无明确诉求",
            "单方断联（一方无回复）",
            "答非所问/表达模糊",
            "纯政策解答存疑"
        ]
    }
}

# ==================== 介入时机的4个触发条件 ====================
INTERVENTION_TRIGGERS = {
    "escalate_to_agent": {
        "name": "明确要求转人工",
        "keywords": ["转人工", "主管", "升级", "投诉", "12315", "工商投诉", "平台介入"]
    },
    "multiple_rejections": {
        "name": "多轮拒绝方案",
        "description": "用户多次拒绝客服提出的方案，双方无法达成共识"
    },
    "no_viable_solution": {
        "name": "客服无法给出方案",
        "keywords": ["重复话术", "无可奈何", "政策限制", "无法处理", "超出权限"]
    },
    "abuse_or_threat": {
        "name": "出现攻击威胁辱骂",
        "keywords": ["废话", "骂人", "威胁", "人身攻击", "诅咒"]
    }
}
