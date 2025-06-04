#!/usr/bin/env python3
"""
Setup script for CybrScan - Refactored Version
"""

from setuptools import setup, find_packages
import os

# Read README file
def read_file(filename):
    with open(filename, 'r', encoding='utf-8') as f:
        return f.read()

# Read requirements
def read_requirements():
    with open('requirements.txt', 'r', encoding='utf-8') as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='cybrscan',
    version='1.0.0',
    description='Security Scanning Platform',
    long_description=read_file('README.md') if os.path.exists('README.md') else '',
    long_description_content_type='text/markdown',
    author='CybrScan Team',
    author_email='admin@cybrscan.com',
    url='https://github.com/cybrscan/cybrscan',
    packages=find_packages(where='src'),
    package_dir={'': 'src'},
    python_requires='>=3.8',
    install_requires=read_requirements(),
    extras_require={
        'dev': [
            'pytest>=6.0.0',
            'pytest-cov>=2.10.0',
            'black>=21.0.0',
            'flake8>=3.8.0',
            'isort>=5.0.0',
        ],
    },
    entry_points={
        'console_scripts': [
            'cybrscan=main:main',
        ],
    },
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
    ],
    include_package_data=True,
    package_data={
        'cybrscan': [
            'templates/**/*.html',
            'static/**/*',
        ],
    },
)