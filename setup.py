from ez_setup import use_setuptools
use_setuptools()

from setuptools import setup, find_packages

setup(
    name='TheBigBangTheory',
    version="1.0",
    description="The Big Bang Theory plugin for TVD dataset",
    author="Anindya Roy",
    packages=find_packages(),
    include_package_data=True,
    install_requires=["tvd>=0.2"],
    entry_points="""
        [tvd.series]
        TheBigBangTheory=TheBigBangTheory:TheBigBangTheory
    """
)
