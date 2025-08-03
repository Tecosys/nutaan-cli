import os
from langchain_core.tools import BaseTool
from .file_timestamp_manager import FileTimestampManager


class FileReadTool(BaseTool):
    """Tool for reading content from files."""
    
    name: str = "file_read"
    description: str = (
        "Read and return the content of a file from the filesystem. "
        "Use this when you need to examine the contents of existing files. "
        "Input should be the full path to the file you want to read. "
        "This tool is safe and doesn't require special permissions. "
        "Files read with this tool are automatically marked as ready for editing."
    )
    
    def __init__(self):
        super().__init__()
        self._timestamp_manager = FileTimestampManager()
    
    def _run(self, filepath: str) -> str:
        try:
            filepath = filepath.strip()
            
            if not os.path.exists(filepath):
                return f"Error: File '{filepath}' does not exist."
            
            if not os.path.isfile(filepath):
                return f"Error: '{filepath}' is not a file."
            
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Mark file as read for editing compatibility
            self._timestamp_manager.mark_file_as_read(filepath)
            
            # Limit output size to prevent overwhelming the context
            if len(content) > 10000:
                content = content[:10000] + f"\n\n... (File truncated, showing first 10000 characters of {len(content)} total)"
            
            return f"\n\nContent of {filepath}:\n\n{content}\n\n"
            
        except UnicodeDecodeError:
            try:
                with open(filepath, 'rb') as f:
                    content = f.read()
                return f"Binary file detected: {filepath} (Size: {len(content)} bytes)"
            except Exception as e:
                return f"Error reading binary file: {str(e)}"
        except Exception as e:
            return f"File read error: {str(e)}"
    
    async def _arun(self, filepath: str) -> str:
        return self._run(filepath)
