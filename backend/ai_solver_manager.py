#!/usr/bin/env python3
"""
AI Solver Manager - Simple Wrapper for Existing ai_solver.py
Just delegates all calls to the existing working ai_solver.py
"""

# Import the existing ai_solver.py functionality
try:
    from ai_solver import (
        EnhancedAISolverManager,
        AISolverManager as ExistingAISolverManager,
        create_enhanced_ai_solver_manager,
        create_ai_solver_manager as create_existing_ai_solver_manager
    )
    AI_SOLVER_AVAILABLE = True
except ImportError as e:
    AI_SOLVER_AVAILABLE = False
    print(f"Warning: Could not import ai_solver.py: {e}")

class AISolverManager:
    """
    Simple wrapper that delegates everything to existing ai_solver.py
    """
    
    def __init__(self, app_instance=None, question_banks_dir=None):
        if AI_SOLVER_AVAILABLE:
            # Just create the existing manager - it does everything we need
            self.existing_manager = create_existing_ai_solver_manager(app_instance, question_banks_dir)
        else:
            self.existing_manager = None
    
    def initialize_solver(self, paper_folder):
        """Delegate to existing manager"""
        if self.existing_manager:
            return self.existing_manager.initialize_solver(paper_folder)
        return {"success": False, "error": "AI Solver not available"}
    
    def create_blueprint(self):
        """Delegate to existing manager"""
        if self.existing_manager:
            return self.existing_manager.create_blueprint()
        return None

def create_ai_solver_manager(app, question_banks_dir):
    """Factory function - same interface as before"""
    return AISolverManager(app, question_banks_dir)