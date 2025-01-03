from setuptools import setup, find_packages

setup(
    name='SpanTree',
    version='0.1.0',
    description='A tool to assist QA Engineers in writing assertions by parsing program call traces.',
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author='volmodaoist',
    url='https://github.com/volmodaoist/SpanTree',
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)