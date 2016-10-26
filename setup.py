"""
python-j1939 requires the setuptools package to be installed.
"""

import logging
from setuptools import setup, find_packages

__version__ = "0.0.0-alpha.0"

logging.basicConfig(level=logging.WARNING)

setup(
    name="python-j1939",
    url="https://github.com/milhead2/python-j1939.git",
    version=__version__,
    packages=find_packages(),
    author="Brian Thorne",
    author_email="hardbyte@gmail.com",
    description="Controller Area Network interface module for Python",
    long_description=open('README.rst').read(),
    license="LGPL v3",
    package_data={
        "": ["CONTRIBUTORS.txt", "LICENSE.txt"],
        "doc": ["*.*"]
    },

    install_requires=["python-can>=1.5"],

    scripts=["./bin/j1939_logger.py"],

    # Tests can be run using `python setup.py test`
    test_suite="nose.collector",
    tests_require=['mock', 'nose']
)
