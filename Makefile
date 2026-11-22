PYTHON = python3
MAIN = a_maze_ing.py
CONFIG = config.txt

MYPY_FLAGS = --warn-return-any --warn-unused-ignores \
	--ignore-missing-imports --disallow-untyped-defs \
	--check-untyped-defs

.PHONY: install run debug clean lint build

install:
	$(PYTHON) -m pip install flake8 mypy build

run:
	$(PYTHON) $(MAIN) "$(CONFIG)"

debug:
	$(PYTHON) -m pdb $(MAIN) "$(CONFIG)"

clean:
	find . -type d \( -name "__pycache__" \
		-o -name ".mypy_cache" \
		-o -name ".pytest_cache" \
		-o -name "*.egg-info" \) -prune -exec rm -rf {} +
	rm -rf build

lint: clean
	$(PYTHON) -m flake8 .
	$(PYTHON) -m mypy . $(MYPY_FLAGS)

build: clean
	$(PYTHON) -m build
	cp dist/mazegen-*.whl dist/mazegen-*.tar.gz .