import subprocess
import os
from langchain_core.tools import BaseTool


class BashRunTool(BaseTool):
    """Tool for executing bash commands with user permission."""
    
    name: str = "bash_run"
    description: str = (
        "Execute bash/shell commands on the system. "
        "Use this when you need to run terminal commands, install packages, "
        "navigate directories, or perform system operations. "
        "Input should be the bash command you want to execute. "
        "IMPORTANT: This tool requires user permission for security as it can modify the system."
    )
    
    def _run(self, command: str) -> str:
        try:
            command = command.strip()
            
            # Execute command
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30  # 30 second timeout
            )
            
            output = ""
            if result.stdout:
                output += f"STDOUT:\n{result.stdout}\n"
            if result.stderr:
                output += f"STDERR:\n{result.stderr}\n"
            
            output += f"Return code: {result.returncode}"
            
            # Limit output size
            if len(output) > 5000:
                output = output[:5000] + "\n\n... (Output truncated)"
            
            return output if output.strip() else "Command executed successfully (no output)"
            
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 30 seconds"
        except Exception as e:
            return f"Bash execution error: {str(e)}"
    
    async def _arun(self, command: str) -> str:
        return self._run(command)
