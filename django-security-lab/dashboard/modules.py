"""dashboard/views.py – replace the dashboard_home function only"""

# The full file is in dashboard/views.py; this patch adds the modules list
# to the context so the home template can render the card grid.

# Paste this replacement into the dashboard_home function in views.py:
#
# MODULES = [
#     {"icon": "💉", "name": "SQL Injection",        "url": "/accounts/login/",      "vuln": "V-08: Raw SQL login"},
#     {"icon": "📝", "name": "Stored XSS",           "url": "/profiles/edit/",       "vuln": "V-13: Bio rendered with |safe"},
#     {"icon": "🔍", "name": "Reflected XSS",        "url": "/feedback/search/",     "vuln": "V-18: ?q= echoed unescaped"},
#     {"icon": "🙈", "name": "IDOR",                 "url": "/profiles/view/",       "vuln": "V-14: Any user_id accessible"},
#     {"icon": "📂", "name": "Path Traversal",       "url": "/documents/list/",      "vuln": "V-21: ?file=../../ in download"},
#     {"icon": "🌐", "name": "SSRF",                 "url": "/dashboard/url-preview/","vuln": "V-24: Fetches any internal URL"},
#     {"icon": "📡", "name": "Command Injection",    "url": "/dashboard/ping/",      "vuln": "V-25: shell=True + user input"},
#     {"icon": "📄", "name": "XXE",                  "url": "/dashboard/xml-import/","vuln": "V-26: External entity in XML"},
#     {"icon": "☣️", "name": "Insecure Deserialize", "url": "/dashboard/deserialize/","vuln": "V-27: pickle.loads user data"},
#     {"icon": "🐛", "name": "Debug Endpoint",       "url": "/dashboard/debug/",     "vuln": "V-29: Dumps secrets/env vars"},
# ]
