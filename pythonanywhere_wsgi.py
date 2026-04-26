"""
PythonAnywhere WSGI entrypoint template for this project.

Copy the contents of this file into your PythonAnywhere WSGI config file and
replace YOUR_USERNAME with your real PythonAnywhere username.
"""

import os
import sys


project_home = "/home/YOUR_USERNAME/briticana-app"
if project_home not in sys.path:
    sys.path.insert(0, project_home)

# Keep secrets and the SQLite database inside your PythonAnywhere home folder.
os.environ.setdefault("SECRET_KEY", "change-this-on-pythonanywhere")
os.environ.setdefault("ADMIN_USERNAME", "admin")
os.environ.setdefault("ADMIN_PASSWORD", "admin123")
os.environ.setdefault("ADMIN_URL_PREFIX", "/secure-admin")
os.environ.setdefault("SQLITE_PATH", "/home/YOUR_USERNAME/briticana-data/briticana.db")
os.environ.setdefault("UPLOAD_FOLDER", "/home/YOUR_USERNAME/briticana-data/uploads")
os.environ.setdefault("PYTHONANYWHERE_SITE", "true")

from app import app as application
