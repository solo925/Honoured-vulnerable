# Django Security Lab

A deliberately vulnerable Django application for learning web security concepts in a **controlled, local environment**.

> ⚠️ **WARNING: This application is intentionally insecure. Never deploy it on a public server or expose it to the internet.**

---

## Vulnerability Index

| Code  | Category                  | Location                              | Payload / Test                                           |
|-------|---------------------------|---------------------------------------|----------------------------------------------------------|
| V-01  | Debug Mode ON             | `config/settings.py`                  | Any error page leaks stack trace + SQL                   |
| V-02  | Hardcoded Secret Key      | `config/settings.py`                  | Forge sessions/CSRF tokens with the key                  |
| V-03  | Wildcard ALLOWED_HOSTS    | `config/settings.py`                  | Host header injection                                    |
| V-04  | No Password Requirements  | `config/settings.py`                  | Register with password `a` or empty                      |
| V-05  | Clickjacking (no X-Frame) | `config/settings.py`                  | Embed in iframe on attacker site                         |
| V-06  | Insecure Cookies          | `config/settings.py`                  | SESSION_COOKIE_SECURE=False                              |
| V-07  | Unprotected Media Files   | `config/urls.py`                      | Direct URL access to any upload                          |
| V-08  | SQL Injection             | `accounts/views.py – login_view`      | Username: `admin'--`  Password: `anything`               |
| V-09  | Username Enumeration      | `accounts/views.py`                   | Error differs for "no user" vs "wrong password"          |
| V-10  | Weak Password Reset Token | `accounts/views.py`                   | Token = base64(username) — trivially guessable           |
| V-11  | No Rate Limiting          | `accounts/views.py`                   | Unlimited login attempts                                 |
| V-12  | Registration Enumeration  | `accounts/views.py – register_view`   | Error reveals if username is taken                       |
| V-13  | Stored XSS                | `profiles/views.py` + template        | Bio: `<script>alert(document.cookie)</script>`           |
| V-14  | IDOR (profiles)           | `profiles/views.py`                   | `/profiles/view/?user_id=1`                              |
| V-15  | Unrestricted File Upload  | `profiles/views.py`                   | Upload `.html`, `.php`, `.exe` as avatar                 |
| V-16  | Stored XSS (feedback)     | `feedback/views.py` + wall template   | Message: `<img src=x onerror=alert(1)>`                  |
| V-17  | CSRF Disabled             | `feedback/views.py – submit_feedback` | `@csrf_exempt` — any site can POST                       |
| V-18  | Reflected XSS             | `feedback/views.py – feedback_search` | `/feedback/search/?q=<script>alert(1)</script>`          |
| V-19  | No Input Validation       | `feedback/views.py`                   | No length limits, no sanitisation                        |
| V-20  | Unrestricted Upload       | `documents/views.py`                  | Upload `.html` → browse `/media/documents/file.html`     |
| V-21  | Path Traversal            | `documents/views.py – download`       | `?file=../../config/settings.py`                         |
| V-22  | IDOR (documents)          | `documents/views.py – download`       | `/documents/download/1/` (any user, any doc)             |
| V-23  | Insecure File Read        | `documents/views.py`                  | open() with user-controlled path                         |
| V-24  | SSRF                      | `dashboard/views.py – url_preview`    | `http://127.0.0.1:8000/dashboard/debug/`                 |
| V-25  | Command Injection         | `dashboard/views.py – ping_host`      | `127.0.0.1; id` or `127.0.0.1; cat /etc/passwd`         |
| V-26  | XXE                       | `dashboard/views.py – xml_import`     | DOCTYPE with `SYSTEM "file:///etc/passwd"`               |
| V-27  | Insecure Deserialization  | `dashboard/views.py – deserialize`    | Malicious pickle payload (see template for generator)    |
| V-28  | Sensitive Data in GET     | `dashboard/views.py`                  | Search terms in URL → appear in server logs              |
| V-29  | Debug Info Endpoint       | `dashboard/views.py – debug_info`     | `/dashboard/debug/` dumps SECRET_KEY + env               |

---

## Quick Start

```bash
# 1. Clone / extract the project
cd django-security-lab

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Apply migrations
python manage.py makemigrations accounts profiles feedback documents dashboard
python manage.py migrate

# 5. Create a superuser
python manage.py createsuperuser

# 6. Run the dev server
python manage.py runserver

# 7. (Optional) Start the listener in a second terminal
cd ../listener
pip install flask
python listener.py
```

Visit **http://127.0.0.1:8000/accounts/login/**

---

## Module Walkthroughs

### SQL Injection (V-08)
1. Go to `/accounts/login/`
2. Enter username `admin'--` with any password
3. You are logged in as admin without knowing the password

### Stored XSS (V-13)
1. Log in, go to `/profiles/edit/`
2. Enter `<script>alert(document.cookie)</script>` in the Bio field
3. Visit `/profiles/view/` — the script executes

### SSRF (V-24)
1. Go to `/dashboard/url-preview/`
2. Enter `http://127.0.0.1:8000/dashboard/debug/`
3. The server fetches its own internal debug page and returns it to you

### Command Injection (V-25)
1. Go to `/dashboard/ping/`
2. Enter `127.0.0.1; cat /etc/passwd`
3. The contents of /etc/passwd are returned in the output

### Path Traversal (V-21)
1. Upload any document at `/documents/upload/`
2. Note its ID (e.g. `1`)
3. Visit `/documents/download/1/?file=../../config/settings.py`
4. `settings.py` (including SECRET_KEY) is downloaded

### Insecure Deserialization (V-27)
1. In a separate Python shell, generate the payload shown in the template
2. Go to `/dashboard/deserialize/`
3. Paste the base64 payload and submit
4. The command executes on the server

---

## Fix-It Exercises

After studying each vulnerability, try implementing the fix:

- **SQL injection** → use `cursor.execute(query, [username, password])` with parameterised queries
- **XSS** → remove `|safe`; use `{{ var }}` (auto-escaped) or `bleach.clean()`
- **IDOR** → add `owner=request.user` filter on every queryset
- **Path traversal** → use `os.path.realpath()` and assert the result starts with `MEDIA_ROOT`
- **SSRF** → validate URL scheme, resolve hostname, block RFC-1918 ranges
- **Command injection** → pass args as a list, never use `shell=True`
- **Pickle** → replace with `json.loads()` or `msgpack`
- **File upload** → check `python-magic` MIME type and whitelist allowed types
- **CSRF** → remove `@csrf_exempt`; always include `{% csrf_token %}`
- **Weak tokens** → use `secrets.token_urlsafe(32)` stored server-side with expiry
