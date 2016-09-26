import os
import numpy as np
import re
import string

folderPath = "./nemData"
fileList = os.listdir(folderPath)
# print fileList

cumulativeData = np.zeros(shape=(1,6))
print "YEAR,MONTH,DAY,HOUR,MIN,SETTLEMENTDATE,TOTALDEMAND,RRP"
for fileName in fileList:
	regex = '.*TAS.*'
	#Check if the file name conforms to this pattern
	m = re.search(regex, fileName)

	#If the filename conforms to the pattern, add the date and the DNI.
	if(m is not None):
		data = np.loadtxt(folderPath+"/"+fileName, delimiter=',',dtype='string',skiprows=1, usecols=None, unpack=False)
		for i in np.arange(data.shape[0]):
			date = data[i][1].replace('/',' ').replace(':',' ').replace('\"',' ')
			date = string.split(date)
			# print date
			
			print str(date[0])+","+str(date[1])+","+str(date[2])+","+str(date[3])+","+str(date[4])+","+str(data[i][2])+","+str(data[i][3])



