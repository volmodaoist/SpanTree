rm -rf dist/ build/ *.egg-info
python setup.py sdist bdist_wheel
twine check dist/*

# API token 不等于 API key
twine upload --repository testpypi dist/*
