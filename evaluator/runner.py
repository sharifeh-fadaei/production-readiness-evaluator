from typing import Dict, List, Any
from faults.taxonomy import FaultType
from faults.injector import FaultInjector
from faults.scenarios import FaultScenario, ExecutionLog, DetectionResult
from agents.target_agent import TargetAgent
from agents.detectors import DetectorSuite
import uuid
from evaluator.flakiness_detector import FlakinessDetector

class EvaluatorRunner:
    """Orchestrates fault injection, detection, and measurement"""
    
    def __init__(self, target_agent: TargetAgent = None):
        self.target_agent = target_agent or TargetAgent()
        self.detector_suite = DetectorSuite()
        self.execution_logs = []
        self.flakiness_detector = FlakinessDetector()

    
    def run_baseline(self, task: str) -> Dict[str, Any]:
        """Run target agent WITHOUT faults - establish ground truth"""
        result = self.target_agent.run(task)
        result["baseline"] = True
        result["fault_type"] = None
        return result
    
    def run_with_fault(self, fault_type: FaultType, task: str, num_runs: int = 10) -> List[ExecutionLog]:
        """Run target agent WITH injected fault, multiple times"""
        execution_logs = []
        
        for run_num in range(num_runs):
            scenario_id = f"{fault_type.value}_{run_num}_{uuid.uuid4().hex[:8]}"
            
            # Create fault scenario
            injector = FaultInjector(fault_type)
            
            # Inject fault into task
            corrupted_task = injector.inject(task)
            
            # Run agent with corrupted task
            execution_result = self.target_agent.run(corrupted_task)
            
            # Run all detectors
            detector_reports = self.detector_suite.run_all(execution_result)
            
            # Create detection results
            detections = [
                DetectionResult(
                    detector_name=name,
                    fault_detected=report.detected,
                    confidence=report.confidence,
                    reasoning=report.reasoning,
                    severity=report.severity
                )
                for name, report in detector_reports.items()
            ]
            
            # Create execution log
            log = ExecutionLog(
                scenario=FaultScenario(
                    scenario_id=scenario_id,
                    fault_type=fault_type,
                    task=task,
                    injected_at="analysis_step",
                    injection_details={"corrupted_task": corrupted_task},
                    ground_truth={"should_fail": True}
                ),
                execution_trace=execution_result,
                final_output=execution_result.get("verification", ""),
                errors=execution_result.get("error", []),
                success=execution_result.get("status") == "success"
            )
            
            # Store detections in log
            log.detections = detections
            
            execution_logs.append(log)
            self.execution_logs.append(log)
        
        return execution_logs
    
    def calculate_detection_metrics(self, logs: List[ExecutionLog]) -> Dict[str, Any]:
        """Calculate detection accuracy from execution logs"""
        if not logs:
            return {}
        
        total_runs = len(logs)
        detected_count = sum(1 for log in logs if any(d.fault_detected for d in log.detections))
        
        per_detector = {}
        for detector_name in ["hallucination", "role_confusion", "context_loss", "message_cycle"]:
            detector_hits = sum(1 for log in logs for d in log.detections if d.detector_name == detector_name and d.fault_detected)
            per_detector[detector_name] = {
                "hits": detector_hits,
                "accuracy": detector_hits / total_runs if total_runs > 0 else 0
            }
        
        return {
            "fault_type": logs[0].scenario.fault_type.value if logs else None,
            "total_runs": total_runs,
            "detected": detected_count,
            "missed": total_runs - detected_count,
            "detection_rate": detected_count / total_runs if total_runs > 0 else 0,
            "per_detector": per_detector,
        }

    def analyze_flakiness(self) -> Dict[str, Any]:
        """Analyze flakiness for all faults tested"""
        # Group logs by fault type
        logs_by_fault = {}
        for log in self.execution_logs:
            fault_type = log.scenario.fault_type
            if fault_type not in logs_by_fault:
                logs_by_fault[fault_type] = []
            logs_by_fault[fault_type].append(log)
        # Generate flakiness report
        return self.flakiness_detector.generate_flakiness_report(logs_by_fault)