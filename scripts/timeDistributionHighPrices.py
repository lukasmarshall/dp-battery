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
		
		averagesPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/market/dailyTrends/highPrices/"+state+".csv"
		
		averagesFile = open(averagesPath, 'w')
		averagesFile.write("Hour, Count, Price, Fixed Output, Tracking Output, DNI, Demand, Overall Probability, Average Fixed Output, Average Tracking Output\n")

		print "==============="+locationName+"==============="

		priceAndSolarTrends = np.zeros(shape=(48,9))
		eventCounter = 0
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
			print str(data.shape[0])

			if timeDiff != lastDays:
				eventCounter = eventCounter + timeDiff.days
			lastDays = timeDiff.days
			print "=====================+++++++++++++++++"+str(data.shape[0])
			for i in np.arange(data.shape[0]):

				halfHourIndex = int(round(((date.hour * 60)+ date.minute) / 30))
				price = data[i][6]
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

				if price > 300:
					priceAndSolarTrends[halfHourIndex][0] = price + priceAndSolarTrends[halfHourIndex][0]
					priceAndSolarTrends[halfHourIndex][1] = (2 *output) + priceAndSolarTrends[halfHourIndex][1]
					priceAndSolarTrends[halfHourIndex][2] = (2 *trackingOutput) + priceAndSolarTrends[halfHourIndex][2]
					priceAndSolarTrends[halfHourIndex][3] = dni + priceAndSolarTrends[halfHourIndex][3]
					priceAndSolarTrends[halfHourIndex][4] = demand + priceAndSolarTrends[halfHourIndex][4]
					priceAndSolarTrends[halfHourIndex][5] = priceAndSolarTrends[halfHourIndex][5] + 1
					priceAndSolarTrends[halfHourIndex][7] = priceAndSolarTrends[halfHourIndex][7] + (float(output) / 0.5)
					priceAndSolarTrends[halfHourIndex][8] = priceAndSolarTrends[halfHourIndex][8] + (float(trackingOutput) / 0.5)
				priceAndSolarTrends[halfHourIndex][6] = priceAndSolarTrends[halfHourIndex][6] + 1
				
				date = date + datetime.timedelta(seconds = (30 * 60))
				
		for i in np.arange(48):
			eventCounter = priceAndSolarTrends[i][5]
			if eventCounter > 0:
				priceAndSolarTrends[i][0] = float(priceAndSolarTrends[i][0]) / float(eventCounter)
				priceAndSolarTrends[i][1] = float(priceAndSolarTrends[i][1]) / float(eventCounter)
				priceAndSolarTrends[i][2] = float(priceAndSolarTrends[i][2]) / float(eventCounter)
				priceAndSolarTrends[i][3] = float(priceAndSolarTrends[i][3]) / float(eventCounter)
				priceAndSolarTrends[i][4] = float(priceAndSolarTrends[i][4]) / float(eventCounter)
				priceAndSolarTrends[i][7] = float(priceAndSolarTrends[i][7]) / float(eventCounter)
				priceAndSolarTrends[i][8] = float(priceAndSolarTrends[i][8]) / float(eventCounter)
				print str(priceAndSolarTrends[i][6])
				priceAndSolarTrends[i][6] = eventCounter / float(priceAndSolarTrends[i][6])

			else:
				priceAndSolarTrends[i][6] = 0

		for i in np.arange(48):

			averageString = str(round((i/2.0), 1))+", "+str(priceAndSolarTrends[i][5])+", "+str(priceAndSolarTrends[i][0])+", "+str(priceAndSolarTrends[i][1])+", "+str(priceAndSolarTrends[i][2])+", "+str(priceAndSolarTrends[i][3])+", "+str(priceAndSolarTrends[i][4])+", "+str(priceAndSolarTrends[i][6])+", "+str(priceAndSolarTrends[i][7])+", "+str(priceAndSolarTrends[i][8])+"\n"
			averagesFile.write(averageString)

		print "Averages written to file."
	
	print "Finished"
	averagesFile.close()
	# yearlyFile.close()







