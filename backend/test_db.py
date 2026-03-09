import os
from config.database import execute_query

# Temporarily force the railway URL if needed for a diagnostic script
# Make sure your shell has these set, or hardcode them here purely for this test.
try:
    posts = execute_query("SELECT id, item_name, user_id FROM posts ORDER BY id DESC LIMIT 5", fetchall=True)
    print("SUCCESS! Recent posts:")
    print(posts)
except Exception as e:
    print(f"FAILED: {e}")
