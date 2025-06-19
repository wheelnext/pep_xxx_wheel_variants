.PHONY: clean test coverage build install lint

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
	flit build --format wheel

	flit build --format wheel --null-variant
	
	flit build --format wheel \
		-p "fictional_hw :: architecture :: hal9000" \
		-p "fictional_hw :: compute_capability :: >=8"

	flit build --format wheel \
		-p "fictional_tech :: quantum :: foam" \
		-p "fictional_tech :: risk_exposure :: 25" \
		-p "fictional_tech :: technology :: auto_chef"

	flit build --format wheel \
		-p "fictional_hw :: architecture :: hal9000" \
		-p "fictional_tech :: quantum :: foam" \
		-p "fictional_tech :: risk_exposure :: 25" \
		-p "fictional_tech :: technology :: auto_chef"

	flit build --format wheel \
		-p "fictional_hw :: compute_capability :: >=8" \
		-p "fictional_tech :: quantum :: foam" \
		-p "fictional_tech :: risk_exposure :: 25" \
		-p "fictional_tech :: technology :: auto_chef"

	flit build --format wheel \
		-p "fictional_hw :: architecture :: hal9000" \
		-p "fictional_hw :: compute_capability :: >=8" \
		-p "fictional_tech :: quantum :: foam" \
		-p "fictional_tech :: risk_exposure :: 25" \
		-p "fictional_tech :: technology :: auto_chef"

	variantlib generate-index-json -d dist/
