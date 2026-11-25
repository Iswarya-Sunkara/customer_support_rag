import subprocess
from pathlib import Path

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
out_png = Path(r"C:\Users\kiran\.gemini\antigravity\brain\b370c2a1-f82b-4e42-a8dd-c2f557143e62\clean_no_roles.png")

cmd = [
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    "--window-size=1280,1024",
    "--virtual-time-budget=3000",
    f"--screenshot={out_png}",
    "http://127.0.0.1:8050/"
]

res = subprocess.run(cmd, capture_output=True, text=True)
print("Screenshot code:", res.returncode)
print("Screenshot size bytes:", out_png.stat().st_size)

