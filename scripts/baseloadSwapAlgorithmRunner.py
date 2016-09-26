from model.algorithms.baseloadSwapAlgorithm import BaseloadSwapAlgorithm as Algorithm
from model.environment import locations
from datetime import datetime
from utils.timezone import SydneyTimezone
from model.plant import batteryStorage
import numpy as np
import sys
from controller import Controller


def printTimeseries(tracking, storageMWh, fractionContracted = 0.25, capped = False, shaved = False):

	if shaved:
		shavedString = "Shaved"
	else:
		shavedString = ""
	# Iterate through each type of battery.
	for spec in batteryStorage.getBatterySpecsList():
		batteryType = spec[0]

		if tracking:
			print "Tracking"
			stateAveragesPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/battery/baseloadSwap/tracking/average/"+batteryType+str(fractionContracted)+"Contracted"+str(storageMWh)+"MWh"+shavedString+".csv"
			averagesPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/battery/baseloadSwap/tracking/averagesAll/"+batteryType+str(fractionContracted)+"Contracted"+str(storageMWh)+"MWh"+shavedString+".csv"
			monthlyPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/battery/baseloadSwap/tracking/monthly/"+batteryType+str(fractionContracted)+"Contracted"+str(storageMWh)+"MWh"+shavedString+".csv"

		else:
			print "Non-Tracking"
			stateAveragesPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/battery/baseloadSwap/fixed/average/"+batteryType+str(fractionContracted)+"Contracted"+str(storageMWh)+"MWh"+shavedString+".csv"
			averagesPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/battery/baseloadSwap/fixed/averagesAll/"+batteryType+str(fractionContracted)+"Contracted"+str(storageMWh)+"MWh"+shavedString+".csv"
			monthlyPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/battery/baseloadSwap/fixed/monthly/"+batteryType+str(fractionContracted)+"Contracted"+str(storageMWh)+"MWh"+shavedString+".csv"

		monthlyFile = open(monthlyPath, 'w')
		averagesFile = open(averagesPath, 'w')
		stateAveragesFile = open(stateAveragesPath, 'w')

		monthlyFile.write("Location, State, Year, Month, Revenue Dollars Per MWh Solar, Average Storage Level\n")
		averagesFile.write("Location, State, Average Revenue Dollars Per MWh Solar, Average Storage Level\n")
		stateAveragesFile.write("Location, Average Revenue Dollars Per MWh Solar, Average Storage Level\n")

		stateAverages = [["nsw",0,0,0], ["qld",0,0,0], ["vic",0,0,0], ["sa",0,0,0]]
		# iterate through each location
		for location in locations.getLocations():
			print str(location[0])
			state = location[2]
			startYear = 2007
			endYear = 2011
			averageRevenue = 0
			averageStorageLevel = 0
			# Iterate through each year
			counter = 0
			for year in np.arange(startYear, endYear + 1):
				for month in np.arange(1,13):
					print "=========== Beginning Baseload Swap Simulation============"
					print "Year = "+str(year)+ " Month = "+str(month)
					print str(batteryType)
					print str(location[3])
					print "Tracking = "+str(tracking)
					counter = counter + 1


					tz = SydneyTimezone()

					startDate = datetime(year=year, month=month, day=1, hour=1, tzinfo = tz)
					# endDate = datetime(year=2010, month=1, day=2, hour=1, tzinfo = tz)
					endDay = 31
					if month == 2:
						endDay = 28
					elif month == 9 or month == 4 or month == 6 or month == 11:
						endDay = 30
					endDate= datetime(year=year, month=month, day=endDay, hour=23, minute=30, tzinfo = tz)

					strikePrice = getStrikePrice(startDate, endDate, location)
					a = Algorithm(strikePrice = strikePrice, fractionContracted = fractionContracted, numStates = 30, batteryType = batteryType, capped = False, shaved = shaved)

					result = a.runAlgorithm( startDate, endDate, location, tracking, storageMWh)
					revenue = result[0]
					averageYearlyStorageLevel = result[1]
					averageRevenue = averageRevenue + revenue
					averageStorageLevel = averageStorageLevel + averageYearlyStorageLevel
					monthlyFile.write(str(location[3])+", "+str(location[2])+", "+str(int(year))+", "+str(int(month))+", "+str(revenue)+", "+str(averageYearlyStorageLevel)+"\n")


			averageRevenue = np.divide(float(averageRevenue), float(counter))
			averageStorageLevel = np.divide(float(averageStorageLevel), float(counter))
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
		# break

		

def getStrikePrice(startDate, endDate, location):
	tz = SydneyTimezone()
	lat= location[0]
	lon = location[1]
	state= location[2]
	startDate = startDate.astimezone(tz)
	endDate = endDate.astimezone(tz)

	controller = Controller(gui=False)
	data = controller.getTimeseriesNemDNICos(state=state, lat = lat, lon = lon, startDate = startDate, endDate = endDate)
	counter = 0
	average = 0
	for i in np.arange(data.shape[0]):
		counter = counter + 1
		price = data[i][6]
		average = average + price

	average = np.divide(float(average), float(counter))
	return average



