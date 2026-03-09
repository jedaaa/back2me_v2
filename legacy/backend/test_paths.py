import os
import sys

# Add backend to path
backend_dir = r"c:\Users\JOSHUA\OneDrive\Desktop\back2me_v2\backend"
os.chdir(backend_dir)

# Test path resolution
print("Current directory:", os.getcwd())
print("__file__ would be:", os.path.join(backend_dir, "app.py"))

root_path = backend_dir
frontend1 = os.path.join(root_path, "../frontend")
frontend2 = os.path.abspath(os.path.join(os.path.dirname(os.path.join(backend_dir, "app.py")), "..", "frontend"))

print("\nMethod 1 (current):", frontend1)
print("Exists?", os.path.exists(frontend1))
print("index.html exists?", os.path.exists(os.path.join(frontend1, "index.html")))

print("\nMethod 2 (absolute):", frontend2)
print("Exists?", os.path.exists(frontend2))
print("index.html exists?", os.path.exists(os.path.join(frontend2, "index.html")))
