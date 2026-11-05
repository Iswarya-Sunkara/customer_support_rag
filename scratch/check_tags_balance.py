with open('src/static/index.html', 'r', encoding='utf-8') as f:
    lines = f.readlines()

stack = []
import re
for line_no, line in enumerate(lines, 1):
    tags = re.findall(r'<(/?[a-zA-Z0-9]+)[^>]*>', line)
    for tag in tags:
        if tag in ('meta', 'link', 'img', 'br', 'hr', 'input', 'source'):
            continue
        if not tag.startswith('/'):
            # opening
            elem_id = ""
            m = re.search(r'id=["\']([^"\']+)["\']', line)
            if m:
                elem_id = f"#{m.group(1)}"
            stack.append((tag, line_no, elem_id))
        else:
            closing = tag[1:]
            if not stack:
                print(f"ERROR: closing </{closing}> on line {line_no} with empty stack")
            else:
                last_tag, last_line, last_id = stack.pop()
                if last_tag != closing:
                    print(f"MISMATCH: on line {line_no} </{closing}> closes <{last_tag}{last_id}> opened at {last_line}")

print(f"Stack at end: {stack}")

