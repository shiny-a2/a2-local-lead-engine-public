.PHONY: install lint test typecheck db-upgrade doctor seed-campaign safety-check foundation-report

install:
	pip install -e ".[dev]"

lint:
	ruff check .

test:
	pytest

typecheck:
	mypy app

db-upgrade:
	python -m app.cli.main db upgrade

doctor:
	python -m app.cli.main doctor

seed-campaign:
	python -m app.cli.main campaign seed

safety-check:
	python -m app.cli.main safety check

foundation-report:
	python -m app.cli.main report foundation

