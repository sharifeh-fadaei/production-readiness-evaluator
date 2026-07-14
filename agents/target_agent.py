from typing import Dict, Any
from dataclasses import dataclass, field

@dataclass
class AgentState:
    """Shared state between agents"""
    query: str
    research_results: str = ""
    analysis: str = ""
    verification: str = ""
    status: str = "running"
    error: str = None
    steps_executed: list = field(default_factory=list)

class TargetAgent:
    """Simple 3-agent system: Research → Analyze → Verify"""
    
    def __init__(self, name: str = "MultiAgentSystem"):
        self.name = name
        self.state = None
    
    def research_agent(self, query: str) -> str:
        """Agent 1: Researches and finds information"""
        result = f"Research on '{query}': Found data about population, economy, and history."
        return result
    
    def analyzer_agent(self, research: str) -> str:
        """Agent 2: Analyzes the research"""
        result = f"Analysis: {research} → Key insights include significant economic indicators."
        return result
    
    def verifier_agent(self, analysis: str) -> str:
        """Agent 3: Verifies the analysis is sound"""
        if "Key insights" in analysis:
            result = f"Verification: Analysis is VALID and well-reasoned."
        else:
            result = f"Verification: Analysis is INVALID or incomplete."
        return result
    
    def run(self, query: str) -> Dict[str, Any]:
        """Execute the 3-agent pipeline"""
        self.state = AgentState(query=query)
        
        try:
            # Step 1: Research
            self.state.research_results = self.research_agent(query)
            self.state.steps_executed.append("research")
            
            # Step 2: Analyze
            self.state.analysis = self.analyzer_agent(self.state.research_results)
            self.state.steps_executed.append("analyze")
            
            # Step 3: Verify
            self.state.verification = self.verifier_agent(self.state.analysis)
            self.state.steps_executed.append("verify")
            
            self.state.status = "success"
            
        except Exception as e:
            self.state.status = "failed"
            self.state.error = str(e)
        
        return self._to_dict()
    
    def _to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary"""
        return {
            "query": self.state.query,
            "research_results": self.state.research_results,
            "analysis": self.state.analysis,
            "verification": self.state.verification,
            "status": self.state.status,
            "error": self.state.error,
            "steps_executed": self.state.steps_executed,
        }