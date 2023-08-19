.PHONY: lint
lint:
	flake8 .


.PHONY: check-fmt
check-fmt:
	isort -rc -m 3 --check-only .


.PHONY: fmt
fmt:
	isort -rc -sl .
	black .
	isort -rc -m 3 .