.PHONY: help
help:
	@fgrep -h "##" $(MAKEFILE_LIST) | fgrep -v fgrep | sed -e 's/\\$$//' | sed -e 's/##//'

.PHONY: clean
clean:
	find . -type d -name __pycache__ -exec rm -r {} \+
	find . -type f -name '*.pyc' -exec rm -r {} \+
	rm -rf .pytest_cache
	rm -rf htmltest
	rm -rf htmlcov
	rm -f celerybeat.pid

.PHONY: test
test:
	@docker-compose run app bash -c "\
		set -x && \
		DEBUG=0 coverage run --source . -m py.test -svv --html=htmltest/report.html --self-contained-html && \
		coverage report && \
		coverage html \
	"

.PHONY: lint
lint:
	isort --settings-path config --recursive .
	black project --exclude project/migrations
	pylint --rcfile config/pylintrc -r n project

.PHONY: debug
debug:
	docker-compose run --rm --service-ports app

.PHONY: up
up:
	docker-compose up -d

.PHONY: down
down:
	docker-compose down

.PHONY: app
app:
	docker-compose exec app bash

.PHONY: db
db:
	docker-compose exec db bash -c 'psql --user=postgres'

.PHONY: log
log:
	docker-compose logs app

.PHONY: build
build:
	docker build -t project/project-server:devel -f Dockerfile . --network=host

.PHONY: base
base:
	docker build -t project/project-server-base:devel -f Dockerfile.base .
