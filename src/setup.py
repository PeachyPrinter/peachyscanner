
#!/usr/bin/env python
from setuptools import setup
import glob
from VERSION import version

setup(name='PeachyScanner',
      version=version,
      description='Peachy Scanner Software for Scanning objects',
      author='Peachy Printer Inc.',
      author_email='development@peachyprinter.com',
      url='www.peachyprinter.com',
      packages=[],
      py_modules=['VERSION'],
      install_requires=['cython==0.21.1', 'numpy==1.10.1', 'kivy==1.9.0',],      data_files=[],
      include_package_data=True
     )
