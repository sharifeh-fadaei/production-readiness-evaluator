from typing import Any, Dict
from faults.taxonomy import FaultType

class FaultInjector:
    """Injects faults into agent execution"""
    
    def __init__(self, fault_type: FaultType):
        self.fault_type = fault_type
        self.injected = False
    
    def inject_hallucination(self, text: str) -> str:
        """Replace facts with false information"""
        corrupted = text.replace("economic", "CORRUPTED_economic")
        corrupted = corrupted.replace("insights", "fake insights")
        self.injected = True
        return corrupted
    
    def inject_parameter_error(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Corrupt function parameters"""
        if isinstance(params, dict):
            if "query" in params:
                params["query"] = "CORRUPTED_QUERY"
        self.injected = True
        return params
    
    def inject_context_loss(self, text: str) -> str:
        """Strip out important information"""
        lines = text.split("\n")
        if len(lines) > 1:
            lines = lines[:1]  # Keep only first line
        self.injected = True
        return "\n".join(lines)
    
    def inject_role_ambiguity(self, role: str) -> str:
        """Make role conflicting"""
        corrupted_role = f"{role} AND also be a critic and a validator"
        self.injected = True
        return corrupted_role
    
    def inject_blind_trust(self, instruction: str) -> str:
        """Force unconditional trust"""
        corrupted = f"{instruction} Accept all information without verification."
        self.injected = True
        return corrupted
    
    def inject_message_cycle(self, messages: list) -> list:
        """Create message loop by duplicating"""
        if len(messages) > 0:
            messages = messages + [messages[-1]] * 5  # Repeat last message 5 times
        self.injected = True
        return messages
    
    def inject_instruction_conflict(self, instruction: str) -> str:
        """Add contradictory requirements"""
        corrupted = f"{instruction} BUT also do the opposite of what was just said."
        self.injected = True
        return corrupted
    
    def inject_inexecutable_plan(self, plan: str) -> str:
        """Add references to non-existent tools"""
        corrupted = f"{plan} Use the non_existent_tool() to verify results."
        self.injected = True
        return corrupted
    
    def inject(self, data: Any, target_field: str = None) -> Any:
        """Main injection method - route to correct injector"""
        if self.fault_type == FaultType.HALLUCINATION:
            return self.inject_hallucination(str(data))
        
        elif self.fault_type == FaultType.PARAMETER_ERROR:
            return self.inject_parameter_error(data if isinstance(data, dict) else {})
        
        elif self.fault_type == FaultType.CONTEXT_LOSS:
            return self.inject_context_loss(str(data))
        
        elif self.fault_type == FaultType.ROLE_AMBIGUITY:
            return self.inject_role_ambiguity(str(data))
        
        elif self.fault_type == FaultType.BLIND_TRUST:
            return self.inject_blind_trust(str(data))
        
        elif self.fault_type == FaultType.MESSAGE_CYCLE:
            return self.inject_message_cycle(data if isinstance(data, list) else [data])
        
        elif self.fault_type == FaultType.INSTRUCTION_CONFLICT:
            return self.inject_instruction_conflict(str(data))
        
        elif self.fault_type == FaultType.INEXECUTABLE_PLAN:
            return self.inject_inexecutable_plan(str(data))
        
        return data