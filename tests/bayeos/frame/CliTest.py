'''
Created on 19.11.2015
@author: oliver
'''
import unittest
import os

from bayeos.frame.cli import FrameClient

user = "root"
password = "bayeos"
url = "http://bayconf/BayEOS-Server/XMLServlet"



class CliTest(unittest.TestCase):
    
    curDir = os.path.dirname(__file__)
    
    def setUp(self):        
        self.cli = FrameClient()
        self.assertEqual(True, self.cli.connect(url,user,password),"Connect failed")
    
    def tearDown(self):
        self.cli.disconnect()    
        
    def testReadNode(self):
        id = self.cli.createSeries("A")
        node = self.cli.getNode(id)        
        self.assertEqual(id,node["id"])
        print(node) 
        self.cli.deleteSeries(id)
    
    def testImportToa5(self):
        # TODO Create Series dynamically
        columns = ['Ts_top_Avg','dH2O_C_Avg']        
        ids = [self.cli.createSeries(x) for x in columns] 
        filePath = os.path.join(self.curDir,"..","..","resources","avg_top.csv")        
        df = self.cli.read_toa5(filePath,"Etc/GMT-1")
        self.cli.writeFrame(ids, df[columns])
        (header, dataOut) = self.cli.getSeries(ids, '2015-11-17 00:00:00','2015-11-17 17:33:00')                         
        self.assertEqual(columns, header, "Invalid header response")                
        self.assertEqual(1054,len(dataOut), "Invalid data length")                                
        [self.cli.deleteSeries(x) for x in ids]

if __name__ == "__main__":
   
    unittest.main()
