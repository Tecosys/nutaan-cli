#!/usr/bin/env python3
"""
Command Line Interface for Nutaan-CLI - ReAct Python Assistant with Multi-Model Support
Made by Tecosys
"""

import sys
import os
import argparse
import json
from datetime import datetime
from typing import Dict, Any, List
from nutaan import __version__

# Global flag to track if we need to load env later
_env_file_path = None

def load_environment_file(env_path: str = None):
    """Load environment variables from specified file or default .env"""
    try:
        from dotenv import load_dotenv
        
        if env_path:
            if os.path.exists(env_path):
                load_dotenv(env_path)
                print(f"✅ Loaded environment from: {env_path}")
                # Refresh agent manager to pick up new environment
                _refresh_agent_manager()
            else:
                print(f"❌ Environment file not found: {env_path}")
                sys.exit(1)
        else:
            # Try to load default .env file
            if os.path.exists('.env'):
                load_dotenv()
                print("📄 Loaded default .env file")
                _refresh_agent_manager()
            elif os.path.exists('.env.example'):
                print("💡 Found .env.example - copy it to .env and configure your API keys")
    except ImportError:
        # dotenv not available, continue without it
        print("⚠️ python-dotenv not installed, environment variables not loaded")

def _refresh_agent_manager():
    """Refresh the global agent manager to pick up new environment variables."""
    try:
        from .core.agent_manager import agent_manager
        agent_manager.refresh_models()
    except ImportError:
        # If agent_manager import fails, it's ok (might be in CLI initialization)
        pass

# Import Rich components
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.table import Table
    from rich.prompt import Prompt
    RICH_AVAILABLE = True
    console = Console()
except ImportError:
    RICH_AVAILABLE = False
    console = None

# Import core modules
from .core.agent_manager import agent_manager
from .core.session_history import session_history
from .core.config_manager import ConfigManager


class UIManager:
    """Handles user interface with Rich formatting."""
    
    def __init__(self):
        self.console = console if RICH_AVAILABLE else None
    
    def display_welcome_banner(self):
        """Display welcome banner."""
        if RICH_AVAILABLE:
            banner = Panel(
                "\n[bold cyan]Nutaan-CLI - ReAct Python Assistant[/bold cyan]\n\n"
                "[green]🧠 Think Mode • 🌐 Web Search • 📁 File Operations • 💻 Bash Commands • 📚 Session History[/green]\n",
                border_style="blue"
            )
            console.print(banner)
        else:
            print("=" * 60)
            print("Nutaan-CLI - ReAct Python Assistant")
            print("🧠 Think Mode • 🌐 Web Search • 📁 File Operations • 💻 Bash Commands")
            print("=" * 60)
    
    def display_main_menu(self):
        """Display main menu and get user choice."""
        if RICH_AVAILABLE:
            menu = Panel(
                "[bold yellow]1.[/bold yellow] Interactive Conversation\n"
                "[bold yellow]2.[/bold yellow] Interactive Conversation (Think Mode)\n"
                "[bold yellow]3.[/bold yellow] Session History\n"
                "[bold yellow]4.[/bold yellow] Statistics\n"
                "[bold yellow]5.[/bold yellow] Model Management\n"
                "[bold yellow]6.[/bold yellow] Tools Information",
                title="🚀 Main Menu",
                border_style="green"
            )
            console.print(menu)
            return console.input("\n[bold cyan]Enter your choice [1/2/3/4/5/6]:[/bold cyan] ").strip()
        else:
            print("\n🚀 Main Menu")
            print("1. Interactive Conversation")
            print("2. Interactive Conversation (Think Mode)")
            print("3. Session History")
            print("4. Statistics")
            print("5. Model Management")
            print("6. Tools Information")
            return input("\nEnter your choice [1/2/3/4/5/6]: ").strip()
    
    def display_session_history(self, sessions: List[Dict]):
        """Display session history."""
        if not sessions:
            if RICH_AVAILABLE:
                console.print("[yellow]No sessions found.[/yellow]")
            else:
                print("No sessions found.")
            return
        
        if RICH_AVAILABLE:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Session ID", style="dim")
            table.add_column("Name", style="cyan")
            table.add_column("Messages", justify="right")
            table.add_column("Created", style="green")
            table.add_column("Last Activity", style="yellow")
            
            for session in sessions:
                table.add_row(
                    session['session_id'][-8:],
                    session.get('display_name', 'Untitled'),
                    str(session.get('message_count', 0)),
                    session.get('created_at', 'Unknown')[:10],
                    session.get('last_activity', 'Unknown')[:10]
                )
            
            console.print(table)
        else:
            print("\n📚 Session History:")
            for i, session in enumerate(sessions, 1):
                print(f"{i}. {session.get('display_name', 'Untitled')} "
                      f"({session['session_id'][-8:]}) - "
                      f"{session.get('message_count', 0)} messages")
    
    def display_statistics(self, stats: Dict):
        """Display usage statistics."""
        if RICH_AVAILABLE:
            stats_panel = Panel(
                f"[bold green]Total Sessions:[/bold green] {stats.get('total_sessions', 0)}\n"
                f"[bold blue]Total Messages:[/bold blue] {stats.get('total_messages', 0)}\n"
                f"[bold yellow]Think Mode Sessions:[/bold yellow] {stats.get('think_mode_sessions', 0)}\n"
                f"[bold cyan]Avg Messages/Session:[/bold cyan] {stats.get('avg_messages_per_session', 0):.1f}",
                title="📊 Usage Statistics",
                border_style="magenta"
            )
            console.print(stats_panel)
        else:
            print("\n📊 Usage Statistics:")
            print(f"Total Sessions: {stats.get('total_sessions', 0)}")
            print(f"Total Messages: {stats.get('total_messages', 0)}")
            print(f"Think Mode Sessions: {stats.get('think_mode_sessions', 0)}")
            print(f"Avg Messages/Session: {stats.get('avg_messages_per_session', 0):.1f}")
    
    def display_error(self, message: str):
        """Display error message."""
        if RICH_AVAILABLE:
            console.print(f"[bold red]❌ Error:[/bold red] {message}")
        else:
            print(f"❌ Error: {message}")
    
    def display_goodbye(self):
        """Display goodbye message."""
        if RICH_AVAILABLE:
            console.print("[bold cyan]👋 Goodbye![/bold cyan]")
        else:
            print("👋 Goodbye!")


