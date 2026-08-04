"""
工作流编排器 - 定义完整的对话分析流程

【适配公司Agent平台的工作流系统】
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from skill.intent_analyzer import IntentAnalysisSkill

logger = logging.getLogger(__name__)

class WorkflowStatus(Enum):
    """工作流状态枚举"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"


class IntentRecognitionWorkflow:
    """
    意图识别工作流类
    
    在公司Agent平台中作为独立的工作流任务运行：
    - workflow_name: "dialog_intent_analysis"
    - trigger_type: "manual" | "scheduled" | "webhook"
    - parallelism: 支持多并发
    """
    
    def __init__(self, llm_service=None, config: Dict = None):
        """
        初始化工作流
        
        Args:
            llm_service: 公司Agent平台的LLM服务
            config: 工作流配置
        """
        self.llm_service = llm_service
        self.skill = IntentAnalysisSkill(llm_service)
        self.config = config or {}
        self.status = WorkflowStatus.PENDING
        self.logger = logger
    
    def execute(self,
                input_source: str,
                input_format: str = 'auto',
                output_format: str = 'json',
                model_name: str = None,
                parallel: bool = True) -> Dict[str, Any]:
        """
        执行完整的工作流
        
        Args:
            input_source: 输入源（文件路径或数据）
            input_format: 输入格式（json/csv/excel/jsonl）
            output_format: 输出格式
            model_name: 大模型名称
            parallel: 是否使用并发处理
        
        Returns:
            Dict: 工作流执行结果
        """
        workflow_id = f"wf_{datetime.now().timestamp()}"
        self.logger.info(f"🚀 启动工作流 {workflow_id}")
        
        try:
            self.status = WorkflowStatus.RUNNING
            
            # ========== 步骤1: 加载输入数据 ==========
            self.logger.info("📥 步骤1: 加载输入数据")
            dialogs = self._load_input(input_source, input_format)
            self.logger.info(f"   ✓ 加载 {len(dialogs)} 条对话")
            
            # ========== 步骤2: 触发Skill进行批量分析 ==========
            self.logger.info(f"🤖 步骤2: 触发大模型Skill进行{len(dialogs)}条对话分析")
            results = self.skill.analyze_batch_dialogs(
                dialogs,
                model_name=model_name,
                parallel=parallel
            )
            self.logger.info(f"   ✓ 分析完成")
            
            # ========== 步骤3: 处理和验证结果 ==========
            self.logger.info("✅ 步骤3: 处理和验证结果")
            processed_results = self._process_results(results)
            self.logger.info(f"   ✓ 处理完成，成功 {processed_results['success_count']} 条")
            
            # ========== 步骤4: 生成报告 ==========
            self.logger.info("📊 步骤4: 生成分析报告")
            report = self._generate_report(processed_results)
            self.logger.info(f"   ✓ 报告生成完成")
            
            self.status = WorkflowStatus.COMPLETED
            
            return {
                'workflow_id': workflow_id,
                'status': 'success',
                'summary': {
                    'total': len(dialogs),
                    'success': processed_results['success_count'],
                    'failed': processed_results['failed_count'],
                    'success_rate': f"{processed_results['success_count']/len(dialogs)*100:.1f}%"
                },
                'report': report,
                'results': processed_results['results'],
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            self.status = WorkflowStatus.FAILED
            self.logger.error(f"❌ 工作流失败: {str(e)}")
            return {
                'workflow_id': workflow_id,
                'status': 'failed',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def _load_input(self, input_source: str, input_format: str) -> List[Dict]:
        """加载输入数据"""
        # 简化版本 - 实际应该使用format_converter
        if isinstance(input_source, list):
            data = input_source
        else:
            # 从文件读取
            try:
                import csv
                data = []
                with open(input_source, 'r', encoding='utf-8') as f:
                    reader = csv.DictReader(f)
                    data = list(reader)
            except:
                data = []
        
        # 标准化输入格式
        normalized = []
        for item in data:
            if isinstance(item, dict):
                normalized.append({
                    'conversation_id': item.get('conversation_id', f'conv_{len(normalized)}'),
                    'dialog': item.get('dialog') or item.get('content') or str(item)
                })
            else:
                normalized.append({
                    'conversation_id': f'conv_{len(normalized)}',
                    'dialog': str(item)
                })
        
        return normalized
    
    def _process_results(self, results: List[Dict]) -> Dict:
        """处理和验证结果"""
        success_results = [r for r in results if r.get('status') == 'success']
        failed_results = [r for r in results if r.get('status') == 'failed']
        
        return {
            'results': results,
            'success_results': success_results,
            'failed_results': failed_results,
            'success_count': len(success_results),
            'failed_count': len(failed_results)
        }
    
    def _generate_report(self, processed_results: Dict) -> Dict:
        """生成分析报告"""
        results = processed_results['success_results']
        
        if not results:
            return {'error': '没有成功的分析结果'}
        
        # 统计各维度的分布
        sentiment_dist = {}
        request_dist = {}
        consensus_dist = {}
        intervention_dist = {}
        
        for result in results:
            sentiment = result.get('merchant_sentiment', 'unknown')
            sentiment_dist[sentiment] = sentiment_dist.get(sentiment, 0) + 1
            
            request = result.get('user_request', 'none')
            request_dist[request] = request_dist.get(request, 0) + 1
            
            consensus = result.get('consensus_reached', 'unknown')
            consensus_dist[consensus] = consensus_dist.get(consensus, 0) + 1
            
            intervention = result.get('intervention_needed', 'unknown')
            intervention_dist[intervention] = intervention_dist.get(intervention, 0) + 1
        
        return {
            'total_analyzed': len(results),
            'merchant_sentiment_distribution': sentiment_dist,
            'user_request_distribution': request_dist,
            'consensus_reached_distribution': consensus_dist,
            'intervention_needed_distribution': intervention_dist,
            'key_metrics': {
                'positive_rate': f"{sentiment_dist.get('正向情绪', 0)/len(results)*100:.1f}%" if results else "0%",
                'intervention_rate': f"{intervention_dist.get('yes', 0)/len(results)*100:.1f}%" if results else "0%",
                'consensus_rate': f"{consensus_dist.get('yes', 0)/len(results)*100:.1f}%" if results else "0%"
            }
        }


# ======================== 工作流配置模板 ========================
WORKFLOW_CONFIG_TEMPLATE = {
    "workflow_name": "dialog_intent_analysis",
    "description": "客服对话意图识别与多维度分析",
    "trigger_type": "manual",  # manual | scheduled | webhook
    "parallelism": True,
    "max_concurrent_tasks": 10,
    "timeout_seconds": 3600
}
