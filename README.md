
**Project Overview**
- **Name**: ecommerce — a Django-based API project providing user accounts, JWT authentication, email OTPs, and background tasks.
- **Purpose**: Serves as a starter e‑commerce backend with account management, async tasks (Celery), and media storage via Cloudinary.

**Features**
- **Authentication**: JWT-based access + refresh tokens with cookie support.
- **Background jobs**: Celery workers and periodic tasks (django-celery-beat).
- **Media storage**: Cloudinary integration for media uploads.
- **Admin UI**: Jazzmin-enhanced Django admin.

**Tech Stack & Tools**
- **Language**: Python (project metadata lists >=3.12; Dockerfile uses Python 3.11).
- **Framework**: Django 6, Django REST Framework.
- **Async / Tasks**: Celery, django-celery-beat, Redis as broker/result backend.
- **Storage**: Cloudinary (via django-cloudinary-storage).
- **Auth**: djangorestframework-simplejwt and a custom cookie middleware.
- **Containerization**: Docker + Docker Compose (optional).

**Repository Layout (key files)**
- **`manage.py`**: Django CLI entrypoint.
- **`core/`**: Django project config (`settings.py`, `asgi.py`, `wsgi.py`, `celery.py`).
- **`accounts/`**: App with models, serializers, views, and auth middleware.
- **`templates/`**: HTML templates used by the project (email templates, index page).
- **`requirements.txt`**, **`pyproject.toml`**: Python dependencies.
- **`Dockerfile`**, **`docker-compose.yml`**: Container and service definitions (web, celery, celery-beat, redis).

**Environment variables (used by project)**
Set these in a `.env` file or your environment. At minimum provide values for:
- `CLOUD_NAME`, `API_KEY`, `API_SECRET` (Cloudinary)
- `SMTP_SERVER`, `SMTP_PORT`, `MAIL_USERNAME`, `MAIL_PASSWORD`, `FROM_EMAIL` (email)
- Optional/important: `DEBUG`, `ALLOWED_HOSTS` and any DB credentials if replacing the default sqlite.

**Install (pip / virtualenv)**
1. Create and activate a virtual environment:

	 - macOS / Linux:
		 ```bash
		 python -m venv venv
		 source venv/bin/activate
		 ```
	 - Windows (PowerShell):
		 ```powershell
		 python -m venv venv
		 venv\Scripts\Activate.ps1
		 ```

2. Install dependencies:

	 ```bash
	 pip install --upgrade pip
	 pip install -r requirements.txt
	 ```

3. Create a `.env` file in the project root with the environment variables listed above.

4. Run migrations and create a superuser:

	 ```bash
	 python manage.py migrate
	 python manage.py createsuperuser
	 ```

5. (Optional) Collect static files before production deployments:

	 ```bash
	 python manage.py collectstatic --noinput
	 ```

**Run (development)**
- Using Django dev server:

	```bash
	python manage.py runserver 0.0.0.0:8000
	```

- Using Uvicorn (ASGI):

	```bash
	uvicorn core.asgi:application --host 0.0.0.0 --port 8000
	```

**Run with Docker Compose**
The project includes a `docker-compose.yml` that defines services for the web app, Celery worker, Celery beat, and Redis. To run everything with Docker:

```bash
docker compose up --build
# or (older installations)
docker-compose up --build
```

The `web` service uses `gunicorn core.wsgi:application` by default in the compose file.

**Running Celery (local / manual)**
- Start Redis locally (or use the Docker Compose `redis` service).
- Start a worker:

	```bash
	celery -A core worker --loglevel=info
	```

- Start Celery beat (periodic tasks scheduler):

	```bash
	celery -A core beat --loglevel=info
	```

**Testing**

```bash
python manage.py test
```

**Notes & Gotchas**
- Default DB: SQLite (`db.sqlite3`) — good for development. The compose file has commented PostgreSQL example if you'd like to switch to Postgres.
- Celery broker/result backend is configured to use Redis at `redis://127.0.0.1:6379/0` by default. When using Docker Compose, use the included `redis` service.
- The project loads variables from a `.env` file via `python-dotenv`; do not commit secrets into version control.
- `pyproject.toml` lists `requires-python = ">=3.12"` while the `Dockerfile` uses Python 3.11; ensure your target runtime matches your environment.

**Where to look in the code**
- Django settings: [core/settings.py](core/settings.py#L1)
- ASGI entry (for Uvicorn): [core/asgi.py](core/asgi.py#L1)
- Django CLI: [manage.py](manage.py#L1)
- Docker compose: [docker-compose.yml](docker-compose.yml#L1)

**Contributing / Next steps**
- If you want, I can:
	- Add a `.env.example` with required environment variable names.
	- Add a `Makefile` or `invoke` tasks for common commands.
	- Create a CI workflow that runs tests and linting on push.

**License**
- Add a LICENSE file or update this README with project license details.

---
*README generated on request.*
