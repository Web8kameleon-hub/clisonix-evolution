"""
Agent Registry - Intelligent Task Orchestration
================================================
Agents select appropriate labs and manage task execution.
Each agent specializes in certain types of tasks/data.

Flow: Input → Agent Selection → Lab Execution → Artifact Generation
"""

import json
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
from datetime import datetime
from enum import Enum


class AgentStatus(Enum):
    """Agent operational status"""
    ACTIVE = "ACTIVE"
    IDLE = "IDLE"
    BUSY = "BUSY"
    DISABLED = "DISABLED"


class AgentCapability(Enum):
    """Agent capabilities"""
    DATA_VALIDATION = "data_validation"
    TRANSFORMATION = "transformation"
    INTEGRATION = "integration"
    ANALYSIS = "analysis"
    REPORTING = "reporting"
    ML_INFERENCE = "ml_inference"


@dataclass
class AgentProfile:
    """Profile of an agent"""
    agent_id: str
    name: str
    description: str
    capabilities: List[AgentCapability]
    supported_layers: List[str]
    supported_protocols: List[str]
    priority: int = 1  # Higher = more preferred
    max_concurrent_tasks: int = 10
    current_tasks: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'agent_id': self.agent_id,
            'name': self.name,
            'description': self.description,
            'capabilities': [c.value for c in self.capabilities],
            'supported_layers': self.supported_layers,
            'supported_protocols': self.supported_protocols,
            'priority': self.priority,
            'max_concurrent_tasks': self.max_concurrent_tasks,
            'current_tasks': self.current_tasks,
            'status': self.status.value
        }
    
    @property
    def status(self) -> AgentStatus:
        """Get current status based on task load"""
        if self.current_tasks >= self.max_concurrent_tasks:
            return AgentStatus.BUSY
        if self.current_tasks > 0:
            return AgentStatus.ACTIVE
        return AgentStatus.IDLE
    
    @property
    def available_capacity(self) -> int:
        """Get available task capacity"""
        return max(0, self.max_concurrent_tasks - self.current_tasks)


class Agent(ABC):
    """Abstract base class for agents"""
    
    @property
    @abstractmethod
    def profile(self) -> AgentProfile:
        """Agent's profile"""
        pass
    
    @abstractmethod
    def can_handle(self, row: Dict[str, Any]) -> bool:
        """Check if this agent can handle the given row"""
        pass
    
    @abstractmethod
    def select_labs(self, row: Dict[str, Any]) -> List[str]:
        """Select appropriate labs for the row"""
        pass
    
    def score(self, row: Dict[str, Any]) -> float:
        """
        Score how well this agent matches the row (0-1)
        Higher score = better match
        """
        if not self.can_handle(row):
            return 0.0
        
        score = 0.0
        
        # Layer match
        layer = row.get('layer', 'L1')
        if layer in self.profile.supported_layers:
            score += 0.3
        
        # Protocol match
        protocol = row.get('source_protocol', '')
        if protocol in self.profile.supported_protocols:
            score += 0.3
        
        # Capacity bonus
        if self.profile.available_capacity > 0:
            score += 0.2 * (self.profile.available_capacity / self.profile.max_concurrent_tasks)
        
        # Priority bonus
        score += 0.2 * (self.profile.priority / 10)
        
        return min(1.0, score)


class DataProcessingAgent(Agent):
    """Agent specialized in data processing and validation"""
    
    def __init__(self):
        self._profile = AgentProfile(
            agent_id="agent-data-processing",
            name="Data Processing Agent",
            description="Handles data validation, cleaning, and transformation",
            capabilities=[
                AgentCapability.DATA_VALIDATION,
                AgentCapability.TRANSFORMATION
            ],
            supported_layers=["L1", "L2", "L3"],
            supported_protocols=["REST", "GraphQL", "File", "Webhook"],
            priority=5
        )
    
    @property
    def profile(self) -> AgentProfile:
        return self._profile
    
    def can_handle(self, row: Dict[str, Any]) -> bool:
        """Can handle any row with data"""
        return 'input_type' in row
    
    def select_labs(self, row: Dict[str, Any]) -> List[str]:
        """Select data processing labs"""
        labs = ["lab-data-validation"]
        
        # Add transformation if not raw file
        if row.get('source_protocol') != 'File':
            labs.append("lab-transformation")
        
        return labs


class IntegrationAgent(Agent):
    """Agent specialized in integration testing"""
    
    def __init__(self):
        self._profile = AgentProfile(
            agent_id="agent-integration",
            name="Integration Agent",
            description="Handles integration testing with external systems",
            capabilities=[
                AgentCapability.INTEGRATION,
                AgentCapability.DATA_VALIDATION
            ],
            supported_layers=["L1", "L2"],
            supported_protocols=["REST", "GraphQL", "gRPC"],
            priority=4
        )
    
    @property
    def profile(self) -> AgentProfile:
        return self._profile
    
    def can_handle(self, row: Dict[str, Any]) -> bool:
        """Can handle rows with external protocol"""
        protocol = row.get('source_protocol', '')
        return protocol in self.profile.supported_protocols
    
    def select_labs(self, row: Dict[str, Any]) -> List[str]:
        """Select integration labs"""
        return ["lab-data-validation", "lab-integration"]


