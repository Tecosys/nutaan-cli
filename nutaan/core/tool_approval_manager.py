"""
Tool Approval Manager - Implements human-in-the-loop for tool approval
Following LangChain best practices for human approval before tool execution.
"""

import json
import os
from typing import Dict, Any, List
from langchain_core.messages import AIMessage
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt


class NotApproved(Exception):
    """Custom exception raised when tool execution is not approved."""
    pass


class ToolApprovalManager:
    """Manages human approval for tool executions."""
    
    def __init__(self, config_file: str = "tool_approvals.json"):
        self.config_file = config_file
        self.approvals = self._load_approvals()
        self.console = Console()
        
        # Tools that require approval
        self.dangerous_tools = {
            'bash_run', 
            'file_write', 
            'file_edit'
        }
        
        # Tools that are always safe
        self.safe_tools = {
            'file_read',
            'brave_web_search', 
            'think',
            'plan'
        }
    
    def _load_approvals(self) -> Dict[str, Any]:
        """Load previous approval decisions from JSON file."""
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {}
        return {}
    
    def _save_approvals(self):
        """Save approval decisions to JSON file."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.approvals, f, indent=2)
        except Exception as e:
            self.console.print(f"[red]Warning: Could not save approvals: {e}[/red]")
    
    def _create_approval_key(self, tool_name: str, args: Dict[str, Any]) -> str:
        """Create a simple key for this tool call for caching decisions."""
        # Use simple tool-based permissions as recommended by LangChain docs
        return tool_name
    
    def _display_tool_call(self, tool_call: Dict[str, Any]) -> str:
        """Display tool call information in a formatted way."""
        tool_name = tool_call.get('name', 'unknown')
        args = tool_call.get('args', {})
        
        # Format based on tool type
        if tool_name == 'bash_run':
            command = args.get('command', 'unknown command')
            # Create syntax highlighting for bash command
            try:
                from rich.syntax import Syntax
                syntax = Syntax(command, "bash", theme="monokai", line_numbers=False)
                # Since we can't return a Rich object, format it as a string
                return f"[bold red]Execute Bash Command:[/bold red]\n[cyan]{command}[/cyan]"
            except ImportError:
                return f"[bold red]Execute Bash Command:[/bold red]\n{command}"
        
        elif tool_name == 'file_write':
            filename = args.get('filename', 'unknown')
            content_preview = args.get('content', '')[:200]
            if len(args.get('content', '')) > 200:
                content_preview += "..."
            return f"[bold yellow]Write File:[/bold yellow] {filename}\n[dim]Content preview: {content_preview}[/dim]"
        
        elif tool_name == 'file_edit':
            file_path = args.get('file_path', 'unknown')
            operation = args.get('operation', 'unknown')
            return f"[bold yellow]Edit File:[/bold yellow] {file_path}\n[dim]Operation: {operation}[/dim]"
        
        else:
            # Generic display
            formatted_args = json.dumps(args, indent=2)
            return f"[bold blue]Tool:[/bold blue] {tool_name}\n[dim]Arguments:\n{formatted_args}[/dim]"
    
    def human_approval(self, msg: AIMessage) -> AIMessage:
        """
        Check if tool calls in the message require approval.
        This function implements the human-in-the-loop pattern from LangChain.
        
        Args:
            msg: AIMessage containing tool calls
            
        Returns:
            msg: Original message if approved
            
        Raises:
            NotApproved: If any tool call is not approved
        """
        if not msg.tool_calls:
            return msg
        
        # Filter tool calls that need approval
        dangerous_calls = [
            call for call in msg.tool_calls 
            if call.get('name') in self.dangerous_tools
        ]
        
        if not dangerous_calls:
            # All tools are safe, no approval needed
            return msg
        
        # Check for cached approvals
        all_approved = True
        pending_calls = []
        
        for tool_call in dangerous_calls:
            tool_name = tool_call.get('name')
            args = tool_call.get('args', {})
            approval_key = self._create_approval_key(tool_name, args)
            
            if approval_key in self.approvals:
                if not self.approvals[approval_key]:
                    # Previously denied
                    raise NotApproved(f"Tool '{tool_name}' was previously denied")
            else:
                # Need to ask for approval
                pending_calls.append((tool_call, approval_key))
                all_approved = False
        
        if all_approved and not pending_calls:
            return msg
        
        # Display approval request
        self.console.print("\n" + "="*60)
        self.console.print(Panel(
            "[bold red]🔒 TOOL APPROVAL REQUIRED[/bold red]",
            style="red",
            expand=False
        ))
        
        for tool_call, approval_key in pending_calls:
            self.console.print("\n" + "-"*40)
            tool_display = self._display_tool_call(tool_call)
            self.console.print(Panel(tool_display, expand=False))
            
            # Ask for approval
            choices = [
                "1. ✅ Yes (approve this once)",
                "2. 🔄 Always (approve this type of operation permanently)", 
                "3. ❌ No (deny this operation)",
                "4. 🛑 Cancel (stop execution)"
            ]
            
            self.console.print("\n[bold]Choose an option:[/bold]")
            for choice in choices:
                self.console.print(f"  {choice}")
            
            while True:
                choice = Prompt.ask("\nYour choice", choices=["1", "2", "3", "4"])
                
                if choice == "1":
                    # Approve once
                    break
                elif choice == "2":
                    # Approve permanently
                    self.approvals[approval_key] = True
                    self._save_approvals()
                    self.console.print("[green]✅ Approved permanently[/green]")
                    break
                elif choice == "3":
                    # Deny
                    tool_name = tool_call.get('name')
                    raise NotApproved(f"Tool '{tool_name}' denied by user")
                elif choice == "4":
                    # Cancel
                    raise NotApproved("Operation cancelled by user")
        
        self.console.print("\n[green]✅ All tools approved. Proceeding with execution...[/green]")
        self.console.print("="*60 + "\n")
        
        return msg
    
    def reset_approvals(self):
        """Reset all saved approvals."""
        self.approvals = {}
        if os.path.exists(self.config_file):
            os.remove(self.config_file)
        self.console.print("[yellow]All approval settings have been reset.[/yellow]")
    
    def list_approvals(self):
        """List all current approval settings."""
        if not self.approvals:
            self.console.print("[dim]No approval settings saved.[/dim]")
            return
        
        self.console.print("\n[bold]Current Approval Settings:[/bold]")
        for key, approved in self.approvals.items():
            status = "✅ Approved" if approved else "❌ Denied"
            self.console.print(f"  {key}: {status}")
