import os
import sys

# Add the 'backend' directory to Python's module search path
# so that absolute imports within the backend package work correctly.
root_path = os.path.dirname(os.path.abspath(__file__))
backend_path = os.path.join(root_path, "backend")
sys.path.insert(0, backend_path)

# Vercel's @vercel/python builder looks for the application instance 
# in the global 'app' variable by default.
from backend.app import app
