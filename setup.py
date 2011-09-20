from setuptools import setup, find_packages
import os

version = '0.1b4'

setup(name='jarn.xmpp.core',
      version=version,
      description="Core package for jarn.xmpp",
      long_description=open("README.rst").read() + "\n" +
                       open(os.path.join("docs", "HISTORY.txt")).read(),
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Plone",
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        ],
      keywords='plone xmpp twisted microblogging',
      author='Yiorgis Gozadinos',
      author_email='ggozad@jarn.com',
      url='https://github.com/ggozad/jarn.xmpp.core',
      license='GPL',
      packages=find_packages(),
      namespace_packages=['jarn', 'jarn.xmpp'],
      include_package_data=True,
      zip_safe=False,
      install_requires=[
          'setuptools',
          'BeautifulSoup',
          'plone.app.registry',
          'plone.app.z3cform',
          'pas.plugins.userdeletedevent',
          'jarn.xmpp.twisted',
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
