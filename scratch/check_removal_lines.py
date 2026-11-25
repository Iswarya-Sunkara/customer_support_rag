with open('src/static/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# Let's verify line starting of viewWeek3 and line starting of viewWeek12
vw3_idx = None
vw12_idx = None
for i, l in enumerate(lines):
    if 'id="viewWeek3"' in l:
        vw3_idx = i
    if 'id="viewWeek12"' in l:
        vw12_idx = i

print(f"viewWeek3 at line {vw3_idx+1}")
print(f"viewWeek12 at line {vw12_idx+1}")
print("Lines before viewWeek12:", lines[vw12_idx-5:vw12_idx])

