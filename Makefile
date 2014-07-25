all:
	true

pypi:
	python setup.py register
	python setup.py sdist upload

clean:
	rm -rf build dist *.egg-info
	find . -type d -name __pycache__ -delete

clean-all: clean
	rm -rf .tox
