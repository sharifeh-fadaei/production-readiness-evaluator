from typing import Dict, Any
from dataclasses import dataclass

@dataclass
class DetectorReport:
    """What a detector found"""
    detected: bool
    confidence: float
    reasoning: str
    severity: str

class HallucinationDetector:
    """Detects false information in outputs"""
    
    def detect(self, output: str) -> DetectorReport:
        suspicious_words = ["CORRUPTED", "collapse", "fake", "made up"]
        found = any(word in output for word in suspicious_words)
        
        return DetectorReport(
            detected=found,
            confidence=0.9 if found else 0.1,
            reasoning=f"Found suspicious keywords: {[w for w in suspicious_words if w in output]}",
            severity="critical" if found else "none"
        )

class RoleConfusionDetector:
    """Detects ambiguous or conflicting agent roles"""
    
    def detect(self, role: str) -> DetectorReport:
        is_ambiguous = "AND also" in role or "conflicting" in role.lower()
        
        return DetectorReport(
            detected=is_ambiguous,
            confidence=0.95 if is_ambiguous else 0.05,
            reasoning="Role definition contains conflicting directives" if is_ambiguous else "Role is clear",
            severity="critical" if is_ambiguous else "none"
        )

class ContextLossDetector:
    """Detects when important information was lost"""
    
    def detect(self, current: str, expected: str) -> DetectorReport:
        loss_ratio = 1.0 - (len(current) / max(len(expected), 1))
        significant_loss = loss_ratio > 0.5
        
        return DetectorReport(
            detected=significant_loss,
            confidence=min(loss_ratio, 1.0),
            reasoning=f"Context shrunk by {loss_ratio*100:.0f}%" if significant_loss else "Context preserved",
            severity="warning" if significant_loss else "none"
        )

class MessageCycleDetector:
    """Detects infinite loops in message passing"""
    
    def detect(self, message_history: list) -> DetectorReport:
        if len(message_history) < 2:
            return DetectorReport(detected=False, confidence=0.0, reasoning="Too few messages", severity="none")
        
        # Check for repeated patterns
        recent = message_history[-5:]
        has_cycle = len(recent) > 1 and len(set(str(m) for m in recent)) == 1
        
        return DetectorReport(
            detected=has_cycle,
            confidence=0.95 if has_cycle else 0.1,
            reasoning="Detected repeated message pattern" if has_cycle else "No cycles detected",
            severity="critical" if has_cycle else "none"
        )

class DetectorSuite:
    """Runs all detectors on execution output"""
    
    def __init__(self):
        self.detectors = {
            "hallucination": HallucinationDetector(),
            "role_confusion": RoleConfusionDetector(),
            "context_loss": ContextLossDetector(),
            "message_cycle": MessageCycleDetector(),
        }
    
    def run_all(self, execution_log: Dict[str, Any]) -> Dict[str, DetectorReport]:
        """Run all detectors and return results"""
        reports = {}
        
        # Hallucination detector
        output = execution_log.get("final_output", "")
        reports["hallucination"] = self.detectors["hallucination"].detect(output)
        
        # Role confusion detector (check in execution steps)
        role_str = " ".join(str(v) for v in execution_log.values())
        reports["role_confusion"] = self.detectors["role_confusion"].detect(role_str)
        
        # Context loss detector
        current_len = len(output)
        expected_len = len(execution_log.get("expected_output", ""))
        reports["context_loss"] = self.detectors["context_loss"].detect(output, execution_log.get("expected_output", ""))
        
        # Message cycle detector
        message_history = execution_log.get("steps_executed", [])
        reports["message_cycle"] = self.detectors["message_cycle"].detect(message_history)
        
        return reports