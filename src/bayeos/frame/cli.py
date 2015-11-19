'''
Created on 19.11.2015

@author: oliver
'''
from bayeos.cli import SimpleClient
import pandas as pd
from pytz import timezone
import datetime


class FrameClient(SimpleClient):
    '''
    A bayeos-server frame client
    '''
                
    def read_toa5(self,url,tz):
        """
        Reads a campbell scientific toa5 format file and returns a pandas DataFrame 
        """                
        return self.read_csv(url,[1,2,3],',',"NAN","%Y-%m-%d %H:%M:%S",tz)
    
    def read_csv(self,url,header,sep,na_values,timeformat,tz):
        """
        Reads a csv file and returns a pandas DataFrame 
        """
        zone = timezone(tz)        
        parser = lambda t: zone.localize(datetime.datetime.strptime(t,timeformat))                
        return pd.read_csv(url,header=header,sep=sep,na_values=na_values,parse_dates=True,index_col=0, date_parser=parser)        

    def writeFrame(self,ids,dataFrame,dataPerBulk=10000,overwrite=False, skipNaN=True):
        """
        Writes a frame to BayEOS Server 
        """
        data = []
        for t in dataFrame.itertuples():
            data.append(list(t))
        return self.writeSeries(ids, data, dataPerBulk, overwrite, skipNaN)    
                
        
    