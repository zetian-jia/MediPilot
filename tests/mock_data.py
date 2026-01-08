import json

# ==========================================
# MediPilot 模拟测试数据 (Mock Data)
# ==========================================

class MockMedicalData:
    """模拟从化验单 PDF 中提取的结构化数据"""
    
    REPORT_SAMPLE_1 = {
        "report_id": "REP-2026-001",
        "patient_info": {
            "name": "张**",  # 脱敏后的数据
            "age": 45,
            "department": "内科"
        },
        "findings": [
            {"metric": "WBC", "value": "7.2", "unit": "10^9/L", "ref_range": "4.0-10.0"},
            {"metric": "RBC", "value": "4.8", "unit": "10^12/L", "ref_range": "4.0-5.5"},
            {"metric": "Hgb", "value": "142", "unit": "g/L", "ref_range": "120-160"},
            {"metric": "PLT", "value": "210", "unit": "10^9/L", "ref_range": "100-300"},
            {"metric": "NEUT%", "value": "65.4", "unit": "%", "ref_range": "50-70"}
        ],
        "extraction_confidence": 0.98,
        "timestamp": "2026-01-08T15:30:00"
    }

class MockAIActions:
    """模拟 AI 认知层返回的动作指令"""
    
    # 动作 1：找到 EMR 系统的输入框并点击
    ACTION_CLICK_INPUT = {
        "thought": "化验单数据显示 WBC 为 7.2。现在在 EMR 系统的录入页面寻找 '白细胞' 对应的输入框。在坐标 B4 区域发现输入框。",
        "action": "click",
        "coordinate": [450, 600],
        "text": None,
        "reasoning": "点击输入框以获得焦点。"
    }
    
    # 动作 2：输入数值
    ACTION_TYPE_VALUE = {
        "thought": "已聚焦输入框，开始输入 WBC 的提取数值 7.2。",
        "action": "type",
        "coordinate": [450, 600],
        "text": "7.2",
        "reasoning": "根据化验单提取结果进行数据录入。"
    }
    
    # 动作 3：完成任务
    ACTION_FINISH = {
        "thought": "所有关键指标均已录入完毕并核对无误。",
        "action": "finish",
        "coordinate": None,
        "text": None,
        "reasoning": "流程结束。"
    }

def get_all_mocks():
    return {
        "data": MockMedicalData.REPORT_SAMPLE_1,
        "actions": [
            MockAIActions.ACTION_CLICK_INPUT,
            MockAIActions.ACTION_TYPE_VALUE,
            MockAIActions.ACTION_FINISH
        ]
    }

if __name__ == "__main__":
    print("--- MediPilot 模拟数据预览 ---")
    print(json.dumps(get_all_mocks(), indent=2, ensure_ascii=False))
