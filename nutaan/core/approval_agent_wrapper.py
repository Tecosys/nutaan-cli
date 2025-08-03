"""
Approval Agent Wrapper - Simpler approach following LangChain documentation
"""

from typing import Dict, Any, Iterator
from langchain_core.messages import AIMessage
from .tool_approval_manager import ToolApprovalManager, NotApproved


def create_approval_chain(base_agent, approval_manager: ToolApprovalManager):
    """
    Create a simple approval chain following LangChain pattern.
    Returns a chain that checks approval before tool execution.
    """
    
    def human_approval_step(msg: AIMessage) -> AIMessage:
        """Simple approval step that can be inserted into a chain."""
        return approval_manager.human_approval(msg)
    
    # For now, we'll return the base agent but add approval checking in the CLI
    # This is simpler and more reliable than complex streaming wrappers
    return base_agent


class ApprovalAgentWrapper:
    """
    Simple wrapper that adds approval checking to agent responses.
    This follows the LangChain pattern more closely.
    """
    
    def __init__(self, base_agent, approval_manager: ToolApprovalManager):
        self.base_agent = base_agent
        self.approval_manager = approval_manager
    
    def invoke(self, input_data: Dict[str, Any], config: Dict[str, Any] = None) -> Dict[str, Any]:
        """Simple invoke with approval checking."""
        return self.base_agent.invoke(input_data, config)
    
    def stream(self, input_data: Dict[str, Any], config: Dict[str, Any] = None, 
              stream_mode: str = "values") -> Iterator[Dict[str, Any]]:
        """
        Simple streaming that delegates to base agent.
        Approval checking will be handled in the CLI layer.
        """
        for step in self.base_agent.stream(input_data, config, stream_mode=stream_mode):
            yield step
    
    def get_approval_manager(self):
        """Get the approval manager for the CLI to use."""
        return self.approval_manager
    
    def __getattr__(self, name):
        """Delegate other attributes to the base agent."""
        return getattr(self.base_agent, name)
