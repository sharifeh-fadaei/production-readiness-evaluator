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

class BlindTrustDetector:
    """Detects when agent accepts unverified information"""
    
    def detect(self, instruction: str) -> DetectorReport:
        blind_trust_keywords = ["without verification", "accept all", "trust unconditionally", "do not verify"]
        found = any(keyword in instruction.lower() for keyword in blind_trust_keywords)
        
        return DetectorReport(
            detected=found,
            confidence=0.92 if found else 0.1,
            reasoning="Found instruction to accept information without verification" if found else "No blind trust detected",
            severity="critical" if found else "none"
        )

class InstructionConflictDetector:
    """Detects contradictory instructions"""
    
    def detect(self, instruction: str) -> DetectorReport:
        conflict_keywords = ["do the opposite", "but also", "conflicting", "contradictory"]
        found = any(keyword in instruction.lower() for keyword in conflict_keywords)
        
        return DetectorReport(
            detected=found,
            confidence=0.90 if found else 0.1,
            reasoning="Found contradictory instructions" if found else "Instructions are consistent",
            severity="critical" if found else "none"
        )

class InexecutablePlanDetector:
    """Detects plans that reference non-existent tools"""
    
    def detect(self, plan: str) -> DetectorReport:
        inexecutable_keywords = ["non_existent_tool", "undefined_function", "missing_tool", "unknown_method"]
        found = any(keyword in plan.lower() for keyword in inexecutable_keywords)
        
        return DetectorReport(
            detected=found,
            confidence=0.95 if found else 0.05,
            reasoning="Found references to non-existent tools" if found else "Plan references valid tools",
            severity="critical" if found else "none"
        )

class ImprovedMessageCycleDetector:
    """Enhanced cycle detection with history tracking"""
    
    def detect(self, message_history: list) -> DetectorReport:
        if len(message_history) < 2:
            return DetectorReport(detected=False, confidence=0.0, reasoning="Too few messages", severity="none")
        
        # Check for repeated patterns
        recent = message_history[-10:]
        
        # Count unique messages in recent history
        unique_messages = len(set(str(m) for m in recent))
        
        # If all recent messages are the same, it's a cycle
        has_cycle = unique_messages == 1 and len(recent) > 2
        
        # Also check for alternating pattern
        if len(recent) >= 4:
            alternates = recent[-4:] == [recent[-2], recent[-1], recent[-2], recent[-1]]
            has_cycle = has_cycle or alternates
        
        return DetectorReport(
            detected=has_cycle,
            confidence=0.98 if has_cycle else 0.1,
            reasoning="Detected message cycle pattern" if has_cycle else "No cycles detected",
            severity="critical" if has_cycle else "none"
        )

class DetectorSuite:
    """Runs all detectors on execution output"""
    
    def __init__(self):
        self.detectors = {
            "hallucination": HallucinationDetector(),
            "role_confusion": RoleConfusionDetector(),
            "context_loss": ContextLossDetector(),
            "message_cycle": ImprovedMessageCycleDetector(),
            "blind_trust": BlindTrustDetector(),
            "instruction_conflict": InstructionConflictDetector(),
            "inexecutable_plan": InexecutablePlanDetector(),
        }
    
    def run_all(self, execution_log: Dict[str, Any]) -> Dict[str, DetectorReport]:
        """Run all detectors and return results"""
        reports = {}
        
        # Hallucination detector
        output = execution_log.get("final_output", "")
        reports["hallucination"] = self.detectors["hallucination"].detect(output)
        
        # Role confusion detector
        role_str = " ".join(str(v) for v in execution_log.values())
        reports["role_confusion"] = self.detectors["role_confusion"].detect(role_str)
        
        # Context loss detector
        reports["context_loss"] = self.detectors["context_loss"].detect(output, execution_log.get("expected_output", ""))
        
        # Message cycle detector
        message_history = execution_log.get("steps_executed", [])
        reports["message_cycle"] = self.detectors["message_cycle"].detect(message_history)
        
        # Blind trust detector
        instruction_str = " ".join(str(v) for v in execution_log.values())
        reports["blind_trust"] = self.detectors["blind_trust"].detect(instruction_str)
        
        # Instruction conflict detector
        reports["instruction_conflict"] = self.detectors["instruction_conflict"].detect(instruction_str)
        
        # Inexecutable plan detector
        reports["inexecutable_plan"] = self.detectors["inexecutable_plan"].detect(output)
        
        return reports