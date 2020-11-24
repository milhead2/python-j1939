"""
python-j1939 requires the setuptools package to be installed.
"""

import logging
from setuptools import setup, find_packages

__version__ = "0.1.0-alpha.3"

logging.basicConfig(level=logging.WARNING)

setup(
    name="python-j1939",
    url="https://github.com/milhead2/python-j1939.git",
    version=__version__,
    packages=find_packages(),
    author="David 'Miller' Lowe",
    author_email="milhead@gmail.com",
    description="SAE J1939 module for Python",
    long_description=open('README.rst').read(),
    license="LGPL v3",
    package_data={
        "": ["CONTRIBUTORS.txt", "LICENSE.txt"],
        "doc": ["*.*"]
    },

    install_requires=["python-can>=2.0.0a2"],

    scripts=[
        "./bin/j1939_logger.py",
        "./bin/j1939_mem_query.py",
        "./bin/j1939_mem_set.py",
        "./bin/j1939_request_pgn.py",
        "./bin/j1939_send_pgn.py"
    ],

    # Tests can be run using `python setup.py test`
    test_suite="nose.collector",
    tests_require=['mock', 'nose']
)
