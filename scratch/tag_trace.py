from html.parser import HTMLParser

class TagTracker(HTMLParser):
    def __init__(self):
        super().__init__()
        self.depth = 0
        self.in_w12 = False

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if d.get('id') == 'viewWeek12':
            self.in_w12 = True
            self.depth = 0
            print(f"{'  '*self.depth}<{tag} id=viewWeek12>")
            self.depth += 1
            return
        if self.in_w12:
            classes = d.get('class', '')
            elem_id = d.get('id', '')
            info = f" class='{classes}'" if classes else ""
            if elem_id: info += f" id='{elem_id}'"
            print(f"{'  '*self.depth}<{tag}{info}>")
            if tag not in ('img', 'br', 'hr', 'input', 'meta', 'link'):
                self.depth += 1

    def handle_endtag(self, tag):
        if self.in_w12:
            self.depth -= 1
            print(f"{'  '*self.depth}</{tag}>")
            if self.depth == 0:
                self.in_w12 = False
                print("--- END OF W12 ---")

with open('src/static/index.html', 'r', encoding='utf-8') as f:
    tracker = TagTracker()
    tracker.feed(f.read())

