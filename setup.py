from setuptools import setup, find_packages

__version__ = '0.1.0'

def read(filename):
    with open(filename) as f:
        return f.read()

setup(
    name = 'wowclient',
    version = __version__,
    description = 'client library for WoW Community API',
    long_description = read('README.md'),
    author = 'Jon Moore',
    url = 'https://github.com/jonm/wowecon-wowclient',
    packages = find_packages(),
    include_package_data = True,
    install_requires = [
        'requests==2.21.0'
    ],
    license='GPLv3'
)