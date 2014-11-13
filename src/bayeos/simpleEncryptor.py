import base64

def encrypt(key, value):         
    return base64.b64encode(_xor(key,value)).decode()
    
def decrypt(key, value):
    return _xor(key,base64.b64decode(value).decode()).decode()
             
def _xor(key, value):               
    if len(value) > len(key):
        raise Exception("Value length exceeds key length")
    if len(value) == 0:
        return        
    ret = bytearray(len(value))           
    for i in range(0,len(value)):
        ret[i] = ord(key[i]) ^ ord(value[i])            
    return ret