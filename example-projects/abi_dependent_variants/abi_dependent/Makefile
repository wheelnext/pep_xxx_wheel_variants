.PHONY: clean test coverage build install lint
.SILENT:

# ============================================================================ #
# CLEAN COMMANDS
# ============================================================================ #

clean: clean-build clean-pyc clean-test ## remove all build, test, coverage and Python artifacts

clean-build: ## remove build artifacts
	rm -fr build/
	rm -fr dist/
	rm -fr .eggs/
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +

clean-pyc: ## remove Python file artifacts
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

clean-test: ## remove test and coverage artifacts
	rm -fr .tox/
	rm -f .coverage*
	rm -fr htmlcov/
	rm -fr .pytest_cache

# ============================================================================ #
# BUILD COMMANDS
# ============================================================================ #

build: clean ## builds source and wheel package
	flit build --format wheel --null-variant

	flit build --format wheel \
	    --variant-label "abi_1.0.0" \
		-p "runtime_dependency :: base_project :: 1.0.0"

	flit build --format wheel \
	    --variant-label "abi_2.0.0" \
		-p "runtime_dependency :: base_project :: 2.0.0"

	flit build --format wheel \
	    --variant-label "abi_3.0.0" \
		-p "runtime_dependency :: base_project :: 3.0.0"

	ls -al dist/
