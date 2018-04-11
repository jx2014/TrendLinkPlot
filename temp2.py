# temperature plotter from Fluke DAQ 6.0.3
#
# Note: fluke saves time stamp in windows/excel format
# convert from windows/excel to unix epoch is:
# (excel_timestamp - 25569) * 86400 + 8*3600 (without day light saving: winter time)
# (excel_timestamp - 25569) * 86400 + 9*3600 (with day light saving: summer time)
# use this to check: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime((excel_timestamp-25569)*86400+8*3600))
#

from InputTemplate import Template
#import matplotlib.pyplot as plt
from decimal import Decimal
from dateutil import parser
import parser as pr
import pandas as pd
import os
import csv
from OpenGL.raw.WGL import _glgets
import time

#


class TempPlotter(Template):
    def __init__(self, log, tempCols=[3], tempNames=['Temp'], tempProcess=None, **kwargs):
        Template.__init__(self, log=log, **kwargs)
        
        #print 'TempPlotter: tempCols, TempNames', tempCols, tempNames
        
        if os.path.exists(log) == True:
            self.plotTemp = True
            self.tempLogPath = log
            self.outputTempLogFullPath = self.OutputFile(self.tempLogPath, '.csv')
            self.tempcols = dict(zip(tempNames, tempCols))
            #self.tempCol = tempCol #specific which column is the temperature data
            self.tempNames = tempNames
            self.templog_pro = tempProcess #process for column values. To use: templog_log = {13: 'value / 0.1'}, return value / 0.1 for data on column 13
                          
        else:
            print 'Temperature log path is not valid, will not plot temperature'
            self.plotTemp = False
        
    
    def GetTempDF(self):
        '''
            Get temperature data frame for plotting purposes
        '''
        self.GenTempCSV()
        df = pd.read_csv(self.outputTempLogFullPath)
        df['DateTime'] = pd.to_datetime(df['DateTime'])
        df = df.set_index('DateTime', drop=True)
        return df

    def Excel2Epoch(self, ets):
        #convert excel time stamp to epoch time stamp
        # (excel_timestamp - 25569) * 86400 + 8*3600 (without day light saving: winter time)
        # (excel_timestamp - 25569) * 86400 + 7*3600 (with day light saving: summer time)
        # use this to check: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime((excel_timestamp-25569)*86400+8*3600))
        if time.localtime((ets-25569)*86400).tm_isdst:
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime((ets-25569)*86400+28800))
        else:
            return time.strftime('%Y-%m-%d %H:%M:%S', time.localtime((ets-25569)*86400+25200))     

    # Generating new temp CSV file, remove excessive data from fluke data logger csv
    def GenTempCSV(self):
        with open(self.tempLogPath, 'r') as tempInput:
            # skip first four lines and get down to header right away
            next(tempInput)
            next(tempInput)
            next(tempInput)
            next(tempInput)
            next(tempInput)
            next(tempInput)
            next(tempInput)

            with open(self.outputTempLogFullPath, 'wb') as csvfile:
                writer = csv.DictWriter(csvfile, fieldnames=['DateTime'] + self.tempNames, lineterminator='\n')
                writer.writeheader()
                tempData = list(csv.reader(tempInput))
                for row in tempData:                
                    try:
                        try:
                            #timeStamp = parser.parse(row[0])
                            # 12/21/2017, the temperature is from Fluke Datalogger 2638A is of windows/excel format:
                            # (excel_timestamp - 25569) * 86400 + 8*3600 (without day light saving: winter time)
                            # (excel_timestamp - 25569) * 86400 + 7*3600 (with day light saving: summer time)
                            # use this to check: time.strftime('%Y-%m-%d %H:%M:%S', time.localtime((excel_timestamp-25569)*86400+8*3600))
                            timeStamp = float(row[0])
                            timeStampStr = self.Excel2Epoch(timeStamp)
                        except ValueError:
                            print 'Warning - failed to parse timestamp element:', row[0]
                            if row[0].lower() == 'time':                                
                                print 'Expected, warning can be ignored. Continue'
                                continue
                            else:
                                print 'Critical failure, STOP'
                                raise
                        if self.CheckStartStop(datetime_input=timeStampStr):
                                           
                            #temp = Decimal(row[tempCol])                            
                            csvrow = {'DateTime': timeStampStr}
                            for Tname, Tcol in self.tempcols.items():
                                #print Tcol
                                if self.templog_pro is not None and self.templog_pro.get(Tcol) is not None:
                                    formula = self.templog_pro.get(Tcol)                                    
                                    x = float(Decimal(row[Tcol]))
                                    #print 'x: %s, formula: %s' % (x, formula)                                                             
                                    csvrow[Tname] = eval(pr.expr(formula).compile())
                                    #print "x: %x, formula: %s, Tname: %s, csvrow[Tname]: %s" % (x, formula, Tname, csvrow[Tname])
                                    #_ = raw_input('press any key to continue')
                                else:
                                    csvrow[Tname] = row[Tcol]
                            #writer.writerow({'DateTime': timeStamp, 'Temp': temp})
                            writer.writerow(csvrow)                    
                    except IndexError:
                        print 'Index Error - row contains: ', row
                        continue
                    except Exception:
                        print 'Other error - row contains: ', row
                        raise
    
    def GenDF(self):
        '''
            plot all data frame 
        '''
        tempDF = self.GetTempDF()
        #tempDF.plot(grid=True, legend=True, sharex=True);
        return tempDF
        
        
        
        
        