GITCHLOGBIN   = gitchangelog
CHANGELOGFILE = HISTORY.rst
GITCHLOG      = $(GITCHLOGBIN) > $(CHANGELOGFILE) || exit 1
TRUNCATE      = python truncate.py $(CHANGELOGFILE)

.PHONY: clean-pyc clean-build docs

help:
	@echo "clean-build - remove build artifacts"
	@echo "clean-pyc - remove Python file artifacts"
	@echo "lint - check style with flake8"
	@echo "test - run tests quickly with the default Python"
	@echo "test-all - run tests on every Python version with tox"
	@echo "coverage - check code coverage quickly with the default Python"
	@echo "docs - generate Sphinx HTML documentation, including API docs"
	@echo "release - package and upload a release"
	@echo "sdist - package"

clean: clean-build clean-pyc

clean-build:
	rm -fr build/
	rm -fr dist/
	rm -fr *.egg-info

clean-pyc:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +

lint:
	flake8 budget tests

test:
	python runtests.py tests

test-all:
	tox

coverage:
	coverage run --source budget runtests.py tests
	coverage report -m
	coverage html
	open htmlcov/index.html

docs:
	rm -f docs/django-pj-budget.rst
	rm -f docs/modules.rst
	$(GITCHLOG)
	$(TRUNCATE)
	sphinx-apidoc -o docs/ budget
	$(MAKE) -C docs clean
	$(MAKE) -C docs html
	sh replace_version.sh

release: clean
	python setup.py sdist upload
	python setup.py bdist_wheel upload

sdist: clean
	python setup.py sdist
	ls -l dist
