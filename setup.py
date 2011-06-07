# -*- coding: utf-8 -*-
"""
This module contains the tool of av.rssnews
"""
import os
from setuptools import setup, find_packages

NAME = 'av.rssnews'
PATH = NAME.split('.') + ['version.txt']
VERSION = open(os.path.join(*PATH)).read().strip()
DESCRIPTION = (open("README.txt").read() + "\n" +
               open(os.path.join("docs", "HISTORY.txt")).read())

tests_require = ['zope.testing']

setup(name=NAME,
      version=VERSION,
      description="",
      long_description=DESCRIPTION,
      # Get more strings from
      # http://pypi.python.org/pypi?:action=list_classifiers
      classifiers=[
        'Framework :: Plone',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        ],
      keywords='',
      author='',
      author_email='',
      url='http://svn.plone.org/svn/collective/',
      license='GPL',
      packages=find_packages(exclude=['ez_setup']),
      namespace_packages=['av', ],
      include_package_data=True,
      zip_safe=False,
      install_requires=['setuptools',
                        # -*- Extra requirements: -*-
                        'Products.cron4plone',
                        ],
      tests_require=tests_require,
      extras_require=dict(tests=tests_require),
      test_suite='av.rssnews.tests.test_docs.test_suite',
      entry_points="""
      # -*- entry_points -*-
      [z3c.autoinclude.plugin]
      target = plone
      """,
      setup_requires=["PasteScript"],
      paster_plugins=["ZopeSkel"],
      )
