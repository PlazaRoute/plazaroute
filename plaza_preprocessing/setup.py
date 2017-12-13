from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()


setup(
    name='plaza_preprocessing',
    version='0.0.1',
    description='Plaza preprocessing for PlazaRoute',
    long_description=readme,
    author='Jonas Matter, Robin Suter',
    author_email='robin@robinsuter.ch',
    url='https://github.com/PlazaRoute/PlazaRoute',
    license="AGPLv3",
    packages=find_packages(exclude=('tests', 'docs', 'scheduled')),
    install_requires=['osmium', 'Shapely', 'geojson', 'networkx', 'Rtree', 'jsonschema', 'ruamel.yaml'],
    entry_points={
        'console_scripts': [
            'plaza_preprocessing=plaza_preprocessing.__main__:plaza_preprocessing'
        ]
    }

)
