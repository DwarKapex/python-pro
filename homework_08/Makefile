SETTINGS_DIR=settings
PYTHON=python3
OS_TYPE=Lin

# Define default server to run
DEV_SETTINGS=settings_dev.py
PROD_SETTINGS=$(SETTINGS_DIR)/settings_prod.py

# Update project name
PROJECT_DIR=./mysite

# Define Django commands
dev:
	$(PYTHON) $(PROJECT_DIR)/manage.py runserver

test:
    $(PYTHON) $(PROJECT_DIR)/manage.py test polls

prod:
	$(PYTHON) manage.py runserver

migrate-dev:
	$(PYTHON) $(PROJECT_DIR)/manage.py migrate

migrate-prod:
	$(PYTHON) manage.py migrate

# Help command to display available options
help:
	@echo "Django Makefile Commands:"
	@echo " dev:             Run the server in dev mode"
	@echo " test:             Run unit tests"
	@echo " prod:            Run the server in prod mode"
	@echo " migrate-dev:     Run migrations in dev mode"
	@echo " migrate-prod:    Run migrations in prod mode"
	@echo " help:            Display this help message"

.PHONY: dev test prod migrate-dev migrate-prod help
