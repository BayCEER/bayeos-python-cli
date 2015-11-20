'''
Created on 06.11.2014
@author: oliver
'''

import base64, calendar, struct, math
from bayeos import connectionFile, timeFilter
from datetime import datetime
import pytz


try:
    from xmlrpc import client
except ImportError:
    import xmlrpclib as client
    
    
class SimpleClient():
        
    def __init__(self):
        self._lookUp = {}    
        self._nDic = {"check_write":0,"check_exec":1,"id":2,"id_super":3,"art":4,"name":5,"rec_start":6,"rec_end":7,"plan_start":8,"plan_end":9,"active":10,"recordsMissing":11,"hasChild":12}   
        self._wd = None
        self._useDateTime = True
        self._proxy = None 
        self._transport = None
        self._rootFolderId = None 
         
    def connect(self, url=None,user=None,password=None, save_as=None, verbose=False, listConnections=False):        
        """Open a connection to server"""                        
        cons = connectionFile.readConnections()
        if listConnections:        
            print("Alias".ljust(20) + "|" + "URL".ljust(80) + "|" + "User".ljust(10))
            print("".ljust(20,"-") + "|" + "".ljust(80,"-") + "|" + "".ljust(10,"-"))
            for alias, con in cons.items():
                print(alias.ljust(20) + '|' + con[0].ljust(80) + '|' + con[1].ljust(10))                
            return True            
                
        if url in cons:
            (url, user, password) = cons[url]
        
        if save_as: 
            if not connectionFile.write(save_as, url, user, password):
                print("WARN", "Failed to save file")
                                                                     
                                                    
        print("Open connection to " + url + " as user " + user)            
        proxy = client.ServerProxy(uri=url, allow_none=True, verbose=verbose)                
        try: 
           
            loginVec = proxy.LoginHandler.createSession(user, password)
            auth = str(loginVec[0]) + ":" + str(loginVec[1])
            authBase = base64.b64encode(auth.encode())            
                    

            class SpecialTransport(client.Transport):
                accept_gzip_encoding = False
                def send_host(self, connection, headers):
                    connection.putheader("Authentication", authBase) 
                def send_headers(self,connection, headers):
                    connection.putheader("Authentication",authBase)      
                              
            self._transport = SpecialTransport()                   
            self._proxy = client.ServerProxy(uri=url, transport=self._transport, verbose=verbose, allow_none=True, use_datetime= self._useDateTime)                                                
            
            # Read only once                           
            self._lookUp['aggfunc'] = {x[1].lower():x[0] for x in self._proxy.LookUpTableHandler.getAgrFunktionen()}                    
            assert(self._lookUp['aggfunc'])                         
            self._lookUp['aggint']  = {x[1].lower():x[0] for x in self._proxy.LookUpTableHandler.getAgrIntervalle()}
            assert(self._lookUp['aggint'])
            self._lookUp['tz']  =  self._proxy.LookUpTableHandler.getTimeZones()
            assert(self._lookUp['tz'])
            self._lookUp['status']  = self._proxy.LookUpTableHandler.getStatus()
            assert(self._lookUp['status'])
            self._lookUp['intervaltypes']  =  self._proxy.LookUpTableHandler.getIntervalTypes()
            assert(self._lookUp['intervaltypes'])            

            # Working dir to root              
            self._wd =  self._proxy.TreeHandler.getRoot('messung_ordner',False,None,None)
            assert(self._wd)
                         
            self._rootFolderId = self._wd[self._nDic["id"]]
                        
        except client.Error as v:
            print("ERROR", v)
            return False        
        return True
    
    def disconnect(self):
        """ Close server connection """                
        try:
            print("Connection closed")
            return self._proxy.LogOffHandler.terminateSession()
        finally:
            ## print("Close transport")               
            self._transport.close()                    
    
    def getVersion(self):
            """ Returns the BayEOS server version """        
            try: 
                return str(self._proxy.LookUpTableHandler.getVersion())
            except client.Error as e:
                print("ERROR", e)
    
    def getAggFunc(self):
        """ Get a dictionary of valid aggregation functions supported by the connected server. """
        return self._lookUp['aggfunc']
    
    def getAggInt(self):
        """ Get a dictionary of valid aggregation intervals supported by the connected server. """
        return self._lookUp['aggint']
    
    def getTimeZone(self):
        """ Get a list of supported time zone names """
        return self._lookUp['tz']
        
    def getNode(self,id):
        """ Get node as dictionary """        
        node = self._proxy.TreeHandler.getNode(id)
        ret = {}       
        for prop,index in self._nDic.iteritems():
            ret[prop] = node[index]
        return ret 
    
    def createSeries(self, name, folderId=None):
        """ Creates a new series in folder. Uses current folder if folderId is null """ 
        if not folderId:
            folderId = self._getPwdId()
        assert(folderId)            
        return self._proxy.TreeHandler.newNode("messung_massendaten",name,folderId)[self._nDic["id"]]                                    
    
    def deleteSeries(self, seriesId):
        """ Deletes a series and all of its records."""
        return self._proxy.TreeHandler.deleteNode(seriesId)
    
    def __validPath(self, path):        
        if ("//" in path) or len(path) == 0 or path.endswith("/"):
            return False
        else: 
            return True
    
    def findOrCreateSeries(self,path):
        """ Creates a new series by path only if series does not exist. """
        """ Uses current folder as parent folder if path is relative. """ 
        """ Path folders are created recursively """
        
        """ 
            Parameters:
                path: Path to series like '/ParentFolder/ChildFolder/SeriesName' or 'ParentFolder/ChildFolder/SeriesName'
            Returns: 
                Series id
        """
        
        
        if not self.__validPath(path):
            print("Not a valid path:{}".format([path]))
            return None
                        
        if path.startswith("/"):
            return self.__findOrCreateSeries(path[1:],self._rootFolderId)
        else:
            return self.__findOrCreateSeries(path,self._getPwdId())
            
    def __findOrCreateSeries(self, path, folderId):    
        items = path.split('/')        
        if len(items) == 1:
            art = 'messung_massendaten'
        else:
            art = 'messung_ordner'        
        id = self.findOrCreateNode(art,items[0],folderId)        
        if len(items) == 1:
            return id
        else:
            return self.__findOrCreateSeries('/'.join(items[1:]),id)
    
    def findOrCreateNode(self, art, name, parentId):        
	""" Create a new node if it does not exist."""
        childs = self._proxy.TreeHandler.getChilds(parentId,art,None,None,None)
        for child in childs:
            if child[self._nDic["name"]] == name:
                return child[self._nDic["id"]]
        print("Creating node:{}".format(name))        
        return self._proxy.TreeHandler.newNode(art,name,parentId)[self._nDic["id"]]
        
     
    def __printByte(self, b):
        for idx, val in enumerate(b):
            print(idx, val)   
    
    def writeSeries(self,ids,data,dataPerBulk=10000, overwrite=False, skipNaN=True):
        """
        Write data frame values to an existing series. Splits data in bulk of size dataPerBulk                 
        Parameters.
        
            ids =   [id,...] 
            data = [[datetime, value, value, ...], ...]
            overwrite 
                False:=  Insert mode, existing records with the same time and series id are skipped 
                True :=  Upsert mode, existing records with the same sampling time and series id are updated 
            skipNaN
                True := Skip NaN values 
                False:= Write NaN values  
        """                               
        _bytes = b''
        i = 0        
        s = struct.Struct('>iqf')                
        for row in data:                          
            if row[0].tzinfo:
                dt = row[0].astimezone(pytz.utc)
            else:
                dt = row[0]                                    
            # Rounds to seconds
            msec = calendar.timegm(dt.timetuple())*1000                                   
            for x in range(0,len(ids)):
                if (not (math.isnan(row[x+1]) and skipNaN == True) ):                                                                                               
                    _bytes += s.pack(ids[x],msec,row[x+1])
                    i +=1
                    if (i%dataPerBulk==0):
                        if (overwrite):
                            self._proxy.MassenTableHandler.upsertByteRows(client.Binary(_bytes))    
                        else:
                            self._proxy.MassenTableHandler.addByteRows(client.Binary(_bytes))                    
                        _bytes = b''                            
        
        if (len(_bytes)>0):
            if (overwrite):
                self._proxy.MassenTableHandler.upsertByteRows(client.Binary(_bytes))
            else:
                self._proxy.MassenTableHandler.addByteRows(client.Binary(_bytes))
        print(str(i) + " records imported.")                            
                        
    
    def getSeries(self, ids=None,start='yesterday',until='today',interval=None,aggfunc=None,aggint=None, statusFilter=[0,1,2,3,4,5,6,7,8,9]):               
            """ Returns a (header, data) record 
                header = [name, ...]
                data = [[datetime, value ,value, ...], ...]                
             
            Parameters:
                ids: int, or list of series ids. Tries to pick up to 10 series ids of current working folder if argument is None
                start: 'today'|'yesterday' or string with format %Y-%m-%d %H:%M:%S
                until: 'today'|'yesterday' or string with format %Y-%m-%d %H:%M:%S}
                interval: today|this week|this month|this year|yesterday|last week|last month|last year
                aggfunc: aggregation function name as string. For a list of valid parameters call getAggFunc() 
                aggint: aggregation interval name as string. For a list of valid parameters call getAggInt()
                statusFilter: List to filter valid records
            """
            # One series  
            if isinstance(ids, int):
                ids = [ids]   
            
            # Fallback to series in current dir         
            if not ids:             
                ids = [n[self._nDic["id"]] for n in self._proxy.TreeHandler.getChilds(self._getPwdId(),"messung_ordner",False,None,None) if n[self._nDic["art"]] == 'messung_massendaten'][:10]
                if ids:
                    print("Fetching data of series:" + str(ids))                      
                else:
                    print("Current folder contains no series to fetch.\nPlease cd() to a folder containing series or pass ids as an argument.\n")
                    return None                                
            assert(ids)
            
            (start,until) = timeFilter.get(datetime.now(),start,until,interval)
            
            # Check time interval
            if (start >= until):
                raise Exception("Invalid time values.")            
                                                                                               
            # Raise error if aggfunc or aggint is invalid
            if aggfunc: 
                if aggfunc not in self._lookUp['aggfunc']:
                    raise Exception("Invalid aggregation function name.\nValid names:{" + "|".join(self._lookUp['aggfunc']) + "}")
            
            if aggint:
                if aggint not in self._lookUp['aggint']:
                    raise Exception("Invalid aggregation interval name.\nValid names:{" + "|".join(self._lookUp['aggint']) + "}")
            
            
            m = self._getMatrix(ids,[start,until],aggfunc,aggint,statusFilter)                                                
            data = []        
            rowlength = 4+4*len(m[0])                                
            for n in range(0,len(m[1].data),rowlength):
                row = struct.unpack_from(">i" + len(m[0])*'f',m[1].data, offset=n)                
                a = [datetime.fromtimestamp(row[0]-60*60)]
                for value in row[1:]:
                    a.append(value)            
                data.append(a)                            
            return m[0], data
                    
    def _getMatrix(self, ids,timeFilter,aggfunc,aggint,statusFilter):
        m = None
        # Get data     
        if aggfunc and aggint:
            m = self._proxy.AggregationTableHandler.getMatrix(ids,timeFilter,[self._lookUp['aggfunc'][aggfunc],self._lookUp['aggint'][aggint]], False)
        else:
            m = self._proxy.MassenTableHandler.getMatrix(ids,timeFilter,statusFilter, False)                                 
        return m 
            
    def _getPwdId(self):
        return self._wd[self._nDic["id"]]   
        
    def pwd(self):
        """ Print out the current working folder name."""       
        print(self._proxy.TreeHandler.getNodePath(self._wd[self._nDic["id"]]))
            
    def _isoToDateTime(self,iso):
        """ Formats an iso date string to %Y-%m-%d %H:%M:%S """
        _dfmt = "%Y-%m-%d %H:%M:%S"
        if not iso:
            return "None"
        else:
            try:
                return datetime.strptime(str(iso),"%Y%m%dT%H:%M:%S").strftime(_dfmt)
            except ValueError:
                return "Invalid"
                        
    def ls(self): 
        """ Shows the content of the current working folder as a table. Rows are composed of ID, NAME, START and END date of observation. """
        print(self._proxy.TreeHandler.getNodePath(self._getPwdId()))
        print(str(self._wd[self._nDic["id_super"]]).ljust(10) + "|..")                        
        for node in self._pwdChildList():                         
            _start = self._isoToDateTime(node[self._nDic["rec_start"]])
            _end = self._isoToDateTime(node[self._nDic["rec_end"]]) 
            _art = node[self._nDic["art"]]                                                       
            print(str(node[self._nDic["id"]]).ljust(10) + "|" + (node[self._nDic["name"]] + "").ljust(50) + "|" + _art.ljust(20) + "|" + _start.ljust(20) + "|" + _end.ljust(20) )
                
    def cd(self, path, verbose=True):
        """ Change current working folder to path. Path must be a folder id."""        
        if isinstance(path,int):
             self._wd = self._proxy.TreeHandler.getNode(path) 
        elif isinstance(path,str):
            if path=="..":
                self._wd = self._proxy.TreeHandler.getNode(self._wd[self._nDic["id_super"]])
        if verbose: self.ls()
    
    def _pwdChildList(self):
        """ Returns current folder childs as list """
        return self._proxy.TreeHandler.getChilds(self._getPwdId(),"messung_ordner",False,None,None)
    
    def _pwdNodeList(self):
        """ Returns list of nodes from pwd to root """
        nodes = []
        id_super = self._wd[self._nDic['id_super']]
        while id_super:
            pa = self._proxy.TreeHandler.getNode(id_super)
            nodes.append(pa)
            id_super = pa[self._nDic['id_super']]          
        nodes.reverse()
        nodes.append(self._wd)  
        return nodes  
    
    def getProxy(self):
        """ Returns the XMLRPC Server proxy """
        return self._proxy  
    
 



if __name__ == '__main__':
    pass