"""
Session History Manager - Handles conversation history persistence
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict


@dataclass
class SessionMetadata:
    """Metadata for a conversation session."""
    session_id: str
    display_name: str
    created: str
    think_mode: bool = False
    total_messages: int = 0
    tools_used: List[str] = None
    last_active: str = None
    
    def __post_init__(self):
        if self.tools_used is None:
            self.tools_used = []
        if self.last_active is None:
            self.last_active = self.created


@dataclass
class SessionHistory:
    """Container for session history data."""
    sessions: Dict[str, Dict[str, Any]]
    metadata: Dict[str, Any]


class SessionHistoryManager:
    """Manages conversation session history with JSON persistence."""
    
    def __init__(self, history_file: str = "history.json"):
        self.history_file = history_file
        self.history = self._load_history()
    
    def _load_history(self) -> SessionHistory:
        """Load history from JSON file."""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return SessionHistory(
                        sessions=data.get('sessions', {}),
                        metadata=data.get('metadata', {})
                    )
            except Exception as e:
                print(f"Warning: Could not load history file: {e}")
        
        # Return empty history with metadata
        return SessionHistory(
            sessions={},
            metadata={'created': datetime.now().isoformat()}
        )
    
    def _save_history(self):
        """Save history to JSON file."""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(asdict(self.history), f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Warning: Could not save history: {e}")
    
    def create_session(self, think_mode: bool = False) -> str:
        """Create a new session and return session ID."""
        timestamp = datetime.now()
        session_id = f"session_{timestamp.strftime('%Y%m%d_%H%M%S')}"
        
        # Create session metadata
        metadata = SessionMetadata(
            session_id=session_id,
            display_name=f"Session {timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            created=timestamp.isoformat(),
            think_mode=think_mode
        )
        
        # Initialize session
        self.history.sessions[session_id] = {
            'display_name': metadata.display_name,
            'created': metadata.created,
            'messages': [],
            'metadata': asdict(metadata)
        }
        
        self._save_history()
        return session_id
    
    def add_message(self, session_id: str, message: Dict[str, Any]):
        """Add a message to session history."""
        if session_id not in self.history.sessions:
            # Create session if it doesn't exist
            self.create_session_with_id(session_id)
        
        session = self.history.sessions[session_id]
        session['messages'].append(message)
        
        # Update metadata
        session['metadata']['total_messages'] = len(session['messages'])
        session['metadata']['last_active'] = datetime.now().isoformat()
        
        # Track tool usage
        if message.get('role') == 'tool':
            tool_name = message.get('name', 'unknown')
            tools_used = session['metadata'].get('tools_used', [])
            if tool_name not in tools_used:
                tools_used.append(tool_name)
                session['metadata']['tools_used'] = tools_used
        
        self._save_history()
    
    def create_session_with_id(self, session_id: str, think_mode: bool = False):
        """Create a session with a specific ID."""
        if session_id in self.history.sessions:
            return session_id
        
        timestamp = datetime.now()
        metadata = SessionMetadata(
            session_id=session_id,
            display_name=f"Session {timestamp.strftime('%Y-%m-%d %H:%M:%S')}",
            created=timestamp.isoformat(),
            think_mode=think_mode
        )
        
        self.history.sessions[session_id] = {
            'display_name': metadata.display_name,
            'created': metadata.created,
            'messages': [],
            'metadata': asdict(metadata)
        }
        
        self._save_history()
        return session_id
    
    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data by ID."""
        return self.history.sessions.get(session_id)
    
    def get_session_messages(self, session_id: str) -> List[Dict[str, Any]]:
        """Get messages for a session."""
        session = self.get_session(session_id)
        return session['messages'] if session else []
    
    def list_sessions(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recent sessions."""
        sessions = []
        for session_id, session_data in self.history.sessions.items():
            sessions.append({
                'session_id': session_id,
                'display_name': session_data['display_name'],
                'created': session_data['created'],
                'last_active': session_data['metadata'].get('last_active', session_data['created']),
                'total_messages': session_data['metadata'].get('total_messages', 0),
                'think_mode': session_data['metadata'].get('think_mode', False),
                'tools_used': session_data['metadata'].get('tools_used', [])
            })
        
        # Sort by last active, most recent first
        sessions.sort(key=lambda x: x['last_active'], reverse=True)
        return sessions[:limit]
    
    def search_sessions(self, query: str) -> List[Dict[str, Any]]:
        """Search sessions by content."""
        matching_sessions = []
        query_lower = query.lower()
        
        for session_id, session_data in self.history.sessions.items():
            # Search in display name
            if query_lower in session_data['display_name'].lower():
                matching_sessions.append({
                    'session_id': session_id,
                    'display_name': session_data['display_name'],
                    'match_type': 'name'
                })
                continue
            
            # Search in messages
            for message in session_data['messages']:
                content = str(message.get('content', ''))
                if query_lower in content.lower():
                    matching_sessions.append({
                        'session_id': session_id,
                        'display_name': session_data['display_name'],
                        'match_type': 'content',
                        'match_preview': content[:100] + '...' if len(content) > 100 else content
                    })
                    break
        
        return matching_sessions
    
    def delete_session(self, session_id: str) -> bool:
        """Delete a session."""
        if session_id in self.history.sessions:
            del self.history.sessions[session_id]
            self._save_history()
            return True
        return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get usage statistics."""
        total_sessions = len(self.history.sessions)
        total_messages = sum(
            session['metadata'].get('total_messages', 0) 
            for session in self.history.sessions.values()
        )
        
        # Tool usage statistics
        tool_usage = {}
        for session in self.history.sessions.values():
            for tool in session['metadata'].get('tools_used', []):
                tool_usage[tool] = tool_usage.get(tool, 0) + 1
        
        # Think mode usage
        think_mode_sessions = sum(
            1 for session in self.history.sessions.values()
            if session['metadata'].get('think_mode', False)
        )
        
        return {
            'total_sessions': total_sessions,
            'total_messages': total_messages,
            'think_mode_sessions': think_mode_sessions,
            'tool_usage': tool_usage,
            'history_file_size': os.path.getsize(self.history_file) if os.path.exists(self.history_file) else 0
        }
    
    def cleanup_old_sessions(self, keep_recent: int = 50):
        """Clean up old sessions, keeping only the most recent ones."""
        sessions = self.list_sessions(limit=None)  # Get all sessions
        
        if len(sessions) <= keep_recent:
            return 0  # Nothing to clean up
        
        # Sort by last active and keep only the most recent
        sessions.sort(key=lambda x: x['last_active'], reverse=True)
        sessions_to_delete = sessions[keep_recent:]
        
        deleted_count = 0
        for session in sessions_to_delete:
            if self.delete_session(session['session_id']):
                deleted_count += 1
        
        return deleted_count


# Global session history manager instance
session_history = SessionHistoryManager()
