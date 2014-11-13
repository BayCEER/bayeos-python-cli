'''
Created on 18.08.2014

@author: oliver
'''
from datetime import datetime, timedelta
import calendar

def get(now,start='yesterday',until='today',interval=None):
    """ Returns a start,until record """ 
    today = now.replace(hour=0,minute=0,second=0,microsecond=0)
    yesterday = today - timedelta(days=1)    
    tomorrow = today + timedelta(days=1)
    monday  = today - timedelta(days=today.isoweekday()-1)
    
    
    if isinstance(start,str):
        if (start.lower() == 'yesterday'):
            start = yesterday
        else:
            start = datetime.strptime(start,"%Y-%m-%d %H:%M:%S")
            
    if isinstance(until,str):            
        if (until.lower() == 'today'):
            until = now
        else:
            until = datetime.strptime(until,"%Y-%m-%d %H:%M:%S")
            
    if start > until:
        raise Exception("Until date less than end date.")
        
    # Overwrite start and until values if interval is set
    if interval:                
            if interval.lower() == 'today':
                start = today 
                until = tomorrow
            elif interval.lower() == "this week":
                start = monday
                until = monday + timedelta(days=7) 
            elif interval.lower() == "this month":
                start = today.replace(day=1)
                until = start + timedelta(days=calendar.monthrange(start.year,start.month)[1])               
            elif interval.lower() == "this year":
                start = today.replace(month=1,day=1)
                until = today.replace(year=today.year+ 1,month=1,day=1)
            elif interval.lower() == "yesterday":
                start = yesterday
                until = today 
            elif interval.lower() == "last week":
                start = monday - timedelta(weeks=1)
                until = monday                 
            elif interval.lower() == "last month":
                until = datetime(today.year,today.month,1)
                t = until - timedelta(days=1)
                start = datetime(t.year,t.month,1)                
            elif interval.lower() == "last year":
                until = datetime(today.year,1,1)
                start = datetime(today.year-1,1,1)                 
            else: 
                raise Exception("Invalid interval format specified.\nMust be:{today|this week|this month|this year|yesterday|last week|last month|last year}")         
          
    return start,until 