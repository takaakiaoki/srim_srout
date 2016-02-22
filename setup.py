import os
from setuptools import setup, find_packages

ver_file = os.path.join('srim_srout', 'version.py')
vars = {}
exec(open(ver_file).read(), vars)

setup(
    name="srim_srout",
    version=vars['__version__'],
    description="Tools for SRIM SR output",
    long_description=open('README.rst').read(),
    author="Takaaki AOKI",
    author_email="aoki.takaaki.6v@kyoto-u.ac.jp",
    url="https://github.com/takaakiaoki/srim_srout/",
    # download_url = "https://github.com/takaakiaoki/srim_srout/",
    packages=find_packages(),
    # package_dir={'srim_srout': 'srim_srout'},
    # package_data={},
    # include_package_data=True,
    entry_points={
        'console_scripts':[
            'srim-srout-parse = srim_srout.parser:main']},
    # options={},
    zip_safe=False,
    # install_requires=[],
    # test_suite='tests',
    # This next part it for the Cheese Shop, look a little down the page.
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
        "License :: OSI Approved :: MIT License",
        "Development Status :: 4 - Beta",
        "Environment :: Other Environment",
        "Intended Audience :: Science/Research",
        "Operating System :: OS Independent",
        "Operating System :: Microsoft :: Windows :: Windows 7",
        "Topic :: Scientific/Engineering :: Physics"])
