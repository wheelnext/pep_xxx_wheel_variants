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
		-p "fictional_hw :: architecture :: mother" \
		-p "fictional_hw :: compute_capability :: 4"

	flit build --format wheel \
		-p "fictional_tech :: quantum :: superposition" \
		-p "fictional_tech :: risk_exposure :: 25" \
		-p "fictional_tech :: technology :: auto_chef"

	flit build --format wheel \
		-p "fictional_hw :: architecture :: deepthought" \
		-p "fictional_hw :: compute_accuracy :: 10" \
		-p "fictional_hw :: compute_capability :: 10" \
		-p "fictional_hw :: humor :: 0" \
		-p "fictional_tech :: quantum :: foam"

	flit build --format wheel \
		-p "fictional_hw :: architecture :: tars" \
		-p "fictional_hw :: compute_accuracy :: 8" \
		-p "fictional_hw :: compute_capability :: 8" \
		-p "fictional_hw :: humor :: 10"

	flit build --format wheel \
		-p "fictional_hw :: architecture :: hal9000" \
		-p "fictional_hw :: compute_accuracy :: 0" \
		-p "fictional_hw :: compute_capability :: 6" \
		-p "fictional_hw :: humor :: 2"

	flit build --format wheel \
		-p "fictional_tech :: quantum :: foam" \
		-p "fictional_tech :: risk_exposure :: 1000000000" \
		-p "fictional_tech :: technology :: improb_drive"
		
	flit build --format wheel \
		-p "fictional_hw :: compute_capability :: >=4,<8"
		
	flit build --format wheel \
		-p "fictional_hw :: compute_capability :: >=4,<6"
		
	flit build --format wheel \
		-p "fictional_hw :: compute_capability :: >=7"

	variantlib generate-index-json -d dist/

