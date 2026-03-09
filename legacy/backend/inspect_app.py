from app import app
print(f"Static URL Path: {app.static_url_path}")
print(f"Static Folder: {app.static_folder}")
print("\nRules:")
for rule in app.url_map.iter_rules():
    print(f"{rule} {rule.methods}")
