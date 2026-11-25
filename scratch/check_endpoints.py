import re

with open('src/server.py', 'r', encoding='utf-8') as f:
    text = f.read()

endpoints = re.findall(r'@app\.(get|post)\(["\']([^"\']+)["\']', text)
for method, path in endpoints:
    print(f"{method.upper():4} {path}")

