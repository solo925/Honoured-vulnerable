"""tools/test_vulns.py
Log in as `admin` and exercise three vulnerable endpoints:
 - /dashboard/url-preview/   (SSRF)        : posts a URL and prints fetched result
 - /dashboard/xml-import/    (XXE/demo)    : uploads an XML file and prints response
 - /dashboard/deserialize/   (pickle)      : posts a base64 pickle and prints output

Run with:
  & c:/Honoured-vulnerable/.venv/Scripts/python.exe tools/test_vulns.py
"""
import re
import sys
import base64
import pickle
import urllib.request
import urllib.parse
import http.cookiejar

BASE = 'http://127.0.0.1:8000'

def make_opener():
    cj = http.cookiejar.CookieJar()
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def login(opener, username='admin', password='adminpass'):
    # Use the admin login page (works around an issue in the custom accounts login)
    login_url = BASE + '/admin/login/'
    resp = opener.open(login_url)
    html = resp.read().decode('utf-8', errors='replace')
    m = re.search(r'name=["\']csrfmiddlewaretoken["\']\s+value=["\']([^"\']+)["\']', html)
    token = m.group(1) if m else ''

    data = urllib.parse.urlencode({
        'username': username,
        'password': password,
        'csrfmiddlewaretoken': token,
        'next': '/admin/'
    }).encode()
    req = urllib.request.Request(login_url, data=data, headers={'Referer': login_url, 'Content-Type': 'application/x-www-form-urlencoded'})
    try:
        r = opener.open(req)
        print('Admin login POST ->', r.getcode(), '->', r.geturl())
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        fname = 'tools/login_500.html'
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(body)
        print('Admin login POST HTTPError', e.code)
        print('Saved full response to', fname)
        print('Response snippet:\n', body[:4000])
        raise

def test_ssrf(opener):
    print('\n== SSRF test: fetch admin page via server ==')
    url_preview = BASE + '/dashboard/url-preview/'
    # GET to obtain CSRF token
    r = opener.open(url_preview)
    html = r.read().decode('utf-8', errors='replace')
    m = re.search(r'name=["\']csrfmiddlewaretoken["\']\s+value=["\']([^"\']+)["\']', html)
    token = m.group(1) if m else ''

    target = BASE + '/admin/'
    data = urllib.parse.urlencode({'url': target, 'csrfmiddlewaretoken': token}).encode()
    req = urllib.request.Request(url_preview, data=data, headers={'Referer': url_preview, 'Content-Type': 'application/x-www-form-urlencoded'})
    r2 = opener.open(req)
    body = r2.read().decode('utf-8', errors='replace')
    print('Fetched content snippet:\n', body[:800])


def test_ssrf_exfiltrate(opener):
    print('\n== SSRF exfiltration test: fetch listener endpoint ==')
    url_preview = BASE + '/dashboard/url-preview/'
    # Get CSRF token
    r = opener.open(url_preview)
    html = r.read().decode('utf-8', errors='replace')
    m = re.search(r'name=["\']csrfmiddlewaretoken["\']\s+value=["\']([^"\']+)["\']', html)
    token = m.group(1) if m else ''

    # Target the local listener (we run it on 8081) which should respond with 'received\n'
    target = 'http://127.0.0.1:8081/?ssrf=test'
    data = urllib.parse.urlencode({'url': target, 'csrfmiddlewaretoken': token}).encode()
    req = urllib.request.Request(url_preview, data=data, headers={'Referer': url_preview, 'Content-Type': 'application/x-www-form-urlencoded'})
    r2 = opener.open(req)
    body = r2.read().decode('utf-8', errors='replace')
    print('Listener fetch result snippet:\n', body[:400])

def multipart_file(fieldname, filename, content, boundary=None):
    if boundary is None:
        boundary = '----WebKitFormBoundaryTest'
    lines = []
    lines.append(f'--{boundary}')
    lines.append(f'Content-Disposition: form-data; name="{fieldname}"; filename="{filename}"')
    lines.append('Content-Type: application/xml')
    lines.append('')
    lines.append(content)
    lines.append(f'--{boundary}--')
    body = '\r\n'.join(lines).encode('utf-8')
    content_type = f'multipart/form-data; boundary={boundary}'
    return content_type, body

def test_xxe(opener):
    print('\n== XXE test: upload simple XML to import customers ==')
    xml_import = BASE + '/dashboard/xml-import/'
    # Simple XML (won't trigger real XXE here; demonstrates import flow)
    xml = '''<?xml version="1.0"?>
<customers>
  <customer>
    <name>VulnTester</name>
    <email>vuln@example.com</email>
  </customer>
</customers>'''
    content_type, body = multipart_file('xmlfile', 'test.xml', xml)
    req = urllib.request.Request(xml_import, data=body, headers={'Content-Type': content_type})
    try:
        r = opener.open(req)
        print('Upload response status:', r.getcode())
        print('Response snippet:\n', r.read().decode('utf-8', errors='replace')[:800])
    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        fname = 'tools/xml_500.html'
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(body)
        print('XML import HTTPError', e.code)
        print('Saved full response to', fname)
        print('Response snippet:\n', body[:2000])
        raise

def test_deserialize():
    print('\n== Deserialization test: safe pickle payload ==')
    url = BASE + '/dashboard/deserialize/'
    payload = base64.b64encode(pickle.dumps({'ok': True})).decode()
    data = urllib.parse.urlencode({'data': payload}).encode()
    req = urllib.request.Request(url, data=data, headers={'Content-Type': 'application/x-www-form-urlencoded'})
    r = urllib.request.urlopen(req)
    print('Deserialise response status:', r.getcode())
    print('Response body:\n', r.read().decode('utf-8', errors='replace')[:800])

def main():
    opener = make_opener()
    login(opener)
    test_ssrf(opener)
    test_ssrf_exfiltrate(opener)
    test_xxe(opener)
    test_deserialize()

if __name__ == '__main__':
    main()
