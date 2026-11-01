"""render.py url iframe_width out.png [height] : screenshot a page inside an iframe of exactly that width (headless Chrome)"""
import os, subprocess, sys, tempfile
url, w, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
h = int(sys.argv[4]) if len(sys.argv) > 4 else 14000
d = tempfile.mkdtemp(prefix="rnd-")
page = os.path.join(d, "p.html")
open(page, "w").write(f'<!doctype html><style>html,body{{margin:0}}iframe{{display:block;border:0;width:{w}px;height:{h}px}}</style><iframe src="{url}"></iframe>')
subprocess.run([r"C:\Program Files\Google\Chrome\Application\chrome.exe", "--headless=new", "--disable-gpu", "--hide-scrollbars",
                f"--user-data-dir={os.path.join(d, 'prof')}", "--virtual-time-budget=12000", f"--window-size={w + 20},{h}",
                f"--screenshot={out}", "file:///" + page.replace(os.sep, "/")], capture_output=True, timeout=180)
from PIL import Image
Image.open(out).crop((0, 0, w, h)).save(out)
print("ok", out)
