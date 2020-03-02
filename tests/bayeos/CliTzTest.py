'''
Created on 11.08.2014
@author: oliver
'''

import unittest, datetime
import pytz
from bayeos.cli import SimpleClient

user = "root"
password = "bayeos"
url = "http://localhost:5532/XMLServlet"

class CliTzTest(unittest.TestCase):
    
    def setUp(self):
        self.cli = SimpleClient()
        self.cli.connect(url,user,password)
    
    def tearDown(self):
        self.cli.disconnect()
              
    def testUTC(self):
       ts0 = pytz.utc.localize(datetime.datetime(2019, 10, 24, 12, 20, 11))
       ts1 = pytz.utc.localize(datetime.datetime(2019, 12, 24, 12, 20, 11))
       
       id = self.cli.findOrCreateSeries("/testFolder/utc")
       
       self.assertGreater(id,0)                   
       self.cli.writeSeries([id],[[ts0,1.0],[ts1,2.0]])       
                     
       (header, dataOut) = self.cli.getSeries(id,start=ts0,until=ts1)       

       self.assertEqual(ts0,dataOut[0][0])  
       self.assertEqual(1.0,dataOut[0][1])  
       
       self.assertEqual(ts1,dataOut[1][0])
       self.assertEqual(2.0,dataOut[1][1])
       
       self.cli.deleteSeries(id)
       
if __name__ == "__main__":
    unittest.main()
