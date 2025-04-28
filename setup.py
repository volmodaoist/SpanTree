from setuptools import setup, find_packages

setup(
    name='tracespantree',
    version='1.0.1',
    description="A reliable, fast trace parser that quickly locates the key–value pairs you’re looking for in a span.",
    long_description=open('README.md').read(),
    long_description_content_type="text/markdown",
    author="volmodaoist",
    url="https://github.com/volmodaoist/SpanTree",
    packages=find_packages(include=["tracespantree", "tracespantree.*"]),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
