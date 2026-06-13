"""tools/test_admin_login.py
Attempt to log into the Django admin with the seeded `admin` user and
print the resulting admin index HTML snippet to verify access.

Run with the project's Python interpreter:
  & c:/Honoured-vulnerable/.venv/Scripts/python.exe tools/test_admin_login.py
"""
import re
import sys
import urllib.request
import urllib.parse
import http.cookiejar

BASE = 'http://127.0.0.1:8000'
LOGIN_URL = BASE + '/admin/login/'
ADMIN_URL = BASE + '/admin/'

def main():
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

    # GET login page to receive csrf cookie and token
    resp = opener.open(LOGIN_URL)
    html = resp.read().decode('utf-8', errors='replace')
    m = re.search(r'name=["\']csrfmiddlewaretoken["\']\s+value=["\']([^"\']+)["\']', html)
    if not m:
        print('CSRF token not found on login page')
        sys.exit(1)
    token = m.group(1)

    data = urllib.parse.urlencode({
        'username': 'admin',
        'password': 'adminpass',
        'csrfmiddlewaretoken': token,
        'next': '/admin/'
    }).encode()

    req = urllib.request.Request(LOGIN_URL, data=data, headers={
        'Referer': LOGIN_URL,
        'Content-Type': 'application/x-www-form-urlencoded'
    })
    resp2 = opener.open(req)
    print('POST to login returned:', resp2.getcode(), '->', resp2.geturl())

    # Fetch admin index
    resp3 = opener.open(ADMIN_URL)
    html3 = resp3.read().decode('utf-8', errors='replace')
    print('\n--- Admin page snippet ---')
    print(html3[:1200])

if __name__ == '__main__':
    main()
