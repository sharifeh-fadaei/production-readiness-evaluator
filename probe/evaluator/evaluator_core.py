from typing import Any, Dict
from probe.agents.target_agent import TargetAgent
from probe.evaluator.runner import EvaluatorRunner
from probe.evaluator.aggregator import MetricsAggregator
from probe.evaluator.report_generator import ReportGenerator
from probe.faults.taxonomy import FaultType

class EvaluationReport:
    """Simple report object"""
    
    def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.overall_score = data.get("overall_reliability_score", 0)
        self.production_ready = data.get("production_ready", False)
        self.critical_risks = data.get("critical_risks", [])
        self.results = data.get("results_per_fault_type", {})
    
    def __str__(self):
        return f"Production Readiness Score: {self.overall_score}% | Ready: {self.production_ready}"

def evaluate(agent: Any, task: str = "Test task", model: str = "openai/gpt-3.5-turbo", num_runs: int = 5) -> EvaluationReport:
    """
    Evaluate an AI agent for production readiness.
    
    Args:
        agent: Your agent system with a run(query) method
        task: The task to test the agent with
        model: OpenRouter model to use
        num_runs: Number of fault injection runs per fault type
    
    Returns:
        EvaluationReport with scores and recommendations
    """
    
    if not hasattr(agent, 'run'):
        raise ValueError("Agent must have a run(query) method")
    
    runner = EvaluatorRunner(agent)
    aggregator = MetricsAggregator()
    report_gen = ReportGenerator()
    
    baseline = runner.run_baseline(task)
    
    all_logs = []
    fault_types = [
        FaultType.HALLUCINATION,
        FaultType.PARAMETER_ERROR,
        FaultType.CONTEXT_LOSS,
        FaultType.ROLE_AMBIGUITY,
        FaultType.BLIND_TRUST,
        FaultType.INSTRUCTION_CONFLICT,
        FaultType.INEXECUTABLE_PLAN,
        FaultType.MESSAGE_CYCLE,
    ]
    
    for fault_type in fault_types:
        logs = runner.run_with_fault(fault_type, task, num_runs=num_runs)
        all_logs.extend(logs)
    
    summary = aggregator.aggregate(all_logs)
    full_summary = aggregator.get_summary()
    report = report_gen.generate_report(full_summary, system_name=agent.__class__.__name__)
    
    return EvaluationReport(report)
