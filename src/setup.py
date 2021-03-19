from setuptools import setup, find_packages

import os
def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

extra_files = package_files('ecldoc/Templates')

setup(
    name="ecldoc",
    version="1.0",
    packages=find_packages(),
    install_requires=['Jinja2==2.11.3', 'lxml==3.8.0'],
    package_data={'': extra_files},
   	scripts=['bin/ecldoc']
)
