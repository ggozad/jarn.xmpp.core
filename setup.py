from setuptools import setup, find_packages
import os

version = '0.1'

setup(name='plone.messaging.core',
      version=version,
      description="Core package for plone.messaging",
      long_description=open("README.txt").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      # Get more strings from http://pypi.python.org/pypi?%3Aaction=list_classifiers
      classifiers=[
        "Framework :: Plone",
        "Programming Language :: Python",
        ],
      keywords='',
      author='Yiorgis Gozadinos',
      author_email='ggozad@jarn.com',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(),
      namespace_packages=['plone', 'plone.messaging'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'plone.messaging.twisted',
          'pas.plugins.userdeletedevent',

          # -*- Extra requirements: -*-
      ],
      extras_require = {
          'test': [
                  'plone.app.testing',
              ]
      },
      entry_points="""
      # -*- Entry points: -*-

      [z3c.autoinclude.plugin]
      target = plone
      """,
      )
