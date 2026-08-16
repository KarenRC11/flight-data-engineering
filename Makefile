.PHONY: venv install lint test run

venv:
	python -m venv .venv

install:
	. .venv/bin/activate && pip install -r requirements.txt

test:
	. .venv/bin/activate && pytest -q

run:
	. .venv/bin/activate && python -m pipeline.main
	. .venv/bin/activate && python -m pipeline.load.upload

lint:
	. .venv/bin/activate && python -m compileall src
