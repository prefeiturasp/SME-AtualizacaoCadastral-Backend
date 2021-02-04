DJANGO_CMD = python manage.py

migrations:
	$(DJANGO_CMD) makemigrations

migrate:
	$(DJANGO_CMD) migrate

create-superuser:
	$(DJANGO_CMD) createsuperuser

runserver:
	$(DJANGO_CMD) runserver 0.0.0.0:8000

collectstatic:
	$(DJANGO_CMD) collectstatic --noinput

install_dev: 
	pip install -r requirements/local.txt

create_superuser_docker:
	docker-compose -f docker-compose-dev.yml run --rm backend sh -c "python manage.py createsuperuser"

start_docker: migrate runserver
