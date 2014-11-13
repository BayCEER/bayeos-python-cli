'''
Created on 12.08.2014

@author: oliver
'''
import unittest
import os

from bayeos import connectionFile
from tempfile import mkdtemp



class ConnectionFileTest(unittest.TestCase):

    def setUp(self):                
        self.tempDir = mkdtemp()
        print("Created temp folder:" + self.tempDir)
                
    def tearDown(self): 
        for myfile in os.listdir(self.tempDir):
            os.remove(self.tempDir + os.sep + myfile)       
        os.rmdir(self.tempDir)
        print("Removed temp folder:" + self.tempDir)
    
    def testWriteRead(self):
        
        alias = "bayceer"
        url = "http://www.bayceer.uni-bayreuth.de/BayEOS-Server/XMLServlet"
        user = "root"
        password = "bayeos"
        
        self.assertTrue(connectionFile.write(alias, url, user, password, self.tempDir),"Failed to write file")
        con = connectionFile.read(alias, self.tempDir)        
        
        self.assertEqual(url,con[0],"Wrong URL")
        self.assertEqual(user,con[1],"Wrong user")
        self.assertEqual(password,con[2],"Wrong password")
        
        
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()