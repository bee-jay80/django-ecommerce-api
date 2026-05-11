.PHONY: help install migrate createsuperuser runserver uvicorn celery-worker celery-beat test lint docker-up

help:
	@echo "Available targets: install, migrate, createsuperuser, runserver, uvicorn, celery-worker, celery-beat, test, lint, docker-up"

install:
	python -m venv .venv
	.venv/Scripts/activate && python -m pip install --upgrade pip && pip install -r requirements.txt

migrate:
	python manage.py migrate

createsuperuser:
	python manage.py createsuperuser

runserver:
	python manage.py runserver 0.0.0.0:8000

uvicorn:
	uvicorn core.asgi:application --host 0.0.0.0 --port 8000

celery-worker:
	celery -A core worker --loglevel=info

celery-beat:
	celery -A core beat --loglevel=info

test:
	python manage.py test

lint:
	python -m pip install --upgrade pip
	python -m pip install flake8
	flake8 .

docker-up:
	docker compose up --build
