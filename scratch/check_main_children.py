from html.parser import HTMLParser

class MainChildren(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_main = False
        self.depth_in_main = 0
        self.children = []

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if tag == 'main':
            self.in_main = True
            self.depth_in_main = 0
            return
        if self.in_main:
            if self.depth_in_main == 0:
                self.children.append((tag, d.get('id'), d.get('class')))
            if tag not in ('img', 'br', 'hr', 'input', 'meta', 'link'):
                self.depth_in_main += 1

    def handle_endtag(self, tag):
        if self.in_main:
            if tag == 'main':
                self.in_main = False
            else:
                self.depth_in_main -= 1

with open('src/static/index.html', 'r', encoding='utf-8') as f:
    p = MainChildren()
    p.feed(f.read())

print("Direct children of <main class='chat-main'>:")
for c in p.children:
    print(c)

