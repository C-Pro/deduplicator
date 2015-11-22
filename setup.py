#!/usr/bin/env python
from setuptools import setup, find_packages

setup(
    name='deduplicator',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'psycopg2==2.5.4',
        'requests==2.1.0'
    ],
    author = "Sergey Melekhin",
    author_email = "sergey@melekhin.me",
    description = "Coding test",
)