class ConversationHandler:
    """Handles conversation flow and agent interactions."""
    
    def __init__(self, ui_manager: UIManager):
        self.ui = ui_manager
        self.current_agent = None
        self.current_agent_data = None
        self.current_session_id = None
    
    def process_single_prompt(self, prompt: str, think_mode: bool = False):
        """Process a single prompt and return the response."""
        try:
            # Create session
            session_id = session_history.create_session(think_mode)
            
            # Get agent
            agent_data = agent_manager.get_agent(session_id, think_mode)
            
            if not agent_data or not agent_data.get('agent'):
                print("❌ Error: Failed to create agent")
                return
                
            self.current_agent = agent_data['agent']
            self.current_agent_data = agent_data
            self.current_session_id = session_id
            
            # Create config
            config = {"configurable": {"thread_id": session_id}}
            
            # Show mode indicator
            if RICH_AVAILABLE:
                mode_indicator = "[dim] (think mode)[/dim]" if think_mode else ""
                console.print(f"[bold cyan]🤖 Nutaan{mode_indicator}[/bold cyan]")
            else:
                mode_indicator = " (think mode)" if think_mode else ""
                print(f"🤖 Nutaan{mode_indicator}")
            
            # Save user message
            user_message = {"role": "user", "content": prompt, "timestamp": datetime.now().isoformat()}
            session_history.add_message(session_id, user_message)
            
            # Prepare message for agent
            input_message = {"role": "user", "content": prompt}
            
            # Process with agent
            self._process_response(input_message, config)
            
        except Exception as e:
            print(f"❌ Error in process_single_prompt: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def start_conversation(self, think_mode: bool = False):
        """Start interactive conversation."""
        # Create new session
        self.current_session_id = session_history.create_session(think_mode)
        
        # Get agent
        agent_data = agent_manager.get_agent(self.current_session_id, think_mode)
        self.current_agent = agent_data['agent']
        self.current_agent_data = agent_data
        
        # Create config for conversation
        config = {"configurable": {"thread_id": self.current_session_id}}
        
        # Display header
        mode_text = " (Think Mode)" if think_mode else ""
        if RICH_AVAILABLE:
            header = Panel(
                f"[bold green]Nutaan Assistant{mode_text}[/bold green]\n"
                f"[dim]Session: {self.current_session_id[-8:]}[/dim]\n"
                f"[yellow]Type 'quit' to exit, 'history' to view sessions[/yellow]",
                title="🤖 Assistant Ready",
                border_style="cyan"
            )
            console.print(header)
        else:
            print(f"🤖 Nutaan Assistant{mode_text}")
            print(f"Session: {self.current_session_id[-8:]}")
            print("Type 'quit' to exit, 'history' to view sessions")
        
        while True:
            try:
                # Get user input
                if RICH_AVAILABLE:
                    user_input = console.input("[bold green]👤 You:[/bold green] ").strip()
                else:
                    user_input = input("👤 You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    if RICH_AVAILABLE:
                        console.print("[bold cyan]👋 Goodbye![/bold cyan]")
                    else:
                        print("👋 Goodbye!")
                    break
                
                if user_input.lower() == 'history':
                    sessions = session_history.list_sessions(limit=10)
                    self.ui.display_session_history(sessions)
                    continue
                
                if not user_input:
                    continue
                
                # Save user message
                user_message = {"role": "user", "content": user_input, "timestamp": datetime.now().isoformat()}
                session_history.add_message(self.current_session_id, user_message)
                
                # Prepare message for agent
                input_message = {"role": "user", "content": user_input}
                
                print("\n🤖 Agent: ", end="")
                
                # Process with agent
                self._process_response(input_message, config)
                
                print("\n" + "-" * 50 + "\n")
                
            except KeyboardInterrupt:
                if RICH_AVAILABLE:
                    console.print("\n[bold cyan]👋 Goodbye![/bold cyan]")
                else:
                    print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    def _process_response(self, input_message: Dict[str, Any], config: Dict[str, Any]):
        """Process agent response with Claude CLI-style tool display and human approval."""
        from .core.tool_approval_manager import NotApproved
        
        try:
            agent_response_content = []
            tool_calls_made = []
            
            for step in self.current_agent.stream(
                {"messages": [input_message]}, 
                config, 
                stream_mode="values"
            ):
                last_message = step["messages"][-1]
                
                # Handle AI messages with tool calls - check for approval BEFORE displaying
                if hasattr(last_message, 'type') and last_message.type == 'ai':
                    if hasattr(last_message, 'tool_calls') and last_message.tool_calls:
                        
                        # Check for dangerous tools that need approval
                        approval_manager = self.current_agent_data.get('approval_manager')
                        if approval_manager:
                            dangerous_calls = [
                                call for call in last_message.tool_calls 
                                if call.get('name') in approval_manager.dangerous_tools
                            ]
                            
                            if dangerous_calls:
                                try:
                                    # Check for approval - this will raise NotApproved if denied
                                    approval_manager.human_approval(last_message)
                                except NotApproved as e:
                                    if RICH_AVAILABLE:
                                        console.print(f"\n[bold red]🚫 Operation cancelled:[/bold red] {str(e)}")
                                    else:
                                        print(f"\n🚫 Operation cancelled: {str(e)}")
                                    return  # Exit without executing tools
                        
                        # If we get here, tools are approved, so display and continue
                        for tool_call in last_message.tool_calls:
                            tool_name = tool_call.get('name', 'unknown')
                            tool_args = tool_call.get('args', {})
                            tool_id = tool_call.get('id', 'unknown')
                            
                            # Format args with truncation for large content
                            args_str = json.dumps(tool_args, default=str)
                            if len(args_str) > 200:
                                # For large args, show first part with truncation
                                preview_args = args_str[:150] + "...})"
                                # Special handling for common long content
                                if 'tool_input' in tool_args and isinstance(tool_args['tool_input'], str):
                                    content = tool_args['tool_input']
                                    if '|' in content:
                                        # File operation with content
                                        parts = content.split('|', 1)
                                        filename = parts[0]
                                        file_content = parts[1] if len(parts) > 1 else ""
                                        if len(file_content) > 100:
                                            preview_content = file_content[:80] + "......"
                                            preview_args = json.dumps({"tool_input": f"{filename}|{preview_content}"}, default=str) + "}"
                                    elif len(content) > 100:
                                        # Long single content
                                        preview_content = content[:80] + "......"
                                        preview_args = json.dumps({"tool_input": preview_content}, default=str) + "}"
                            else:
                                preview_args = args_str
                            
                            # Display tool call in Claude CLI style (hide for plan_tool)
                            if tool_name != 'plan_tool':
                                if RICH_AVAILABLE:
                                    console.print(f"\n[bold yellow]Tool call:[/bold yellow] [cyan]{tool_name}[/cyan]([dim]{preview_args}[/dim])")
                                else:
                                    print(f"\nTool call: {tool_name}({preview_args})")
                            
                            tool_calls_made.append({
                                'name': tool_name,
                                'args': tool_args,
                                'id': tool_id
                            })
                    
                    # Collect AI response content
                    if hasattr(last_message, 'content') and last_message.content:
                        if last_message.content.strip() != input_message['content'].strip():
                            agent_response_content.append(last_message.content)
                
                # Handle tool results with enhanced display
                elif hasattr(last_message, 'type') and last_message.type == 'tool':
                    if hasattr(last_message, 'content') and last_message.content:
                        content = last_message.content
                        tool_name = getattr(last_message, 'name', 'unknown')
                        
                        # Format tool result like Claude CLI
                        if tool_name == 'plan_tool':
                            # Special handling for plan tool - show full output with Rich formatting
                            if RICH_AVAILABLE:
                                console.print(content)
                            else:
                                print(content)
                        else:
                            if RICH_AVAILABLE:
                                # Show first few lines of output with proper formatting
                                preview_lines = content.split('\n')[:5]
                                preview = '\n'.join(preview_lines)
                                total_lines = len(content.split('\n'))
                                if total_lines > 5:
                                    remaining_lines = total_lines - 5
                                    preview += f"\n[dim]... ({remaining_lines} more lines)[/dim]"
                                
                                console.print(f"[bold green]  {preview}[/bold green]")
                            else:
                                # Simple format for non-rich terminals
                                if len(content) > 300:
                                    preview = content[:300] + "..."
                                else:
                                    preview = content
                                print(f"  {preview}")
            
            # Display final agent response
            if agent_response_content:
                final_response = agent_response_content[-1]
                print(f"\n{final_response}")
                
                # Check if response seems incomplete and encourage follow-up
                if tool_calls_made and not any(word in final_response.lower() for word in ['details', 'more', 'specific', 'would you like', 'anything else']):
                    print("\nWould you like more details about this result or help with anything else?")
                
                # Save response to session
                agent_message = {
                    "role": "assistant", 
                    "content": final_response,
                    "tool_calls": tool_calls_made if tool_calls_made else None,
                    "timestamp": datetime.now().isoformat()
                }
                session_history.add_message(self.current_session_id, agent_message)
                        
        except Exception as e:
            print(f"❌ Error: {str(e)}")
    
    def run_tests(self, think_mode: bool = False):
        """Run test queries."""
        test_session_id = session_history.create_session(think_mode)
        agent_data = agent_manager.get_agent(test_session_id, think_mode)
        agent = agent_data['agent']
        
        config = {"configurable": {"thread_id": test_session_id}}
        
        test_queries = [
            "Hi! I'm testing the system.",
            "What files are in the current directory?", 
            "Create a simple test file",
            "Search for Python programming news"
        ]
        
        if RICH_AVAILABLE:
            console.print(Panel("Testing Nutaan Agent with Sample Queries", style="yellow"))
        else:
            print("🧪 Testing Nutaan Agent")
        
        for i, query in enumerate(test_queries, 1):
            print(f"\n{i}. Testing: '{query}'")
            print("-" * 30)
            
            input_message = {"role": "user", "content": query}
            
            try:
                for step in agent.stream({"messages": [input_message]}, config, stream_mode="values"):
                    last_message = step["messages"][-1]
                    
                    if hasattr(last_message, 'type') and last_message.type == 'ai':
                        if hasattr(last_message, 'content') and last_message.content:
                            if last_message.content.strip() != query.strip():
                                print(f"Response: {last_message.content}")
                                break
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")


def show_session_history(ui_manager):
    """Show session history management interface."""
    while True:
        if RICH_AVAILABLE:
            console.print("\n[bold cyan]📚 Session History Management[/bold cyan]")
            console.print("1. View Recent Sessions")
            console.print("2. Search Sessions")
            console.print("3. Delete Session")
            console.print("4. Cleanup Old Sessions")
            console.print("5. Back to Main Menu")
            
            choice = console.input("\n[bold yellow]Choose option (1-5):[/bold yellow] ").strip()
        else:
            print("\n📚 Session History Management")
            print("1. View Recent Sessions")
            print("2. Search Sessions")
            print("3. Delete Session")
            print("4. Cleanup Old Sessions")
            print("5. Back to Main Menu")
            
            choice = input("\nChoose option (1-5): ").strip()
        
        if choice == "1":
            sessions = session_history.list_sessions(limit=20)
            ui_manager.display_session_history(sessions)
            
        elif choice == "2":
            if RICH_AVAILABLE:
                query = console.input("[yellow]Enter search query:[/yellow] ").strip()
            else:
                query = input("Enter search query: ").strip()
                
            if query:
                results = session_history.search_sessions(query)
                if results:
                    if RICH_AVAILABLE:
                        console.print(f"\n[green]Found {len(results)} matching sessions:[/green]")
                        for result in results:
                            console.print(f"• {result['display_name']} (ID: {result['session_id'][-8:]})")
                            if 'match_preview' in result:
                                console.print(f"  Preview: [dim]{result['match_preview']}[/dim]")
                    else:
                        print(f"\nFound {len(results)} matching sessions:")
                        for result in results:
                            print(f"• {result['display_name']} (ID: {result['session_id'][-8:]})")
                            if 'match_preview' in result:
                                print(f"  Preview: {result['match_preview']}")
                else:
                    if RICH_AVAILABLE:
                        console.print("[yellow]No sessions found matching that query.[/yellow]")
                    else:
                        print("No sessions found matching that query.")
                    
        elif choice == "3":
            sessions = session_history.list_sessions(limit=10)
            if sessions:
                ui_manager.display_session_history(sessions)
                if RICH_AVAILABLE:
                    session_id = console.input("\n[yellow]Enter session ID to delete (last 8 chars):[/yellow] ").strip()
                else:
                    session_id = input("\nEnter session ID to delete (last 8 chars): ").strip()
                
                # Find full session ID
                full_session_id = None
                for session in sessions:
                    if session['session_id'].endswith(session_id):
                        full_session_id = session['session_id']
                        break
                
                if full_session_id:
                    if RICH_AVAILABLE:
                        confirm = console.input(f"[red]Are you sure you want to delete this session? (yes/no):[/red] ").strip().lower()
                    else:
                        confirm = input(f"Are you sure you want to delete this session? (yes/no): ").strip().lower()
                        
                    if confirm == 'yes':
                        if session_history.delete_session(full_session_id):
                            if RICH_AVAILABLE:
                                console.print("[green]✅ Session deleted successfully.[/green]")
                            else:
                                print("✅ Session deleted successfully.")
                        else:
                            if RICH_AVAILABLE:
                                console.print("[red]❌ Failed to delete session.[/red]")
                            else:
                                print("❌ Failed to delete session.")
                    else:
                        if RICH_AVAILABLE:
                            console.print("[yellow]Deletion cancelled.[/yellow]")
                        else:
                            print("Deletion cancelled.")
                else:
                    if RICH_AVAILABLE:
                        console.print("[red]Session not found.[/red]")
                    else:
                        print("Session not found.")
            else:
                if RICH_AVAILABLE:
                    console.print("[yellow]No sessions available.[/yellow]")
                else:
                    print("No sessions available.")
                
        elif choice == "4":
            if RICH_AVAILABLE:
                keep_count = console.input("[yellow]How many recent sessions to keep? (default: 50):[/yellow] ").strip()
            else:
                keep_count = input("How many recent sessions to keep? (default: 50): ").strip()
                
            try:
                keep_count = int(keep_count) if keep_count else 50
                deleted = session_history.cleanup_old_sessions(keep_count)
                if RICH_AVAILABLE:
                    console.print(f"[green]✅ Cleaned up {deleted} old sessions.[/green]")
                else:
                    print(f"✅ Cleaned up {deleted} old sessions.")
            except ValueError:
                if RICH_AVAILABLE:
                    console.print("[red]Invalid number.[/red]")
                else:
                    print("Invalid number.")
                
        elif choice == "5":
            break
        else:
            if RICH_AVAILABLE:
                console.print("[red]Invalid choice.[/red]")
            else:
                print("Invalid choice.")


def show_statistics(ui_manager):
    """Show CLI statistics."""
    stats = session_history.get_statistics()
    
    if RICH_AVAILABLE:
        stats_panel = Panel(
            f"[bold green]📊 Statistics[/bold green]\n\n"
            f"Total Sessions: [yellow]{stats.get('total_sessions', 0)}[/yellow]\n"
            f"Total Messages: [yellow]{stats.get('total_messages', 0)}[/yellow]\n"
            f"Total User Messages: [yellow]{stats.get('user_messages', 0)}[/yellow]\n"
            f"Total Assistant Messages: [yellow]{stats.get('assistant_messages', 0)}[/yellow]\n"
            f"Average Messages per Session: [yellow]{stats.get('avg_messages_per_session', 0):.1f}[/yellow]",
            title="📈 Usage Statistics",
            border_style="cyan"
        )
        console.print(stats_panel)
        console.input("\n[dim]Press Enter to continue...[/dim]")
    else:
        print("\n📊 Statistics")
        print(f"Total Sessions: {stats.get('total_sessions', 0)}")
        print(f"Total Messages: {stats.get('total_messages', 0)}")
        print(f"Total User Messages: {stats.get('user_messages', 0)}")
        print(f"Total Assistant Messages: {stats.get('assistant_messages', 0)}")
        print(f"Average Messages per Session: {stats.get('avg_messages_per_session', 0):.1f}")
        input("\nPress Enter to continue...")


def show_model_management(ui_manager):
    """Show model management interface."""
    from .core.agent_manager import agent_manager
    
    while True:
        # Get current model info
        current_model = agent_manager.get_current_model_info()
        available_models = agent_manager.list_available_models()
        
        if RICH_AVAILABLE:
            # Display current model
            current_info = f"[green]✅ {current_model['provider']}/{current_model['model']}[/green]" if current_model else "[red]❌ No model selected[/red]"
            
            menu = Panel(
                f"[bold blue]Current Model:[/bold blue] {current_info}\n\n"
                "[bold yellow]1.[/bold yellow] List Available Models\n"
                "[bold yellow]2.[/bold yellow] Set Preferred Model\n"
                "[bold yellow]3.[/bold yellow] Reset to Auto-Selection\n"
                "[bold yellow]4.[/bold yellow] Show Model Status\n"
                "[bold yellow]5.[/bold yellow] Back to Main Menu",
                title="🤖 Model Management",
                border_style="blue"
            )
            console.print(menu)
            choice = console.input("\n[bold cyan]Enter your choice [1/2/3/4/5]:[/bold cyan] ").strip()
        else:
            current_info = f"✅ {current_model['provider']}/{current_model['model']}" if current_model else "❌ No model selected"
            print(f"\n🤖 Model Management")
            print(f"Current Model: {current_info}")
            print("1. List Available Models")
            print("2. Set Preferred Model")
            print("3. Reset to Auto-Selection")
            print("4. Show Model Status")
            print("5. Back to Main Menu")
            choice = input("\nEnter your choice [1/2/3/4/5]: ").strip()
        
        if choice == "1":
            _display_available_models(available_models)
        elif choice == "2":
            _set_preferred_model(available_models)
        elif choice == "3":
            agent_manager.reset_model_selection()
            if RICH_AVAILABLE:
                console.print("[green]✅ Reset to auto-selection[/green]")
            else:
                print("✅ Reset to auto-selection")
        elif choice == "4":
            _show_model_status(available_models)
        elif choice == "5":
            break
        else:
            if RICH_AVAILABLE:
                console.print("[yellow]Invalid choice. Please try again.[/yellow]")
            else:
                print("Invalid choice. Please try again.")


def _display_available_models(models):
    """Display list of available models."""
    if RICH_AVAILABLE:
        from rich.table import Table
        
        table = Table(title="🤖 Available Language Models")
        table.add_column("Provider", style="cyan")
        table.add_column("Model", style="yellow")
        table.add_column("Status", style="green")
        table.add_column("API Key", style="dim")
        
        for model in models:
            status = "✅ Available" if model['available'] else "❌ Unavailable"
            api_key = model['api_key_env'] if model['api_key_env'] else "None"
            table.add_row(
                model['provider'],
                model['model'],
                status,
                api_key
            )
        
        console.print(table)
        console.input("\n[dim]Press Enter to continue...[/dim]")
    else:
        print("\n🤖 Available Language Models:")
        print("-" * 80)
        for model in models:
            status = "✅ Available" if model['available'] else "❌ Unavailable"
            api_key = model['api_key_env'] if model['api_key_env'] else "None"
            print(f"{model['provider']:<15} {model['model']:<35} {status:<15} {api_key}")
        input("\nPress Enter to continue...")


def _set_preferred_model(models):
    """Set preferred model."""
    available_models = [m for m in models if m['available']]
    
    if not available_models:
        if RICH_AVAILABLE:
            console.print("[red]❌ No available models found![/red]")
        else:
            print("❌ No available models found!")
        return
    
    if RICH_AVAILABLE:
        console.print("[bold blue]Available Models:[/bold blue]")
        for i, model in enumerate(available_models, 1):
            console.print(f"[yellow]{i}.[/yellow] {model['provider']}/{model['model']}")
        
        try:
            choice = int(console.input(f"\n[cyan]Select model [1-{len(available_models)}]:[/cyan] "))
            if 1 <= choice <= len(available_models):
                selected = available_models[choice - 1]
                from .core.agent_manager import agent_manager
                success = agent_manager.set_preferred_model(selected['provider'], selected['model'])
                if success:
                    console.print(f"[green]✅ Set preferred model: {selected['provider']}/{selected['model']}[/green]")
                else:
                    console.print("[red]❌ Failed to set model[/red]")
            else:
                console.print("[yellow]Invalid selection[/yellow]")
        except ValueError:
            console.print("[red]Invalid input[/red]")
    else:
        print("\nAvailable Models:")
        for i, model in enumerate(available_models, 1):
            print(f"{i}. {model['provider']}/{model['model']}")
        
        try:
            choice = int(input(f"\nSelect model [1-{len(available_models)}]: "))
            if 1 <= choice <= len(available_models):
                selected = available_models[choice - 1]
                from .core.agent_manager import agent_manager
                success = agent_manager.set_preferred_model(selected['provider'], selected['model'])
                if success:
                    print(f"✅ Set preferred model: {selected['provider']}/{selected['model']}")
                else:
                    print("❌ Failed to set model")
            else:
                print("Invalid selection")
        except ValueError:
            print("Invalid input")


def _show_model_status(models):
    """Show detailed model status."""
    import os
    
    if RICH_AVAILABLE:
        from rich.table import Table
        
        table = Table(title="🔧 Model Configuration Status")
        table.add_column("Provider", style="cyan")
        table.add_column("Model", style="yellow")
        table.add_column("API Key Set", style="green")
        table.add_column("Base URL", style="blue")
        table.add_column("Status", style="magenta")
        
        for model in models:
            api_key_set = "✅ Yes" if model['api_key_env'] and os.getenv(model['api_key_env']) else "❌ No"
            base_url = os.getenv(model['base_url_env']) if model.get('base_url_env') else "Default"
            status = "Ready" if model['available'] else "Not Available"
            
            table.add_row(
                model['provider'],
                model['model'],
                api_key_set,
                base_url,
                status
            )
        
        console.print(table)
        console.input("\n[dim]Press Enter to continue...[/dim]")
    else:
        print("\n🔧 Model Configuration Status:")
        print("-" * 100)
        for model in models:
            api_key_set = "✅ Yes" if model['api_key_env'] and os.getenv(model['api_key_env']) else "❌ No"
            base_url = os.getenv(model['base_url_env']) if model.get('base_url_env') else "Default"
            status = "Ready" if model['available'] else "Not Available"
            print(f"{model['provider']:<15} {model['model']:<35} {api_key_set:<10} {base_url:<20} {status}")
        input("\nPress Enter to continue...")


def show_tools_info(ui_manager):
    """Show information about available tools."""
    from .core.agent_manager import agent_manager
    
    tools_info = agent_manager.get_tools_info()
    
    if RICH_AVAILABLE:
        from rich.table import Table
        
        table = Table(title="🛠️ Available Tools")
        table.add_column("Tool Name", style="cyan")
        table.add_column("Description", style="yellow")
        
        for tool in tools_info:
            table.add_row(tool['name'], tool['description'])
        
        console.print(table)
        console.input("\n[dim]Press Enter to continue...[/dim]")
    else:
        print("\n🛠️ Available Tools:")
        print("-" * 80)
        for tool in tools_info:
            print(f"{tool['name']:<20} {tool['description']}")
        input("\nPress Enter to continue...")


def show_statistics(ui_manager):
    """Show usage statistics."""
    stats = session_history.get_statistics()
    ui_manager.display_statistics(stats)


def run_interactive_mode(think_mode=False):
    """Run interactive mode."""
    ui_manager = UIManager()
    conversation_handler = ConversationHandler(ui_manager)
    
    ui_manager.display_welcome_banner()
    
    while True:
        try:
            choice = ui_manager.display_main_menu()
            
            if choice == "1":
                conversation_handler.start_conversation(think_mode=False)
                
            elif choice == "2":
                conversation_handler.start_conversation(think_mode=True)
                
            elif choice == "3":
                show_session_history(ui_manager)
                
            elif choice == "4":
                show_statistics(ui_manager)
                
            elif choice == "5":
                show_model_management(ui_manager)
                
            elif choice == "6":
                show_tools_info(ui_manager)
                
            else:
                if RICH_AVAILABLE:
                    console.print("[yellow]Invalid choice. Please try again.[/yellow]")
                else:
                    print("Invalid choice. Please try again.")
                
        except KeyboardInterrupt:
            ui_manager.display_goodbye()
            break
        except Exception as e:
            ui_manager.display_error(f"Unexpected error: {str(e)}")


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Nutaan-CLI - A powerful ReAct Python Assistant with AI capabilities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  nutaan                    Start interactive mode
  nutaan -e .env.prod       Start with production environment
  nutaan --env config/.env  Load custom environment file
  nutaan --think            Start with think mode enabled
  nutaan --test             Run test queries
  nutaan --history          Show session history
  nutaan --stats            Show usage statistics
  nutaan --list-approvals   Show current tool approval settings
  nutaan --reset-approvals  Reset all tool approval settings
  nutaan --list-models      List all available language models
  nutaan --current-model    Show currently selected model
  nutaan --set-model openai gpt-4o    Set preferred model
  nutaan --model-status     Show detailed model configuration
  nutaan --reset-model      Reset to automatic model selection
  nutaan --version          Show version information
        """
    )
    
    parser.add_argument(
        'prompt',
        nargs='*',
        help='Your prompt to process (if provided, runs in non-interactive mode)'
    )
    
    parser.add_argument(
        "-e", "--env", 
        dest="env_file",
        metavar="ENV_FILE",
        help='Load environment variables from specified file (e.g., -e .env.production)'
    )
    
    parser.add_argument(
        "--think", 
        action="store_true", 
        help="Start in think mode for complex reasoning"
    )
    
    parser.add_argument(
        "--test", 
        action="store_true", 
        help="Run test queries to validate the system"
    )
    
    parser.add_argument(
        "--history", 
        action="store_true", 
        help="Show session history management"
    )
    
    parser.add_argument(
        "--stats", 
        action="store_true", 
        help="Show usage statistics"
    )
    
    parser.add_argument(
        "--reset-approvals", 
        action="store_true", 
        help="Reset all tool approval settings"
    )
    
    parser.add_argument(
        "--list-approvals", 
        action="store_true", 
        help="List current tool approval settings"
    )
    
    parser.add_argument(
        "--list-models",
        action="store_true",
        help="List all available language models"
    )
    
    parser.add_argument(
        "--set-model",
        nargs=2,
        metavar=('PROVIDER', 'MODEL'),
        help="Set preferred language model (e.g., --set-model openai gpt-4o)"
    )
    
    parser.add_argument(
        "--model-status",
        action="store_true",
        help="Show detailed model configuration status"
    )
    
    parser.add_argument(
        "--reset-model",
        action="store_true",
        help="Reset to automatic model selection"
    )
    
    parser.add_argument(
        "--current-model",
        action="store_true",
        help="Show currently selected model"
    )
    
    parser.add_argument(
        "--setup",
        action="store_true",
        help="Run the setup wizard to configure your AI assistant"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version="Nutaan-CLI version " + __version__,
    )
    
    args = parser.parse_args()
    
    # Load environment file first if specified
    load_environment_file(args.env_file)
    
    # Initialize configuration manager
    config_manager = ConfigManager()
    
    # Check if this is a command that doesn't need model setup
    setup_not_needed = any([
        args.env_file,  # User provided env file
        args.reset_approvals,
        args.list_approvals,
        args.reset_model,
        args.setup,  # User explicitly wants to run setup
        hasattr(args, 'version') and args.version
    ])
    
    # If no env file provided and no valid config exists, run setup wizard
    if not args.env_file and not config_manager.has_valid_config() and not setup_not_needed:
        console.print("\n[yellow]🔧 No configuration found. Let's set up your AI assistant![/yellow]")
        
        # Run setup wizard
        config = config_manager.setup_wizard()
        
        # Apply configuration to environment
        env_config = config_manager.get_env_config()
        for key, value in env_config.items():
            os.environ[key] = str(value)
        
        # Refresh agent manager with new config
        _refresh_agent_manager()
        
        console.print("\n[green]🚀 Setup complete! Starting Nutaan CLI...[/green]\n")
    
    # If we have saved config but no env file, load the saved config
    elif not args.env_file and config_manager.has_valid_config():
        env_config = config_manager.get_env_config()
        for key, value in env_config.items():
            os.environ[key] = str(value)
        _refresh_agent_manager()
    
    # Join prompt arguments if provided
    prompt_text = ' '.join(args.prompt) if args.prompt else None
    
    ui_manager = UIManager()
    conversation_handler = ConversationHandler(ui_manager)
    
    try:
        # If prompt provided, run in non-interactive mode
        if prompt_text:
            conversation_handler.process_single_prompt(prompt_text, think_mode=args.think)
            
        elif args.think:
            # Start in think mode
            conversation_handler.start_conversation(think_mode=True)
            
        elif args.test:
            # Run tests
            conversation_handler.run_tests(think_mode=False)
            
        elif args.history:
            # Show history
            show_session_history(ui_manager)
            
        elif args.stats:
            # Show statistics
            show_statistics(ui_manager)
            
        elif args.reset_approvals:
            # Reset approval settings
            agent_manager.reset_tool_approvals()
            if RICH_AVAILABLE:
                console.print("[green]✅ Tool approval settings have been reset.[/green]")
            else:
                print("✅ Tool approval settings have been reset.")
            
        elif args.list_approvals:
            # List approval settings
            agent_manager.list_tool_approvals()
            
        elif args.list_models:
            # List available models
            models = agent_manager.list_available_models()
            _display_available_models(models)
            
        elif args.set_model:
            # Set preferred model
            provider, model = args.set_model
            success = agent_manager.set_preferred_model(provider, model)
            if success:
                if RICH_AVAILABLE:
                    console.print(f"[green]✅ Set preferred model: {provider}/{model}[/green]")
                else:
                    print(f"✅ Set preferred model: {provider}/{model}")
            else:
                if RICH_AVAILABLE:
                    console.print(f"[red]❌ Failed to set model: {provider}/{model}[/red]")
                else:
                    print(f"❌ Failed to set model: {provider}/{model}")
                    
        elif args.model_status:
            # Show model status
            models = agent_manager.list_available_models()
            _show_model_status(models)
            
        elif args.reset_model:
            # Reset model selection
            agent_manager.reset_model_selection()
            if RICH_AVAILABLE:
                console.print("[green]✅ Reset to automatic model selection[/green]")
            else:
                print("✅ Reset to automatic model selection")
                
        elif args.current_model:
            # Show current model
            model_info = agent_manager.get_current_model_info()
            if model_info:
                if RICH_AVAILABLE:
                    console.print(f"[green]Current model: {model_info['provider']}/{model_info['model']}[/green]")
                else:
                    print(f"Current model: {model_info['provider']}/{model_info['model']}")
            else:
                if RICH_AVAILABLE:
                    console.print("[yellow]No model currently selected[/yellow]")
                else:
                    print("No model currently selected")
                    
        elif args.setup:
            # Run setup wizard
            config = config_manager.setup_wizard()
            
            # Apply configuration to environment
            env_config = config_manager.get_env_config()
            for key, value in env_config.items():
                os.environ[key] = str(value)
            
            # Refresh agent manager with new config
            _refresh_agent_manager()
            
            if RICH_AVAILABLE:
                console.print("\n[green]🚀 Setup complete! You can now start using Nutaan CLI.[/green]")
            else:
                print("\n🚀 Setup complete! You can now start using Nutaan CLI.")
            
        else:
            # Default interactive mode
            run_interactive_mode()
            
    except KeyboardInterrupt:
        ui_manager.display_goodbye()
    except Exception as e:
        ui_manager.display_error(f"Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
