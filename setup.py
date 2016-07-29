import os
from io import open
from setuptools import setup

DIST_NAME = 'PTCAccount'
VERSION = '0.0a1'
AUTHOR = 'James Payne'
EMAL = 'jepayne1138@gmail.com'
GITHUB_USER = 'jepayne1138'
GITHUB_URL = 'https://github.com/{GITHUB_USER}/{DIST_NAME}'.format(**locals())

# Get the long description from the README file
setup_dir = os.path.dirname(os.path.realpath(__file__))
with open(os.path.join(setup_dir, 'README.rst'), encoding='utf-8') as readme:
    long_description = readme.read()

setup(
    name=DIST_NAME,
    packages=['ptcaccount'],
    version=VERSION,
    description='Automatic creation of Pokémon Trainer Club accounts.',
    author=AUTHOR,
    author_email=EMAL,
    url=GITHUB_URL,
    license='BSD-new',
    download_url='{GITHUB_URL}/tarball/{VERSION}'.format(**locals()),
    keywords='',
    install_requires=[
        'requests==2.10.0',
        'six==1.10.0',
    ],
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'License :: OSI Approved :: BSD License',
    ],
    entry_points={
        'console_scripts': [
        ],
    }
)
