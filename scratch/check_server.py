import urllib.request

try:
    resp = urllib.request.urlopen("http://127.0.0.1:8050/")
    print(f"Status: {resp.status}")
    html = resp.read().decode('utf-8')
    print(f"HTML length: {len(html)}")
    print(f"Has viewWeek12: {'viewWeek12' in html}")
    print(f"Has tabBtnWeek12Header: {'tabBtnWeek12Header' in html}")
except Exception as e:
    print(f"Error: {e}")

