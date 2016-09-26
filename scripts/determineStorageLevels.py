from model.algorithms.algorithm import Algorithm as Algorithm
from model.environment import locations
from datetime import datetime
from utils.timezone import SydneyTimezone
import numpy as np
import sys



def printTimeseries(tracking=False):
	batteryType="Pb-A"
	print "Non-Tracking"
	path = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/storageLevelDetermination.csv"

	outputFile = open(path, 'w')
	

	outputFile.write("Storage Levels, Revenue Per Solar MWh")
	location = locations.getLocations()[0]
	
	storageLevels = [10,30,50,100,200]
	storageMWh = 3
	for level in storageLevels:
		a = Algorithm(level, batteryType)
		tz = SydneyTimezone()
		startDate = datetime(year=2010, month=1, day=1, hour=1, tzinfo = tz)
		# endDate = datetime(year=2010, month=1, day=2, hour=1, tzinfo = tz)
		endDate= datetime(year=2010, month=1, day=3, hour=23, minute=30, tzinfo = tz)
		revenue = a.runAlgorithm( startDate, endDate, location, tracking, storageMWh)
		outputFile.write(str(level)+", "+str(revenue))
		print str(level)+" Done"
