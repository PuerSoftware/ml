from setuptools import setup, find_packages
from version    import Version


setup(
    name='puerml',
    version=Version.get(),
    packages=find_packages(),
    install_requires=[],
)
