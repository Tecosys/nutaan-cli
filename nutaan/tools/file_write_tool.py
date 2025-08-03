import os
from langchain_core.tools import BaseTool

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.text import Text
    from rich.markdown import Markdown
    from rich.syntax import Syntax
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class FileWriteTool(BaseTool):
    """Enhanced file writing tool with Rich console and markdown display."""
    
    name: str = "file_write"
    description: str = (
        "Write content to a file on the filesystem with beautiful Rich display. "
        "Use this when you need to create new files or overwrite existing files. "
        "Input should be in format: 'filepath|content' where filepath is the full path "
        "and content is what you want to write to the file. "
        "IMPORTANT: This tool requires user permission for security. "
        "Features Rich syntax highlighting and file preview."
    )
    
    def __init__(self):
        super().__init__()
        self._console = Console() if RICH_AVAILABLE else None
    
    def _get_file_extension(self, filepath: str) -> str:
        """Get file extension for syntax highlighting."""
        return os.path.splitext(filepath)[1].lstrip('.')
    
    def _display_file_preview(self, filepath: str, content: str, is_new: bool = True):
        """Display a beautiful preview of the file being written."""
        if not RICH_AVAILABLE or not self._console:
            return
        
        file_ext = self._get_file_extension(filepath)
        
        # Create syntax highlighted content
        try:
            syntax = Syntax(content, file_ext or "text", theme="monokai", line_numbers=True)
        except:
            syntax = Syntax(content, "text", theme="monokai", line_numbers=True)
        
        # Create preview panel
        title = f"📝 {'Creating' if is_new else 'Overwriting'}: {filepath}"
        panel = Panel(
            syntax,
            title=title,
            border_style="green" if is_new else "yellow",
            padding=(1, 2)
        )
        
        self._console.print()
        self._console.print(panel)
        
        # Show summary
        lines = len(content.split('\n'))
        chars = len(content)
        summary = Text()
        summary.append("📊 ", style="bold")
        summary.append(f"Lines: {lines}, Characters: {chars}", style="dim")
        
        if not is_new:
            summary.append(" (File will be overwritten)", style="bold red")
        
        self._console.print(summary)
    
    def _run(self, query: str) -> str:
        try:
            if "|" not in query:
                error_msg = "Error: Input must be in format 'filepath|content'"
                if RICH_AVAILABLE and self._console:
                    self._console.print(f"[red]{error_msg}[/red]")
                return error_msg
            
            filepath, content = query.split("|", 1)
            filepath = filepath.strip()
            
            # Check if file exists for preview purposes
            file_exists = os.path.exists(filepath)
            
            # Display preview
            self._display_file_preview(filepath, content, is_new=not file_exists)
            
            # Ensure directory exists
            directory = os.path.dirname(filepath)
            if directory and not os.path.exists(directory):
                os.makedirs(directory, exist_ok=True)
                if RICH_AVAILABLE and self._console:
                    self._console.print(f"[dim]📁 Created directory: {directory}[/dim]")
            
            # Write file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            
            # Success message with Rich formatting
            success_msg = f"\nSuccessfully wrote content to {filepath}\n\n"
            if RICH_AVAILABLE and self._console:
                self._console.print(f"✅ [green]{success_msg}[/green]")
                
                # Show file info
                file_size = os.path.getsize(filepath)
                info = Text()
                info.append("💾 ", style="bold")
                info.append(f"File saved ({file_size} bytes)", style="dim green")
                self._console.print(info)
            
            return success_msg
            
        except Exception as e:
            error_msg = f"File write error: {str(e)}"
            if RICH_AVAILABLE and self._console:
                self._console.print(f"[red]❌ {error_msg}[/red]")
            return error_msg
    
    async def _arun(self, query: str) -> str:
        return self._run(query)
