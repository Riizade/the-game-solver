from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='the-game',
    version='0.1.0',
    description='simulator for The Game by Pandasaurus Games',
    long_description=readme,
    author='riizade',
    author_email='riizade@gmail.com',
    url='https://github.com/Riizade/the-game-solver',
    license=license,
    packages=find_packages(exclude=('test', 'docs'))
)