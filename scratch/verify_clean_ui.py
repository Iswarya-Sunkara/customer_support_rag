import urllib.request
import subprocess
from pathlib import Path

# 1. Test server response
try:
    resp = urllib.request.urlopen("http://127.0.0.1:8050/")
    html = resp.read().decode('utf-8')
    print("Server HTTP status:", resp.status)
    print("Has viewChat:", 'id="viewChat"' in html)
    print("Has viewWeek12:", 'id="viewWeek12"' in html)
    print("Has viewWeek3 (should be False):", 'id="viewWeek3"' in html)
    print("Has viewWeek7 (should be False):", 'id="viewWeek7"' in html)
    print("Has viewWeek10 (should be False):", 'id="viewWeek10"' in html)
    print("Has weeksPopoverWrapper (should be False):", 'id="weeksPopoverWrapper"' in html)
except Exception as e:
    print("HTTP error:", e)

# 2. Take screenshot of clean UI
chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
out_png = Path(r"C:\Users\kiran\.gemini\antigravity\brain\b370c2a1-f82b-4e42-a8dd-c2f557143e62\clean_capstone_ui.png")

cmd = [
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    "--window-size=1280,1024",
    "--virtual-time-budget=3000",
    f"--screenshot={out_png}",
    "http://127.0.0.1:8050/#week12"
]

res = subprocess.run(cmd, capture_output=True, text=True)
print("Screenshot return code:", res.returncode)
print("Screenshot exists:", out_png.exists())
if out_png.exists():
    print("Screenshot size bytes:", out_png.stat().st_size)

