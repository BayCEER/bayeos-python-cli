set PY3=C:\Python34
set PY2=C:\Python278

SET PATH=%PY3%
python setup.py install 
python tests\bayeos\CliTest.py

SET PATH=%PY2%
python setup.py install 
python tests\bayeos\CliTest.py




