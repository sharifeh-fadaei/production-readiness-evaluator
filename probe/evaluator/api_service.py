from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any
import json
from datetime import datetime

from probe.agents.target_agent import TargetAgent
from probe.evaluator.runner import EvaluatorRunner
from probe.evaluator.aggregator import MetricsAggregator
from probe.evaluator.report_generator import ReportGenerator
from probe.agents.breaker_agent import BreakerAgent
from probe.faults.taxonomy import FaultType

app = FastAPI(
    title="Production Readiness Evaluator API",
    description="Evaluate AI agent systems for production readiness",
    version="1.0.0"
)

class EvaluationRequest(BaseModel):
    """Input for evaluation request"""
    system_name: str
    task: str
    num_runs_per_fault: int = 5
    num_adversarial_attacks: int = 3
    model: str = "openai/gpt-3.5-turbo"

class EvaluationResponse(BaseModel):
    """Output of evaluation"""
    timestamp: str
    system_name: str
    overall_reliability_score: float
    production_ready: bool
    results_by_fault_type: Dict[str, Any]
    critical_risks: list
    adversarial_results: Dict[str, Any]

@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "Production Readiness Evaluator"}

@app.post("/evaluate", response_model=EvaluationResponse)
def evaluate_system(request: EvaluationRequest):
    """
    Evaluate an agent system for production readiness
    
    Returns:
    - Overall reliability score (0-100)
    - Detection rates per fault type
    - Critical risks
    - Adversarial attack results
    """
    
    try:
        # Initialize components
        target_agent = TargetAgent(name=request.system_name, model=request.model)
        runner = EvaluatorRunner(target_agent)
        aggregator = MetricsAggregator()
        report_gen = ReportGenerator()
        breaker = BreakerAgent(model=request.model)
        
        # Run baseline
        baseline = runner.run_baseline(request.task)
        
        # Run fault injections
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
            logs = runner.run_with_fault(fault_type, request.task, num_runs=request.num_runs_per_fault)
            all_logs.extend(logs)
        
        # Aggregate results
        summary = aggregator.aggregate(all_logs)
        full_summary = aggregator.get_summary()
        
        # Run adversarial attacks
        adversarial_results = breaker.run_attack_sequence(target_agent, num_attacks=request.num_adversarial_attacks)
        
        # Generate report
        report = report_gen.generate_report(full_summary, system_name=request.system_name)
        
        # Format response
        return EvaluationResponse(
            timestamp=datetime.now().isoformat(),
            system_name=request.system_name,
            overall_reliability_score=report["overall_reliability_score"],
            production_ready=report["production_ready"],
            results_by_fault_type=report["results_per_fault_type"],
            critical_risks=report["critical_risks"],
            adversarial_results={
                "total_attacks": adversarial_results["total_attacks"],
                "successful_breaks": adversarial_results["successful_breaks"],
                "resilience_score": adversarial_results["resilience_score"]
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/models")
def get_available_models():
    """Get list of available LLM models"""
    from probe.evaluator.openrouter_client import OpenRouterClient
    client = OpenRouterClient()
    return {"available_models": client.get_available_models()}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)