from langchain_core.tools import BaseTool
from typing import List
import json
import os
from datetime import datetime


class ThinkTool(BaseTool):
    """Think tool for complex reasoning and cache memory."""
    
    name: str = "think"
    description: str = (
        "Use this tool to think about something. It will not obtain new information "
        "or change the database, but just append the thought to the log. Use it when "
        "complex reasoning or some cache memory is needed. This tool helps you reason "
        "through problems, analyze requirements, break down tasks, and maintain "
        "context across conversations."
    )
    
    def __init__(self, log_file: str = "thinking_log.json"):
        super().__init__()
        self._log_file = log_file
        self._thoughts = self._load_thoughts()
    
    def _load_thoughts(self) -> List[dict]:
        """Load existing thoughts from log file."""
        if os.path.exists(self._log_file):
            try:
                with open(self._log_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                return []
        return []
    
    def _save_thoughts(self):
        """Save thoughts to log file."""
        with open(self._log_file, 'w', encoding='utf-8') as f:
            json.dump(self._thoughts, f, indent=2, ensure_ascii=False)
    
    def _run(self, thought: str) -> str:
        """Add a thought to the thinking log."""
        try:
            timestamp = datetime.now().isoformat()
            
            thought_entry = {
                "timestamp": timestamp,
                "thought": thought.strip(),
                "session_id": self._get_session_id()
            }
            
            self._thoughts.append(thought_entry)
            self._save_thoughts()
            
            return f"\n\n💭 Thought logged: {thought[:100]}{'...' if len(thought) > 100 else ''}\n\n"
            
        except Exception as e:
            return f"Think tool error: {str(e)}"
    
    def _get_session_id(self) -> str:
        """Generate a simple session ID based on current working directory and date."""
        cwd = os.getcwd()
        date = datetime.now().strftime("%Y-%m-%d")
        return f"{os.path.basename(cwd)}_{date}"
    
    def get_recent_thoughts(self, limit: int = 5) -> List[dict]:
        """Get recent thoughts for context."""
        return self._thoughts[-limit:] if self._thoughts else []
    
    def clear_thoughts(self) -> str:
        """Clear all thoughts from the log."""
        self._thoughts = []
        self._save_thoughts()
        return "🧹 All thoughts cleared from log."
    
    async def _arun(self, thought: str) -> str:
        return self._run(thought)
