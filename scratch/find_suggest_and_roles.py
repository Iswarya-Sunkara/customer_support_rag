with open('src/static/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

import re

# Find anything with 'suggest'
for i, line in enumerate(html.splitlines(), 1):
    if 'suggest' in line.lower():
        print(f"Line {i}: {line.strip()[:100]}")

# Find role modal and header buttons
for i, line in enumerate(html.splitlines(), 1):
    if 'loginmodal' in line.lower() or 'btnswitchrole' in line.lower() or 'btnfullscreeneval' in line.lower():
        print(f"Line {i}: {line.strip()[:100]}")

