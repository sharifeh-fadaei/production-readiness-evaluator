from dataclasses import dataclass
from typing import Dict, Any
from faults.taxonomy import FaultType

@dataclass
class FaultScenario:
    """One instance of a fault being injected"""
    scenario_id: str
    fault_type: FaultType
    task: str
    injected_at: str
    injection_details: Dict[str, Any]
    ground_truth: Dict[str, Any]

@dataclass
class ExecutionLog:
    """Record of what happened during a test run"""
    scenario: FaultScenario
    execution_trace: Dict[str, Any]
    final_output: str
    errors: list
    success: bool

@dataclass
class DetectionResult:
    """What one detector reported"""
    detector_name: str
    fault_detected: bool
    confidence: float
    reasoning: str
    severity: str  # "critical", "warning", "none"

@dataclass
class FaultMetrics:
    """Aggregated results for one fault type"""
    fault_type: FaultType
    total_runs: int
    detection_rate: float
    false_positive_rate: float
    recovery_success_rate: float
    critical_failures: int
    per_detector: Dict[str, Dict[str, float]]