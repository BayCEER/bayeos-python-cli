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

class CliTest(unittest.TestCase):
    
    def setUp(self):
        self.cli = SimpleClient()
    
    def tearDown(self):
        pass    
    
    def testListConnections(self):        
        # List connection information and exit 
        self.cli.connect(listConnections=True)            
        
    def testConnect(self):                                                                                       
        # Save and open connection information            
        self.assertEqual(True, self.cli.connect(url,user,password,save_as="myAlias"),"Connect failed")
        self.assertIsNotNone(self.cli.getVersion(), "Failed to get version")        
        self.assertTrue(self.cli.disconnect(), "Failed to disconnect")        
        
        # Reuse connection by alias                  
        self.assertEqual(True, self.cli.connect("myAlias"),"Connect failed")
        self.assertIsNotNone(self.cli.getVersion(), "Failed to get version")        
        self.assertTrue(self.cli.disconnect(), "Failed to disconnect")
    
    def testSimple(self):
        # Open connection without file access                                  
        self.assertEqual(True, self.cli.connect(url,user,password),"Connect failed")        
        self.assertIsNotNone(self.cli.getVersion(), "Failed to get version")
        self.assertTrue(self.cli.disconnect(), "Failed to disconnect")
            
        
    def testCreateDeleteSeries(self):
        """ 
            CRUD Example with response validation
        """
        
        # Connect
        self.assertEqual(True, self.cli.connect(url,user,password),"Connect failed")                                     
        
        # Create
        ids = [self.cli.createSeries("Dummy" + x) for x in ["A","B","C"] ]
        
        ## print(ids)
        
        # Truncate microseconds because server sends seconds back  
        now = datetime.datetime.utcnow()
        now -= datetime.timedelta(microseconds=now.microsecond)
                
        # Write                             
        dataIn  = [[pytz.utc.localize(now),121.1,122.2,123.3]]                 
        self.cli.writeSeries(ids,dataIn)
        
        # Read                 
        (header, dataOut) = self.cli.getSeries(ids,interval='today')                
        self.assertEqual(["DummyA","DummyB","DummyC"], header, "Invalid header response")        
        self.assertEqual(dataIn[0][0], dataOut[0][0], "Invalid date data")        
        for x in range(1,3):
            self.assertAlmostEqual(dataIn[0][x],dataOut[0][x],msg="Invalid record response",delta=0.1)                                
        
        # Delete 
        [self.cli.deleteSeries(x) for x in ids]                
        self.assertTrue(self.cli.disconnect(), "Failed to disconnect")
    
    def testNaNValues(self):
        # Connect
        self.assertEqual(True, self.cli.connect(url,user,password),"Connect failed")
        
        # Create
        id = self.cli.createSeries("Dummy NaN")
                
        # Truncate microseconds because server sends seconds back  
        t0 = datetime.datetime.utcnow()
        t0 -= datetime.timedelta(microseconds=t0.microsecond)        
        t0 = pytz.utc.localize(t0)
        t1 = t0 + datetime.timedelta(seconds=60)
                
        # Write Series with NaN values                           
        dataIn  = [[t0,float('nan')],[t1,12.9]]                 
        self.cli.writeSeries([id],dataIn)        
        
        # Read                 
        (header, dataOut) = self.cli.getSeries(id,interval='today')
        
        # Expect NaN values to be skipped 
        self.assertEqual(len(dataOut),1)                                             
        self.assertEqual(dataIn[1][0], dataOut[0][0], "Invalid date data")
        self.assertAlmostEqual(dataIn[1][1], dataOut[0][1], msg="Invalid record response",delta=0.1)
                
        # Delete 
        self.cli.deleteSeries(id)               
        self.assertTrue(self.cli.disconnect(), "Failed to disconnect")        
             
    def testPWD(self):                
        self.assertEqual(True, self.cli.connect(url,user,password),"Connect failed")        
        self.cli.pwd()
        self.cli.ls()   
        self.assertTrue(self.cli.disconnect(), "Failed to disconnect")  
    
    def testFindOrCreateSeries(self):
        # Connect
        self.assertEqual(True, self.cli.connect(url,user,password),"Connect failed")
        
                
        # Create Series 
        ids = [self.cli.findOrCreateSeries("/testFolder/" + x) for x in ["A","B","C"] ]        
        self.assertTrue(len(ids)==3,'Invalid function response')
        
        # Find Series only 
        ids = [self.cli.findOrCreateSeries("/testFolder/" + x) for x in ["A","B","C","D"] ]
        self.assertTrue(len(ids)==4,'Invalid function response')  
        
        [self.cli.deleteSeries(x) for x in ids]                
        self.assertTrue(self.cli.disconnect(), "Failed to disconnect")
              
    def testUTCHandling(self):
       # Without tz := UTC
       self.assertEqual(True, self.cli.connect(url,user,password),"Connect failed")
       id = self.cli.findOrCreateSeries("/testFolder/utc")
       self.assertGreater(id,0)      
      
       self.cli.writeSeries([id],[[datetime.datetime(2019, 10, 24, 12, 20, 11),1.0]])
       # Get series
       (header, dataOut) = self.cli.getSeries(id,start='2019-10-24 12:20:11',until='2019-10-24 12:20:12')
       print("Output:",dataOut)

       self.cli.deleteSeries(id)
       self.cli.disconnect()
    
       
    #def testGMTHandling(self):
        # GMT-1
        #tz = pytz.timezone('Etc/GMT-1')
        #t_tz = tz.localize(datetime.datetime(2019, 11, 1, 12, 20, 11))
        #self.cli.writeSeries([id],[[t_tz,2.0]])


if __name__ == "__main__":
    unittest.main()
