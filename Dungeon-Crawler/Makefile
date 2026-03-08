DOCS = ./docs
TESTS = ./tests/test_*
SRC = ./src/*.py

.PHONY: all check-styles fix-styles check-types create-docs test-coverage test clean

all: check-styles fix-styles check-types create-docs test-coverage create-uml clean
	@echo "done!"

check-styles:
	flake8 .

fix-styles:
	autopep8 --in-place --recursive --aggressive --aggressive .

check-types:
	mypy --disallow-untyped-defs --strict .

create-docs:
	@echo "Creating documentation..."
	mkdir -p $(DOCS)
	pdoc --output-dir $(DOCS)/code_docs $(SRC)

test-coverage: create-docs
	@echo "Running test-coverage..."
	pytest -v --color=yes --cov --cov-report=term-missing --cov-report=html:$(DOCS)/html_cov $(TESTS)

test:
	pytest -v ${TESTS}

clean:
	rm -rf `find . -type d -name __pycache__`
	rm -rf `find . -type d -name .pytest_cache`
	rm -rf `find . -type d -name .mypy_cache`
	rm -rf `find . -type f -name .coverage`
	