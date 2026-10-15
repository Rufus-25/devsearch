# DevSearch

A full-stack developer directory built with Django. Developers create profiles, list their skills, share projects, review each other's work, and send messages. The project also ships a JWT-secured REST API and a small standalone JavaScript frontend that consumes it.

## Live demo

| | Link |
| --- | --- |
| Web app (Django) | <https://devsearch-yy0r.onrender.com> |
| API demo frontend (static site) | <https://devsearch-frontend.onrender.com> |

> **Good to know:** the demo runs entirely on free hosting tiers. After a period of inactivity the server goes to sleep, so the first request can take up to a minute. Email is disabled in the live demo, so welcome and password-reset emails are not delivered.

<!--
Add screenshots here, for example:
![Home page](docs/home.png)
-->

## Features

- **Developer profiles** with name, headline, bio, location, profile photo, and social links
- **Skills** that developers can add, edit, and remove from their account page
- **Projects** with a title, description, image, demo link, repository link, and tags
- **Reviews and voting**: one up/down vote and comment per user per project, with an automatically calculated vote ratio
- **Search and pagination** for both developers and projects
- **Messaging**: a contact form on every profile and an inbox with read/unread tracking
- **Authentication**: sign-up, login with safe `?next=` redirects, logout, and password reset
- **REST API** with JWT authentication for reading projects and voting
- **Django admin** for managing all data
- **Custom 404 page** and ownership checks so users can only change their own content

## Architecture

```text
Browser
  ├── Django web app   (Render web service: Gunicorn + WhiteNoise)
  │       ├── PostgreSQL        (Neon)
  │       └── Image uploads     (Cloudinary)
  └── API demo frontend (Render static site) ── calls ──▶ Django REST API (JWT)
```

## Tech stack

| Area | Technology |
| --- | --- |
| Backend | Python 3.12, Django 6, Django REST Framework, Simple JWT, django-cors-headers |
| Database | PostgreSQL on Neon in production, SQLite for local development |
| File storage | Cloudinary in production, local `media/` folder for development |
| Static files | WhiteNoise |
| Configuration | django-environ (`.env` file) |
| Web server | Gunicorn |
| Frontend demo | Plain HTML, CSS, and JavaScript modules |
| Hosting | Render (web service and static site) |

## Getting started

### Prerequisites

Python 3.12 or newer, and `git`. The commands below are for PowerShell on Windows; on macOS or Linux, activate the virtual environment with `source .venv/bin/activate` instead.

### 1. Clone and install

```powershell
git clone https://github.com/Rufus-25/devsearch.git
cd devsearch
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell blocks the activation script, call the interpreter directly: `.\.venv\Scripts\python.exe -m pip install -r requirements.txt`.

### 2. Configure environment variables

```powershell
Copy-Item .env.example .env
```

Open `.env` and set at least `SECRET_KEY` and `DEBUG=True`. Generate a secret key with:

```powershell
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

`.env` is ignored by Git. Never commit it.

### 3. Set up the database and run

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open <http://127.0.0.1:8000/> for the site and <http://127.0.0.1:8000/admin/> for the admin. With no `DATABASE_URL`, the project uses a local `db.sqlite3` file, and uploads go to the `media/` folder.

## Environment variables

| Variable | Required | Description |
| --- | --- | --- |
| `SECRET_KEY` | Yes | Django secret key. Use a long random value. |
| `DEBUG` | No (default `False`) | Set to `True` for local development only. |
| `ALLOWED_HOSTS` | No | Comma-separated host names. Defaults to `localhost,127.0.0.1`. |
| `CSRF_TRUSTED_ORIGINS` | No | Comma-separated origins including the scheme, e.g. `https://example.com`. |
| `DATABASE_URL` | No | Postgres connection URL. If empty, SQLite is used. |
| `CLOUDINARY_URL` | No | If set, uploaded images are stored on Cloudinary instead of `media/`. |
| `EMAIL_HOST_USER` | No | SMTP username used for outgoing email in local development. |
| `EMAIL_HOST_PASSWORD` | No | SMTP password (use an app password, not your account password). |
| `RENDER_EXTERNAL_HOSTNAME` | Set by Render | When present, the app adds the host to `ALLOWED_HOSTS` and turns on HTTPS-only cookies and redirects. |

