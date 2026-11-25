with open('src/static/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

for i, l in enumerate(lines, 1):
    if 'id="view' in l or 'id="sidebarCurriculum' in l or 'id="weeksPopover' in l:
        print(f"Line {i}: {l.strip()[:80]}")

