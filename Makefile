include .env
# vars
env_file = --env-file .env
app = app
nginx = nginx
db = database

.PHONY: help setup build up start down destroy stop restart app_connect nginx_connect db_connect migrate make_migrations collect_static create_superuser
help:
	@echo "Makefile commands:"
	@echo "setup"
	@echo "build"
	@echo "up"
	@echo "start"
	@echo "down"
	@echo "destroy"
	@echo "stop"
	@echo "restart"
	@echo "app_connect"
	@echo "nginx_connect"
	@echo "db_connect"
	@echo "migrate"
	@echo "make_migrations"
	@echo "collect_static"
	@echo "create_superuser"
setup:
	docker-compose -f docker-compose.yml ${env_file} build $(c)
	docker-compose -f docker-compose.yml ${env_file} up -d $(c)
	docker exec -it ${db} psql --username=${DB_USER} --dbname=${DB_NAME} -c \
	'CREATE SCHEMA IF NOT EXISTS content; exit;'
	docker-compose exec ${app} ./manage.py collectstatic --noinput
build:
	docker-compose -f docker-compose.yml ${env_file} build $(c)
up:
	docker-compose -f docker-compose.yml ${env_file} up $(c)
upd:
	docker-compose -f docker-compose.yml ${env_file} up -d $(c)
start:
	docker-compose -f docker-compose.yml ${env_file} start $(c)
down:
	docker-compose -f docker-compose.yml ${env_file} down $(c)
destroy:
	docker-compose -f docker-compose.yml ${env_file} down -v $(c)
stop:
	docker-compose -f docker-compose.yml ${env_file} stop $(c)
restart:
	docker-compose -f docker-compose.yml ${env_file} stop $(c)
	docker-compose -f docker-compose.yml ${env_file} up -d $(c)
app_connect:
	docker exec -it ${app} sh
nginx_connect:
	docker exec -it ${nginx} sh
db_connect:
	docker exec -it ${db} psql --username=${DB_USER} --dbname=${DB_NAME}
migrate:
	docker-compose exec ${app} ./manage.py migrate
collect_static:
	docker-compose exec ${app} ./manage.py collectstatic --noinput
create_superuser:
	docker-compose exec ${app} ./manage.py createsuperuser --email=monkey@mail.chimp --noinput
rebuild:
	docker-compose -f docker-compose.yml ${env_file} build $(c)
	docker-compose -f docker-compose.yml ${env_file} up -d $(c)
