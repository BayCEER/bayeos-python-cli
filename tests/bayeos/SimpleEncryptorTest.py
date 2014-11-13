'''
Created on 13.08.2014

@author: oliver
'''
import unittest
from bayeos import simpleEncryptor


class SimpleEncryptorTest(unittest.TestCase):
    
    key = "69383743459319518275589758784885."
    encrypted = "VFhKXVxE"        
    decrypted = "bayeos"
        

    def testEncryptor(self):        
        self.assertEqual(self.encrypted,simpleEncryptor.encrypt(self.key, self.decrypted) , 'Wrong encryption result')        
        
    def testDecryptor(self):                
        self.assertEqual(self.decrypted,simpleEncryptor.decrypt(self.key, self.encrypted) , 'Wrong decryption result')
    

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'SimpleEncryptorTest.testEncrypt']
    unittest.main()