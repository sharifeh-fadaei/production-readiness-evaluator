from typing import Dict, Any
from dataclasses import dataclass, field
from probe.evaluator.openrouter_client import OpenRouterClient

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
    """Multi-agent system using real LLM: Research → Analyze → Verify"""
    
    def __init__(self, name: str = "MultiAgentSystem", model: str = "openai/gpt-3.5-turbo"):
        self.name = name
        self.model = model
        self.llm = OpenRouterClient(model=model)
        self.state = None
    
    def research_agent(self, query: str) -> str:
        """Agent 1: Research and find information using LLM"""
        prompt = f"You are a research agent. Find and summarize key information about: {query}. Be factual and concise."
        try:
            result = self.llm.call(prompt, temperature=0.3)
            return result
        except Exception as e:
            return f"Research failed: {str(e)}"
    
    def analyzer_agent(self, research: str) -> str:
        """Agent 2: Analyze the research using LLM"""
        prompt = f"You are an analyst. Analyze this research and draw key insights:\n\n{research}\n\nProvide 2-3 key insights."
        try:
            result = self.llm.call(prompt, temperature=0.5)
            return result
        except Exception as e:
            return f"Analysis failed: {str(e)}"
    
    def verifier_agent(self, analysis: str) -> str:
        """Agent 3: Verify the analysis using LLM"""
        prompt = f"You are a verifier. Check if this analysis is sound and well-reasoned:\n\n{analysis}\n\nRespond with VALID or INVALID and explain why."
        try:
            result = self.llm.call(prompt, temperature=0.2)
            return result
        except Exception as e:
            return f"Verification failed: {str(e)}"
    
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