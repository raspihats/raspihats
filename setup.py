from sys import argv
from os import chdir
from setuptools import setup

if "install" in argv:
    chdir("clk_stretch")
    exec(open("clk_stretch.py").read())
    chdir("..")
    


setup( name             = 'raspihats',
       version          = '1.0.0',
       description      = 'package for controlling raspihats.com boards',
       long_description = open('README.md').read(),
       license          = open('LICENSE').read(),
       url              = 'https://github.com/raspihats/raspihats',
       author           = 'Florin Costa',
       author_email     = 'hardhat@raspihats.com',
       keywords         = 'Raspberry Pi hats add-on boards',
       packages         = ['raspihats'],
       classifiers      = ['Development Status :: 5 - Production/Stable',
                           'Operating System :: POSIX :: Linux',
                           'License :: OSI Approved :: MIT License',
                           'Intended Audience :: Developers',
                           'Intended Audience :: Education',
                           'Programming Language :: Python :: 2.7',
                           'Programming Language :: Python :: 3',
                           'Topic :: Software Development',
                           'Topic :: Home Automation',
                           'Topic :: System :: Hardware'],
)
