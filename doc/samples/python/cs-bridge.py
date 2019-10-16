#!/usr/bin/python
from bayeos.frame.cli import FrameClient
import datetime
import csv
import sys
import bayeos


def main():
    
    if len(sys.argv)!=6:
        print("usage: CsBridge <Connection Alias> <id> <Mapping file> <Host name> <Table>")        
        sys.exit(1)      
    
    alias = sys.argv[1]
    id = int(sys.argv[2])
    ids = []
    cols = []
    with open(sys.argv[3],'r') as mfile:
        reader = csv.DictReader(mfile)
        for row in reader:
            cols.append(row['column'])
            ids.append(int(row['id']))
                          
    host = sys.argv[4]
    table = sys.argv[5]

    # Connect
    cli = FrameClient()    
    if (not cli.connect(str(alias))):
        sys.exit(-1)                

    # Get last date in db 
    node = cli.getNode(id)
    if node['rec_end']:
        rec_end = node['rec_end'].strftime('%Y-%m-%dT%H:%M:%S.00')
    else:
        rec_end = "2000-01-01"

    print("Getting records since: {0}".format(rec_end))    
    url = "http://{0}/?command=dataquery&uri=dl:{1}&format=toa5&mode=since-time&p1={2}".format(host,table,rec_end)

    # Read values 
    dataFrame = cli.read_toa5(url,'Etc/GMT-1')
    # Import values 
    cli.writeFrame(ids,dataFrame[cols])
    cli.disconnect()

if __name__ == '__main__':
    main()
