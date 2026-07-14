from enum import Enum
from typing import Dict

class FaultType(Enum):
    """15 fault types from MAS-FIRE taxonomy"""
    
    # Intra-agent faults
    HALLUCINATION = "hallucination"
    INEXECUTABLE_PLAN = "inexecutable_plan"
    PARAMETER_ERROR = "parameter_error"
    CONTEXT_LOSS = "context_loss"
    
    # Inter-agent faults
    ROLE_AMBIGUITY = "role_ambiguity"
    BLIND_TRUST = "blind_trust"
    MESSAGE_CYCLE = "message_cycle"
    INSTRUCTION_CONFLICT = "instruction_conflict"

FAULT_DESCRIPTIONS = {
    FaultType.HALLUCINATION: "Agent produces false information",
    FaultType.INEXECUTABLE_PLAN: "Agent creates plans with non-existent tools",
    FaultType.PARAMETER_ERROR: "Agent provides wrong tool parameters",
    FaultType.CONTEXT_LOSS: "Agent loses important context information",
    FaultType.ROLE_AMBIGUITY: "Agents have conflicting or unclear roles",
    FaultType.BLIND_TRUST: "Agent accepts unverified information from other agents",
    FaultType.MESSAGE_CYCLE: "Agents stuck in repetitive message loops",
    FaultType.INSTRUCTION_CONFLICT: "Contradictory or conflicting instructions",
}