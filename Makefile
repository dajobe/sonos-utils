lint:
	flake8 common.py
	pylint common.py

test:
	py.test --cov-config .coveragerc --cov