class AnalyticsAgent(Agent):
    """Agent specialized in analytics and reporting"""
    
    def __init__(self):
        self._profile = AgentProfile(
            agent_id="agent-analytics",
            name="Analytics Agent",
            description="Handles data analysis and report generation",
            capabilities=[
                AgentCapability.ANALYSIS,
                AgentCapability.REPORTING
            ],
            supported_layers=["L2", "L3"],
            supported_protocols=["REST", "File", "Webhook"],
            priority=3
        )
    
    @property
    def profile(self) -> AgentProfile:
        return self._profile
    
    def can_handle(self, row: Dict[str, Any]) -> bool:
        """Can handle rows with analytics data"""
        input_type = row.get('input_type', '')
        return 'analytics' in input_type.lower() or 'report' in input_type.lower()
    
    def select_labs(self, row: Dict[str, Any]) -> List[str]:
        """Select analytics labs"""
        return ["lab-data-validation", "lab-transformation"]


class MLAgent(Agent):
    """Agent specialized in ML inference (only for MATURE rows)"""
    
    def __init__(self):
        self._profile = AgentProfile(
            agent_id="agent-ml",
            name="ML Agent",
            description="Handles ML inference - only activated for MATURE rows",
            capabilities=[
                AgentCapability.ML_INFERENCE,
                AgentCapability.ANALYSIS
            ],
            supported_layers=["L1", "L2", "L3"],
            supported_protocols=["REST", "GraphQL", "gRPC", "File", "Webhook"],
            priority=2
        )
    
    @property
    def profile(self) -> AgentProfile:
        return self._profile
    
    def can_handle(self, row: Dict[str, Any]) -> bool:
        """Only handle MATURE rows"""
        maturity = row.get('maturity_state', 'IMMATURE')
        return maturity == 'MATURE'
    
    def select_labs(self, row: Dict[str, Any]) -> List[str]:
        """ML agent doesn't use labs, uses ML overlay instead"""
        return []


class AgentRegistry:
    """Registry of available agents"""
    
    def __init__(self):
        self.agents: Dict[str, Agent] = {}
        self._register_defaults()
    
    def _register_defaults(self):
        """Register default agents"""
        self.register(DataProcessingAgent())
        self.register(IntegrationAgent())
        self.register(AnalyticsAgent())
        self.register(MLAgent())
    
    def register(self, agent: Agent):
        """Register an agent"""
        self.agents[agent.profile.agent_id] = agent
    
    def get_agent(self, agent_id: str) -> Optional[Agent]:
        """Get agent by ID"""
        return self.agents.get(agent_id)
    
    def get_available_agents(self, row: Dict[str, Any]) -> List[Agent]:
        """Get all agents that can handle the given row"""
        return [
            agent for agent in self.agents.values()
            if agent.can_handle(row) and agent.profile.available_capacity > 0
        ]
    
    def select_best_agent(self, row: Dict[str, Any]) -> Optional[Agent]:
        """
        Select the best agent for the given row
        
        Uses scoring to find the most suitable agent
        """
        available = self.get_available_agents(row)
        if not available:
            return None
        
        # Score each agent and return the best
        scored = [(agent, agent.score(row)) for agent in available]
        scored.sort(key=lambda x: x[1], reverse=True)
        
        return scored[0][0] if scored else None
    
    def list_agents(self) -> List[Dict[str, Any]]:
        """List all registered agents"""
        return [agent.profile.to_dict() for agent in self.agents.values()]


class AgentManager:
    """
    Manages agent selection and task assignment
    """
    
    def __init__(self, registry: Optional[AgentRegistry] = None):
        self.registry = registry or AgentRegistry()
    
    def select_agent(self, row: Dict[str, Any]) -> Optional[str]:
        """
        Select the best agent for a row
        
        Args:
            row: Canonical row data
            
        Returns:
            Agent ID or None if no suitable agent
        """
        agent = self.registry.select_best_agent(row)
        if agent:
            return agent.profile.agent_id
        return None
    
    def get_labs_for_row(self, row: Dict[str, Any], agent_id: Optional[str] = None) -> List[str]:
        """
        Get appropriate labs for a row
        
        Args:
            row: Canonical row data
            agent_id: Optional specific agent to use
            
        Returns:
            List of lab IDs to execute
        """
        if agent_id:
            agent = self.registry.get_agent(agent_id)
        else:
            agent = self.registry.select_best_agent(row)
        
        if agent:
            return agent.select_labs(row)
        
        # Default: run data validation
        return ["lab-data-validation"]
    
    def assign_task(self, row: Dict[str, Any], agent_id: str) -> bool:
        """
        Assign a task to an agent
        
        Args:
            row: Canonical row data
            agent_id: Agent to assign to
            
        Returns:
            True if assignment successful
        """
        agent = self.registry.get_agent(agent_id)
        if not agent:
            return False
        
        if agent.profile.available_capacity <= 0:
            return False
        
        agent.profile.current_tasks += 1
        return True
    
    def complete_task(self, agent_id: str) -> bool:
        """
        Mark a task as complete
        
        Args:
            agent_id: Agent that completed the task
            
        Returns:
            True if successful
        """
        agent = self.registry.get_agent(agent_id)
        if not agent:
            return False
        
        if agent.profile.current_tasks > 0:
            agent.profile.current_tasks -= 1
        return True


# Global agent manager
_agent_manager: Optional[AgentManager] = None

def get_agent_manager() -> AgentManager:
    """Get or create the global agent manager"""
    global _agent_manager
    if _agent_manager is None:
        _agent_manager = AgentManager()
    return _agent_manager


def select_agent(row: Dict[str, Any]) -> Optional[str]:
    """
    Main entry point: Select the best agent for a row
    
    Args:
        row: Canonical row data
        
    Returns:
        Agent ID or None
    """
    manager = get_agent_manager()
    return manager.select_agent(row)
