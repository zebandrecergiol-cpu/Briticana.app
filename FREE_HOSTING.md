# Free Hosting Guide

This project is prepared for a free Render deployment without a custom domain.

## Why not GitHub Pages?

GitHub Pages only hosts static HTML, CSS, and JavaScript. This project uses Flask, a database, sessions, and a private admin panel, so it needs a Python web server.

## Recommended free setup

- Host the app as a free Render web service
- Use the free Render Postgres database defined in `render.yaml`
- Use the default `onrender.com` URL
- In the admin panel, prefer direct image URLs instead of file uploads

## Deploy steps

1. Open Render.
2. Click `New` -> `Blueprint`.
3. Connect the GitHub repository.
4. Select this repo.
5. Render will read `render.yaml`.
6. Enter values for:
   - `ADMIN_USERNAME`
   - `ADMIN_PASSWORD`
7. Create the Blueprint.

## After deploy

- Your public site will get an `onrender.com` link.
- Your admin panel will be available at `/admin/login`.
- On the first deploy, the app will try to copy your current SQLite content into the hosted database automatically.

## Free plan limits

- Free web services spin down after inactivity.
- The site can take some time to wake up on the next visit.
- Uploaded files on the app's local filesystem are not reliable on free hosting.
- Free Render Postgres databases expire after 30 days unless upgraded.

## Best practice for admin edits

- Text edits, products, domains, and admin-managed settings should be stored in the database.
- For images, paste hosted image URLs when possible.
- Avoid depending on local file uploads for important production assets on free hosting.
