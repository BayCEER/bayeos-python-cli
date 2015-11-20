try:
    from setuptools import setup
except ImportError:
	from distutils.core import setup 

setup(name='bayeos-python-cli',
      version='1.3',
      description='A simple bayeoes-server client',
      url='http://github.com/BayCEER/bayeos-python-cli',
      author='Oliver Archner',
      author_email='oliver.archner@uni-bayreuth.de',
      license='GPL2',
      packages=['bayeos'],
      package_dir = {'': 'src'},
      install_requires=[
        'pytz'
      ])


setup(name='bayeos-python-frame',
      version='1.3',
      description='A bayeoes-server frame client',
      url='http://github.com/BayCEER/bayeos-python-frame',
      author='Oliver Archner',
      author_email='oliver.archner@uni-bayreuth.de',
      license='GPL2',
      packages=['bayeos.frame', ],
      package_dir = {'': 'src'},
      install_requires=[
        'pytz',
        'numpy',
        'pandas'
      ]
      )
