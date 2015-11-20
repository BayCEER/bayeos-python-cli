from bayeos.frame.cli import FrameClient
import datetime
import csv
import sys


def main():
    
    if len(sys.argv)!=4:
        print("usage: CsImportToa5 <Connection Alias> <Mapping file> <toa5 file>")        
        sys.exit(1)      
    
        
    alias = sys.argv[1]
    ids = []
    cols = []
    with open(sys.argv[2],'r') as mfile:
        reader = csv.DictReader(mfile)
        for row in reader:
            cols.append(row['column'])
            ids.append(int(row['id']))                              
    toa5 = sys.argv[3]
        
    # Connect
    cli = FrameClient()    
    if (not cli.connect(alias)):
        sys.exit(-1)                

    # Read values 
    dataFrame = cli.read_toa5(toa5,'Etc/GMT-1')
    # Import values 
    cli.writeFrame(ids,dataFrame[cols])
    cli.disconnect()

if __name__ == '__main__':
    main()
