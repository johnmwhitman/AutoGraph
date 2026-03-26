# Thumbprint Intake Server
# Serves intake_form.html, accepts POST /submit-intake, relays /chat to Claude API
# Run: python intake_server.py
# Serves on http://localhost:8765

import json
import os
import sys
import time
import subprocess
import threading
from collections import defaultdict
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from urllib.parse import urlparse

BASE_DIR  = Path(__file__).parent
INTAKES   = BASE_DIR / "intakes"
LOG_FILE  = Path(r"C:\AI\logs\autograph_submissions.log")
PORT      = 8765

# Analytics -- import lazily so server still starts if analytics.py is missing
try:
    import sys as _sys
    _sys.path.insert(0, str(BASE_DIR))
    from analytics import log_event as _log_event, hash_ip as _hash_ip
    _ANALYTICS_OK = True
except Exception as _analytics_err:
    print(f"[WARN] analytics.py not loaded: {_analytics_err}")
    _ANALYTICS_OK = False
    def _log_event(*a, **kw): pass
    def _hash_ip(ip): return "unknown"

# Rate limiting: max requests per hour per IP
RATE_LIMIT = 20
_rate_store = defaultdict(list)   # ip -> [timestamps]
_rate_lock  = threading.Lock()


# ---------------------------------------------------------------------------
# API key loader — same three-level pattern as intake_processor.py
# ---------------------------------------------------------------------------
def load_api_key() -> str:
    key = os.environ.get("ANTHROPIC_API_KEY", "").strip()
    if key:
        return key
    try:
        import winreg
        reg_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,
            r"SYSTEM\CurrentControlSet\Control\Session Manager\Environment"
        )
        key, _ = winreg.QueryValueEx(reg_key, "ANTHROPIC_API_KEY")
        winreg.CloseKey(reg_key)
        if key and key.strip():
            return key.strip()
    except Exception:
        pass
    env_path = Path(r"C:\AI\.env")
    if env_path.exists():
        with open(env_path, encoding="utf-8-sig") as f:
            for line in f:
                line = line.strip()
                if line.startswith("ANTHROPIC_API_KEY=") and not line.startswith("ANTHROPIC_API_KEY_"):
                    return line.split("=", 1)[1].strip()
    return ""


# ---------------------------------------------------------------------------
# Rate limiter
# ---------------------------------------------------------------------------
def check_rate_limit(ip: str) -> bool:
    """Returns True if request allowed, False if rate-limited."""
    now = time.time()
    hour_ago = now - 3600
    with _rate_lock:
        _rate_store[ip] = [t for t in _rate_store[ip] if t > hour_ago]
        if len(_rate_store[ip]) >= RATE_LIMIT:
            return False
        _rate_store[ip].append(now)
    return True


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
def log_submission(name: str, email: str, intake_file: str):
    LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] SUBMISSION | name={name} | email={email} | file={intake_file}\n"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(line)
    print(line.strip())


# ---------------------------------------------------------------------------
# Trigger synthesis in background
# ---------------------------------------------------------------------------
def trigger_synthesis(intake_path: str):
    def run():
        processor = BASE_DIR / "intake_processor.py"
        if not processor.exists():
            print(f"[WARN] intake_processor.py not found, skipping synthesis")
            return
        try:
            result = subprocess.run(
                [sys.executable, str(processor), intake_path],
                capture_output=True, text=True, timeout=300
            )
            print(f"[SYNTHESIS] Done for {intake_path}")
            if result.stdout: print(result.stdout[:500])
            if result.stderr: print("[SYNTHESIS ERR]", result.stderr[:200])
        except Exception as e:
            print(f"[SYNTHESIS ERROR] {e}")
    t = threading.Thread(target=run, daemon=True)
    t.start()


