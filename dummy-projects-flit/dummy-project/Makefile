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

# Valid `fictional_hw :: architecture`
	flit build --format wheel \
		-p "fictional_hw :: architecture :: hal9000"

	flit build --format wheel \
		-p "fictional_hw :: architecture :: deepthought"

	flit build --format wheel \
		-p "fictional_hw :: architecture :: hal9000" \
		-p "fictional_hw :: architecture :: deepthought"

# Invalid `fictional_hw :: architecture`
	flit build --format wheel \
		-p "fictional_hw :: architecture :: jarvis"

	flit build --format wheel \
		-p "fictional_hw :: architecture :: tar"

	flit build --format wheel \
		-p "fictional_hw :: architecture :: jarvis" \
		-p "fictional_hw :: architecture :: tar"

# Valid `fictional_hw :: compute_capability`
	flit build --format wheel \
		-p "fictional_hw :: compute_capability :: >=8"

	flit build --format wheel \
		-p "fictional_hw :: compute_capability :: <9"

	flit build --format wheel \
		-p "fictional_hw :: compute_capability :: >=5.0,<10.0"

	flit build --format wheel \
		-p "fictional_hw :: compute_capability :: >=8" \
		-p "fictional_hw :: compute_capability :: <9" \
		-p "fictional_hw :: compute_capability :: >=5.0,<10.0"

# Invalid `fictional_hw :: compute_capability
	flit build --format wheel \
		-p "fictional_hw :: compute_capability :: >=9"

	flit build --format wheel \
		-p "fictional_hw :: compute_capability :: <8"

	flit build --format wheel \
		-p "fictional_hw :: compute_capability :: >=8,<9,!=8.3.2"

	flit build --format wheel \
		-p "fictional_hw :: compute_capability :: <8" \
		-p "fictional_hw :: compute_capability :: >=9" \
		-p "fictional_hw :: compute_capability :: >=8,<9,!=8.3.2"

# Valid `fictional_hw :: compute_accuracy`
	flit build --format wheel \
		-p "fictional_hw :: compute_accuracy :: 0.7"

	flit build --format wheel \
		-p "fictional_hw :: compute_accuracy :: 0.99"

	flit build --format wheel \
		-p "fictional_hw :: compute_accuracy :: 0.8"

	flit build --format wheel \
		-p "fictional_hw :: compute_accuracy :: 0.7" \
		-p "fictional_hw :: compute_accuracy :: 0.8" \
		-p "fictional_hw :: compute_accuracy :: 0.99"

# Invalid `fictional_hw :: compute_capability

	flit build --format wheel \
		-p "fictional_hw :: compute_accuracy :: 0.996"

	flit build --format wheel \
		-p "fictional_hw :: compute_accuracy :: 0.9999"

	flit build --format wheel \
		-p "fictional_hw :: compute_accuracy :: 0.996" \
		-p "fictional_hw :: compute_accuracy :: 0.9999"

# Mix n Match - VALID

	flit build --format wheel \
		-p "fictional_hw :: architecture :: deepthought" \
		-p "fictional_hw :: compute_accuracy :: 0.99"

	flit build --format wheel \
		-p "fictional_hw :: architecture :: hal9000" \
		-p "fictional_hw :: compute_accuracy :: 0.995"

# Mix n Match - INVALID

	flit build --format wheel \
		-p "fictional_hw :: architecture :: hal9000" \
		-p "fictional_hw :: compute_accuracy :: 0.996"

