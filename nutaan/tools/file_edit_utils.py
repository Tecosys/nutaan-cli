"""
File editing utilities for the Python FileEditTool.
Handles file operations, encoding detection, and diff generation.
"""

import os
import chardet
import difflib
from typing import Tuple, List, Dict, Any, Optional
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Hunk:
    """Represents a diff hunk."""
    old_start: int
    old_lines: int
    new_start: int
    new_lines: int
    lines: List[str]


@dataclass
class EditResult:
    """Result of applying an edit operation."""
    updated_file: str
    patch: List[Hunk]
    original_file: str


def detect_file_encoding(file_path: str) -> str:
    """Detect the encoding of a file."""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read()
            result = chardet.detect(raw_data)
            encoding = result.get('encoding', 'utf-8')
            # Fallback to utf-8 if detection is uncertain
            if not encoding or result.get('confidence', 0) < 0.7:
                encoding = 'utf-8'
            return encoding
    except Exception:
        return 'utf-8'


def detect_line_endings(file_path: str) -> str:
    """Detect line endings in a file."""
    try:
        with open(file_path, 'rb') as f:
            content = f.read()
            
        if b'\r\n' in content:
            return 'CRLF'
        elif b'\n' in content:
            return 'LF'
        elif b'\r' in content:
            return 'CR'
        else:
            return 'LF'  # Default
    except Exception:
        return 'LF'


def write_text_content(file_path: str, content: str, encoding: str = 'utf-8', line_ending: str = 'LF'):
    """Write text content to a file with specified encoding and line endings."""
    # Convert line endings
    if line_ending == 'CRLF':
        content = content.replace('\n', '\r\n')
    elif line_ending == 'CR':
        content = content.replace('\n', '\r')
    # LF is default, no conversion needed
    
    with open(file_path, 'w', encoding=encoding, newline='') as f:
        f.write(content)


def find_similar_file(file_path: str) -> Optional[str]:
    """Find a similar file with different extension in the same directory."""
    path = Path(file_path)
    directory = path.parent
    name_without_ext = path.stem
    
    if not directory.exists():
        return None
    
    # Look for files with same name but different extension
    for file in directory.iterdir():
        if file.is_file() and file.stem == name_without_ext and file.suffix != path.suffix:
            return str(file)
    
    return None


def add_line_numbers(content: str, start_line: int = 1) -> str:
    """Add line numbers to content."""
    lines = content.split('\n')
    numbered_lines = []
    
    for i, line in enumerate(lines):
        line_num = start_line + i
        numbered_lines.append(f"{line_num:4d}  {line}")
    
    return '\n'.join(numbered_lines)


def generate_diff_hunks(original: str, updated: str) -> List[Hunk]:
    """Generate diff hunks between original and updated content."""
    original_lines = original.split('\n')
    updated_lines = updated.split('\n')
    
    differ = difflib.unified_diff(
        original_lines,
        updated_lines,
        lineterm='',
        n=3  # Context lines
    )
    
    hunks = []
    current_hunk_lines = []
    old_start = new_start = 0
    old_lines = new_lines = 0
    
    for line in differ:
        if line.startswith('@@'):
            # Save previous hunk if exists
            if current_hunk_lines:
                hunks.append(Hunk(old_start, old_lines, new_start, new_lines, current_hunk_lines[:]))
                current_hunk_lines = []
            
            # Parse hunk header: @@ -old_start,old_count +new_start,new_count @@
            parts = line.split()
            if len(parts) >= 3:
                old_part = parts[1][1:]  # Remove '-'
                new_part = parts[2][1:]  # Remove '+'
                
                if ',' in old_part:
                    old_start, old_lines = map(int, old_part.split(','))
                else:
                    old_start, old_lines = int(old_part), 1
                
                if ',' in new_part:
                    new_start, new_lines = map(int, new_part.split(','))
                else:
                    new_start, new_lines = int(new_part), 1
        
        elif line.startswith(('---', '+++')):
            # Skip file headers
            continue
        else:
            current_hunk_lines.append(line)
    
    # Add final hunk
    if current_hunk_lines:
        hunks.append(Hunk(old_start, old_lines, new_start, new_lines, current_hunk_lines))
    
    return hunks


def apply_edit(file_path: str, old_string: str, new_string: str) -> EditResult:
    """Apply an edit operation to a file."""
    full_path = os.path.abspath(file_path)
    
    # Read original file if it exists
    if os.path.exists(full_path):
        encoding = detect_file_encoding(full_path)
        with open(full_path, 'r', encoding=encoding) as f:
            original_file = f.read()
    else:
        original_file = ''
    
    # Apply the edit
    if old_string == '':
        # Creating new content
        updated_file = new_string
    else:
        # Replacing existing content
        updated_file = original_file.replace(old_string, new_string)
    
    # Generate diff hunks
    patch = generate_diff_hunks(original_file, updated_file)
    
    return EditResult(
        updated_file=updated_file,
        patch=patch,
        original_file=original_file
    )


def get_snippet(initial_text: str, old_str: str, new_str: str, n_lines_snippet: int = 4) -> Tuple[str, int]:
    """Get a snippet of the file around the edit location with line numbers."""
    if not initial_text and old_str == '':
        # New file creation
        new_lines = new_str.split('\n')
        snippet_lines = new_lines[:n_lines_snippet * 2 + 1]
        return '\n'.join(snippet_lines), 1
    
    # Find the replacement location
    before = initial_text.split(old_str)[0] if old_str else ''
    replacement_line = len(before.split('\n')) - 1 if before else 0
    
    # Create the new file content
    new_file_content = initial_text.replace(old_str, new_str) if old_str else new_str
    new_file_lines = new_file_content.split('\n')
    
    # Calculate snippet bounds
    start_line = max(0, replacement_line - n_lines_snippet)
    end_line = replacement_line + n_lines_snippet + len(new_str.split('\n'))
    
    # Get snippet
    snippet_lines = new_file_lines[start_line:end_line + 1]
    snippet = '\n'.join(snippet_lines)
    
    return snippet, start_line + 1
