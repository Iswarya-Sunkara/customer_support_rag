import subprocess
from pathlib import Path

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
out_png = Path(r"C:\Users\kiran\OneDrive\Desktop\projects\customer_support_rag\scratch\live_render.png")

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
print("Return code:", res.returncode)
print("File exists:", out_png.exists())
if out_png.exists():
    print("File size bytes:", out_png.stat().st_size)

