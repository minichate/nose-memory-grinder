from setuptools import setup, find_packages

setup(
    name='nose-memory-grind',
    version="0.0.1",
    install_requires=['nose>=1.2.1'],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    entry_points = {
        'nose.plugins.0.10': [
            'memorygrind = memorygrind:MemoryGrindPlugin'
            ]
        },
    )
