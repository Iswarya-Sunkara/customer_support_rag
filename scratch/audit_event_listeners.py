with open('src/static/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
lines = text.splitlines()

for i, line in enumerate(lines, 1):
    if '.addeventlistener' in line.lower():
        # check if there's a null check guard before it
        print(f"Line {i}: {line.strip()[:80]}")

