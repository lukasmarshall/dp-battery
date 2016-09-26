from controller import Controller
from utils.timezone import SydneyTimezone
import datetime
import numpy as np
from model.plant.solarPlant import SolarPlant
import model.environment.cosine as cosine
import model.environment.locations as locations
from scripts import lcoe


def printTimeseries(tracking):

	controller = Controller(gui=False)
	tz = SydneyTimezone()
	inflation = 1.027

	for location in locations.getLocations():

		lat= location[0]
		lon = location[1]
		state= location[2]
		locationName = location[3]
		
		lcoes = lcoe.getLCOEHighLow(tracking, location)
		lcoeHigh = lcoes[0]
		lcoeLow = lcoes[1]

		if tracking:
			path = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/market/solarMarketFactorCapped/tracking/"+locationName+".csv"
		else:
			path = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/market/solarMarketFactorCapped/fixed/"+locationName+".csv"
		
		outFile = open(path, 'w')
		outFile.write("Month, Solar-Market Factor High, Solar-Market Factor Low, Average Revenue, Average Market Price\n" ) 
		
		for month in np.arange(1,13):
			lastDayOfMonth = 31
			if month == 9 or month == 4 or month == 6 or month == 11:
				lastDayOfMonth = 30
			elif month == 2:
				lastDayOfMonth = 28

			counter = 0
			averageMonthlyRevenue = 0
			averageMonthlySpotPrice =0
			totalMonthlyMWh = 0
			totalMonthlyRevenue = 0
			totalMonthlyMWh = 0
			totalMonthlySpotPrice = 0
			totalMonthlyRevenue = totalMonthlyMWh = totalMonthlySpotPrice = totalYearlyPSH = 0
			for year in np.arange(2005, 2012):
				print year
				startDate = datetime.datetime(year=year, month=month, day=1, hour=1, tzinfo = tz)
				endDate= datetime.datetime(year=year, month=month, day=lastDayOfMonth, hour=23, minute=30, tzinfo = tz)
				print "retrieving data"
				data = controller.getTimeseriesNemDNICos(state=state, lat = lat, lon = lon, startDate = startDate, endDate = endDate)
				print "data retrieved"
				plant = SolarPlant(namePlateMW = 1)

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

					totalMonthlyRevenue = totalMonthlyRevenue + (output * price)

					totalMonthlyMWh = totalMonthlyMWh + output
					totalMonthlySpotPrice = totalMonthlySpotPrice + price
					counter = counter + 1

			averageMonthlyRevenue = np.divide(totalMonthlyRevenue, totalMonthlyMWh)
			averageMonthlySpotPrice = np.divide(totalMonthlySpotPrice, float(counter))
			# averagePshPerDay = (totalYearlyPSH / 365.0)

			factorHigh = (averageMonthlyRevenue / max(lcoeHigh, averageMonthlySpotPrice)) - 1
			factorLow = (averageMonthlyRevenue / max(lcoeLow, averageMonthlySpotPrice)) - 1

			# Write to the yearly data file.
			outString =  str(int(round(month))) +", "+ str(np.round(factorHigh, decimals = 2)) +", "+ str(np.round(factorLow, decimals = 2))+ ", "+str(np.round(averageMonthlyRevenue, decimals = 2))+", "+ str(np.round(averageMonthlySpotPrice, decimals = 2)) +"\n"
			outFile.write(outString)
		

	print "Finished"
	outFile.close()