# ---------------------------------------------------------------------------
# HTTP Handler
# ---------------------------------------------------------------------------
class AutoGraphHandler(BaseHTTPRequestHandler):

    def log_message(self, fmt, *args):
        print(f"[HTTP] {self.address_string()} {fmt % args}")

    def send_json(self, code: int, data: dict):
        body = json.dumps(data).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Access-Control-Allow-Origin", "*")
        self.end_headers()
        self.wfile.write(body)

    def send_html(self, path: Path):
        content = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(content)))
        self.end_headers()
        self.wfile.write(content)

    def do_OPTIONS(self):
        self.send_response(204)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        parsed = urlparse(self.path)
        path   = parsed.path.rstrip("/") or "/"

        if path in ("/", "/intake"):
            html_file = BASE_DIR / "intake_form.html"
            # Log page view
            ip = self.client_address[0]
            ua = self.headers.get("User-Agent", "")[:60]
            _log_event("page_view", path=path, ip_hash=_hash_ip(ip),
                       user_agent_short=ua.split("/")[0] + "/" + ua.split("/")[1].split(" ")[0] if "/" in ua else ua[:20])
            if html_file.exists():
                self.send_html(html_file)
            else:
                self.send_json(404, {"error": "intake_form.html not found"})

        elif path == "/round2":
            html_file = BASE_DIR / "round2_form.html"
            if html_file.exists():
                self.send_html(html_file)
            else:
                self.send_json(404, {"error": "round2_form.html not found"})

        elif path == "/chat":
            html_file = BASE_DIR / "portrait_chat.html"
            if html_file.exists():
                self.send_html(html_file)
            else:
                self.send_json(404, {"error": "portrait_chat.html not found"})

        else:
            self.send_json(404, {"error": "Not found"})

    def do_POST(self):
        parsed = urlparse(self.path)
        path   = parsed.path.rstrip("/")
        length = int(self.headers.get("Content-Length", 0))
        body   = self.rfile.read(length)
        ip     = self.client_address[0]

        try:
            data = json.loads(body)
        except Exception:
            self.send_json(400, {"error": "Invalid JSON"}); return

        # ---- POST /submit-intake ----
        if path == "/submit-intake":
            name  = data.get("name", "unknown").strip()
            email = data.get("email", "").strip()
            ts    = datetime.now().strftime("%Y%m%d_%H%M%S")
            slug  = name.lower().replace(" ", "_")[:30]
            INTAKES.mkdir(exist_ok=True)
            out_file = INTAKES / f"{slug}_{ts}.json"

            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            log_submission(name, email, str(out_file))
            trigger_synthesis(str(out_file))
            _log_event("portrait_delivered", client_slug=slug, tier="standard", round=int(data.get("round", 1)))
            self.send_json(200, {"status": "ok", "message": "Intake received", "file": out_file.name})

        # ---- POST /chat ----
        elif path == "/chat":
            if not check_rate_limit(ip):
                self.send_json(429, {"error": "Rate limit exceeded. Try again later."}); return

            portrait = data.get("portrait", "").strip()
            messages = data.get("messages", [])

            if not portrait:
                self.send_json(400, {"error": "portrait field required"}); return
            if not messages:
                self.send_json(400, {"error": "messages field required"}); return

            api_key = load_api_key()
            if not api_key:
                self.send_json(500, {"error": "API key not configured on server"}); return

            system_prompt = (
                "You are the Thumbprint Portrait Navigator.\n\n"
                "You have the user's behavioral portrait below. It contains specific findings about "
                "their cognitive patterns, decision style, signature behaviors, tensions, and blind spots.\n\n"
                "Your job: help them navigate and apply their portrait.\n\n"
                "Rules:\n"
                "- Always ground responses in specific portrait findings\n"
                "- Reference their actual evidence when relevant\n"
                "- Help them apply the portrait to real situations they describe\n"
                "- Do NOT add new assessments beyond what the portrait established\n"
                "- Do NOT soften the blind spot findings — they were written accurately\n"
                "- You are a navigator, not a therapist. Be direct and specific.\n"
                "- Short responses are fine. Portrait-grounded always.\n\n"
                f"THE PORTRAIT:\n\n{portrait}"
            )

            try:
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                response = client.messages.create(
                    model="claude-sonnet-4-6",
                    max_tokens=1024,
                    system=system_prompt,
                    messages=messages
                )
                reply = response.content[0].text
                self.send_json(200, {"reply": reply})
            except Exception as e:
                self.send_json(500, {"error": f"API error: {str(e)}"})

        else:
            self.send_json(404, {"error": "Not found"})


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    api_key = load_api_key()
    if api_key:
        print(f"[OK] API key loaded ({api_key[:8]}...)")
    else:
        print("[WARN] No ANTHROPIC_API_KEY found — /chat endpoint will fail")

    server = HTTPServer(("0.0.0.0", PORT), AutoGraphHandler)
    print(f"Thumbprint server running on http://localhost:{PORT}")
    print(f"  GET  /          -> intake_form.html")
    print(f"  GET  /round2    -> round2_form.html")
    print(f"  GET  /chat      -> portrait_chat.html")
    print(f"  POST /submit-intake -> saves intake JSON, triggers synthesis")
    print(f"  POST /chat          -> Portrait Navigator API relay")
    print(f"  Intakes dir: {INTAKES}")
    print(f"  Log: {LOG_FILE}")
    print("Press Ctrl+C to stop.\n")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")
