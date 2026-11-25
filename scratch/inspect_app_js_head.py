with open('src/static/app.js', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Lines 1 to 40:")
for i in range(40):
    print(lines[i], end='')

print("\nLines 470 to 520:")
for i in range(470, 520):
    print(lines[i], end='')

