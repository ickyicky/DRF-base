VERSION=`git rev-parse HEAD`
APPNAME=api
PROJECT=project
APPVERSION=0.1

.PHONY: help
help:
	@echo "project's api avalibe build quick options:"
	@echo "  clean     - clean developpement folder"
	@echo "  black     - formats all python source files"
	@echo "  base      - builds project base"
	@echo "  build     - builds docker container"
	@echo "  test      - run tests"

.PHONY: clean
clean:
	find . -type d -name __pycache__ -exec rm -r {} \+
	find . -type f -name '*.pyc' -exec rm -r {} \+
	rm -rf static
	rm -rf .pytest_cache
	rm -rf htmltest
	rm -rf htmlcov

.PHONY: black
black:
	black . *.py -l 120

.PHONY: base
base:
	docker build -t project/api-base -f Dockerfile.base .

.PHONY: build
build:
	docker-compose build \
		--build-arg version="$(VERSION)" \
		--build-arg appname="$(APPNAME)" \
		--build-arg project="$(PROJECT)" \
		--build-arg appversion="$(APPVERSION)" \
		app

.PHONY: test
test:
	docker-compose run app bash -c "\
		set -x && \
		DEBUG=0 coverage run --source api --omit api/wsgi.py,api/asgi.py,api/migrations,api/settings.py,api/urls.py -m py.test -svv --html=htmltest/report.html --self-contained-html && \
		coverage report && \
		coverage html \
	"