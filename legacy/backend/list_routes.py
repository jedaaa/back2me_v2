
from app import app

with open("routes.txt", "w") as f:
    for rule in app.url_map.iter_rules():
        f.write(f"{rule} {rule.methods}\n")
