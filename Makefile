.PHONY: clean download preprocess data start stop requirements activate

#################################################################################
# GLOBALS                                                                       #
#################################################################################

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
VENV_PATH=covid-latvia-env

#################################################################################
# COMMANDS                                                                      #
#################################################################################

## Downloads data
download:
	docker-compose run data scripts/download.py

## Preprocesses data
preprocess:
	docker-compose run data scripts/clean.py
	docker-compose run data scripts/preprocess.py

## Downloads and clean
data: clean download preprocess

## Cleans data
clean:
	rm -rf data/raw/*
	rm -rf data/processed/*

## Starts serving dashboard
start:
	docker-compose down && docker-compose up -d --remove-orphans dashboard

## Stops serving dashboard
stop:
	docker-compose down

## Creates virtual environment and install requirements for development
requirements:
	python -m venv --clear --upgrade-deps ${VENV_PATH}
	source ${VENV_PATH}/bin/activate && pip install --no-cache-dir -r requirements/data.txt
	source ${VENV_PATH}/bin/activate && pip install --no-cache-dir -r requirements/dashboard.txt

## Returns path to the environment activation script, enabling `. $(make activate)`
activate:
	@echo ${VENV_PATH}/bin/activate

#################################################################################
# PROJECT RULES                                                                 #
#################################################################################



#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: help
help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
