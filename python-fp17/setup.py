#!/usr/bin/env python

from setuptools import setup, find_packages

setup(
    name='python-fp17',

    url='https://github.com/openhealthcare/python-fp17',
    version='0.0.1',
    description="",

    author="Open Health Care, Ltd.",
    author_email="hello@openhealthcare.co.uk",
    license="BSD",

    packages=find_packages(),
    include_package_data=True,

    install_requires=(
        'cerberus',
        'click',
        'lxml',
        'requests',
        'xmlschema',
    ),
)
