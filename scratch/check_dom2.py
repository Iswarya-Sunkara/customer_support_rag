from html.parser import HTMLParser

class MyParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_w12 = False
        self.w12_depth = 0
        self.elements = []

    def handle_starttag(self, tag, attrs):
        attrs_dict = dict(attrs)
        if attrs_dict.get('id') == 'viewWeek12':
            self.in_w12 = True
            self.w12_depth = 1
            self.elements.append(('START_W12', tag, attrs_dict))
            return
        
        if self.in_w12:
            self.w12_depth += 1
            if 'class' in attrs_dict or 'id' in attrs_dict:
                self.elements.append((f'depth={self.w12_depth}', tag, attrs_dict.get('id'), attrs_dict.get('class')))

    def handle_endtag(self, tag):
        if self.in_w12:
            self.w12_depth -= 1
            if self.w12_depth == 0:
                self.in_w12 = False
                self.elements.append(('END_W12', tag, {}))

with open('src/static/index.html', 'r', encoding='utf-8') as f:
    parser = MyParser()
    parser.feed(f.read())

for el in parser.elements:
    print(el)

