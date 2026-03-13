#!/usr/bin/env python3
"""Quick launcher for AI Cloud Migration Copilot dashboard."""
import subprocess
import sys
import os

os.chdir(os.path.dirname(os.path.abspath(__file__)))
subprocess.run([sys.executable, "-m", "streamlit", "run", "dashboard/app_v2.py", "--server.headless", "true"])
