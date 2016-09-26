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
		stateAveragesPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/market/merchantModelCappedSpot/tracking/average.csv"
		averagesPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/market/merchantModelCappedSpot/tracking/averageAll.csv"
		yearlyPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/market/merchantModelCappedSpot/tracking/yearly.csv"

	else:
		print "Non-Tracking"
		stateAveragesPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/market/merchantModelCappedSpot/fixed/average.csv"
		averagesPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/market/merchantModelCappedSpot/fixed/averageAll.csv"
		yearlyPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/market/merchantModelCappedSpot/fixed/yearly.csv"

	yearlyFile = open(yearlyPath, 'w')
	averagesFile = open(averagesPath, 'w')
	stateAveragesFile = open(stateAveragesPath, 'w')

	yearlyFile.write("Location, State, Year, Average Market Price, Average Revenue, Total Generation MWh, Average PSH/Day\n" ) 
	averagesFile.write("Location, State, Average Market Price, Average Revenue\n")
	stateAveragesFile.write("Location, Average Market Price, Average Revenue\n")

	print "Beginning Merchant Model Simulation"
	controller = Controller(gui=False)
	tz = SydneyTimezone()
	inflation = 1.027

	stateAverages = [["nsw",0,0,0], ["qld",0,0,0], ["vic",0,0,0], ["sa",0,0,0]]
	for location in locations.getLocations():

		lat= location[0]
		lon = location[1]
		state= location[2]
		locationName = location[3]
		print "==============="+locationName+"==============="
		averageMarketPrice = averageRevenue = count = 0
		
		for year in np.arange(2005, 2012):
			print year
			startDate = datetime.datetime(year=year, month=1, day=1, hour=1, tzinfo = tz)
			endDate= datetime.datetime(year=year, month=12, day=31, hour=23, minute=30, tzinfo = tz)
			print "retrieving data"
			data = controller.getTimeseriesNemDNICos(state=state, lat = lat, lon = lon, startDate = startDate, endDate = endDate)
			print "data retrieved"
			plant = SolarPlant(namePlateMW = 1)

			totalYearlyRevenue = totalYearlyMWh = totalYearlySpotPrice = totalYearlyPSH = 0

			# Iterate through the time series and perform calculations.
			for i in np.arange(data.shape[0]):
				price = min(data[i][6], 300)
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
					totalYearlyPSH = totalYearlyPSH + (ghi/1000.0)
				else:
					cos = 0
					ghi_factor = 0
					ghi = 0
					output = 0

				totalYearlyRevenue = totalYearlyRevenue + (output * price)

				totalYearlyMWh = totalYearlyMWh + output
				totalYearlySpotPrice = totalYearlySpotPrice + price

			averageYearlyRevenue = np.divide(totalYearlyRevenue, totalYearlyMWh)
			averageYearlyMarketPrice = np.divide(totalYearlySpotPrice, data.shape[0])
			averagePshPerDay = (totalYearlyPSH / 365.0)


			# Write to the yearly data file.
			yearlyString =  locationName +", "+state+", "+ str(endDate.year) +", "+ str(np.round(averageYearlyMarketPrice, decimals = 2)) +", "+ str(np.round(averageYearlyRevenue, decimals = 2)) 
			yearlyString = yearlyString + ", "+ str(totalYearlyMWh) + ", "+ str(averagePshPerDay)+"\n"
			yearlyFile.write(yearlyString)
			print "Yearly data written to file."

			averageRevenue = averageRevenue +(averageYearlyRevenue  *  np.power(inflation, (2014 - year) ) )
			averageMarketPrice = averageMarketPrice + (averageYearlyMarketPrice * np.power(inflation, 2014 - year))
			count = count + 1

		# Write to the averages data file.
		averageRevenue = averageRevenue / float(count)
		averageMarketPrice = averageMarketPrice / float(count)

		averageString = locationName +", "+state+", "+ str(np.round(averageMarketPrice, decimals = 2))+ ", "+ str(np.round(averageRevenue, decimals = 2))+"\n"
		averagesFile.write(averageString)
		print "Averages written to file."
		for stateAverage in stateAverages:
			if state == stateAverage[0]:
				stateAverage[1] = stateAverage[1] + averageMarketPrice
				stateAverage[2] = stateAverage[2] + averageRevenue
				stateAverage[3] = stateAverage[3] + 1
	for stateAverage in stateAverages:
		state = stateAverage[0]
		averageMarketPrice = float(stateAverage[1]) / float(stateAverage[3])
		averageRevenue = float(stateAverage[2]) / float(stateAverage[3])
		stateAveragesFile.write(str(state)+", "+str(averageMarketPrice)+", "+str(averageRevenue)+"\n")
	
	print "Finished"
	stateAveragesFile.close()
	averagesFile.close()
	yearlyFile.close()







