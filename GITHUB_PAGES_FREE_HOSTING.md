# GitHub Pages Free Hosting

This project now supports a free-hosted public site by exporting the public pages to `docs/`.

## How it works

- Your Flask admin panel stays local and private.
- The public website is exported as a static site.
- The exported files go into `docs/`.
- GitHub Pages can publish `docs/` for free.
- Your purchased domain can later point to GitHub Pages.

## Your editing workflow

1. Run the Flask admin locally.
2. Make your content changes in the admin panel.
3. Click `Export Static Site` in the admin header.
4. Commit and push the updated files to GitHub.
5. GitHub Pages serves the updated public site.

## What exports

- homepage
- domain pages
- product detail pages
- verification page
- certificate pages
- static assets
- certificate verification JSON data

## What stays local

- the admin panel
- direct database editing
- student login/dashboard features

## GitHub Pages setup

1. In your GitHub repo, open `Settings` -> `Pages`.
2. Under `Build and deployment`, choose `Deploy from a branch`.
3. Select branch `main`.
4. Select folder `/docs`.
5. Save.

After that, GitHub Pages will publish the static export in `docs/`.

## Custom domain later

GitHub Pages supports custom domains. When you are ready:

1. Open `Settings` -> `Pages`.
2. Add your purchased domain.
3. Update DNS records at your domain provider as GitHub instructs.

## Important note

The public hosted site is static. If you change content in the admin panel, you must export again and push the changed files to GitHub.

## Helpful commands

Export manually from the terminal:

```powershell
.\venv\Scripts\python.exe export_static.py
```
