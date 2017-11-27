#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os

from setuptools import setup
from django_rester import config

build_number = os.getenv('TRAVIS_BUILD_NUMBER', '')
branch = os.getenv('TRAVIS_BRANCH', '')
travis = any((build_number, branch,))
version = config.__version__.split('.')
develop_status = '4 - Beta'
url = 'http://lexycore.github.io/django-rester'

if travis:
    version = version[0:3]
    if branch == 'master':
        develop_status = '5 - Production/Stable'
        version.append(build_number)
    else:
        version.append('{}{}'.format('dev' if branch == 'develop' else branch, build_number))
else:
    if len(version) < 4:
        version.append('local')

version = '.'.join(version)
if travis:
    with open('django_rester/config.py', 'w', encoding="utf-8") as f:
        f.write("__version__ = '{}'".format(version))

try:
    import pypandoc

    print("Converting README...")
    long_description = pypandoc.convert('README.md', 'rst')
    if branch:
        long_description = long_description.replace('django-rester.svg?branch=master', 'django-rester.svg?branch={}'.format(branch))

except (IOError, ImportError, OSError):
    print("Pandoc not found. Long_description conversion failure.")
    with open('README.md', encoding="utf-8") as f:
        long_description = f.read()
else:
    print("Saving README.rst...")
    try:
        if len(long_description) > 0:
            with open('README.rst', 'w', encoding="utf-8") as f:
                f.write(long_description)
            if travis:
                os.remove('README.md')
    except:
        print("  failed!")

setup(
    name='django-rester',
    version=version,
    description='Django REST API build helper',
    license='MIT',
    author='Sergei Kovalev',
    author_email='zili.tnd@gmail.com',
    url=url,
    long_description=long_description,
    download_url='https://github.com/lexycore/django-rester.git',
    classifiers=[
        'Development Status :: {}'.format(develop_status),
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords=[
        'development',
        'API',
    ],
    packages=[
        'django_rester',
        'django_rester.rester_jwt',
    ],
    setup_requires=[
        'wheel',
        'pypandoc',
    ],
    tests_require=[
        'pytest',
    ],
    install_requires=[
        'django',
        'pyjwt',
        'django-rediser',
    ],
    package_data={
        '': [
            '../LICENSE',
        ],
    },
)