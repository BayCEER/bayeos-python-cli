'''

QliImport.py 

Created on 04.03.2015
@author: oliver.archner@uni-bayreuth.de

Imports vaisala qli csv files
Uses bayeos.cli.SimpleClient 
 
Requirements:   + Existing series for each column
                + Write privileges on series
                + Connection alias
                + CSV File with format:

                Date, Time, m{id}, m{id}, ...
                30.1.2015,03:10:00,94.84,-1.91,...
                30.1.2015,03:20:00,'#N/A,-1.92,...
'''
import csv
import sys
import datetime
from bayeos.cli import SimpleClient 

test = False

def main():
    
    if len(sys.argv)!=3:
        print("usage: QliImport <Connection Alias> <File>")
        sys.exit(1)               
            
    infile = open(sys.argv[2],'r')
    
    if not test:
        cli = SimpleClient()
        cli.connect(url=sys.argv[1])
                                       
    reader = csv.reader(infile)
    headers = reader.next()                          
        
    ids =  [int(x[1:]) for x in headers[2:]]      
    data = []                     
    for row in reader:   
        if len(row) > 0:     
            rec = []               
            d = datetime.datetime.strptime(row[0] + " " + row[1],"%d.%m.%Y %H:%M:%S") ## GMT+1
            d -= datetime.timedelta(hours=1,minutes=d.minute%10,seconds=d.second) ## UTC truncated to 10 min resolution                        
            rec.append(d)
            for i in range(2,len(row)):                        
                if row[i] == "#N/A":
                    rec.append(float("nan"))
                else:
                    rec.append(float(row[i]))             
            data.append(rec)
            if test:
                print(rec)
    
    if not test:                                                                    
        cli.writeSeries(ids, data)
        cli.disconnect()
                                                                          
    infile.close()
                

if __name__ == '__main__':
    main()
    