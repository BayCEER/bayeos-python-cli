# Simple Read Data Example 
# API Doc http://bayceer.github.io/bayeos-python-cli/api/bayeos.cli.html

from bayeos.cli import SimpleClient
bayeos = SimpleClient()
bayeos.connect(url="https://bayeos.bayceer.uni-bayreuth.de/BayEOS-Server/XMLServlet",user="gast",password="gast")

# Set current directory 
bayeos.cd(14294)

# Fetches up to ten channels in current directory 
(header, data) = bayeos.getSeries(interval='today')

# Close connection
bayeos.disconnect()
