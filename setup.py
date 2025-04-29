from setuptools import setup, find_packages

import os



def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


extra_files = package_files('ecldoc/Templates')
print(extra_files)
setup(
    name="ecldoc",
    version="1.0.3",
    packages=find_packages(),
    install_requires=['Jinja2==3.1.6', 'lxml==4.9.0'],
    package_data={'': extra_files},
    scripts=['bin/ecldoc'],
    url="https://github.com/lilyclemson/ECLDocGenerator",
)

