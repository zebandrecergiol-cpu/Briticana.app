# Koyeb Free Hosting

This project is prepared to run on Koyeb using:

- a free web service
- a free PostgreSQL database
- an optional custom domain later

## Why Koyeb for this project

Koyeb officially documents:

- free app instances
- free PostgreSQL database instances
- custom domains with automatic TLS

That makes it a stronger fit for this Flask app than static hosting services.

## What the app is ready for

- `Procfile` starts the app with Gunicorn
- `app.py` supports `DATABASE_URL`
- `app.py` supports a private `ADMIN_URL_PREFIX`
- `app.py` includes `/health`
- first deploy can seed data from the included SQLite database

## Koyeb settings to use

### Web service

- Builder: `Buildpack`
- Run command: use the repository `Procfile`
- Port: let Koyeb inject `PORT`

### Environment variables

Set these in Koyeb:

- `SECRET_KEY`
- `ADMIN_USERNAME`
- `ADMIN_PASSWORD`
- `ADMIN_URL_PREFIX`
- `DATABASE_URL` from your Koyeb Postgres database connection string

Suggested admin path example:

```text
/briticana-control-room
```

## Free database

Create a Koyeb PostgreSQL database service with the free instance type and copy its connection string into the web service `DATABASE_URL`.

## Public URLs

Without your own domain:

- `https://your-app-name-your-org-hash.koyeb.app`

With your purchased domain later:

- `https://www.briticana.com`

For apex domains, Koyeb recommends serving `www.yourdomain.com` and redirecting the apex domain to it with your DNS provider.

## Best practice on free hosting

- Keep text, products, domains, and settings in the database
- Prefer direct image URLs where possible
- Keep your admin path private
- Keep your admin password strong

## Health check

Use:

```text
/health
```

## Official docs

- Flask on Koyeb: https://www.koyeb.com/docs/deploy/flask
- Deploy with GitHub: https://www.koyeb.com/docs/build-and-deploy/deploy-with-git
- Procfile support: https://www.koyeb.com/docs/build-and-deploy/build-from-git
- Custom domains: https://www.koyeb.com/docs/run-and-scale/domains
- Koyeb databases: https://www.koyeb.com/docs/databases
