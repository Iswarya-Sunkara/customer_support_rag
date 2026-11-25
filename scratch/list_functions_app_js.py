with open('src/static/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines, 1):
    if l.strip().startswith('function ') or l.strip().startswith('async function '):
        print(f"Line {i}: {l.strip()[:60]}")

