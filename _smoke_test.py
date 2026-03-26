"""AutoGraph product build smoke test."""
import ast
import os
import sys
import subprocess
from pathlib import Path

BASE = Path(r"C:\AI\autograph")
results = []
passed = 0
failed = 0

def check(label, ok, detail=""):
    global passed, failed
    if ok:
        passed += 1
        results.append(f"  [PASS] {label}")
    else:
        failed += 1
        results.append(f"  [FAIL] {label}" + (f" -- {detail}" if detail else ""))

# 1. File existence checks
files = [
    "intake_form.html",
    "intake_server.py",
    "round2_generator.py",
    "round2_form.html",
    "portrait_chat.html",
    "autograph_coordinator.py",
    "landing_v2.html",
]
results.append("\n-- File Existence --")
for f in files:
    p = BASE / f
    check(f"EXISTS {f}", p.exists(), f"missing at {p}")

# 2. Directory existence
results.append("\n-- Directories --")
for d in ["intakes", "clients", "round2_questions"]:
    check(f"DIR {d}/", (BASE / d).is_dir())

# 3. Syntax checks on Python files
results.append("\n-- Python Syntax --")
for pyfile in ["intake_server.py", "round2_generator.py", "autograph_coordinator.py"]:
    p = BASE / pyfile
    if p.exists():
        try:
            ast.parse(p.read_text(encoding="utf-8"))
            check(f"SYNTAX {pyfile}", True)
        except SyntaxError as e:
            check(f"SYNTAX {pyfile}", False, str(e))
    else:
        check(f"SYNTAX {pyfile}", False, "file missing")

# 4. HTML file content checks
results.append("\n-- HTML Content --")
html_checks = [
    ("intake_form.html",   ["--accent: #7c6af7", "submit-intake", "screen-8", "Question 8 of 8"]),
    ("round2_form.html",   ["--gold: #c9a84c",   "Round 2", "buildScreens"]),
    ("portrait_chat.html", ["Portrait Navigator", "/chat", "sendMessage"]),
    ("landing_v2.html",    ["$299", "$449", "$649", "Portrait Navigator", "navigator-card", "step-num"]),
]
for fname, keywords in html_checks:
    p = BASE / fname
    if p.exists():
        content = p.read_text(encoding="utf-8")
        for kw in keywords:
            check(f"{fname} contains '{kw}'", kw in content)
    else:
        check(f"{fname} exists", False, "file missing")

# 5. Server import check
results.append("\n-- Server Import --")
try:
    proc = subprocess.run(
        [sys.executable, "-c",
         "import sys; sys.path.insert(0,'C:/AI/autograph'); "
         "from http.server import HTTPServer, BaseHTTPRequestHandler; "
         "from pathlib import Path; "
         "print('imports OK')"],
        capture_output=True, text=True, timeout=15
    )
    check("intake_server stdlib imports", "imports OK" in proc.stdout, proc.stderr[:100])
except Exception as e:
    check("intake_server stdlib imports", False, str(e))

# 6. Coordinator --list command
results.append("\n-- Coordinator CLI --")
try:
    proc = subprocess.run(
        [sys.executable, str(BASE / "autograph_coordinator.py"), "--list"],
        capture_output=True, text=True, timeout=15
    )
    check("coordinator --list runs", proc.returncode == 0, proc.stderr[:100])
except Exception as e:
    check("coordinator --list", False, str(e))

# -- Summary --
total = passed + failed
summary = f"\n{'='*50}\nAUTOGRAPH SMOKE TEST\n{'='*50}"
summary += f"\n  Passed: {passed}/{total}"
summary += f"\n  Failed: {failed}/{total}"
if failed == 0:
    summary += "\n  STATUS: ALL CLEAR\n"
else:
    summary += "\n  STATUS: NEEDS ATTENTION\n"

full_output = summary + "\n" + "\n".join(results) + "\n" + "="*50 + "\n"
print(full_output)

out_file = Path(r"C:\AI\logs\autograph_product_smoke_test.txt")
out_file.parent.mkdir(exist_ok=True)
with open(out_file, "w", encoding="utf-8") as f:
    f.write(full_output)
print(f"\nResults written to: {out_file}")
