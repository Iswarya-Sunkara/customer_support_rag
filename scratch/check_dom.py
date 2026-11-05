from bs4 import BeautifulSoup

with open('src/static/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

soup = BeautifulSoup(html, 'html.parser')
w12 = soup.find(id='viewWeek12')
if w12 is None:
    print("viewWeek12 NOT FOUND in DOM!")
else:
    print(f"viewWeek12 found! Direct children: {[c.name for c in w12.children if c.name]}")
    container = w12.find(class_='w7-container')
    if container:
        print(f"w7-container children: {[c.name for c in container.children if c.name]}")
        print(f"Number of section cards: {len(container.find_all(class_='w7-section-card'))}")
        print(f"Header card found: {container.find(class_='w7-header-card') is not None}")
        print(f"KPI grid found: {container.find(class_='w7-kpi-grid') is not None}")
        print(f"Console found: {container.find(id='w12LiveOutputConsole') is not None}")
    else:
        print("w7-container NOT FOUND inside viewWeek12!")

