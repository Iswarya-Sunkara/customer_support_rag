from html.parser import HTMLParser

class ViewTracker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.views = []
        self.void_tags = {'meta', 'link', 'img', 'br', 'hr', 'input', 'source'}

    def handle_starttag(self, tag, attrs):
        if tag.lower() in self.void_tags:
            return
        attrs_dict = dict(attrs)
        elem_id = attrs_dict.get('id', '')
        pos = self.getpos()
        self.stack.append((tag.lower(), elem_id, pos))
        if elem_id.startswith('view'):
            parent = self.stack[-2] if len(self.stack) >= 2 else None
            self.views.append((elem_id, pos, parent))

    def handle_endtag(self, tag):
        t = tag.lower()
        if t in self.void_tags:
            return
        if self.stack:
            last_tag, last_id, pos = self.stack.pop()
            if last_id.startswith('view'):
                print(f"View closed: #{last_id} closed at {self.getpos()} (opened at {pos})")

with open('src/static/index.html', 'r', encoding='utf-8') as f:
    vt = ViewTracker()
    vt.feed(f.read())

print("\n--- Views and their parents at open time ---")
for v in vt.views:
    print(v)

