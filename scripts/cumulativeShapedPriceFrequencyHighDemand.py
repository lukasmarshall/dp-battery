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
		
		averagesPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/market/cumulativeShapedPriceFrequencyHighDemand/"+state+".csv"
		
		averagesFile = open(averagesPath, 'w')
		averagesFile.write("Price, Count\n")

		print "==============="+locationName+"==============="

		
		dayCounter = 0
		lastDays = 0
		counter = 0
		
		contractStartHour = 7
		contractEndHour = 16
		
		# Find average demand in contractual period.
		averageDemand = 0
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
				demand = data[i][5]

				date = datetime.datetime(year=int(data[i][0]), month = int(data[i][1]), day = int(data[i][2]), hour=int(data[i][3]), minute=int(data[i][4]), tzinfo=SydneyTimezone())
				
				hour = date.hour + (float(date.minute)/60.0)
				if date.hour >= contractStartHour and date.hour <= contractEndHour:
					averageDemand = averageDemand + demand
					counter = counter + 1
		averageDemand = float(averageDemand) / float(counter)	
				
		maxPrice = 300
		maxBucket = int(maxPrice / 10.0)
		priceFrequency = np.zeros(shape=(maxBucket,1))
		dayCounter = 0
		lastDays = 0
		counter = 0
		
		contractStartHour = 7
		contractEndHour = 16
		
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
				
				price = data[i][6]
				demand = data[i][5]
				dni = data[i][7]
				date = datetime.datetime(year=int(data[i][0]), month = int(data[i][1]), day = int(data[i][2]), hour=int(data[i][3]), minute=int(data[i][4]), tzinfo=SydneyTimezone())
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
				hour = date.hour + (float(date.minute)/60.0)
				if date.hour >= contractStartHour and date.hour <= contractEndHour and demand > averageDemand:
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

		# Make cumulative
		for i in np.arange(priceFrequency.shape[0])[::-1]:
			if i < priceFrequency.shape[0] - 1:
				priceFrequency[i] = priceFrequency[i] + priceFrequency[i+1]

		for i in np.arange(priceFrequency.shape[0]):
			averageString = "> "+str(i*10)+", "+str(float(priceFrequency[i]))+"\n"
			averagesFile.write(averageString)

		print "Averages written to file."
	
	print "Finished"
	averagesFile.close()
	# yearlyFile.close()







