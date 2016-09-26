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
		
		averagesPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/market/priceFrequency/"+state+".csv"
		
		averagesFile = open(averagesPath, 'w')
		averagesFile.write("Price, Count\n")

		print "==============="+locationName+"==============="

		maxPrice = 300
		maxBucket = int(maxPrice / 10.0)
		priceFrequency = np.zeros(shape=(maxBucket,1))
		dayCounter = 0
		lastDays = 0
		counter = 0
		for year in np.arange(2005, 2012):
			print year
			startDate = datetime.datetime(year=year, month=1, day=1, hour=1, tzinfo = tz)
			date = datetime.datetime(year=year, month=1, day=1, hour=1, tzinfo = tz)
			endDate= datetime.datetime(year=year, month=12, day=31, hour=23, minute=30, tzinfo = tz)
			data = controller.getTimeseriesNemDNICos(state=state, lat = lat, lon = lon, startDate = startDate, endDate = endDate)
			plant = SolarPlant(namePlateMW = 1)
			timeDiff = endDate - startDate

			if timeDiff != lastDays:
				dayCounter = dayCounter + timeDiff.days
			lastDays = timeDiff.days
			for i in np.arange(data.shape[0]):
				counter = counter + 1
				halfHourIndex = int(round(((date.hour * 60)+ date.minute) / 30))
				price = min(data[i][6], 300)
				demand = data[i][5]
				dni = data[i][7]
				# date = datetime.datetime(year=int(data[i][0]), month = int(data[i][1]), day = int(data[i][2]), hour=int(data[i][3]), minute=int(data[i][4]), tzinfo=SydneyTimezone())
				if dni > 0:
					trackingCos = data[i][10]
					cos = data[i][9]
					ghi_factor = data[i][8]
					ghi = np.multiply(ghi_factor, dni)
					output = plant.getPlantOutput(dni=dni, ghi=ghi, timePeriodHrs=0.5, cosine=cos)
					trackingOutput = plant.getPlantOutput(dni=dni, ghi=ghi, timePeriodHrs=0.5, cosine=trackingCos)
				else:
					cos = 0
					ghi_factor = 0
					ghi = 0
					output = 0
					trackingOutput = 0
				price = int(price)
				
				if price < 0:
					price = 0
				index = int(price / 10.0)
				index = min(index, priceFrequency.shape[0] - 1)
				priceFrequency[index] = priceFrequency[index] + 1

				# priceFrequency[halfHourIndex][0] = price + priceFrequency[halfHourIndex][0]
				# priceFrequency[halfHourIndex][1] = (2 *output) + priceFrequency[halfHourIndex][1]
				# priceFrequency[halfHourIndex][2] = (2 *trackingOutput) + priceFrequency[halfHourIndex][2]
				# priceFrequency[halfHourIndex][3] = dni + priceFrequency[halfHourIndex][3]
				# priceFrequency[halfHourIndex][4] = demand + priceFrequency[halfHourIndex][4]
				# priceFrequency[halfHourIndex][5] = priceFrequency[halfHourIndex][5] + 1
				
				date = date + datetime.timedelta(seconds = (30 * 60))

		for i in np.arange(priceFrequency.shape[0]):
			averageString = str(i*10)+"-"+str(i*10+10)+", "+str(float(priceFrequency[i]))+"\n"
			averagesFile.write(averageString)

		print "Averages written to file."
	
	print "Finished"
	averagesFile.close()
	# yearlyFile.close()







