#!/usr/bin/env python
# -*- coding: utf-8 -*-

import ast
import os
import sys
from setuptools import setup, find_packages


if sys.version_info < (3, 6, 4):
    print("Python version 3.6.4 or superior is required for use with toolbelt")
    raise SystemExit(1)


def local_file(*f):
    with open(os.path.join(os.path.dirname(__file__), *f), "r") as fd:
        return fd.read()


class VersionFinder(ast.NodeVisitor):
    VARIABLE_NAME = "version"

    def __init__(self):
        self.version = None

    def visit_Assign(self, node):
        try:
            if node.targets[0].id == self.VARIABLE_NAME:
                self.version = node.value.s
        except Exception:
            pass


def read_version():
    finder = VersionFinder()
    finder.visit(ast.parse(local_file("thick_denim", "version.py")))
    return finder.version


install_requires = [
    "beautifulsoup4==4.8.0",
    "boto3>=1.9",
    "click>=7.0",
    "docutils==0.14",
    "humanfriendly>=4.18",
    "inquirer>=2.6.3",
    "jira>=2.0.0",
    "keyring==19.2.0",
    "kubernetes>=10.0",
    "paramiko>=2.4.2",
    "pendulum>=2.0",
    "pip>=19.1.1",
    "progress>=1.5",
    "psycopg2-binary>=2.8",
    "pyfiglet>=0.8.0",
    "pynacl>=1.3.0",
    "pync>=2.0",
    "requests>=2.22",
    "ruamel.yaml>=0.15.96",
    "sshtunnel>=0.1.4",
]

tests_require = [
    "coverage>=4.5",
    "doc8>=0.8.0",
    "flake8>=3.7",
    "freezegun>=0.3.11",
    "httpretty>=0.9.6",
    "ipdb>=0.12.0",
    "mccabe>=0.6.1",
    "mock>=3.0",
    "moto>=1.3",
    "nose>=1.3",
    "nose-timer>=0.7.5",
    "nose-watch>=0.9.2",
    "parameterized>=0.7.0",
    "rednose>=1.3",
    "sphinx>=2.0",
    "sphinx-click>=2.0",
    "sphinx-rtd-theme>=0.4.3",
    "sure>=1.4",
    "vcrpy>=2.0",
]


setup(
    name="thick-denim",
    version=read_version(),
    description="\n".join(
        [
            "Thick-Denim is a python tool that allows querying and",
            "cross-referencing GitHub and Jira and processing data",
            "into metrics.",
            "Provides DSLs to describe queries, references and ",
            "data processing.",
        ]
    ),
    long_description=local_file("README.rst"),
    entry_points={"console_scripts": ["thick_denim = thick_denim.cli:entrypoint"]},
    url="https://github.com/NewStore/thick-denim",
    packages=find_packages(exclude=["*tests*"]),
    include_package_data=True,
    package_data={
        "thick_denim": [
            "README.rst", "*.png", "thick_denim/*.png", "*.rst", "docs/*", "docs/*/*"
        ]
    },
    package_dir={
        'thick-denim': 'thick_denim'
    },
    zip_safe=False,
    author="Gabriel Falcão",
    author_email="gabriel@newstore.com",
    install_requires=install_requires,
    extras_require={"tests": tests_require},
    tests_require=tests_require,
    dependency_links=[],
)
