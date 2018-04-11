import temp2


templog_names = ['temp1', 'temp2', 'temp3', 'temp4']
templog_cols = [19, 20, 39, 40]
tempfile = r'C:\Users\jxue\Box Sync\Documents\Projects_LocalDrive\APREL 5.0 8585\fluke\2638A_Relay_5.0_8585_BBU_Monitoring_data.csv'
tempPlt = temp2.TempPlotter(log=tempfile, start=startTime, end=endTime, tempCols=templog_cols, tempNames=templog_names, tempProcess=None,error_bad_lines=False, skipfooter=1, engine='python')            
tempDF = tempPlt.GenDF()
# remove duplicated index
tempDF = tempDF.groupby(tempDF.index).first()