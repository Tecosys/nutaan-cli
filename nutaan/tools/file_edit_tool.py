import os
import difflib
import tempfile
from langchain_core.tools import BaseTool
from .file_timestamp_manager import FileTimestampManager

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.syntax import Syntax
    from rich.text import Text
    from rich.markdown import Markdown
    from rich.prompt import Confirm
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False


class FileEditTool(BaseTool):
    """Enhanced file editing tool with beautiful Rich diff display using rich-diff approach."""
    
    name: str = "file_edit"
    description: str = (
        "Edit files with enhanced Rich diff display. Input format: 'filepath|old_text|new_text'. "
        "Shows beautiful unified diff, syntax highlighting, and confirmation prompts. "
        "Files must be read first using file_read tool before editing. "
        "Supports multi-line content with proper formatting and validation. "
        "IMPORTANT: This tool requires user permission for security."
    )

    def __init__(self):
        super().__init__()
        if RICH_AVAILABLE:
            self._console = Console()
        self._timestamp_manager = FileTimestampManager()

    def _show_rich_diff(self, filepath: str, old_content: str, new_content: str) -> None:
        """Display beautiful unified diff using rich-diff approach."""
        if not RICH_AVAILABLE:
            print(f"--- {filepath} (original)")
            print(f"+++ {filepath} (modified)")
            for line in difflib.unified_diff(
                old_content.splitlines(keepends=True),
                new_content.splitlines(keepends=True),
                fromfile=f"a/{filepath}",
                tofile=f"b/{filepath}",
                lineterm=""
            ):
                print(line.rstrip())
            return

        # Create unified diff
        old_lines = old_content.splitlines(keepends=True)
        new_lines = new_content.splitlines(keepends=True)
        
        diff_lines = list(difflib.unified_diff(
            old_lines,
            new_lines,
            fromfile=f"a/{filepath}",
            tofile=f"b/{filepath}",
            lineterm=""
        ))
        
        if not diff_lines:
            self._console.print("🔄 No changes detected", style="yellow")
            return
            
        # Join diff lines and display with Rich markdown
        diff_text = "\n".join(diff_lines)
        
        # Display in a beautiful panel with syntax highlighting
        self._console.print()
        self._console.print(Panel.fit(
            f"📝 File Edit Preview: [bold blue]{filepath}[/bold blue]",
            style="cyan"
        ))
        
        # Create markdown with diff syntax highlighting
        markdown_content = f"""
```diff
{diff_text}
```
"""
        
        # Display the diff with Rich markdown
        self._console.print(Markdown(markdown_content, code_theme="monokai"))
        
        # Show summary
        added_lines = sum(1 for line in diff_lines if line.startswith('+') and not line.startswith('+++'))
        removed_lines = sum(1 for line in diff_lines if line.startswith('-') and not line.startswith('---'))
        
        summary_text = Text()
        summary_text.append("📊 Summary: ", style="bold")
        summary_text.append(f"+{added_lines}", style="green")
        summary_text.append(" additions, ", style="white")
        summary_text.append(f"-{removed_lines}", style="red")
        summary_text.append(" deletions", style="white")
        
        self._console.print(Panel(summary_text, style="blue"))

    def _validate_file_ready(self, filepath: str) -> str:
        """Validate that file exists and is ready for editing."""
        if not os.path.exists(filepath):
            return f"Error: File '{filepath}' does not exist."
        
        if not os.path.isfile(filepath):
            return f"Error: '{filepath}' is not a file."
        
        # Check if file has been read
        if not self._timestamp_manager.is_file_ready_for_edit(filepath):
            return (
                f"Error: File '{filepath}' must be read first using the file_read tool "
                f"before it can be edited. This ensures you have the latest content."
            )
        
        return ""

    def _detect_encoding(self, filepath: str) -> str:
        """Detect file encoding."""
        try:
            with open(filepath, 'rb') as f:
                raw_data = f.read()
            
            # Try common encodings
            for encoding in ['utf-8', 'utf-8-sig', 'ascii', 'latin-1']:
                try:
                    raw_data.decode(encoding)
                    return encoding
                except UnicodeDecodeError:
                    continue
            
            return 'utf-8'  # fallback
        except Exception:
            return 'utf-8'

    def _apply_edit(self, filepath: str, old_text: str, new_text: str) -> str:
        """Apply the edit to the file without backup."""
        try:
            encoding = self._detect_encoding(filepath)
            
            # Read current content
            with open(filepath, 'r', encoding=encoding) as f:
                current_content = f.read()
            
            # Apply replacement
            if old_text not in current_content:
                # Try to find close matches
                lines = current_content.split('\n')
                old_lines = old_text.split('\n')
                
                for i, line in enumerate(lines):
                    if len(old_lines) > 0 and old_lines[0].strip() in line:
                        # Found potential match, check context
                        context_start = max(0, i - 2)
                        context_end = min(len(lines), i + len(old_lines) + 2)
                        context = '\n'.join(lines[context_start:context_end])
                        
                        if old_text.strip() in context:
                            return f"Found similar text but exact match failed. Please check the exact formatting."
                
                return f"Error: Could not find exact text to replace in {filepath}."
            
            # Perform replacement
            new_content = current_content.replace(old_text, new_text, 1)
            
            # Write new content
            with open(filepath, 'w', encoding=encoding) as f:
                f.write(new_content)
            
            # Update timestamp
            self._timestamp_manager.mark_file_as_read(filepath)
            
            if RICH_AVAILABLE:
                self._console.print(f"✅ [green]Successfully edited[/green] [bold]{filepath}[/bold]")
                
                # Show file info
                file_size = os.path.getsize(filepath)
                info = Text()
                info.append("💾 ", style="bold")
                info.append(f"File saved ({file_size} bytes)", style="dim green")
                self._console.print(info)
            else:
                print(f"✅ Successfully edited {filepath}")

            return f"\n\nSuccessfully edited {filepath}.\n\n"

        except Exception as e:
            return f"Error applying edit: {str(e)}"

    def _run(self, tool_input: str) -> str:
        try:
            # Parse input
            parts = tool_input.split('|', 2)
            if len(parts) != 3:
                return (
                    "Error: Input must be in format 'filepath|old_text|new_text'. "
                    "Use | as separator between filepath, old text, and new text."
                )
            
            filepath = parts[0].strip()
            old_text = parts[1].strip()
            new_text = parts[2].strip()
            
            # Validate file
            validation_error = self._validate_file_ready(filepath)
            if validation_error:
                return validation_error
            
            # Read current content
            encoding = self._detect_encoding(filepath)
            with open(filepath, 'r', encoding=encoding) as f:
                current_content = f.read()
            
            # Create preview content
            if old_text not in current_content:
                return f"Error: Could not find the specified text to replace in {filepath}."
            
            preview_content = current_content.replace(old_text, new_text, 1)
            
            # Show rich diff
            self._show_rich_diff(filepath, current_content, preview_content)
            
            # Apply the edit
            return self._apply_edit(filepath, old_text, new_text)
            
        except Exception as e:
            error_msg = f"File edit error: {str(e)}"
            if RICH_AVAILABLE:
                self._console.print(f"❌ [red]{error_msg}[/red]")
            return error_msg

    async def _arun(self, tool_input: str) -> str:
        return self._run(tool_input)
