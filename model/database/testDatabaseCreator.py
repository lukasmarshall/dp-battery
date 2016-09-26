import databaseManager
import h5py
import numpy as np
import os
import solarDataTextUtils





#597 is the tip of Australia - it won't always have a value of -999 so its a suitable test candidate.
desiredIndex = 597

# Get the desired index values from the text files.
path = "/Volumes/SOLAR/SOLAR_DATA/time_series_hourly_dni/1996"
datasetPath = "/Volumes/SOLAR/SOLAR_DATA/time_series_hourly_dni/1996/test.hdf5"
# path = "./2008"
valueList = []
for fileName in os.listdir(path):

	if(solarDataTextUtils.isFileNameValid(fileName)):
		print fileName
		number = solarDataTextUtils.getValueAtIndex(path+"/"+fileName, 0,597)
		valueList.append(int(number))
	


dset = databaseManager.createSolarDataset(path, datasetPath)
counter = 0
valueListIndex = 0
unmatchedCounter = 0
for i in np.arange(dset.shape[2]):
	
	value = dset[0,desiredIndex,i]
	if(value == -888):
		counter += 1
	else:
		# print "Blank Points Found: "+str(counter)
		if(int(dset[0,desiredIndex,i]) == valueList[valueListIndex]):
			print "OK"
		else:
			print "NO MATCH: "+ str(dset[0,desiredIndex,i]) + "     "+ str(valueListIndex[valueListIndex])
			unmatchedCounter += 1
		counter = 0
		valueListIndex += 1

if(unmatchedCounter > 0):
	print "============================"
	print "============================"
	print "======= TEST FAILED ========"
	print "============================"
	print "============================"
	print "========NON-MATCHES: "+unmatchedCounter+"===" 
	print "============================"
	print "============================"
else:
	print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	print "!!!!!!!!TEST PASSED!!!!!!!!!"
	print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
	print "!!!!!!!!!!!!!!!!!!!!!!!!!!!!"



