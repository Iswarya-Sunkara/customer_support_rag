from html.parser import HTMLParser

class FullParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack = []
        self.void_tags = {'meta', 'link', 'img', 'br', 'hr', 'input', 'source'}

    def handle_starttag(self, tag, attrs):
        if tag.lower() in self.void_tags:
            return
        self.stack.append((tag.lower(), self.getpos()))

    def handle_endtag(self, tag):
        t = tag.lower()
        if t in self.void_tags:
            return
        if not self.stack:
            print(f"End tag </{t}> at {self.getpos()} with empty stack!")
            return
        last, pos = self.stack.pop()
        if last != t:
            print(f"Mismatched end tag </{t}> at {self.getpos()}, expected </{last}> (opened at {pos})")

with open('src/static/index.html', 'r', encoding='utf-8') as f:
    p = FullParser()
    p.feed(f.read())
print(f"Remaining tags on stack at EOF: {len(p.stack)}")
for item in p.stack:
    print(item)

