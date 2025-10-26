from setuptools import setup, find_packages

setup(
    name='unique-fname',
    version='0.1.0',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'unique-fname = unique_fname.main:main',
        ],
    },
)