## Running the tests

```powershell
python manage.py test
```

To run one app's tests, name it: `python manage.py test users`, `python manage.py test projects`, or `python manage.py test api`.

The suite covers profile creation, login and safe redirects, ownership checks on skills, messages, and projects, vote calculation, tag removal, form link validation, and the API (public reads, authenticated voting, token issuing, and that no emails are exposed).

## API

Base URL: `https://devsearch-yy0r.onrender.com/api/` (or `http://127.0.0.1:8000/api/` locally).

| Method | Endpoint | Description | Authentication |
| --- | --- | --- | --- |
| `GET` | `/api/` | List available routes | None |
| `GET` | `/api/projects/` | List projects | None |
| `GET` | `/api/projects/<project-id>/` | Get one project by UUID | None |
| `POST` | `/api/projects/<project-id>/vote/` | Create or change your vote (`"up"` or `"down"`) | JWT access token |
| `POST` | `/api/users/token/` | Obtain access and refresh tokens | None |
| `POST` | `/api/users/token/refresh/` | Refresh an access token | None |

Project owners are returned with only their `id`, `name`, `headline`, and `profile_image`. Email addresses are never exposed.

Get a token with your Django username and password:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/users/token/ `
  -H "Content-Type: application/json" `
  -d '{"username":"your-username","password":"your-password"}'
```

Then vote with the `access` token:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/projects/PROJECT_UUID/vote/ `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer ACCESS_TOKEN" `
  -d '{"value":"up"}'
```

## API demo frontend

`devsearch-frontend/` is a separate static client that lists projects, signs in with JWT, and lets you vote. It chooses its API address automatically in `config.js`: the local Django server when opened from `localhost`, and the live backend otherwise.

To run it locally, start Django first, then in a second terminal:

```powershell
python -m http.server 5500 --directory devsearch-frontend
```

Open <http://localhost:5500/>. JavaScript modules do not work from `file://` URLs, so it must be served over HTTP.

## Deployment

The live site follows this setup, all on free tiers:

1. **Neon** provides the PostgreSQL database. Use the direct (non-pooled) connection string as `DATABASE_URL`.
2. **Cloudinary** stores uploaded images. Its `CLOUDINARY_URL` switches the default file storage over automatically.
3. **Render web service** runs the Django app:

   | Setting | Value |
   | --- | --- |
   | Build command | `bash build.sh` |
   | Start command | `python -m gunicorn devsearch.wsgi:application` |
   | Environment | `SECRET_KEY`, `DEBUG=False`, `DATABASE_URL`, `CLOUDINARY_URL` |

   `build.sh` installs dependencies, collects static files for WhiteNoise, and applies migrations. The Python version comes from `.python-version`.
4. **Render static site** serves the frontend demo with root directory `devsearch-frontend`, an empty build command, and publish directory `.`.

Pushing to `main` redeploys both services automatically.

## Project layout

```text
api/                  REST API views, serializers, routes, and tests
devsearch/            Django project settings and root URLs
devsearch-frontend/   Static API demo client
projects/             Projects, reviews, tags, and tests
users/                Profiles, skills, messaging, authentication, and tests
templates/            Shared templates (base layout, 404, delete confirmation)
static/               Source CSS, JavaScript, and images
media/                Local uploads in development (not committed)
build.sh              Render build steps
.python-version       Python version used by Render
manage.py             Django entry point
requirements.txt      Python dependencies
.env.example          Names of the environment variables the app reads
```

## Security notes

- Secrets live in environment variables, never in the repository.
- Users can only edit or delete their own skills and projects, and only read messages they sent or received.
- Redirects after login only go to addresses on the same site.
- Project links are validated as real URLs, and the frontend demo escapes user text before displaying it.
- In production, cookies are HTTPS-only and all HTTP requests are redirected to HTTPS.

## Roadmap

- Real email delivery through an HTTP email provider, since the free host blocks SMTP
- More tests, including the messaging flow and profile editing
- Return a 404 instead of a server error for unknown IDs in the remaining views
- Pagination controls and a nicer loading state in the frontend demo

## Author

Built by Rufus. Find more on GitHub: [Rufus-25](https://github.com/Rufus-25).