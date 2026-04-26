# PythonAnywhere Deployment

This project is prepared to run on PythonAnywhere free hosting.

## What you get

- Public website on `yourusername.pythonanywhere.com`
- Private admin panel at `/admin/login`
- Flask backend kept intact
- SQLite database stored in your PythonAnywhere home directory

## Important limits

- Free PythonAnywhere accounts currently include 1 web app and 512 MiB disk space.
- Free accounts currently expire after 1 month.
- Free accounts use the `pythonanywhere.com` subdomain only.

Official docs:

- https://help.pythonanywhere.com/pages/FreeAccountsFeatures/
- https://help.pythonanywhere.com/pages/WebAppBasics/
- https://help.pythonanywhere.com/pages/Flask

## Exact setup

1. Create a free PythonAnywhere account.
2. Open a Bash console.
3. Clone the repository:

   ```bash
   git clone https://github.com/zebandrecergiol-cpu/Briticana.app.git ~/briticana-app
   ```

4. Create a virtualenv:

   ```bash
   mkvirtualenv --python=/usr/bin/python3.13 briticana-venv
   workon briticana-venv
   pip install -r ~/briticana-app/requirements.txt
   ```

5. Create folders for persistent app data:

   ```bash
   mkdir -p ~/briticana-data/uploads
   ```

6. Copy the local starter database from the repo into your data folder:

   ```bash
   cp ~/briticana-app/briticana.db ~/briticana-data/briticana.db
   ```

7. Go to the `Web` tab.
8. Click `Add a new web app`.
9. Choose your free `yourusername.pythonanywhere.com` domain.
10. Choose `Manual configuration`.
11. Choose `Python 3.13`.
12. In the `Virtualenv` field, enter:

   ```text
   /home/YOUR_USERNAME/.virtualenvs/briticana-venv
   ```

13. Open the WSGI configuration file from the `Web` tab.
14. Replace its contents with the file in this repo:

   - `pythonanywhere_wsgi.py`

15. Replace every `YOUR_USERNAME` in that file with your real PythonAnywhere username.
16. Set stronger values in that WSGI file for:

   - `SECRET_KEY`
   - `ADMIN_USERNAME`
   - `ADMIN_PASSWORD`
   - `ADMIN_URL_PREFIX`

17. Keep `ADMIN_URL_PREFIX` private, for example:

   ```text
   /briticana-control-room
   ```

18. In the `Files` tab or Bash console, keep a note of that private admin path for yourself only.
17. Reload the web app from the `Web` tab.

## After setup

- Public website:
  - `https://yourusername.pythonanywhere.com/`
- Admin login:
  - `https://yourusername.pythonanywhere.com/YOUR_PRIVATE_PREFIX/login`

## When you edit code later

1. Push changes to GitHub from your computer.
2. In PythonAnywhere Bash console:

   ```bash
   cd ~/briticana-app
   git pull
   workon briticana-venv
   pip install -r requirements.txt
   ```

3. Reload the web app from the `Web` tab.

## Best practice for images on free hosting

- Text edits and product/domain changes can stay in SQLite.
- Uploaded files count toward your 512 MiB quota.
- Prefer image URLs when possible for hero images and product images.
- Health-check URL:
  - `https://yourusername.pythonanywhere.com/health`
