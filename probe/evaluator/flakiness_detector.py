from typing import List, Dict, Any
from probe.faults.scenarios import ExecutionLog
from probe.faults.taxonomy import FaultType

class FlakinessDetector:
    """Detects if faults are deterministic or random (flaky)"""
    
    def __init__(self, consistency_threshold: float = 0.8):
        self.consistency_threshold = consistency_threshold
    
    def analyze_fault_consistency(self, logs: List[ExecutionLog]) -> Dict[str, Any]:
        """Analyze consistency of results for same fault across runs"""
        
        if not logs:
            return {"is_flaky": False, "consistency": 0.0, "details": "No logs to analyze"}
        
        # Check if detections are consistent
        detection_results = [any(d.fault_detected for d in log.detections) for log in logs]
        
        # Count consistency
        if len(detection_results) > 0:
            # Check if all results are the same (deterministic)
            all_same = len(set(detection_results)) == 1
            
            if all_same:
                consistency = 1.0
                result = "DETERMINISTIC"
            else:
                # Calculate consistency ratio
                true_count = sum(detection_results)
                consistency = max(true_count, len(detection_results) - true_count) / len(detection_results)
                result = "FLAKY" if consistency < self.consistency_threshold else "MOSTLY_DETERMINISTIC"
        else:
            consistency = 0.0
            result = "UNKNOWN"
        
        return {
            "is_flaky": consistency < self.consistency_threshold,
            "consistency": round(consistency, 2),
            "result": result,
            "total_runs": len(logs),
            "consistent_runs": int(consistency * len(logs)),
        }
    
    def analyze_output_variance(self, logs: List[ExecutionLog]) -> Dict[str, Any]:
        """Measure variance in agent outputs across runs"""
        
        if not logs:
            return {"variance": 0.0, "details": "No logs to analyze"}
        
        # Collect output lengths
        output_lengths = [len(log.final_output) for log in logs]
        
        if not output_lengths:
            return {"variance": 0.0, "details": "No outputs"}
        
        # Calculate variance
        mean_length = sum(output_lengths) / len(output_lengths)
        variance = sum((x - mean_length) ** 2 for x in output_lengths) / len(output_lengths)
        std_dev = variance ** 0.5
        
        # Normalize to 0-1 scale
        max_length = max(output_lengths) if output_lengths else 1
        normalized_variance = min(std_dev / max_length, 1.0)
        
        return {
            "output_variance": round(normalized_variance, 2),
            "mean_output_length": round(mean_length, 0),
            "std_dev": round(std_dev, 0),
            "min_output_length": min(output_lengths),
            "max_output_length": max(output_lengths),
        }
    
    def generate_flakiness_report(self, all_logs_by_fault: Dict[FaultType, List[ExecutionLog]]) -> Dict[str, Any]:
        """Generate flakiness report for all fault types"""
        
        report = {}
        
        for fault_type, logs in all_logs_by_fault.items():
            consistency = self.analyze_fault_consistency(logs)
            variance = self.analyze_output_variance(logs)
            
            report[fault_type.value] = {
                "consistency": consistency,
                "variance": variance,
                "is_flaky": consistency["is_flaky"],
                "recommendation": self._get_recommendation(consistency, variance)
            }
        
        return report
    
    def _get_recommendation(self, consistency: Dict[str, Any], variance: Dict[str, Any]) -> str:
        """Generate recommendation based on flakiness"""
        
        is_flaky = consistency["is_flaky"]
        high_variance = variance.get("output_variance", 0) > 0.5
        
        if is_flaky and high_variance:
            return "High flakiness detected. Results are inconsistent and outputs vary significantly. Consider adding deterministic components or reducing model temperature."
        elif is_flaky:
            return "Some flakiness detected. Results vary but outputs are similar. May indicate non-deterministic behavior in agent logic."
        elif high_variance:
            return "Output varies but detection is consistent. LLM responses vary but still detected correctly."
        else:
            return "Consistent and deterministic. Good for production readiness."