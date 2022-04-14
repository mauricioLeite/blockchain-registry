# Get Makefile full path
mkfile_path := $(abspath $(lastword $(MAKEFILE_LIST)))
# Get Makefile dir name only
root_dir := $(notdir $(patsubst %/,%,$(dir $(mkfile_path))))

# Force to use buildkit for all images and for docker-compose to invoke
# Docker via CLI (otherwise buildkit isn't used for those images)
export DOCKER_BUILDKIT=1
export COMPOSE_DOCKER_CLI_BUILD=1


# HELP
# This will output the help for each task
.PHONY: help -

# Automated helper
help: ## Show this help information.
	@awk 'BEGIN {FS = ":.*?## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-15s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

-: ## 

# LOCAL / DEV - docker-compose commands

up: ## Start development environment.
	@docker-compose up

CONTAINER ?= ${root_dir}
sh: ## Execute a shell inside a container of your choice (Defaults to microservice).
	@docker-compose exec \
		${CONTAINER} /bin/bash

logs: ## Display logs from all containers with timestamps.
	@docker-compose logs \
		--timestamps

ps: ## List all containers from project.
	@docker-compose ps \
		--all

build: ## Build docker images for development.
	@docker-compose build \
		--progress plain

build-nc: ## Rebuild docker images (ignore existing build cache).
	@docker-compose build \
		--progress plain \
		--no-cache

recreate: ## Force recreate all containers.
	@docker-compose up \
		--force-recreate

reload: build recreate ## Build and force recreate all containers (using cache).

reload-nc: build-nc recreate ## Build and force recreate all containers (ignore existing cache).

down: ## Stop and remove all containers.
	@docker-compose down \
		--remove-orphans

DOCKERFILE ?= Dockerfile
lint-dockerfile: ## Lint any Dockerfile provided using Hadolint.
	@docker run \
		--pull always \
		--rm \
		--interactive \
		--volume "${PWD}/.hadolint.yml:/.hadolint.yaml:ro" \
			hadolint/hadolint:latest < ${DOCKERFILE}

stress-test-build: ## Create container for stress testing
	@docker-compose \
		--file docker-compose.yml \
		--file test/docker-compose.test.yml \
		build \
			--progress plain

stress-test: stress-test-build ## Create container for stress testing
	@docker-compose \
		--file docker-compose.yml \
		--file test/docker-compose.test.yml \
		--compatibility \
		up