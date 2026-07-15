from langfuse import Langfuse
from typing import Dict, Any, Optional
import os

class EvaluatorTracer:
    """Integrates Langfuse tracing for observability"""
    
    def __init__(self, enabled: bool = True):
        self.enabled = enabled
        
        if self.enabled:
            # Initialize Langfuse (requires LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY)
            self.client = Langfuse(
                public_key=os.getenv("LANGFUSE_PUBLIC_KEY", ""),
                secret_key=os.getenv("LANGFUSE_SECRET_KEY", ""),
                host=os.getenv("LANGFUSE_HOST", "https://cloud.langfuse.com")
            )
        else:
            self.client = None
    
    def trace_baseline_run(self, task: str, result: Dict[str, Any]) -> None:
        """Trace a baseline run"""
        if not self.enabled or not self.client:
            return
        
        self.client.trace(
            name="baseline_run",
            input={"task": task},
            output=result,
            metadata={
                "type": "baseline",
                "status": result.get("status")
            }
        )
    
    def trace_fault_injection(self, fault_type: str, scenario_id: str, result: Dict[str, Any]) -> None:
        """Trace a fault injection run"""
        if not self.enabled or not self.client:
            return
        
        self.client.trace(
            name="fault_injection",
            input={
                "fault_type": fault_type,
                "scenario_id": scenario_id
            },
            output=result,
            metadata={
                "type": "fault_injection",
                "fault_type": fault_type,
                "status": result.get("status")
            }
        )
    
    def trace_detection(self, detector_name: str, detection_result: Dict[str, Any]) -> None:
        """Trace a detector run"""
        if not self.enabled or not self.client:
            return
        
        self.client.trace(
            name=f"detector_{detector_name}",
            input={},
            output=detection_result,
            metadata={
                "detector": detector_name,
                "detected": detection_result.get("detected")
            }
        )
    
    def trace_aggregation(self, metrics: Dict[str, Any]) -> None:
        """Trace aggregation results"""
        if not self.enabled or not self.client:
            return
        
        self.client.trace(
            name="aggregation",
            input={},
            output=metrics,
            metadata={
                "type": "aggregation"
            }
        )
    
    def trace_report(self, report: Dict[str, Any]) -> None:
        """Trace final report generation"""
        if not self.enabled or not self.client:
            return
        
        self.client.trace(
            name="report_generation",
            input={},
            output={
                "overall_reliability_score": report.get("overall_reliability_score"),
                "production_ready": report.get("production_ready")
            },
            metadata={
                "type": "report",
                "production_ready": report.get("production_ready")
            }
        )
    
    def flush(self) -> None:
        """Flush all traces to Langfuse"""
        if self.enabled and self.client:
            self.client.flush()