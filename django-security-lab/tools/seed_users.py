"""tools/seed_users.py
Create a superuser and a couple of test accounts for the lab.

Run this with the project's Python interpreter:
  & c:/Honoured-vulnerable/.venv/Scripts/python.exe tools/seed_users.py

This script is idempotent and will not overwrite existing users.
"""
import os
import sys

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, BASE_DIR)
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django
django.setup()

from accounts.models import User


def create_user_if_missing(username, password, is_super=False):
    if User.objects.filter(username=username).exists():
        print(f"User exists: {username}")
        return
    if is_super:
        User.objects.create_superuser(username=username, email=f"{username}@example.com", password=password)
        print(f"Created superuser: {username}")
    else:
        User.objects.create_user(username=username, password=password, email=f"{username}@example.com")
        print(f"Created user: {username}")


if __name__ == "__main__":
    create_user_if_missing("admin", "adminpass", is_super=True)
    create_user_if_missing("alice", "alicepass")
    create_user_if_missing("bob", "bobpass")

    print("Current users:")
    for u in User.objects.all().order_by("id"):
        print(f" - {u.username} (id={u.id})")
