
import sys
import os

# Add current directory to path
sys.path.append(os.getcwd())

from routes import auth
from routes.auth import auth_bp
print(f"Auth module file: {auth.__file__}")
print(f"Blueprint name: {auth_bp.name}")
print(f"Deferred functions count: {len(auth_bp.deferred_functions)}")

# Print each deferred function to see if it's a route
for func in auth_bp.deferred_functions:
    print(func)
