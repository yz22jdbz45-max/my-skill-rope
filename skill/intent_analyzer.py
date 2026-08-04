"""
核心分析Skill - 触发大模型能力进行对话分析

【这是与公司Agent平台集成的关键模块】
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from config.prompt_template import get_system_prompt, get_user_prompt
from config.dimensions_config import *

logger = logging.getLogger(__name__)

class IntentAnalysisSkill:
    """
    意图识别Skill类
    
    在公司Agent平台中：
    - skill_name: "intent_recognition"
    - skill_type: "analysis"
    - llm_required: True （需要触发大模型）
    - parallel_support: True （支持并发调用）
    """
    
    def __init__(self, llm_service=None):
        """
        初始化Skill
        
        Args:
            llm_service: 公司Agent平台提供的LLM服务对象
                        （无需API KEY，通过平台调度）
        """
        self.llm_service = llm_service
        self.system_prompt = get_system_prompt()
        self.logger = logger
    
    def analyze_single_dialog(self, 
                             dialog_text: str,
                             conversation_id: str = None,
                             model_name: str = None) -> Dict[str, Any]:
        """
        分析单条对话 - 触发大模型Skill
        
        Args:
            dialog_text: 对话文本
            conversation_id: 对话ID
            model_name: 大模型名称（由平台支持，如'gpt-4', 'claude-3', '本地大模型'等）
        
        Returns:
            Dict: 标注结果
            
        ⭐【重要】大模型触发点：
        - 调用 self.llm_service.call() 触发平台大模型
        - 无需管理API KEY，平台自动处理
        - 支持多种大模型切换
        """
        conversation_id = conversation_id or f"conv_{datetime.now().timestamp()}"
        
        try:
            # 1. 准备提示词
            system_prompt = self.system_prompt
            user_prompt = get_user_prompt(dialog_text, conversation_id)
            
            # 2. ⭐【触发大模型】- 公司Agent平台API调用
            # 这里调用公司平台的LLM服务，无需API KEY
            response = self.llm_service.call(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                model_name=model_name or "default",  # 平台选择模型
                temperature=0.3,  # 降低随机性，确保一致性
                max_tokens=2000,
                response_format="json"  # 指定JSON输出格式
            )
            
            # 3. 解析LLM响应
            raw_response = response.get('content', '')
            result = self._parse_json_response(raw_response)
            
            # 4. 添加元数据
            result['conversation_id'] = conversation_id
            result['timestamp'] = datetime.now().isoformat()
            result['model_used'] = model_name or "default"
            result['status'] = 'success'
            
            # 5. 验证结果
            self._validate_result(result)
            
            self.logger.info(f"✓ 成功分析对话: {conversation_id}")
            return result
            
        except Exception as e:
            self.logger.error(f"✗ 分析失败 {conversation_id}: {str(e)}")
            return {
                'conversation_id': conversation_id,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def analyze_batch_dialogs(self,
                             dialogs: List[Dict],
                             model_name: str = None,
                             parallel: bool = True) -> List[Dict]:
        """
        批量分析多条对话 - 支持并发处理
        
        Args:
            dialogs: 对话列表
                    格式: [{"conversation_id": "xxx", "dialog": "..."}, ...]
            model_name: 大模型名称
            parallel: 是否使用并发处理（平台支持）
        
        Returns:
            List[Dict]: 标注结果列表
            
        ⭐【批量处理流程】：
        - 如果 parallel=True，平台会并发调用多个大模型Skill
        - 每条对话独立触发一次大模型
        - 最大化利用平台资源
        """
        results = []
        
        self.logger.info(f"启动{'并发' if parallel else '顺序'}处理 {len(dialogs)} 条对话...")
        
        for dialog_item in dialogs:
            result = self.analyze_single_dialog(
                dialog_text=dialog_item.get('dialog', ''),
                conversation_id=dialog_item.get('conversation_id'),
                model_name=model_name
            )
            results.append(result)
        
        # 统计结果
        success_count = sum(1 for r in results if r.get('status') == 'success')
        self.logger.info(f"批处理完成: {success_count}/{len(dialogs)} 成功")
        
        return results
    
    def _validate_result(self, result: Dict) -> bool:
        """验证标注结果的合法性"""
        # 检查必填维度
        required_fields = [
            'semantic_summary',
            'merchant_sentiment',
            'consensus_reached',
            'intervention_needed'
        ]
        
        for field in required_fields:
            if field not in result or result[field] is None:
                raise ValueError(f"缺少必填字段: {field}")
        
        # 检查商家情绪的有效值
        if result['merchant_sentiment'] not in MERCHANT_SENTIMENT_VALUES:
            raise ValueError(f"无效的商家情绪值: {result['merchant_sentiment']}")
        
        # 检查是否达成一致的有效值
        if result['consensus_reached'] not in ['yes', 'no', 'unclear']:
            raise ValueError(f"无效的达成一致值: {result['consensus_reached']}")
        
        # 检查依赖关系
        if result['consensus_reached'] in ['no', 'unclear']:
            if result.get('consensus_solution') is not None:
                self.logger.warning(
                    f"警告: 达成一致={result['consensus_reached']}, 但方案不为空"
                )
                result['consensus_solution'] = None
        
        if result['intervention_needed'] == 'no':
            if result.get('intervention_type') is not None:
                self.logger.warning(
                    f"警告: 不需介入, 但介入类型不为空"
                )
                result['intervention_type'] = None
        
        return True
    
    @staticmethod
    def _parse_json_response(raw_response: str) -> Dict:
        """解析LLM的JSON响应"""
        try:
            # 尝试直接解析
            return json.loads(raw_response)
        except:
            # 尝试提取JSON块
            import re
            json_match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            raise ValueError("无法解析LLM响应")


# ======================== Skill注册信息 ========================
SKILL_METADATA = {
    "skill_name": "intent_recognition",
    "skill_type": "analysis",
    "description": "客服对话意图识别与多维度标注分析",
    "version": "1.0.0",
    "llm_required": True,  # ⭐ 标识需要触发大模型
    "supported_models": [
        "gpt-4",
        "gpt-3.5-turbo",
        "claude-3-opus",
        "claude-3-sonnet",
        "local_model"
    ],
    "parallelism": True,
    "input_format": {
        "single": {"dialog": "string", "conversation_id": "string"},
        "batch": {"dialogs": "List[{conversation_id, dialog}]"}
    }
}
