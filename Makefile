.PHONY: doctor demo test wheel

doctor:
	python -m flashpilot.cli doctor

demo:
	python -m flashpilot.cli demo --provider fixture

test:
	python -m ruff check .
	python -m ruff format --check .
	python -m pytest -q

wheel:
	python -m pip wheel . --no-deps --no-build-isolation --wheel-dir dist
