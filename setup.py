import os

import setuptools

module_path = os.path.join(os.path.dirname(__file__), 's3_saver.py')
version_line = [line for line in open(module_path)
                if line.startswith('__version__')][0]

__version__ = version_line.split('__version__ = ')[-1][1:][:-2]

setuptools.setup(
    name="s3-saver",
    version=__version__,
    url="https://github.com/Jaza/s3-saver",

    author="Jeremy Epstein",
    author_email="jazepstein@gmail.com",

    description="Utility class in Python for finding, saving, and deleting files that are either on Amazon S3, or on the local filesystem.",
    long_description=open('README.rst').read(),

    py_modules=['s3_saver'],
    zip_safe=False,
    platforms='any',

    install_requires=['boto'],

    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
    ],
)
