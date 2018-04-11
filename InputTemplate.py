# Template Class
# as a template for file halding and such
#

from dateutil import parser
from decimal import Decimal
import pandas as pd
import time
import datetime
import csv
import os, sys
import re


class Template(object):
    def __init__(self, log, **kwargs):
        '''
            kwargs: 
             templog='', 
             tempCol=3,
        '''
        
        start= kwargs.get('start', '1970-1-1,01:01:01') 
        end= kwargs.get('end', '2099-9-9,09:09:09')
        self.startTS = parser.parse(start)
        self.endTS = parser.parse(end)
        self.debug = kwargs.get('debug', False)
        
        self.logFullPath = log #use this variable for input log file
        if os.path.exists(log) == False:                
            print 'Path does not exist: %s' % log
            sys.exit(0)
        else:
            self.outputFullPath = self.OutputFile(self.logFullPath, '.csv') #use this variable for output csv file
            self.macID = self.GetMac(self.outputFullPath)
        
        self.timeStart = self.DT2Epoch(start)
        self.timeEnd = self.DT2Epoch(end)
        self.deltatime = self.timeStart-self.timeEnd

    def OutputFile(self, inputfile, ext=None):
        '''
            generate output file by appending _output to the end of file
            The input file must be full path
            e.g.
            inputfile = r'c:\temp\WAN_Ping_Plotter.txt'            
            self.OutputFile(self, inputfile, ext='.csv')
            output file: c:\temp\test_output.csv
        '''
        ext = ext
        input_directory = os.path.dirname(inputfile)
        input_bname = os.path.basename(inputfile)
        input_name, input_ext = os.path.splitext(input_bname)
        
        output_ext = ext if ext is not None else input_ext
        
        outputName = input_name + '_output' + output_ext
        
        return os.path.join(input_directory, outputName)
    
    
    def RemoveFile(self, logdir, ext='.csv'):
        '''
            remove all .csv files in log dir
            by default, log dir only has txt files and macIDs.
            .csv are generated by running GenCSV()
        '''
        [os.remove(os.path.join(logdir, f)) for f in os.listdir(logdir) if f.endswith(ext)]
      
    
    def GetMac(self, filename):
        '''
            get mac ID from filename
        '''
        mac = re.search(r'[0-9a-z]{16}', filename, flags=re.IGNORECASE)
        if mac is not None:
            return mac.group()
    
    def GetUUT(self, filename):
        '''
            get uut number from filename
        '''
        uut = re.search(r'(?<=uut)[0-9]{1,2}', filename)
        if uut is not None:
            return ''.join(['uut','%.2d' % int(uut.group())])
    
    def dateparserCombiner(self, x, y):
        try:
            DateTimeData = datetime.datetime.strptime(' '.join([x,y]), '%m/%d/%Y %H:%M:%S')
        except:
            DateTimeData = datetime(month=1, day=1, year=1970, hour=0, minute=0, second=0)
        return DateTimeData

    def dateparser(self, x):
        '''
            if x is this format: 11-25-2017  23:16:14
            then dateformat_str should be: '%m-%d-%Y %H:%M:%S'
        '''
        return pd.datetime.strptime(x, '%Y-%m-%d %H:%M:%S')
        
    
    def DT2Epoch(self, dateTime):
        '''
            convert date time to epoch time
            i.e. convert string '2016-05-13,12:52:03' to 1461024652.0
                or convert string '05/13/2016 12:52:03' to 1461024652.0
        '''
        dateTime = (', ').join(dateTime.split(','))
        try:
            dt = parser.parse(dateTime)
        except Exception as e:
            print "DT2Epoch encountered an error %s" % e
            print 'dateTime variable: %s' % dateTime
        #ts = time.mktime(datetime.datetime.strptime(dateTime, "%Y-%m-%d,%H:%M:%S").timetuple())
        ts = time.mktime(dt.timetuple())
        return ts
    
    def Epoch2DT(self, timestamp):        
        return datetime.datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S') 
    
    def GetTimeStamp(self, line):
        timestamp = re.match(r"\d{4}-\d{2}-\d{2},\d{2}:\d{2}:\d{2}", line)
        if timestamp is not None:
            date, time = timestamp.group().split(',')
            dateTime = (' ').join([date,time])
            return dateTime, date, time
        else:
            return None
    
    def CheckStartStop(self, **kwargs):
        '''
            function to check if its time to begin to parser
            or time to stop the parser based on pre-defined time window
            argument: 
                date, time,
                or 
                datetime
        '''
        
        date = kwargs.get('date_input')
        time = kwargs.get('time_input')
        dateTime = kwargs.get('datetime_input')        
        
        try:
            if date is not None and time is not None:
                rowtime = self.DT2Epoch(','.join([date,time]))
            elif dateTime is not None:
                rowtime = self.DT2Epoch(dateTime)
            else:
                'Does not understand data input\ndate: %s\ntime: %s\ndatetime: %s' % (date, time, dateTime)            
            
            if rowtime >= self.timeStart and rowtime <= self.timeEnd:
                return True
            else:
                return False
        except NameError:
            print 'Check kwargs input'
        
    def DictAdd(self, adict, key, value):
        '''
            update a dictionary element with new value
        '''
        if adict.get(key) is None:
            newValue = value
        else:
            newValue = adict.get(key) + value
        adict.update({key:newValue})
   
   #3/20/2017 removed fn, to generate csv from each WAN_Ping_Plotter python files.
    def GetDF(self, usecols, **kwargs):
        '''
            Generate panda data frame based on csv input and header requirement           
        '''
        csvpath = kwargs.get('csvpath', self.outputFullPath)        
        df = pd.read_csv(csvpath, usecols=usecols)
        df['DateTime'] = pd.to_datetime(df['DateTime'])
        df = df.set_index('DateTime', drop=True)
        print df.describe()
        return df

    def Run(self):
        '''
            use self.Run to make the plot
        '''
        print 'this is self.Run(self)'








