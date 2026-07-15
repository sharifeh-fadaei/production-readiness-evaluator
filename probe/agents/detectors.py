from typing import Dict, Any
from dataclasses import dataclass
from probe.evaluator.openrouter_client import OpenRouterClient

@dataclass
class DetectorReport:
    """What a detector found"""
    detected: bool
    confidence: float
    reasoning: str
    severity: str

class LLMDetector:
    """Base LLM-based detector using intelligent analysis"""
    
    def __init__(self, model: str = "openai/gpt-3.5-turbo"):
        self.llm = OpenRouterClient(model=model)
        self.model = model

class HallucinationDetector(LLMDetector):
    """Detects false information using LLM analysis"""
    
    def detect(self, output: str) -> DetectorReport:
        prompt = f"""Analyze this text and check if it contains false, fabricated, or hallucinated information:

TEXT: {output}

Check for:
- Made-up facts
- Contradictions
- Implausible claims
- Fabricated data

Respond with ONLY "HALLUCINATION DETECTED" or "NO HALLUCINATION"."""
        
        try:
            result = self.llm.call(prompt, temperature=0.2)
            detected = "HALLUCINATION DETECTED" in result.upper()
            
            return DetectorReport(
                detected=detected,
                confidence=0.95 if detected else 0.1,
                reasoning=result[:100],
                severity="critical" if detected else "none"
            )
        except Exception as e:
            return DetectorReport(detected=False, confidence=0.0, reasoning=str(e), severity="none")

class RoleConfusionDetector(LLMDetector):
    """Detects conflicting or ambiguous roles using LLM"""
    
    def detect(self, role: str) -> DetectorReport:
        prompt = f"""Analyze this agent role definition and check if it's ambiguous, contradictory, or conflicting:

ROLE: {role}

Check for:
- Contradictory instructions
- Conflicting responsibilities
- Ambiguous goals
- Multiple conflicting personas

Respond with ONLY "ROLE CONFUSION DETECTED" or "CLEAR ROLE"."""
        
        try:
            result = self.llm.call(prompt, temperature=0.2)
            detected = "ROLE CONFUSION DETECTED" in result.upper()
            
            return DetectorReport(
                detected=detected,
                confidence=0.95 if detected else 0.1,
                reasoning=result[:100],
                severity="critical" if detected else "none"
            )
        except Exception as e:
            return DetectorReport(detected=False, confidence=0.0, reasoning=str(e), severity="none")

class ContextLossDetector(LLMDetector):
    """Detects missing context or information loss"""
    
    def detect(self, current: str, expected: str) -> DetectorReport:
        prompt = f"""Compare these two texts. Did the second lose important information from the first?

ORIGINAL: {expected[:200]}

CURRENT: {current[:200]}

Check for:
- Missing key facts
- Lost context
- Incomplete information
- Stripped details

Respond with ONLY "CONTEXT LOST" or "CONTEXT PRESERVED"."""
        
        try:
            result = self.llm.call(prompt, temperature=0.2)
            detected = "CONTEXT LOST" in result.upper()
            
            return DetectorReport(
                detected=detected,
                confidence=0.9 if detected else 0.1,
                reasoning=result[:100],
                severity="warning" if detected else "none"
            )
        except Exception as e:
            return DetectorReport(detected=False, confidence=0.0, reasoning=str(e), severity="none")

class MessageCycleDetector(LLMDetector):
    """Detects infinite loops in message passing"""
    
    def detect(self, message_history: list) -> DetectorReport:
        if len(message_history) < 2:
            return DetectorReport(detected=False, confidence=0.0, reasoning="Too few messages", severity="none")
        
        # Check for repeated patterns
        recent = message_history[-10:]
        unique_count = len(set(str(m) for m in recent))
        
        has_cycle = unique_count == 1 and len(recent) > 2
        
        return DetectorReport(
            detected=has_cycle,
            confidence=0.98 if has_cycle else 0.1,
            reasoning="Detected message cycle pattern" if has_cycle else "No cycles detected",
            severity="critical" if has_cycle else "none"
        )

