"""Delete the project's SQLite database file (dev helper).
Run with the virtualenv Python to avoid shell restrictions.
"""
import pathlib

DB = pathlib.Path(r"c:\Honoured-vulnerable\django-security-lab\db.sqlite3")
if DB.exists():
    DB.unlink()
    print("Deleted:", DB)
else:
    print("No DB file found at", DB)
