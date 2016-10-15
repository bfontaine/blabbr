# -*- coding: UTF-8 -*-

from setuptools import setup

# http://stackoverflow.com/a/7071358/735926
import re
VERSIONFILE='blabbr/__init__.py'
verstrline = open(VERSIONFILE, 'rt').read()
VSRE = r'^__version__\s+=\s+[\'"]([^\'"]+)[\'"]'
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % VERSIONFILE)

setup(
    name='blabbr',
    version=verstr,
    author='Baptiste Fontaine',
    author_email='b@ptistefontaine.fr',
    packages=['blabbr'],
    url='https://github.com/bfontaine/blabbr',
    license=open('LICENSE', 'r').read(),
    description='Twitter bot',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
    ],
    entry_points={
        'console_scripts':[
            'blabbr = blabbr.cli:cli',
        ]
    },
)
