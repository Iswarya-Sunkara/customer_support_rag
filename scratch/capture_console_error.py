import subprocess

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
cmd = [
    chrome_path,
    "--headless=new",
    "--disable-gpu",
    "--virtual-time-budget=3000",
    "--enable-logging=stderr",
    "--v=1",
    "http://127.0.0.1:8050/"
]

res = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
print("STDOUT:")
print(res.stdout)
print("STDERR:")
for line in res.stderr.splitlines():
    if 'error' in line.lower() or 'exception' in line.lower() or 'uncaught' in line.lower() or 'app.js' in line:
        print(line)

