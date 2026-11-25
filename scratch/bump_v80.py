with open('src/static/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

html = html.replace("app.js?v=70", "app.js?v=80")
html = html.replace("styles.css?v=70", "styles.css?v=80")

with open('src/static/index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Bumped to v=80!")

