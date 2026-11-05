import subprocess
import re

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
cmd = [
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    "--virtual-time-budget=3000",
    "--dump-dom",
    "http://127.0.0.1:8050/#week12"
]

res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8')
html = res.stdout

match = re.search(r'<div[^>]*id=["\']viewWeek12["\'][^>]*>', html)
if match:
    print("Found viewWeek12 tag in live DOM:")
    print(match.group(0))
else:
    print("viewWeek12 tag NOT found in live DOM")

match10 = re.search(r'<div[^>]*id=["\']viewWeek10["\'][^>]*>', html)
if match10:
    print("Found viewWeek10 tag in live DOM:")
    print(match10.group(0))

