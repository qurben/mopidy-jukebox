#!/usr/bin/env python

import os
import setuptools
import re


def get_contents(filename):
    """Get the contents of a file relative to the source distribution directory."""
    root = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(root, filename)) as handle:
        return handle.read()


def get_version(filename):
    """Extract the version number from a Python module."""
    contents = get_contents(filename)
    metadata = dict(re.findall('__([a-z]+)__ = [\'"]([^\'"]+)', contents))
    return metadata['version']


setuptools.setup(
        name='Mopidy-Jukebox',
        version=get_version('mopidy_jukebox/__init__.py'),
        description="Jukebox for Mopidy",
        long_description=get_contents('README.rst'),
        url='https://github.com/qurben/mopidy-jukebox',
        author='Gerben Oolbekkink',
        author_email='g.j.w.oolbekkink@gmail.com',
        packages=setuptools.find_packages(),
        zip_safe=False,
        include_package_data=True,
        install_requires=[
            'Mopidy >= 0.19.4',
            'setuptools',
            'peewee'
        ],
        entry_points={
            'mopidy.ext': [
                'jukebox = mopidy_jukebox:Extension',
            ],
        },
        classifiers=[
            'Environment :: No Input/Output (Daemon)',
            'Intended Audience :: End Users/Desktop',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
            'Programming Language :: Python :: 2',
            'Topic :: Multimedia :: Sound/Audio :: Players',
        ])
