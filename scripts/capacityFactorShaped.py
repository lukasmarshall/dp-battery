from controller import Controller
from utils.timezone import SydneyTimezone
import datetime
import numpy as np
from model.plant.solarPlant import SolarPlant
import model.environment.cosine as cosine
import model.environment.locations as locations

def printTimeseries(tracking):
	if tracking:
		print "Tracking"
		stateAveragesPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/market/capacityFactorShaped/tracking.csv"

	else:
		print "Non-Tracking"
		stateAveragesPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/market/capacityFactorShaped/fixed.csv"

	nameplateCapacityMW = 1
	stateAveragesFile = open(stateAveragesPath, 'w')

	stateAveragesFile.write("Location, Capacity Factor\n")

	print "Beginning Capacity Factor Simulation"
	controller = Controller(gui=False)
	tz = SydneyTimezone()
	inflation = 1.027

	stateAverages = [["nsw",0,0], ["qld",0,0], ["vic",0,0], ["sa",0,0]]
	contractStartHour = 7
	contractEndHour = 16

	for location in locations.getLocations():
		lat= location[0]
		lon = location[1]
		state= location[2]
		
		totalMWh = 0
		totalHours = 0
		for year in np.arange(2005, 2012):
			print year
			startDate = datetime.datetime(year=year, month=1, day=1, hour=1, tzinfo = tz)
			endDate= datetime.datetime(year=year, month=12, day=31, hour=23, minute=30, tzinfo = tz)
			data = controller.getTimeseriesNemDNICos(state=state, lat = lat, lon = lon, startDate = startDate, endDate = endDate)
			plant = SolarPlant(namePlateMW = 1)



			# Iterate through the time series and perform calculations.
			for i in np.arange(data.shape[0]):
				
				date = datetime.datetime(year=int(data[i][0]), month = int(data[i][1]), day = int(data[i][2]), hour=int(data[i][3]), minute=int(data[i][4]), tzinfo=SydneyTimezone())
				dni = data[i][7]
				if dni > 0:
					if tracking:
						cos = data[i][10]
					else:
						cos = data[i][9]
					ghi_factor = data[i][8]
					ghi = np.multiply(ghi_factor, dni)
					output = plant.getPlantOutput(dni=dni, ghi=ghi, timePeriodHrs=0.5, cosine=cos)
				else:
					cos = 0
					ghi_factor = 0
					ghi = 0
					output = 0
				hour = date.hour + (float(date.minute)/60.0)

				if hour >= contractStartHour and hour <= contractEndHour: 
					totalMWh = totalMWh + output
					totalHours = totalHours + 0.5


		for stateAverage in stateAverages:
			if state == stateAverage[0]:
				stateAverage[1] = stateAverage[1] + totalMWh
				stateAverage[2] = stateAverage[2] + totalHours

	for stateAverage in stateAverages:
		state = stateAverage[0]
		capacityFactor = float(stateAverage[1]) / (float(stateAverage[2]) * float(nameplateCapacityMW))
		stateAveragesFile.write(str(state)+", "+str(capacityFactor)+"\n")
		

	print "Finished"
	stateAveragesFile.close()
	







