"""
ADK Tool wrapper for agents
Simple Tool class if ADK SDK structure is different
"""

from typing import Callable, Any, Dict


class Tool:
    """Simple Tool wrapper for agent tools"""
    
    def __init__(self, name: str, description: str, func: Callable):
        self.name = name
        self.description = description
        self.func = func
    
    def __call__(self, *args, **kwargs) -> Any:
        """Call the tool function"""
        return self.func(*args, **kwargs)

