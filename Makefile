PYTHON ?= python

install:
	$(PYTHON) -m pip install -e '.[dev]'

test:
	pytest -q

run:
	$(PYTHON) -m synergy_relative_value.api

