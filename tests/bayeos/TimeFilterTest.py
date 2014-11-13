'''
Created on 18.08.2014

@author: oliver
'''
import unittest
from bayeos import timeFilter
from datetime import datetime, timedelta


class TimeFilterTest(unittest.TestCase):
    
    _dfmt = "%Y-%m-%d %H:%M:%S"
    
    def setUp(self):                
        self._now = datetime(2014,8,18,10)
            
    def _check(self, msg, start, until):        
        self.assertIsNotNone(start, "No start value returned")
        self.assertIsNotNone(until, "No until value returned")
        print(msg.ljust(20) + ":" + str(start) + " -> " + str(until))
        self.assertGreater(until, start, "Start less than until");
                 
    def testDefault(self):
        (start,until) = timeFilter.get(self._now)
        self._check("default",start, until)      
                
    def testStart(self):      
        (start,until) = timeFilter.get(self._now, start=str(self._now.year-1) +"-01-01 00:00:00")
        self._check("start", start, until)
       
    
    def testUntil(self):                
        (start,until) = timeFilter.get(self._now, until=str(self._now.year+1) +"-01-01 00:00:00")
        self._check("until", start, until)
             
        
    def testStartUntil(self):    
        (start,until) = timeFilter.get(self._now,start=str(self._now.year-1) +"-02-01 00:00:00", 
        until=str(self._now.year-1) +"-06-01 00:00:00",)
        self._check("start and until", start, until)
        
    def testToday(self):
        (start,until) = timeFilter.get(self._now,interval="today")
        self._check("interval today",start, until)

    def testThisWeek(self):
        (start,until) = timeFilter.get(self._now,interval="this week")
        self._check("interval this week",start, until)
            
    def testThisMonth(self):
        (start,until) = timeFilter.get(self._now,interval="this month")
        self._check("interval this month", start, until)        
    
    def testThisYear(self):
        (start,until) = timeFilter.get(self._now,interval="this year")
        self._check("interval this year", start, until)        
        
    def testYesterday(self):
        (start,until) = timeFilter.get(self._now,interval="yesterday")
        self._check("interval yesterday", start, until)        
    
    def testLastWeek(self):
        (start,until) = timeFilter.get(self._now,interval="last week")
        self._check("interval last week", start, until)
                
    
    def testLastMonth(self):
        (start,until) = timeFilter.get(self._now,interval="last month")
        self._check("interval last month", start, until)
    
    def testLastYear(self):
        (start,until) = timeFilter.get(self._now,interval="last year")
        self._check("interval last year", start, until)
    
    @unittest.expectedFailure
    def testInvalidStart(self):        
        (start,until) = timeFilter.get(self._now, start=str(self._now.year-1) +"+01-01 00:00:00")
        
        
    @unittest.expectedFailure   
    def testInvalidInterval(self):
        (start,until) = timeFilter.get(self._now,interval="last year")
    
    def testDateTimeValues(self):
        (start,until) = timeFilter.get(self._now,start=self._now,until=self._now + timedelta(days=2))
        self._check("start and until date values", start, until)
   
                

if __name__ == "__main__":
   unittest.main()