#!/usr/bin/env python3
"""
AI Tutor Package Initialization
"""

__version__ = "2.0.0"
__description__ = "AI Tutor - Modular exam paper processing system"

# Make key components available at package level
from .config import BASE_DIR, QUESTION_BANKS_DIR, get_app_state
from .utils import generate_paper_folder_name, get_image_count
from .module_manager import ModuleManager
from .ai_solver_manager import SimpleAISolverManager

__all__ = [
    'BASE_DIR',
    'QUESTION_BANKS_DIR', 
    'get_app_state',
    'generate_paper_folder_name',
    'get_image_count',
    'ModuleManager',
    'SimpleAISolverManager'
]