from typing import Dict, List, Any
from probe.faults.scenarios import ExecutionLog, FaultMetrics
from probe.faults.taxonomy import FaultType

class MetricsAggregator:
    """Aggregates results across all fault types"""
    
    def __init__(self):
        self.fault_metrics = {}
    
    def aggregate(self, execution_logs: List[ExecutionLog]) -> Dict[str, Any]:
        """Aggregate execution logs by fault type"""
        
        # Group logs by fault type
        logs_by_fault = {}
        for log in execution_logs:
            fault_type = log.scenario.fault_type
            if fault_type not in logs_by_fault:
                logs_by_fault[fault_type] = []
            logs_by_fault[fault_type].append(log)
        
        # Calculate metrics per fault type
        all_metrics = {}
        for fault_type, logs in logs_by_fault.items():
            metrics = self._calculate_fault_metrics(fault_type, logs)
            all_metrics[fault_type.value] = metrics
            self.fault_metrics[fault_type] = metrics
        
        return all_metrics
    
    def _calculate_fault_metrics(self, fault_type: FaultType, logs: List[ExecutionLog]) -> Dict[str, Any]:
        """Calculate metrics for one fault type"""
        
        total_runs = len(logs)
        detected_count = sum(1 for log in logs if any(d.fault_detected for d in log.detections))
        missed_count = total_runs - detected_count
        
        # Per-detector accuracy
        per_detector = {}
        detector_names = set()
        for log in logs:
            for detection in log.detections:
                detector_names.add(detection.detector_name)
        
        for detector_name in detector_names:
            hits = sum(1 for log in logs for d in log.detections 
                      if d.detector_name == detector_name and d.fault_detected)
            accuracy = hits / total_runs if total_runs > 0 else 0
            per_detector[detector_name] = {
                "hits": hits,
                "accuracy": accuracy
            }
        
        # Recovery success (did the system handle it after detection?)
        recovery_success = sum(1 for log in logs if log.success) if logs else 0
        recovery_rate = recovery_success / total_runs if total_runs > 0 else 0
        
        # Critical failures
        critical_failures = sum(1 for log in logs if not log.success)

        
        return {
            "fault_type": fault_type.value,
            "total_runs": total_runs,
            "detected": detected_count,
            "missed": missed_count,
            "detection_rate": detected_count / total_runs if total_runs > 0 else 0,
            "false_positive_rate": 0.0,  # Placeholder
            "recovery_success_rate": recovery_rate,
            "critical_failures": critical_failures,
            "per_detector": per_detector,
        }
    
    def calculate_overall_score(self) -> float:
        """Calculate overall reliability score (0-100)"""
        if not self.fault_metrics:
            return 0.0
        
        # Weight each fault type equally
        total_detection_rate = 0.0
        for metrics in self.fault_metrics.values():
            total_detection_rate += metrics["detection_rate"]
        
        avg_detection_rate = total_detection_rate / len(self.fault_metrics)
        
        # Convert to 0-100 scale
        overall_score = avg_detection_rate * 100
        
        return round(overall_score, 1)
    
    def identify_critical_risks(self) -> List[Dict[str, Any]]:
        """Identify faults the system fails on"""
        risks = []
        
        for fault_type, metrics in self.fault_metrics.items():
            detection_rate = metrics["detection_rate"]
            
            # Flag if detection rate is below 70%
            if detection_rate < 0.7:
                risks.append({
                    "fault_type": fault_type.value,
                    "detection_rate": detection_rate,
                    "issue": f"System fails to detect {fault_type.value} in {(1-detection_rate)*100:.0f}% of cases",
                    "severity": "critical" if detection_rate < 0.3 else "warning",
                    "recommendation": f"Improve detection for {fault_type.value}"
                })
        
        return sorted(risks, key=lambda x: x["detection_rate"])
    
    def get_summary(self) -> Dict[str, Any]:
        """Get overall summary of evaluation"""
        return {
            "overall_reliability_score": self.calculate_overall_score(),
            "total_fault_types_tested": len(self.fault_metrics),
            "metrics_per_fault": {
                ft.value: {
                    "detection_rate": metrics["detection_rate"],
                    "recovery_rate": metrics["recovery_success_rate"],
                    "critical_failures": metrics["critical_failures"]
                }
                for ft, metrics in self.fault_metrics.items()
            },
            "critical_risks": self.identify_critical_risks(),
            "production_ready": self.calculate_overall_score() >= 80,
        }