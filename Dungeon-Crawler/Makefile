DOCS = ./docs
TESTS = ./tests/test_*
UMLFILES = ./uml/*.plantuml
UMLDIAGRAMDIR = ./uml/diagrams/
SRC = ./src/*.py

.PHONY: all check-styles fix-styles check-types create-docs test-coverage test create-uml clean

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

create-uml: ./uml
ifeq ($(wildcard ~/plantuml.jar), )
	@echo "Downloading plantuml..."
	curl -L -o ~/plantuml.jar https://sourceforge.net/projects/plantuml/files/plantuml.jar/download
endif

ifeq ($(wildcard $(UMLFILES)), )
	@echo "No UML Diagrams found."
else
	mkdir -p $(UMLDIAGRAMDIR)
	@echo "Creating UML Diagrams..."
	@for file in $(UMLFILES); do \
		java -jar ~/plantuml.jar $$file; \
	done
	mv ./uml/*.png $(UMLDIAGRAMDIR)
	@echo "UML Diagrams created and saved in $(UMLDIAGRAMDIR)."
endif

clean:
	rm -rf `find . -type d -name __pycache__`
	rm -rf `find . -type d -name .pytest_cache`
	rm -rf `find . -type d -name .mypy_cache`
	rm -rf `find . -type f -name .coverage`
	