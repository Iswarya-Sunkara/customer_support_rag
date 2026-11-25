import subprocess
import re

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
out_png = r"C:\Users\kiran\.gemini\antigravity\brain\b370c2a1-f82b-4e42-a8dd-c2f557143e62\dashboard_tab_shot.png"

cmd = [
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    "--window-size=1280,1024",
    "--virtual-time-budget=3000",
    f"--screenshot={out_png}",
    "http://127.0.0.1:8050/?tab=week12"
]

res = subprocess.run(cmd, capture_output=True, text=True)
print("Return code:", res.returncode)

# Dump DOM to check
cmd_dom = [
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    "--virtual-time-budget=3000",
    "--dump-dom",
    "http://127.0.0.1:8050/?tab=week12"
]
res_dom = subprocess.run(cmd_dom, capture_output=True, text=True, encoding='utf-8')
for line in res_dom.stdout.splitlines():
    if 'id="viewWeek12"' in line or 'id="viewChat"' in line:
        print(line)

