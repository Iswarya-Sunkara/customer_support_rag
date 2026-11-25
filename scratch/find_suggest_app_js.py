with open('src/static/app.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
for i, line in enumerate(text.splitlines(), 1):
    if 'suggest' in line.lower():
        print(f"Line {i}: {line.strip()[:100]}")

