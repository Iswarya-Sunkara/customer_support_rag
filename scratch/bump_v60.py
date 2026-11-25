with open('src/static/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace("app.js?v=50", "app.js?v=60")
html = html.replace("styles.css?v=50", "styles.css?v=60")

with open('src/static/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Bumped to v=60!")

