venv:
	uv sync

format: venv
	uv run ruff format
	uv run ruff check --fix

run: venv
	uv run python src/main.py --email='$(email)' --password='$(password)' --booking-goals='$(booking-goals)' --box-name='$(box-name)' --box-id='$(box-id)' $(if $(days-in-advance),--days-in-advance='$(days-in-advance)',) $(if $(hours-in-advance),--hours-in-advance='$(hours-in-advance)',) --proxy='$(proxy)'

docker-run:
	python src/main.py --email='$(email)' --password='$(password)' --booking-goals='$(booking-goals)' --box-name='$(box-name)' --box-id='$(box-id)' $(if $(days-in-advance),--days-in-advance='$(days-in-advance)',) $(if $(hours-in-advance),--hours-in-advance='$(hours-in-advance)',) --proxy='$(proxy)'

tests: venv
	uv run pytest src/tests

docker/build:
	docker build --no-cache	--tag=fitbot .

docker/run:
	docker run --rm -e email='$(email)' -e password='$(password)' -e booking-goals='$(booking-goals)' -e box-name='$(box-name)' -e box-id='$(box-id)' $(if $(days-in-advance),-e days-in-advance='$(days-in-advance)',) $(if $(hours-in-advance),-e hours-in-advance='$(hours-in-advance)',) -e proxy='$(proxy)' fitbot

docker/tests:
	docker run --rm fitbot /bin/sh -c 'make tests'