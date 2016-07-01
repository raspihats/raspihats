import sys
import os
from distutils.core import setup

if "install" in sys.argv:
    os.chdir('clk_stretch')
    execfile('clk_stretch.py')
    os.chdir('..')

setup(
    name='raspihats',
    description='library for raspihats.com boards',
    version='1.0',
    packages=['raspihats'],
    author='Florin Costa',
    author_email='hardhat@raspihats.com',
    url='https://www.raspihats.com/',
    license=open('LICENSE').read(),
    long_description=open('README.md').read(),
    # ext_modules = [set_module]
)
