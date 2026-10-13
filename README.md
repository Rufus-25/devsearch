# DevSearch

DevSearch is a Django web application for discovering developer profiles and projects. Users can create profiles, share projects, add skills, and contact other developers. The repository also includes a Django REST Framework API and a small standalone frontend that demonstrates how to call it.

## Features

- Developer profiles with skills and social links
- Project listings with tags, images, demo links, and repository links
- Project reviews and up/down voting
- User messaging and an inbox
- REST API for listing and retrieving projects, voting, and JWT authentication
- Django admin for managing application data

## Tech stack

- Python 3.12 or newer
- Django 6
- Django REST Framework
- Simple JWT
- SQLite (default database)

## Getting started

### Prerequisites

Install Python 3.12 or newer and make sure `python` and `pip` are available in PowerShell.

### Install dependencies

From the repository root, create and activate a virtual environment, then install the requirements:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell prevents activation, run the commands using the virtual environment's interpreter directly:

```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### Configure environment variables

Copy the example environment file to `.env`:

```powershell
Copy-Item .env.example .env
```

Set values in `.env`:

```dotenv
SECRET_KEY=replace-with-a-long-random-secret
DEBUG=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-app-password
```

The email credentials are read by Django's SMTP email backend, which is used for password-reset emails. Keep `.env` private; it is excluded from Git. Do not use `DEBUG=True` or a development secret key in production.

### Initialize and run the application

```powershell
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) to use the web application. The admin is available at [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/).

The project uses SQLite by default and creates `db.sqlite3` in the repository root. Uploaded media is stored in `media/` during development.

## API

The API base URL for local development is `http://127.0.0.1:8000/api/`.

| Method | Endpoint | Description | Authentication |
| --- | --- | --- | --- |
| `GET` | `/api/` | List available API routes | No |
| `GET` | `/api/projects/` | List projects | No |
| `GET` | `/api/projects/<project-id>/` | Get a project by UUID | No |
| `POST` | `/api/projects/<project-id>/vote/` | Create or update the current user's vote | JWT access token |
| `POST` | `/api/users/token/` | Obtain an access and refresh token | No |
| `POST` | `/api/users/token/refresh/` | Refresh an access token | No |

Obtain a token by posting the user's Django username and password:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/users/token/ `
  -H "Content-Type: application/json" `
  -d '{"username":"your-username","password":"your-password"}'
```

The token response contains `access` and `refresh` values. Send the access token as a Bearer token when voting; the request body accepts `"up"` or `"down"`:

```powershell
curl.exe -X POST http://127.0.0.1:8000/api/projects/PROJECT_UUID/vote/ `
  -H "Content-Type: application/json" `
  -H "Authorization: Bearer ACCESS_TOKEN" `
  -d '{"value":"up"}'
```

Replace `PROJECT_UUID` and `ACCESS_TOKEN` with values from the API and token response.

## Optional API demo frontend

`devsearch-frontend/` contains a plain HTML/CSS/JavaScript client used to demonstrate the API. It is separate from the Django application and is not required to run the site. Its API URL is configured in `devsearch-frontend/config.js` and defaults to `http://127.0.0.1:8000`.

Run the Django server first, then serve the frontend directory over HTTP. Browser JavaScript modules do not work when opening the HTML files directly with a `file://` URL.

In a second PowerShell window, from the repository root:

```powershell
python -m http.server 5500 --directory devsearch-frontend
```

Open [http://localhost:5500/login.html](http://localhost:5500/login.html) to sign in to the API demo. The demo uses the same username and password as the Django application.

## Project layout

```text
api/                  REST API views, serializers, and routes
devsearch/            Django project configuration
devsearch-frontend/   Optional static API demo client
projects/             Project, review, and tag functionality
users/                Profiles, skills, messaging, and authentication
templates/             Shared Django templates
static/               Source static assets
media/                Development uploads (created/used at runtime)
manage.py             Django management entry point
requirements.txt      Python dependencies
```
