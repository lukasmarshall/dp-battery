from model.algorithms.algorithm import Algorithm as Algorithm
from model.environment import locations
from datetime import datetime
from utils.timezone import SydneyTimezone
from model.plant import batteryStorage
import numpy as np
import sys



def printTimeseries(tracking, storageMWh, capped = False, shaved = False):
	if shaved:
		shavedString = "Shaved"
	else:
		shavedString = ""
	
	# Iterate through each type of battery.
	for spec in batteryStorage.getBatterySpecsList():
		batteryType = spec[0]
		cappedString = ""
		if capped:
			cappedString = "Capped"
		if tracking:
			print "Tracking"
			averagesPath = "simulationResults/battery/noContract/tracking/averagesAll/"+batteryType+str(storageMWh)+"MWh"+cappedString+shavedString+".csv"
			yearlyPath = "simulationResults/battery/noContract/tracking/yearly/"+batteryType+str(storageMWh)+"MWh"+cappedString+shavedString+".csv"
			stateAveragesPath = "simulationResults/battery/noContract/tracking/average/"+batteryType+str(storageMWh)+"MWh"+cappedString+shavedString+".csv"

		else:
			print "Non-Tracking"
			averagesPath = "simulationResults/battery/noContract/fixed/averagesAll/"+batteryType+str(storageMWh)+"MWh"+cappedString+shavedString+".csv"
			yearlyPath = "simulationResults/battery/noContract/fixed/yearly/"+batteryType+str(storageMWh)+"MWh"+cappedString+shavedString+".csv"
			stateAveragesPath = "simulationResults/battery/noContract/fixed/average/"+batteryType+str(storageMWh)+"MWh"+cappedString+shavedString+".csv"

		yearlyFile = open(yearlyPath, 'w')
		averagesFile = open(averagesPath, 'w')
		stateAveragesFile = open(stateAveragesPath, 'w')

		yearlyFile.write("Location, State, Year, Revenue Dollars Per MWh Solar, Average Storage Level\n")
		averagesFile.write("Location, State, Average Revenue Dollars Per MWh Solar, Average Storage Level\n")
		stateAveragesFile.write("Location, Average Revenue Dollars Per MWh Solar, Average Storage Level\n")

		stateAverages = [["nsw",0,0,0], ["qld",0,0,0], ["vic",0,0,0], ["sa",0,0,0]]

		# iterate through each location
		for location in locations.getLocations():
			print str(location[3])
			state = location[2]
			startYear = 2005
			endYear = 2011
			averageRevenue = 0
			averageStorageLevel = 0
			# Iterate through each year
			for year in np.arange(startYear, endYear + 1):
				print "\n\n============== ********* Beginning Battery Simulation - No Contracts *********** ====================="
				print str(location[3]) +"    "+ str(year)
				if tracking:
					print "Tracking"
				else:
					print "Fixed"
				print batteryType
				a = Algorithm(30, batteryType, capped, shaved)
				a = Algorithm(numStates=30, batteryType=batteryType, capped = capped, shaved = shaved)
				tz = SydneyTimezone()

				startDate = datetime(year=year, month=1, day=1, hour=1, tzinfo = tz)
				# endDate = datetime(year=2010, month=1, day=2, hour=1, tzinfo = tz)
				endDate= datetime(year=year, month=12, day=31, hour=23, minute=30, tzinfo = tz)

				result = a.runAlgorithm( startDate, endDate, location, tracking, storageMWh)
				revenue = result[0]
				averageYearlyStorageLevel = result[1]
				averageRevenue = averageRevenue + revenue
				averageStorageLevel = averageStorageLevel + averageYearlyStorageLevel
				yearlyFile.write(str(location[3])+", "+str(location[2])+", "+str(int(year))+", "+str(revenue)+", "+str(averageYearlyStorageLevel)+"\n")
				

				printDispatchPaths(a, tracking, batteryType, cappedString, location, year, storageMWh, shavedString)
				

			averageRevenue = np.divide(float(averageRevenue), float(endYear - startYear + 1))
			averageStorageLevel = np.divide(float(averageStorageLevel), float(endYear - startYear + 1))
			averagesFile.write(str(location[3])+", "+str(location[2])+", "+str(averageRevenue)+", "+str(averageStorageLevel)+"\n")
			for stateAverage in stateAverages:
				if state == stateAverage[0]:
					stateAverage[1] = stateAverage[1] + averageRevenue
					stateAverage[2] = stateAverage[2] + averageStorageLevel
					stateAverage[3] = stateAverage[3] + 1
		
		for stateAverage in stateAverages:
			state = stateAverage[0]
			averageRevenue = float(stateAverage[1]) / float(stateAverage[3])
			averageStorageLevel = float(stateAverage[2]) / float(stateAverage[3])

			stateAveragesFile.write(str(state)+", "+str(averageRevenue)+", "+str(averageStorageLevel)+"\n")
		

def printDispatchPaths(algorithm, tracking, batteryType, cappedString, location, year, storageMWh, shavedString):
	# Average Dispatch Path
	a = algorithm
	if tracking:
		dispatchFilePath = "simulationResults/battery/noContract/tracking/dispatchPath/"+batteryType+str(storageMWh)+"MWh"+cappedString+location[3]+str(year)+shavedString+".csv"
		fullDispatchFilePath = "simulationResults/battery/noContract/tracking/fullDispatchPath/"+batteryType+str(storageMWh)+"MWh"+cappedString+location[3]+str(year)+shavedString+".csv"
	else:
		dispatchFilePath = "simulationResults/battery/noContract/fixed/dispatchPath/"+batteryType+str(storageMWh)+"MWh"+cappedString+location[3]+str(year)+shavedString+".csv"
		fullDispatchFilePath = "simulationResults/battery/noContract/fixed/fullDispatchPath/"+batteryType+str(storageMWh)+"MWh"+cappedString+location[3]+str(year)+shavedString+".csv"
	

	# Average Dispatch Path
	averageDispatchStrategyFile = open(dispatchFilePath, 'w')
	averageDispatchStrategy = a.getAverageStrategy()
	# averageDispatchStrategy = a.getProbabilityPath()
	averageDispatchStrategyFile.write("Hour, Charge\n")

	for i in np.arange(averageDispatchStrategy.shape[0]):
		outString = str(round(float(i) / 2.0, 1))+", "+str(averageDispatchStrategy[i])+"\n"
		averageDispatchStrategyFile.write(outString)

	# Full Dispatch Path
	fullDispatchPathFile = open(fullDispatchFilePath, 'w')
	fullDispatchStrategy = a.getFullStrategy()
	fullDispatchPathFile.write("Hour, Price, Sun, Charge\n")
	for i in np.arange(fullDispatchStrategy.shape[0]):
		outString = str(fullDispatchStrategy[i][0])+", "+str(fullDispatchStrategy[i][1])+", "+str(fullDispatchStrategy[i][2])+", "+str(fullDispatchStrategy[i][3])+"\n"
		fullDispatchPathFile.write(outString)


