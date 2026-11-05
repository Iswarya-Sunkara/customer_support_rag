with open('src/static/index.html', 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace("app.js?v=35", "app.js?v=40")
content = content.replace("styles.css?v=35", "styles.css?v=40")

with open('src/static/index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Bumped to v=40!")

