#!/usr/bin/env python3
"""
Essential configuration settings for the Enhanced AI Solver
"""

from pathlib import Path

# API Configuration
ANTHROPIC_API_KEY = "${ANTHROPIC_API_KEY}"

# Quality Control Settings
CONFIDENCE_THRESHOLD = 0.91  # 91% quality threshold
QUALITY_THRESHOLD_DISPLAY = "91%"

# Directory Settings
BASE_DIR = Path("/Users/wynceaxcel/Apps/axcelscore/backend")
QUESTION_BANKS_DIR = Path("/Users/wynceaxcel/Apps/axcelscore/question_banks")

# Image Settings
SUPPORTED_IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
IMAGE_FOLDER_PRIORITY = ["images", "extracted_images"]  # Primary -> Fallback

# Flask Settings
FLASK_HOST = '0.0.0.0'
FLASK_PORT = 5005

# Claude API Settings
CLAUDE_API_MODEL = "claude-3-5-sonnet-20241022"
CLAUDE_API_MAX_TOKENS = 2048

# Version Information
SOLVER_VERSION = "Enhanced v2.1 - Claude API Ready"