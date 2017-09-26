from sys import argv
from os import chdir, getcwd, system
from setuptools import setup
from setuptools.command.install import install

# Build and install the clock stretch timeout script automatically during setup
class ClockStretchTimeoutInstall(install):
    def run(self):
        cwd = getcwd()
        try:
            chdir("clk_stretch/")
            system("python clk_stretch.py")
        finally:
            chdir(cwd)
            install.run(self)

setup(
    name             = 'raspihats',
    version          = '2.2.3',
    description      = 'package for controlling raspihats.com boards',
    long_description = open('README.rst').read(),
    license          = open('LICENSE').read(),
    url              = 'https://github.com/raspihats/raspihats',
    author           = 'Florin COSTA',
    author_email     = 'hardhat@raspihats.com',
    keywords         = 'Raspberry Pi hats add-on boards',
    packages         = ['raspihats', 'raspihats/i2c_hats'],
    install_requires = ['enum34;python_version<"3.4"'],
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
    cmdclass         = { 'install': ClockStretchTimeoutInstall },
)
