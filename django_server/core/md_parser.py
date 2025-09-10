"""
Markdown parser utility for extracting JSON blocks from markdown files.
"""

import re
from typing import Optional, Dict, Any


def extract_first_json_block(file_path: str) -> Optional[Dict[str, Any]]:
    """
    Extract the first fenced JSON block from a markdown file.
    
    Args:
        file_path: Path to the markdown file
        
    Returns:
        Parsed JSON as dictionary, or None if no JSON block found
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Pattern to match fenced code blocks with json language
        pattern = r'```json\s*\n(.*?)\n```'
        match = re.search(pattern, content, re.DOTALL)
        
        if match:
            json_str = match.group(1).strip()
            import json
            return json.loads(json_str)
        
        return None
        
    except (FileNotFoundError, json.JSONDecodeError, Exception) as e:
        print(f"Error extracting JSON from {file_path}: {e}")
        return None