from distutils.core import setup
from setuptools import find_packages

setup(
    name='foodScan',
    version='0.1.0',
    packages=find_packages(),
    url='',
    license='MIT',
    author='Daniel Breitlauch',
    author_email='github@flying-stampe.de',
    description='A barcode scanner adds items to wunderlist. '
                'Items on the wunderlist are put into the online shop cart.',
    dependency_links=['https://github.com/danielBreitlauch/wunderpy2/zipball/master#egg=wunderpy2'],
    install_requires=[
        'requests',
        'wunderpy2',
        'bs4',
        'selenium',
        'pysimplelog',
        'werkzeug'
    ],
    long_description=open('README.md').read(),
    keywords=['online food shop', 'home automation', 'codecheck', 'wunderlist', 'barcode', 'anti captcha']
)
