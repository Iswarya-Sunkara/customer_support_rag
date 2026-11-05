import shutil
from pathlib import Path

src = Path(r"C:\Users\kiran\OneDrive\Desktop\projects\customer_support_rag\scratch\live_render.png")
dst = Path(r"C:\Users\kiran\.gemini\antigravity\brain\b370c2a1-f82b-4e42-a8dd-c2f557143e62\live_render.png")

shutil.copyfile(src, dst)
print("Copied to:", dst)
print("Size:", dst.stat().st_size)

