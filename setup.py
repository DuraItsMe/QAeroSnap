from setuptools import setup, find_packages

setup(
    name='QAeroSnap',
    version='1.1.0',
    packages=find_packages(),
    install_requires=[
        'PyQt6',
        'pywin32'
    ],
    description='Aero Snap Implementation for PyQt6',
    author='Dura',
    url='https://github.com/DuraItsMe/QAeroSnap',
)