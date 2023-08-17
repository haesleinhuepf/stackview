call python -m pip install --user --upgrade setuptools wheel

call python setup.py sdist bdist_wheel

call python -m pip install --user --upgrade twine

call python -m twine upload --repository pypi dist/*




