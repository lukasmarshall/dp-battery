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
	contractStartHour = 7
	contractEndHour = 16

	


	strikePrices = [100,150,200,250]

	for strikePrice in strikePrices:
		averagesPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/market/minimumShapedCapValue/"+str(strikePrice)+".csv"
		averagesFile = open(averagesPath, 'w')
		averagesFile.write("Location, Minimum Value\n")

		for location in locations.getLocations():
			lat= location[0]
			lon = location[1]
			state= location[2]
			locationName = location[3]
			

			maxPrice = 300
			maxBucket = int(maxPrice / 10.0)
			priceFrequency = np.zeros(shape=(maxBucket,1))
			dayCounter = 0
			lastDays = 0
			counter = 0
			
			contractStartHour = 7
			contractEndHour = 16

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
					if hour >= contractStartHour and hour <= contractEndHour:
						averageDemand = averageDemand + demand
						counter = counter + 1
			averageDemand = float(averageDemand) / float(counter)	


			minValue = 0
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
					dni = data[i][7]
					demand = data[i][5]
					date = datetime.datetime(year=int(data[i][0]), month = int(data[i][1]), day = int(data[i][2]), hour=int(data[i][3]), minute=int(data[i][4]), tzinfo=SydneyTimezone())
					if dni > 0:
						trackingCos = data[i][10]
						cos = data[i][9]
						ghi_factor = data[i][8]
						ghi = np.multiply(ghi_factor, dni)
						output = plant.getPlantOutput(dni=dni, ghi=ghi, timePeriodHrs=0.5, cosine=cos)
						trackingOutput = plant.getPlantOutput(dni=dni, ghi=ghi, timePeriodHrs=0.5, cosine=trackingCos)
					else:
						output = 0
						trackingOutput = 0
					price = int(price)
					
					if price < 0:
						price = 0

					hour = date.hour + (float(date.minute)/60.0)
					timePeriodHrs = 0.5

					if date.hour >= contractStartHour and date.hour <= contractEndHour: 
						# print "Demand:"+str(demand)
						# print "Average Demand:" + str(averageDemand)
						if demand > averageDemand and price > strikePrice:
							# print "WOOOOO"
							minValue = minValue + min((price - strikePrice), (300 - strikePrice)) * timePeriodHrs
					
			minValueMonthly = float(minValue) / float(7 * 12)
			averageString = state+", "+str(float(minValueMonthly))+"\n"
			averagesFile.write(averageString)

			print "Averages written to file."
	
	print "Finished"
	averagesFile.close()
	# yearlyFile.close()







