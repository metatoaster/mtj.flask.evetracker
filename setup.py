from setuptools import setup, find_packages
import os

version = '0.0'

setup(name='mtj.flask.evetracker',
      version=version,
      description="MTJ Flask implementation of pos tracker",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.rst")).read(),
      # Get more strings from http://www.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Programming Language :: Python",
        "Topic :: Software Development :: Libraries :: Python Modules",
        ],
      keywords='',
      author='Tommy Yu',
      author_email='y@metatoaster.com',
      url='https://github.com/metatoaster/mtj.flask.evetracker',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['mtj', 'mtj.flask'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          # -*- Extra requirements: -*-
          'flask',
          'passlib',
          'mtj.eve.tracker',
      ],
      entry_points="""
      # -*- Entry points: -*-
      """,
      )
