"""
Agent Manager - Handles agent creation and configuration
"""

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver

# Import tools from the tools folder
from ..tools.brave_search_tool import BraveWebSearchTool
from ..tools.bash_run_tool import BashRunTool
from ..tools.file_read_tool import FileReadTool
from ..tools.file_write_tool import FileWriteTool
from ..tools.file_edit_tool import FileEditTool
from ..tools.think_tool import ThinkTool
from ..tools.plan_tool import PlanTool

# Import prompt system, LLM manager, and tool approval
from .prompt_system import PromptSystem
from .llm_manager import llm_manager
from .tool_approval_manager import ToolApprovalManager
from .approval_agent_wrapper import ApprovalAgentWrapper


class AgentManager:
    """Manages agent creation and configuration."""
    
    def __init__(self):
        self._agents = {}
        self._llm = None
        self._tools = None
        self._approval_manager = ToolApprovalManager()
        self._llm_manager = None
        
    def refresh_models(self):
        """Refresh the LLM manager to pick up new environment variables."""
        # Import here to avoid circular imports
        from .llm_manager import LLMManager
        self._llm_manager = LLMManager()
        self._llm = None  # Force re-initialization
        
    def _initialize_llm(self):
        """Initialize the language model using the LLM manager."""
        if self._llm is None:
            if self._llm_manager is None:
                # Import here to avoid circular imports
                from .llm_manager import LLMManager
                self._llm_manager = LLMManager()
            
            self._llm = self._llm_manager.get_best_available_llm()
            if not self._llm:
                raise RuntimeError("No available language model found. Please check your API keys and configurations.")
        return self._llm
    
    def _initialize_tools(self):
        """Initialize all tools."""
        if self._tools is None:
            search_tool = BraveWebSearchTool()
            bash_tool = BashRunTool()
            file_read_tool = FileReadTool()
            file_write_tool = FileWriteTool()
            file_edit_tool = FileEditTool()
            think_tool = ThinkTool()
            plan_tool = PlanTool()
            
            self._tools = [think_tool, plan_tool, search_tool, bash_tool, file_read_tool, file_write_tool, file_edit_tool]
        return self._tools
    
    def create_agent(self, think_mode: bool = False, session_id: str = None):
        """Create a LangChain agent with all custom tools, memory, and human approval."""
        
        # Use session_id as agent key, or create default
        agent_key = session_id or f"default_{'think' if think_mode else 'normal'}"
        
        # Return existing agent if available
        if agent_key in self._agents:
            return self._agents[agent_key]
        
        # Initialize components
        llm = self._initialize_llm()
        tools = self._initialize_tools()
        
        # Create memory for conversation history
        memory = MemorySaver()
        
        # Get system prompt
        prompt_system = PromptSystem(think_mode=think_mode)
        
        # Create the base agent with memory
        base_agent = create_react_agent(llm, tools, checkpointer=memory)
        
        # Wrap the agent with approval system
        wrapped_agent = ApprovalAgentWrapper(base_agent, self._approval_manager)
        
        # Store and return
        agent_data = {
            'agent': wrapped_agent,
            'prompt_system': prompt_system,
            'think_mode': think_mode,
            'session_id': session_id,
            'approval_manager': self._approval_manager
        }
        
        self._agents[agent_key] = agent_data
        return agent_data
    
    def get_agent(self, session_id: str = None, think_mode: bool = False):
        """Get an existing agent or create a new one."""
        return self.create_agent(think_mode=think_mode, session_id=session_id)
    
    def list_agents(self):
        """List all active agents."""
        return list(self._agents.keys())
    
    def clear_agents(self):
        """Clear all agents from memory."""
        self._agents.clear()
    
    def reset_tool_approvals(self):
        """Reset all tool approval settings."""
        self._approval_manager.reset_approvals()
    
    def list_tool_approvals(self):
        """List current tool approval settings."""
        self._approval_manager.list_approvals()
    
    def get_approval_manager(self):
        """Get the tool approval manager for direct access."""
        return self._approval_manager
    
    def get_llm_manager(self):
        """Get the LLM manager for direct access."""
        if self._llm_manager is None:
            from .llm_manager import LLMManager
            self._llm_manager = LLMManager()
        return self._llm_manager
    
    def list_available_models(self):
        """List all available language models."""
        if self._llm_manager is None:
            from .llm_manager import LLMManager
            self._llm_manager = LLMManager()
        return self._llm_manager.get_available_models()
    
    def set_preferred_model(self, provider: str, model: str):
        """Set preferred language model."""
        if self._llm_manager is None:
            from .llm_manager import LLMManager
            self._llm_manager = LLMManager()
        
        success = self._llm_manager.set_preferred_model(provider, model)
        if success:
            # Reset LLM to use new model
            self._llm = None
            # Clear existing agents to force recreation with new model
            self._agents.clear()
        return success
    
    def get_current_model_info(self):
        """Get information about the current language model."""
        return llm_manager.get_current_model_info()
    
    def reset_model_selection(self):
        """Reset model selection to auto-detect best available."""
        llm_manager.reset_llm()
        self._llm = None
        self._agents.clear()
    
    def get_tools_info(self):
        """Get information about available tools."""
        tools = self._initialize_tools()
        tools_info = []
        
        for tool in tools:
            tools_info.append({
                'name': tool.name,
                'description': tool.description
            })
        
        return tools_info


# Global agent manager instance
agent_manager = AgentManager()
