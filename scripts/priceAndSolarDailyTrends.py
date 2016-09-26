from controller import Controller
from utils.timezone import SydneyTimezone
import datetime
import numpy as np
from model.plant.solarPlant import SolarPlant
import model.environment.locations as locations

def printTimeseries():
	print "Price and Solar Daily Trends"
	controller = Controller(gui=False)
	tz = SydneyTimezone()
	inflation = 1.027
	
	for location in locations.getLocations():
		lat= location[0]
		lon = location[1]
		state= location[2]
		locationName = location[3]
		
		averagesPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/market/dailyTrends/"+locationName+".csv"
		
		averagesFile = open(averagesPath, 'w')
		averagesFile.write("Hour, Price, Fixed Output, Tracking Output, DNI, Demand\n")

		print "==============="+locationName+"==============="

		priceAndSolarTrends = np.zeros(shape=(48,6))
		dayCounter = 0
		lastDays = 0
		for year in np.arange(2005, 2012):
			print year
			startDate = datetime.datetime(year=year, month=1, day=1, hour=1, tzinfo = tz)
			date = datetime.datetime(year=year, month=1, day=1, hour=1, tzinfo = tz)
			endDate= datetime.datetime(year=year, month=12, day=31, hour=23, minute=30, tzinfo = tz)
			print "retrieving data"
			data = controller.getTimeseriesNemDNICos(state=state, lat = lat, lon = lon, startDate = startDate, endDate = endDate)
			print "data retrieved"
			plant = SolarPlant(namePlateMW = 1)
			timeDiff = endDate - startDate

			if timeDiff != lastDays:
				dayCounter = dayCounter + timeDiff.days
			lastDays = timeDiff.days
			for i in np.arange(data.shape[0]):
				halfHourIndex = int(round(((date.hour * 60)+ date.minute) / 30))
				price = min(data[i][6], 300)
				demand = data[i][5]
				dni = data[i][7]
				# date = datetime.datetime(year=int(data[i][0]), month = int(data[i][1]), day = int(data[i][2]), hour=int(data[i][3]), minute=int(data[i][4]), tzinfo=SydneyTimezone())
				if dni > 0:
					timePeriodHrs = 0.5
					trackingCos = data[i][10]
					cos = data[i][9]
					ghi_factor = data[i][8]
					ghi = np.multiply(ghi_factor, dni)
					outputMW = plant.getPlantOutput(dni=dni, ghi=ghi, timePeriodHrs=0.5, cosine=cos)/ timePeriodHrs
					trackingOutputMW = plant.getPlantOutput(dni=dni, ghi=ghi, timePeriodHrs=0.5, cosine=trackingCos)/ timePeriodHrs
				else:
					cos = 0
					ghi_factor = 0
					ghi = 0
					outputMW = 0
					trackingOutputMW = 0

				priceAndSolarTrends[halfHourIndex][0] = price + priceAndSolarTrends[halfHourIndex][0]
				priceAndSolarTrends[halfHourIndex][1] = (2 *outputMW) + priceAndSolarTrends[halfHourIndex][1]
				priceAndSolarTrends[halfHourIndex][2] = (2 *trackingOutputMW) + priceAndSolarTrends[halfHourIndex][2]
				priceAndSolarTrends[halfHourIndex][3] = dni + priceAndSolarTrends[halfHourIndex][3]
				priceAndSolarTrends[halfHourIndex][4] = demand + priceAndSolarTrends[halfHourIndex][4]
				priceAndSolarTrends[halfHourIndex][5] = priceAndSolarTrends[halfHourIndex][5] + 1
				
				date = date + datetime.timedelta(seconds = (30 * 60))
				
		for i in np.arange(48):
			dayCounter = priceAndSolarTrends[i][5]
			priceAndSolarTrends[i][0] = float(priceAndSolarTrends[i][0]) / float(dayCounter)
			priceAndSolarTrends[i][1] = float(priceAndSolarTrends[i][1]) / float(dayCounter)
			priceAndSolarTrends[i][2] = float(priceAndSolarTrends[i][2]) / float(dayCounter)
			priceAndSolarTrends[i][3] = float(priceAndSolarTrends[i][3]) / float(dayCounter)
			priceAndSolarTrends[i][4] = float(priceAndSolarTrends[i][4]) / float(dayCounter)

		for i in np.arange(48):

			averageString = str(round((i/2.0), 1))+", "+str(priceAndSolarTrends[i][0])+", "+str(priceAndSolarTrends[i][1])+", "+str(priceAndSolarTrends[i][2])+", "+str(priceAndSolarTrends[i][3])+", "+str(priceAndSolarTrends[i][4])+"\n"
			averagesFile.write(averageString)

		print "Averages written to file."
	
	print "Finished"
	averagesFile.close()
	# yearlyFile.close()







