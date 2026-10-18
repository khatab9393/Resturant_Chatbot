"""Restaurant chatbot server. Python 3 standard library only.
Run:  python server.py   then open http://localhost:8000
"""
import json, os, urllib.request
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
MODEL = os.getenv("MODEL", "qwen2.5:7b")   # any Qwen model you pulled with `ollama pull`
HERE = os.path.dirname(os.path.abspath(__file__))

def build_system_prompt():
    # Re-read every request so you can edit menu.json without restarting.
    with open(os.path.join(HERE, "menu.json"), encoding="utf-8") as f:
        menu = json.load(f)
    return (
        f"You are the friendly assistant of the restaurant {menu['restaurant']}. "
        "Answer ONLY using the restaurant data below. "
        "If something is not in the data (an item, price, ingredient, allergen), say you don't know "
        "and suggest asking the staff. Never invent dishes or prices. "
        "Keep answers short and reply in the same language the customer uses.\n\n"
        "RESTAURANT DATA:\n" + json.dumps(menu, ensure_ascii=False, indent=1)
    )

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path in ("/", "/index.html"):
            body = open(os.path.join(HERE, "index.html"), "rb").read()
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_error(404)

    def do_POST(self):
        if self.path != "/api/chat":
            return self.send_error(404)
        length = int(self.headers.get("Content-Length", 0))
        history = json.loads(self.rfile.read(length))["messages"][-20:]  # keep last 20 turns
        payload = {
            "model": MODEL,
            "stream": True,
            "think": False,  # stops Qwen3 from printing its reasoning
            "messages": [{"role": "system", "content": build_system_prompt()}] + history,
            "options": {"temperature": 0.3},
        }
        req = urllib.request.Request(
            OLLAMA_URL + "/api/chat", json.dumps(payload).encode(),
            {"Content-Type": "application/json"})
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        try:
            with urllib.request.urlopen(req) as resp:
                for line in resp:  # Ollama streams one JSON object per line
                    chunk = json.loads(line)
                    text = chunk.get("message", {}).get("content", "")
                    if text:
                        self.wfile.write(text.encode("utf-8"))
                        self.wfile.flush()
        except Exception as e:
            self.wfile.write(f"[Error talking to Ollama: {e}. Is it running and is the model pulled?]".encode())

if __name__ == "__main__":
    print(f"Using model {MODEL} at {OLLAMA_URL}")
    print("Open http://localhost:8000")
    ThreadingHTTPServer(("0.0.0.0", 8000), Handler).serve_forever()
