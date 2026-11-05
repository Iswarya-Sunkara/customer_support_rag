with open('src/static/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("--- Lines 1910-1915 ---")
for i in range(1909, 1915):
    print(f"{i+1}: {lines[i]}", end='')

print("\n--- Lines 2138-2148 ---")
for i in range(2137, 2148):
    print(f"{i+1}: {lines[i]}", end='')

print("\n--- Lines 2438-2448 ---")
for i in range(2437, 2448):
    print(f"{i+1}: {lines[i]}", end='')

