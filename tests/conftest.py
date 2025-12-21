"""Test configuration for pytest."""

import os
import tempfile
from pathlib import Path

# Add src directory to Python path for imports
SRC_DIR = Path(__file__).parent.parent / 'src'
import sys
sys.path.insert(0, str(SRC_DIR))
