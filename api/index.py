import os
import sys

# Add parent directory to path so we can import modules from root
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api_server import app
