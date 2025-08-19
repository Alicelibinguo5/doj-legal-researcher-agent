"""Base agent interface for the multi-agent DOJ research system."""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import datetime
import logging
from ..llm.llm import LLMManager
from ..core.utils import setup_logger


class BaseAgent(ABC):
    """Base class for all agents in the multi-agent system.
    
    This abstract base class defines the common interface and functionality
    that all agents must implement, including memory management, LLM integration,
    and inter-agent communication protocols.
    """
    
    def __init__(self, agent_id: str, llm_config: Optional[Dict] = None) -> None:
        """Initialize base agent with ID and LLM configuration.
        
        Args:
            agent_id: Unique identifier for this agent
            llm_config: Configuration dictionary for LLM initialization
        """
        self.agent_id = agent_id
        self.llm_manager = LLMManager(**(llm_config or {}))
        self.logger = setup_logger(f"{__name__}.{agent_id}")
        self.memory: Optional[Any] = None  # Will be AgentMemory when available
    
    def initialize_memory(self, shared_memory: Any) -> None:
        """Initialize agent's memory from shared store.
        
        Args:
            shared_memory: Shared memory store instance
        """
        self.memory = shared_memory.get_agent_memory(self.agent_id)
    
    @abstractmethod
    async def process(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Process the current state and return updates.
        
        This is the main processing method that each agent must implement.
        It receives the current multi-agent state and returns updates to apply.
        
        Args:
            state: Current multi-agent state dictionary
            
        Returns:
            Dictionary of state updates to apply
        """
        pass
    
    @abstractmethod
    def get_prompt_template(self) -> str:
        """Get agent-specific prompt template.
        
        Returns:
            Prompt template string for this agent's LLM interactions
        """
        pass
    
    def update_memory(self, key: str, value: Any) -> None:
        """Update agent's memory with new information.
        
        Args:
            key: Memory key to update
            value: Value to store
        """
        if self.memory and hasattr(self.memory, 'update_knowledge'):
            self.memory.update_knowledge(key, value)
        else:
            self.logger.warning(f"Memory not initialized for agent {self.agent_id}")
    
    def get_memory(self, key: str) -> Optional[Any]:
        """Retrieve information from agent's memory.
        
        Args:
            key: Memory key to retrieve
            
        Returns:
            Retrieved value or None if not found
        """
        if self.memory and hasattr(self.memory, 'knowledge_base') and key in self.memory.knowledge_base:
            return self.memory.knowledge_base[key]["value"]
        return None
    
    def communicate_with_agent(self, state: Dict[str, Any], target_agent: str, 
                             message_type: str, data: Any) -> None:
        """Send message to another agent through shared state.
        
        Args:
            state: Current multi-agent state
            target_agent: ID of target agent
            message_type: Type of message being sent
            data: Message data payload
        """
        message = {
            "from": self.agent_id,
            "to": target_agent,
            "type": message_type,
            "data": data,
            "timestamp": datetime.now().isoformat()
        }
        
        # Add to communication queue if it exists
        if "agent_communication_queue" in state:
            state["agent_communication_queue"].append(message)
        
        # Also update shared memory if available
        if "shared_memory" in state and hasattr(state["shared_memory"], 'share_knowledge'):
            state["shared_memory"].share_knowledge(
                self.agent_id, target_agent, message_type, data
            )
        
        self.logger.info(f"Message sent from {self.agent_id} to {target_agent}: {message_type}")
    
    def get_agent_messages(self, state: Dict[str, Any], from_agent: Optional[str] = None) -> list:
        """Get messages sent to this agent.
        
        Args:
            state: Current multi-agent state
            from_agent: Optional filter for messages from specific agent
            
        Returns:
            List of messages for this agent
        """
        messages = []
        communication_queue = state.get("agent_communication_queue", [])
        
        for message in communication_queue:
            if message["to"] == self.agent_id:
                if from_agent is None or message["from"] == from_agent:
                    messages.append(message)
        
        return messages
    
    async def generate_llm_response(self, prompt: str, **kwargs) -> str:
        """Generate response using agent's LLM manager.
        
        Args:
            prompt: Prompt to send to LLM
            **kwargs: Additional arguments for LLM generation
            
        Returns:
            Generated response string
        """
        try:
            if hasattr(self.llm_manager, 'generate_async'):
                return await self.llm_manager.generate_async(prompt, **kwargs)
            else:
                return self.llm_manager.generate(prompt, **kwargs)
        except Exception as e:
            self.logger.error(f"LLM generation failed for {self.agent_id}: {e}")
            return f"Error generating response: {str(e)}"
    
    def log_performance_metric(self, metric_name: str, value: Any) -> None:
        """Log performance metric for this agent.
        
        Args:
            metric_name: Name of the metric
            value: Metric value
        """
        if self.memory:
            performance_history = self.get_memory("performance_history") or []
            performance_history.append({
                "metric": metric_name,
                "value": value,
                "timestamp": datetime.now().isoformat(),
                "agent_id": self.agent_id
            })
            self.update_memory("performance_history", performance_history[-100:])  # Keep last 100
        
        self.logger.info(f"Performance metric for {self.agent_id}: {metric_name} = {value}")
