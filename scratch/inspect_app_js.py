with open('src/static/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(500, min(750, len(lines))):
    print(f"{i+1}: {lines[i]}", end='')

