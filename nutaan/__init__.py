"""
Nutaan-CLI - A powerful ReAct Python Assistant with AI capabilities
Made by Tecosys

This package provides an intelligent assistant that can:
- Think through complex problems
- Search the web for information
- Read and write files
- Execute bash commands
- Maintain conversation history
- Manage plans and tasks with progress tracking

Usage:
    nutaan              # Start interactive mode
    nutaan --think      # Start with think mode enabled
    nutaan --test       # Run test queries
    nutaan --history    # Show session history
    nutaan --stats      # Show usage statistics
"""

__version__ = "1.0.1"
__author__ = "Tecosys"
__email__ = "support@tecosys.com"

from .core.agent_manager import agent_manager
from .core.session_history import session_history

__all__ = ["agent_manager", "session_history"]
