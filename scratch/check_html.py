with open('src/static/index.html', 'r', encoding='utf-8') as f:
    for i, line in enumerate(f, 1):
        if '<main' in line or '</main>' in line or 'id="view' in line:
            print(f"Line {i}: {line.strip()[:70]}")

