ifneq (,$(wildcard ./.env))
    include .env
    export
endif

ENV      := local
VERSION  ?= $(shell grep 'version' pyproject.toml | sed 's/.*"\(.*\)".*/\1/')

LOCAL_RUN = python3 manage.py runserver

ifneq ($(ENV), local)
	ifeq ($(ENV), dev)
		DOCKER_ARGS = -f docker-compose.dev.yml
	else
		DOCKER_ARGS = -f docker-compose.prod.yml
	endif
	RUN_COMMAND = docker-compose $(DOCKER_ARGS) up --build
else
	RUN_COMMAND = $(LOCAL_RUN)
endif

version:
	@echo "$(VERSION)"

run: prod-build
	@echo "Running for $(ENV) environment"
	$(RUN_COMMAND)

build:
	@echo "Building image version $(VERSION)"
	docker build --tag acm:v.$(VERSION) .

prod-build:
	@if [ "$(ENV)" = "prod" ]; then \
		echo "Build docker image for prod environment."; \
		$(MAKE) build; \
	fi

migrations:
	@if [ "$(ENV)" = "local" ]; then \
		python3 manage.py makemigrations; \
		python3 manage.py migrate; \
	fi

init_config:
	@if [ "$(ENV)" = "local" ]; then \
		python3 manage.py init_config;\
	fi

createsuperuser:
	@if [ "$(ENV)" = "local" ]; then \
		python3 manage.py createsuperuser;\
	fi

translations:
	@if [ "$(ENV)" = "local" ]; then \
		python3 manage.py load_translations translations.json --force;\
	fi

balloons:
	@if [ "$(ENV)" = "local" ]; then \
		python3 manage.py balloons;\
	fi