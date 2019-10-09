# prepare toolbelt to run in test-mode
current_dir := $(shell pwd)
export THICK_DENIM_CONFIG_PATH	:= $(current_dir)/tests/thick-denim.yml
export THICK_DENIM_TEST_MODE	:= yes
export THICK_DENIM_VERBOSE_MODE	:= yes
export PYTHONDONTWRITEBYTECODE	:= yes


# NOTE: the first target of a makefile executed when ``make`` is
# executed without arguments.
# It was deliberately named "default" here but could be any name.
# Also feel free to modify it to execute a custom command.
#
#
default: recreate develop tests docs


recreate: clean  # destroys virtualenv, create new virtualenv and install all python dependencies
	rm -rf .venv poetry.lock
	make dependencies

dependencies: # install and configure poetry, create new virtualenv and install python dependencies
	pip3 install -q -U pip poetry --no-cache-dir --user
	poetry config settings.virtualenvs.in-project true
	make develop

lint: # run flake8
	poetry run flake8 --ignore=E501 thick_denim tests docs/source/conf.py

black: # format all python code with black
	poetry run black --line-length 79 thick_denim tests docs/source/conf.py

develop: # install all development dependencies with poetry
	poetry install
	poetry run python setup.py develop

tests:  # run unit and functional tests together aggregating total coverage
	poetry run nosetests tests --cover-erase

tests-with-timer:  # run all tests with time tracking (nice for seeing slow ones)
	poetry run nosetests tests --cover-erase --with-timer

unit:   # run unit tests, erases coverage file
	@echo $$THICK_DENIM_CONFIG_PATH
	poetry run nosetests tests/$@ --cover-erase # let's clear the test coverage report during unit tests only

functional: # run functional tests
	@echo $$THICK_DENIM_CONFIG_PATH
	poetry run nosetests tests/$@

end-to-end:
	poetry run tests/end-to-end/run-e2e-tests.sh all

tdd-unit:  # run unit tests in watch mode
	@echo $$THICK_DENIM_CONFIG_PATH
	poetry run nosetests --with-watch tests/unit

tdd-functional:  # run functional tests in watch mode
	@echo $$THICK_DENIM_CONFIG_PATH
	poetry run nosetests --with-watch tests/functional/

tdd:  # run all tests in watch mode (nice for top-down tdd)
	poetry run nosetests --with-watch tests/

docs-html: # (re) generates documentation
	poetry run make -C docs html

docs: docs-html  # (re) generates documentation and open in browser
	poetry run thick_denim docs

release: docs-html tests  # runs all tests and launch script to make new release
	@./.release

distribution: docs-html  # generates new build file
	@rm -rf dist/*
	@python setup.py build sdist

clean:  # remove temporary files including byte-compiled python files
	@rm -rf thick_denim/docs *egg-info* .noseids pip-wheel-metadata
	@find . -type d -path '*/thick_denim/*/__pycache__' -or -path '*/tests/*/__pycache__' | xargs rm -rf

# tells "make" that the target "make docs" is phony, meaning that make
# should ignore the existence of a file or folder named "docs" and
# simply execute commands described in the target
.PHONY: docs black tests thick_denim operations dist build
