.PHONY: test demo cli server server-file clean

test:
	pytest -q

demo:
	python hexshop/infrastructure/cli/main.py

cli:
	python -m hexshop.infrastructure.cli.main

server:
	uvicorn hexshop.infrastructure.http.fastapi_app:app --reload

server-file:
	REPO_FILE=./orders.json uvicorn hexshop.infrastructure.http.fastapi_app_file:app --reload

clean:
	rm -f orders.json
