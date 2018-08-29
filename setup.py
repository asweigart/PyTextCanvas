from setuptools import setup
import os

here = os.path.abspath(os.path.dirname(__file__))

# Get the long description from the README file
with open(os.path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='PyTextCanvas',
    version=__import__('pytextcanvas').__version__,
    url='https://github.com/asweigart/pytextcanvas',
    author='Al Sweigart',
    author_email='al@inventwithpython.com',
    description=('PyTextCanvas is a module for writing text and ascii art to a 2D string "canvas" in Python.'),
    license='BSD',
    long_description=long_description,
    packages=['pytextcanvas'],
    test_suite='tests',
    install_requires=['pybresenham'],
    keywords="text canvas bresenham line circle drawing 2D geometry shapes vector bitmap rotate rotation vector2bitmap",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Win32 (MS Windows)',
        'Environment :: X11 Applications',
        'Environment :: MacOS X',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.1',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7'
    ],
)