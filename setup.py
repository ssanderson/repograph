#!/usr/bin/env python
from setuptools import setup

long_description = 'Visualize GitHub submodule dependencies.'


def install_requires():
    return ['click', 'PyGithub', 'pygraphviz']


setup(
    name='repograph',
    version='0.1',
    description=long_description,
    author="Scott Sanderson",
    author_email="scott.b.sanderson90@gmail.com",
    py_modules=['repograph'],
    long_description=long_description,
    license='Apache 2.0',
    classifiers=[
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
    ],
    url='https://github.com/ssanderson/repograph',
    install_requires=install_requires(),
    entry_points="""
        [console_scripts]
        repograph=repograph:main
    """,
)
