with open('src/static/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i in range(1670, len(lines)):
    print(lines[i], end='')

