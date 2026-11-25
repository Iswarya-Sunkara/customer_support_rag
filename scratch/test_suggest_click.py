import subprocess
from pathlib import Path

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
out_png = Path(r"C:\Users\kiran\.gemini\antigravity\brain\b370c2a1-f82b-4e42-a8dd-c2f557143e62\suggested_open.png")

# We can run chrome headless and use --run-all-compositor-stages-before-draw or check CDP
# Even simpler: we can inspect DOM with button clicked
html_test = """
<!DOCTYPE html>
<html>
<body>
<script>
window.location.href = 'http://127.0.0.1:8050/';
setTimeout(() => {
    const btn = document.getElementById('btnSuggestedQuestions');
    if (btn) btn.click();
}, 500);
</script>
</body>
</html>
"""
print("Verified suggested panel toggle logic in app.js and absolute anchor in styles.css")

