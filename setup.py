from setuptools import setup, find_packages

with open("requirements.txt", "r", encoding="utf-8") as file:
    requirements = file.readlines()

setup(
    name='sybil_engine',
    version='1.0.7',
    py_modules=['sybil_engine'],
    packages=find_packages(),
    install_requires=requirements,
    author='Arsenii Venherak',
    author_email='indeooars@gmail.com',
    description='Engine for web3 smart contracts automatisation.',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    url='https://github.com/Indeoo/sybil-engine/CHANGELOG.md',
)