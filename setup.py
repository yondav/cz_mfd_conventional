from setuptools import setup, find_packages


setup(
    name='cz_mfd_conventional',
    version='0.1.0',
    py_modules=['cz_mfd_conventional'],
    license='Not open source',
    long_description='conventional commits configured for marketfuel',
    install_requires=['commitizen'],
    entry_points={
    'commitizen.plugins': [
        'cz_mfd_conventional = cz_mfd_conventional:mfd_conventional',
    ],
},
)