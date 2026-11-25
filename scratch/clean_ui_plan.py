import re

with open('src/static/index.html', 'r', encoding='utf-8') as f:
    html = f.read()

print("Total lines in index.html:", len(html.splitlines()))

views = re.findall(r'<div class=["\']view-container[^"\']*["\'] id=["\']([^"\']+)["\']', html)
print("Views found:", views)

# Check sidebar
curriculum_sidebar = re.search(r'id=["\']sidebarCurriculumSection["\']', html)
print("Sidebar curriculum section exists:", curriculum_sidebar is not None)

# Check popover
popover = re.search(r'id=["\']weeksPopoverWrapper["\']', html)
print("Popover menu exists:", popover is not None)

