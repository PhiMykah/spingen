from setuptools import setup,find_packages

setup(name='spingen',
    version='0.7.5',
    packages=find_packages(), 
    install_requires=[
        'nmrsim',
        'numpy',
    ],
    entry_points={
        'console_scripts': [
            'spingen = spingen.main:main',
        ]
    },
    author='Micah Smith',
    author_email='mykahsmith21@gmail.com',
    description='Python implementation of Nuclear Magnetic \
                Resonance (NMR) signal analysis program \'nmrPipe\''
)