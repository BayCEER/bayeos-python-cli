from setuptools import setup

setup(name='bayeos-python-cli',
      version='0.1',
      description='A simple bayeoes-server client',
      url='http://github.com/BayCEER/bayeos-python-cli',
      author='Oliver Archner',
      author_email='oliver.archner@uni-bayreuth.de',
      license='GPL2',
      packages=['bayeos'],
      package_dir = {'': 'src'},
      zip_safe=False)

