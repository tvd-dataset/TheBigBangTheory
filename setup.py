from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
    name='GameOfThrones',
    version="1.0",
    description="Game of Thrones plugin for TVD dataset",
    author="Herve Bredin",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["tvd>=0.2"],
    entry_points="""
        [tvd.series]
        GameOfThrones=GameOfThrones:GameOfThrones
    """
)
