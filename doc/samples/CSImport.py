'''

CSImport.py 

Created on 23.10.2015
@author: oliver.archner@uni-bayreuth.de

Imports Campbell Scientific logger files in TOACI1 format to BayEOS Server.
 
Requirements:   
                + Write privileges on home folder 
                + Connection alias
                + File in TOACI1 format
Parameters:
                + Connection Alias: Alias in file .bayeos.pwd. Can be created with function bayeos.SimpleClient.connect()
                + Home Folder Path: Destination folder for data. Used to create an absolute path in combination with station, table and channel name.  
                + File: Source file path 
                + TzOffset: Time zone offset to UTC in hours  
'''
import csv
import sys
import datetime
from bayeos.cli import SimpleClient 

def main():
    
    if len(sys.argv)!=5:
        print("usage: CSImport <Connection Alias> <Home Folder Path> <File> <tzOffset>")
        print("e.g.: CSImport myAlias /Project/Logger CS5000.dat +01")
        sys.exit(1)               
    
    # Parameters       
    con = sys.argv[1]
    path = sys.argv[2]
    file = open(sys.argv[3],'r')
    tzOffset = int(sys.argv[4])
    
    
    # Connection 
    cli = SimpleClient()
    cli.connect(con)
    
    # Open File
    reader = csv.reader(file)          
    
    # Check format 
    head = next(reader)
    if head[0] != 'TOACI1':
        print("File format:{} not supported.".format(head[0]));
        sys.exit(1)
    
    # Origin
    relPath = head[1] + "/" + head[2]    
    if path == "/":
        origin = path + relPath                                     
    else:
        origin = path + "/" + relPath
                                     
    # Create series by path
    ids = [cli.findOrCreateSeries(origin + "/" + cha) for cha in next(reader)[1:]]
                
    # Channel data   
    data = []                     
    for row in reader:   
        if len(row) > 0:     
            rec = []               
            d = datetime.datetime.strptime(row[0],"%Y-%m-%d %H:%M:%S") - datetime.timedelta(hours=tzOffset) ## UTC                                         
            rec.append(d)
            for i in range(1,len(row)):                        
                if row[i] == "":
                    rec.append(float("nan"))
                else:
                    rec.append(float(row[i]))             
            data.append(rec)
                                                                            
    cli.writeSeries(ids, data)
    
    # Close 
    cli.disconnect()                                                                          
    file.close()
                

if __name__ == '__main__':
    main()
    