from controller import Controller
from utils.timezone import SydneyTimezone
import datetime
import numpy as np
from model.plant.solarPlant import SolarPlant
import model.environment.locations as locations

def printTimeseries(tracking):
	if tracking:
		print "Tracking"
		lcoePath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/lcoe/trackingAll.csv"
		stateAveragesPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/lcoe/tracking.csv"
	else:
		print "Non-Tracking"
		lcoePath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/lcoe/fixedAll.csv"
		stateAveragesPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/lcoe/fixed.csv"
	

	lcoeFile = open(lcoePath, 'w')
	headingString = "Location, State, PSH, LCOE Low, LCOE High\n"
	lcoeFile.write(headingString)

	stateAveragesFile = open(stateAveragesPath, 'w')
	headingString = "Location, PSH, LCOE Low, LCOE High\n"
	stateAveragesFile.write(headingString)

	print "Beginning LCOE Simulation"
	controller = Controller(gui=False)
	tz = SydneyTimezone()
	stateAverages = [["nsw",0,0,0,0], ["qld",0,0,0,0], ["vic",0,0,0,0], ["sa",0,0,0,0]]

	for location in locations.getLocations():

		lat= location[0]
		lon = location[1]
		state= location[2]
		locationName = location[3]
		print "==============="+locationName+"==============="


		totalPSHIncident = 0
		timePeriodCouner = 0
		yearCounter = 0
		for year in np.arange(2005, 2012):
			yearCounter = yearCounter + 1
			print year
			startDate = datetime.datetime(year=year, month=1, day=1, hour=1, tzinfo = tz)
			endDate= datetime.datetime(year=year, month=12, day=31, hour=23, minute=30, tzinfo = tz)
			print "retrieving data"
			data = controller.getTimeseriesNemDNICos(state=state, lat = lat, lon = lon, startDate = startDate, endDate = endDate)
			print "data retrieved"
			plant = SolarPlant(namePlateMW = 1)

			# Iterate through the time series and perform calculations.
			for i in np.arange(data.shape[0]):
				timePeriodCouner = timePeriodCouner + 1
				price = data[i][6]
				dni = data[i][7]
				# date = datetime.datetime(year=int(data[i][0]), month = int(data[i][1]), day = int(data[i][2]), hour=int(data[i][3]), minute=int(data[i][4]), tzinfo=SydneyTimezone())
				if dni > 0:
					if tracking:
						cos = data[i][10]
					else:
						cos = data[i][9]
					ghi_factor = data[i][8]
					ghi = np.multiply(ghi_factor, dni)
					output = plant.getPlantOutput(dni=dni, ghi=ghi, timePeriodHrs=0.5, cosine=cos)
					totalPSHIncident = totalPSHIncident + ((dni * cos)/1000.0) 

		# Write to the averages data file.
		numDays = timePeriodCouner / 48.0
		averagePSHPerDay = totalPSHIncident / (numDays)
		if tracking:
			lcoeLow = getLCOELowTracking(averagePSHPerDay)
			lcoeHigh = getLCOEHighTracking(averagePSHPerDay)
		else:
			lcoeLow = getLCOELowFixed(averagePSHPerDay)
			lcoeHigh = getLCOEHighFixed(averagePSHPerDay)
		averageString = locationName +", "+state+", "+str(round(averagePSHPerDay, 2)) +", "+str(round(lcoeLow, 2))+", "+str(round(lcoeHigh, 2))+"\n"
		lcoeFile.write(averageString)
		print "Averages written to file."
		for stateAverage in stateAverages:
			if stateAverage[0] == state:
				stateAverage[1] = lcoeLow + stateAverage[1]
				stateAverage[2] = lcoeHigh + stateAverage[2]
				stateAverage[3] = stateAverage[3] + averagePSHPerDay
				stateAverage[4] = stateAverage[4] + 1
 
	
	for stateAverage in stateAverages:
		state = stateAverage[0]
		lcoeLow = float(stateAverage[1]) / float(stateAverage[4])
		lcoeHigh = float(stateAverage[2]) / float(stateAverage[4])
		averagePSHPerDay = float(stateAverage[3]) / float(stateAverage[4])
		averageString = state+", "+str(round(averagePSHPerDay, 2)) +", "+str(round(lcoeLow, 2))+", "+str(round(lcoeHigh, 2))+"\n"
		stateAveragesFile.write(averageString)

	print "Finished"
	lcoeFile.close()
	stateAveragesFile.close()

# Fixed PV, Low Cost: \textit{LCOE = - 30.25 * ln(PSH) + 99.198 }\linebreak
# Fixed PV, High Cost: \textit{LCOE = - 41.07 * ln(PSH) + 134.44}\linebreak
# Single-Axis Tracking PV, Low Cost: \textit{LCOE = - 35.27 * ln(PSH) + 115.54}\linebreak
# Single-Axis Tracking PV, High Cost: \textit{LCOE = - 49.43 * ln(PSH) + 161.66}\linebreak


def getLCOELowFixed(averagePSHPerDay):
	return  -39.02 * np.log(averagePSHPerDay) + 127

def getLCOEHighFixed(averagePSHPerDay):
	return -52.98 * np.log(averagePSHPerDay) + 172.43

def getLCOELowTracking(averagePSHPerDay):
	return  -45.5 * np.log(averagePSHPerDay) + 148.08

def getLCOEHighTracking(averagePSHPerDay):
	return -63.62 * np.log(averagePSHPerDay) + 207.06




def getLCOEHighLow(tracking, location):
	

	print "Beginning LCOE Simulation"
	controller = Controller(gui=False)
	tz = SydneyTimezone()


	lat= location[0]
	lon = location[1]
	state= location[2]
	locationName = location[3]

	totalPSHIncident = 0
	timePeriodCouner = 0
	yearCounter = 0
	for year in np.arange(2005, 2012):
		yearCounter = yearCounter + 1
		print year
		startDate = datetime.datetime(year=year, month=1, day=1, hour=1, tzinfo = tz)
		endDate= datetime.datetime(year=year, month=12, day=31, hour=23, minute=30, tzinfo = tz)
		print "retrieving data"
		data = controller.getTimeseriesNemDNICos(state=state, lat = lat, lon = lon, startDate = startDate, endDate = endDate)
		print "data retrieved"
		plant = SolarPlant(namePlateMW = 1)

		# Iterate through the time series and perform calculations.
		for i in np.arange(data.shape[0]):
			timePeriodCouner = timePeriodCouner + 1

			dni = data[i][7]
			# date = datetime.datetime(year=int(data[i][0]), month = int(data[i][1]), day = int(data[i][2]), hour=int(data[i][3]), minute=int(data[i][4]), tzinfo=SydneyTimezone())
			if dni > 0:
				if tracking:
					cos = data[i][10]
				else:
					cos = data[i][9]
				ghi_factor = data[i][8]
				ghi = np.multiply(ghi_factor, dni)
				output = plant.getPlantOutput(dni=dni, ghi=ghi, timePeriodHrs=0.5, cosine=cos)
				totalPSHIncident = totalPSHIncident + ((dni * cos)/1000.0) 

	# Write to the averages data file.
	numDays = timePeriodCouner / 48.0
	averagePSHPerDay = totalPSHIncident / (numDays)
	if tracking:
		lcoeLow = getLCOELowTracking(averagePSHPerDay)
		lcoeHigh = getLCOEHighTracking(averagePSHPerDay)
	else:
		lcoeLow = getLCOELowFixed(averagePSHPerDay)
		lcoeHigh = getLCOEHighFixed(averagePSHPerDay)
	return (lcoeHigh, lcoeLow)
	









