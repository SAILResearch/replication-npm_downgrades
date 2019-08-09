from setuptools import setup, find_packages

setup (
       name='npm_parser',
       version='0.1',
       packages=find_packages(),

       install_requires=['kids.cache', 'parsimonious'],

       author='Filipe Cogo',
       author_email='cogo@cs.queensu.ca',

       summary = 'Package for parsing semantic version and npm ranges',
       )