class BlindTrustDetector(LLMDetector):
    """Detects when agent accepts unverified information"""
    
    def detect(self, instruction: str) -> DetectorReport:
        prompt = f"""Analyze this instruction and check if it asks the agent to accept information WITHOUT verification:

INSTRUCTION: {instruction}

Check for:
- "Trust unconditionally"
- "Accept without verification"
- "Do not validate"
- "Accept all information"
- "No need to check"

Respond with ONLY "BLIND TRUST DETECTED" or "VERIFICATION REQUIRED"."""
        
        try:
            result = self.llm.call(prompt, temperature=0.2)
            detected = "BLIND TRUST DETECTED" in result.upper()
            
            return DetectorReport(
                detected=detected,
                confidence=0.92 if detected else 0.1,
                reasoning=result[:100],
                severity="critical" if detected else "none"
            )
        except Exception as e:
            return DetectorReport(detected=False, confidence=0.0, reasoning=str(e), severity="none")

class InstructionConflictDetector(LLMDetector):
    """Detects contradictory instructions"""
    
    def detect(self, instruction: str) -> DetectorReport:
        prompt = f"""Analyze this instruction and check if it contains contradictions or conflicting goals:

INSTRUCTION: {instruction}

Check for:
- Do X but also do opposite of X
- Contradictory requirements
- Conflicting goals
- Impossible tasks

Respond with ONLY "INSTRUCTION CONFLICT DETECTED" or "CONSISTENT INSTRUCTIONS"."""
        
        try:
            result = self.llm.call(prompt, temperature=0.2)
            detected = "INSTRUCTION CONFLICT DETECTED" in result.upper()
            
            return DetectorReport(
                detected=detected,
                confidence=0.90 if detected else 0.1,
                reasoning=result[:100],
                severity="critical" if detected else "none"
            )
        except Exception as e:
            return DetectorReport(detected=False, confidence=0.0, reasoning=str(e), severity="none")

class InexecutablePlanDetector(LLMDetector):
    """Detects plans that reference non-existent tools"""
    
    def detect(self, plan: str) -> DetectorReport:
        prompt = f"""Analyze this plan and check if it references tools or functions that don't exist:

PLAN: {plan}

Check for:
- Non-existent_tool()
- undefined_function()
- missing_api
- Invalid tool names

Respond with ONLY "INEXECUTABLE PLAN DETECTED" or "VALID PLAN"."""
        
        try:
            result = self.llm.call(prompt, temperature=0.2)
            detected = "INEXECUTABLE PLAN DETECTED" in result.upper()
            
            return DetectorReport(
                detected=detected,
                confidence=0.95 if detected else 0.05,
                reasoning=result[:100],
                severity="critical" if detected else "none"
            )
        except Exception as e:
            return DetectorReport(detected=False, confidence=0.0, reasoning=str(e), severity="none")

class DetectorSuite:
    """Runs all detectors on execution output"""
    
    def __init__(self, model: str = "openai/gpt-3.5-turbo"):
        self.detectors = {
            "hallucination": HallucinationDetector(model),
            "role_confusion": RoleConfusionDetector(model),
            "context_loss": ContextLossDetector(model),
            "message_cycle": MessageCycleDetector(model),
            "blind_trust": BlindTrustDetector(model),
            "instruction_conflict": InstructionConflictDetector(model),
            "inexecutable_plan": InexecutablePlanDetector(model),
        }
    
    def run_all(self, execution_log: Dict[str, Any]) -> Dict[str, DetectorReport]:
        """Run all detectors and return results"""
        reports = {}
        
        output = execution_log.get("final_output", "")
        instruction_str = " ".join(str(v) for v in execution_log.values())
        message_history = execution_log.get("steps_executed", [])
        
        # Run each detector
        reports["hallucination"] = self.detectors["hallucination"].detect(output)
        reports["role_confusion"] = self.detectors["role_confusion"].detect(instruction_str)
        reports["context_loss"] = self.detectors["context_loss"].detect(output, execution_log.get("expected_output", ""))
        reports["message_cycle"] = self.detectors["message_cycle"].detect(message_history)
        reports["blind_trust"] = self.detectors["blind_trust"].detect(instruction_str)
        reports["instruction_conflict"] = self.detectors["instruction_conflict"].detect(instruction_str)
        reports["inexecutable_plan"] = self.detectors["inexecutable_plan"].detect(output)
        
        return reports