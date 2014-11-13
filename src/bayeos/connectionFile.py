'''
Created on 12.08.2014
@author: oliver
'''
import os
import platform
from bayeos import simpleEncryptor
from os import path
import random
import string

KEY_LENGTH=32

def read(alias, path=None):
    """ Read connection information from file and return list: [url, user, password] """          
    return readConnections(path)[alias]    


def readConnections(path=None):
    """ Returns connection information as a dictionary """
    if not path:
        path = getHomePath()           
    key = _readKey(getKeyPath(path))
    if key:        
        return _readConnections(key,getConnectionPath(path))
    else:
        return {}
        
    

def write(alias,url,user,password='', path=None):        
    """ Write connection information to file """
    if not path:
        path = getHomePath() 
    keyFile = getKeyPath(path)         
    key = _readKey(keyFile)
    if not key:        
        key = _writeKey(keyFile)
        if not key: raise Exception("Failed to create key file")
        
    conFile = getConnectionPath(path)    
    cons = _readConnections(key,conFile)
    cons[alias] = [url,user,password]
    _writeConnections(key,conFile,cons)    
    return True
    
def _readKey(keyFile):
    """ Reads key from file and returns key as string """    
    if not path.isfile(keyFile):
        return None
    file = open(keyFile)    
    key = file.read()
    file.close()
    return key

def _writeKey(keyFile):
    """ Writes key to file and returns key as string """
    file = open(keyFile, "w")                
    key = ''.join(random.choice(string.ascii_lowercase) for i in range(KEY_LENGTH))    
    file.write(key)
    file.close()
    return key 

def getConnectionPath(path):
    """ Gets path of connection file as string """
    return path + os.sep + ".bayeos.pwd"
    
def getKeyPath(path):
    """ Gets path of key file as string """
    return path + os.sep + ".bayeos.pwd_key"

def getHomePath():    
    """ Gets default path location for key and connection file"""
    p = path.expanduser("~")
    if (platform.system() == 'Windows'): p = p + "\Documents"
    return p



def _readConnections(key,conFile):
    """ Reads connections form file and returns information as dictionary with values as list:[url,user,password]"""
    cons = {}    
    
    if not path.isfile(conFile):
        return cons
               
    file = open(conFile)
    for line in file:
            v = line.split(None,4)
            if (len(v)==3):
                cons[v[0]] = [v[1],v[2],None]
            elif (len(v)==4):
                cons[v[0]] = [v[1],v[2],simpleEncryptor.decrypt(key, v[3])]
            else:
                file.close() 
                raise Exception("Invalid file format: " + file)
    file.close()
    return cons

def _writeConnections(key, conFile, cons):
    """ Writes connections to file """
    file = open(conFile, "w")
    for alias, con in cons.items():
        if len(con)>1:             
            file.write(alias)                
            file.write(" " + con[0])
            file.write(" " + con[1])
            if con[2]:
                file.write(" " + simpleEncryptor.encrypt(key, con[2]))        
            file.write("\n")
    file.close()    
   

