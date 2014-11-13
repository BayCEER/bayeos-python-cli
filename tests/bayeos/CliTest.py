'''
Created on 11.08.2014
@author: oliver
'''
import unittest, datetime, struct
from bayeos.cli import SimpleClient as cli

user = "root"
password = "bayeos"
url = "http://bayeos-master/BayEOS-Server/XMLServlet"


class CliTest(unittest.TestCase):
    
    def setUp(self):
        self.cli = cli()
    
    def tearDown(self):
        pass
    
    
    def testListConnections(self):        
        # List connection information and exit 
        self.cli.connect(listConnections=True)            
        
    
    def testConnect(self):                                                                                       
        # Save and open connection information            
        self.assertEqual(True, self.cli.connect(url,user,password,save_as="myAlias",verbose=True),"Connect failed")
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
        
    def testAddByteValues(self):
        """
            Create a series and add a row 
        """
        self.assertEqual(True, self.cli.connect(url,user,password),"Connect failed")
        id = self.cli.createSeries("Dummy with one record")                 
        self.cli.getProxy().MassenTableHandler.upsertByteRows(struct.pack('>iqf',id,1415606942969,12.0))
        self.cli.deleteSeries(id)
        self.assertTrue(self.cli.disconnect(), "Failed to disconnect")
        
    def testCreateDeleteSeries(self):
        """ 
            CRUD Example with response validation
        """
        
        # Connect
        self.assertEqual(True, self.cli.connect(url,user,password),"Connect failed")                                     
        
        # Create
        ids = [self.cli.createSeries("Dummy" + x) for x in ["A","B","C"] ]
        
        # Truncate microseconds because server sends seconds back  
        now = datetime.datetime.utcnow();
        now -= datetime.timedelta(microseconds=now.microsecond)
                
        # Write                             
        dataIn  = [[now,121.1,122.2,123.3]]                 
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
             
        
    def testPWD(self):                
        self.assertEqual(True, self.cli.connect(url,user,password),"Connect failed")        
        self.cli.pwd()
        self.cli.ls()   
        self.assertTrue(self.cli.disconnect(), "Failed to disconnect")             

if __name__ == "__main__":
   
    unittest.main()
