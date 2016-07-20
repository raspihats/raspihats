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
        except Exception as e:
            print ("Warning: clock stretch timeout setup failed! " + str(e))
        finally:
            chdir(cwd)
            install.run(self) 

setup(
    name             = 'raspihats',   
    version          = '1.1.1',
    description      = 'package for controlling raspihats.com boards',
    long_description = open('README.rst').read(),
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
    cmdclass         = { 'install': ClockStretchTimeoutInstall },
)
