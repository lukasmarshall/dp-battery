from controller import Controller
from utils.timezone import SydneyTimezone
import datetime
import numpy as np
from model.plant.solarPlant import SolarPlant
import model.environment.cosine as cosine
import model.environment.locations as locations

def printTimeseries(tracking, fractionContracted):
	if tracking:
		print "Tracking"
		stateAveragesPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/market/shapedCap/tracking/average/"+str(fractionContracted)+"Contracted.csv"
		averagesPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/market/shapedCap/tracking/averagesAll/"+str(fractionContracted)+"Contracted.csv"
		yearlyPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/market/shapedCap/tracking/yearly/"+str(fractionContracted)+"Contracted.csv"

	else:
		print "Non-Tracking"
		stateAveragesPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/market/shapedCap/fixed/average/"+str(fractionContracted)+"Contracted.csv"
		averagesPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/market/shapedCap/fixed/averagesAll/"+str(fractionContracted)+"Contracted.csv"
		yearlyPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/market/shapedCap/fixed/yearly/"+str(fractionContracted)+"Contracted.csv"

	yearlyFile = open(yearlyPath, 'w')
	averagesFile = open(averagesPath, 'w')
	stateAveragesFile = open(stateAveragesPath, 'w')

	yearlyFile.write("Location, State, Year, Average Market Price, Average Revenue, Total Generation MWh, Average PSH/Day, Value of Call, Count Over 300 And Generation, Count Over 300 No Generation\n" ) 
	averagesFile.write("Location, State, Average Market Price, Average Revenue, Average Call Value, Average Count Over 300 And Generation, Average Count Over 300 No Generation\n")
	stateAveragesFile.write("Location, Average Market Price, Average Revenue, Average Call Value, Average Count Over 300 And Generation, Average Count Over 300 No Generation\n")

	stateAverages = [["nsw",0,0,0,0,0,0], ["qld",0,0,0,0,0,0], ["vic",0,0,0,0,0,0], ["sa",0,0,0,0,0,0]]

	print "Beginning Shaped $300 Cap Simulation"
	controller = Controller(gui=False)
	tz = SydneyTimezone()
	inflation = 1.027

	startHour = 7
	finishHour = 20

	for location in locations.getLocations():

		lat= location[0]
		lon = location[1]
		state= location[2]
		locationName = location[3]
		print "==============="+locationName+"==============="
		averageMarketPrice = averageRevenue  = averageCallValue = 0
		averageCountOver300Gen = averageCountOver300NoGen = 0

		startYear = 2005
		endYear = 2011
		for year in np.arange(startYear, endYear + 1):
			print year
			startDate = datetime.datetime(year=year, month=1, day=1, hour=1, tzinfo = tz)
			endDate= datetime.datetime(year=year, month=12, day=31, hour=23, minute=30, tzinfo = tz)
			print "retrieving data"
			data = controller.getTimeseriesNemDNICos(state=state, lat = lat, lon = lon, startDate = startDate, endDate = endDate)
			print "data retrieved"
			plant = SolarPlant(namePlateMW = 1)

			totalYearlyRevenue = totalYearlyMWh = totalYearlySpotPrice = totalYearlyPSH = callValue = yearlyCountOver300Gen = yearlyCountOver300NoGen = 0

			# Iterate through the time series and perform calculations.
			for i in np.arange(data.shape[0]):
				price = data[i][6]
				dni = data[i][7]
				date = datetime.datetime(year=int(data[i][0]), month = int(data[i][1]), day = int(data[i][2]), hour=int(data[i][3]), minute=int(data[i][4]), tzinfo=SydneyTimezone())
				
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

				# ######################################################################
				# Put options pricing stuff here.
				timePeriodHrs = 0.5
				if price > 300 and date.hour >= startHour and date.hour <= finishHour:
					payout = (timePeriodHrs * (price - 300) ) * fractionContracted 
					callValue = callValue + payout
					totalYearlyRevenue= totalYearlyRevenue + (output * price) -  payout
					if output > 0:
						yearlyCountOver300Gen = yearlyCountOver300Gen + 1
					else:
						yearlyCountOver300NoGen = yearlyCountOver300NoGen + 1	
				else:
					totalYearlyRevenue = totalYearlyRevenue + (output * price)
					

				totalYearlyMWh = totalYearlyMWh + output
				totalYearlySpotPrice = totalYearlySpotPrice + price
				# ######################################################################


			# Calculate Yearly Averages
			averageYearlyRevenue = np.divide(totalYearlyRevenue, totalYearlyMWh)
			averageYearlyMarketPrice = np.divide(totalYearlySpotPrice, data.shape[0])
			averagePshPerDay = (totalYearlyPSH / 365.0)

			# Write to the yearly data file.
			yearlyString =  locationName +", "+state+", "+ str(endDate.year) +", "+ str(np.round(averageYearlyMarketPrice, decimals = 2)) +", "+ str(np.round(averageYearlyRevenue, decimals = 2)) 
			yearlyString = yearlyString + ", "+ str(totalYearlyMWh) + ", "+ str(averagePshPerDay)+ ", "+str(callValue)+ ", "+str(yearlyCountOver300Gen)+ ", "+str(yearlyCountOver300NoGen)+"\n"
			yearlyFile.write(yearlyString)
			print "Yearly data written to file."

			# Add to cumulative totals for averaging.
			averageCallValue = averageCallValue + callValue
			averageCountOver300Gen = averageCountOver300Gen + yearlyCountOver300Gen
			averageCountOver300NoGen = averageCountOver300NoGen + yearlyCountOver300NoGen
			averageRevenue = averageRevenue +(averageYearlyRevenue  *  np.power(inflation, (2014 - year) ) )
			averageMarketPrice = averageMarketPrice + (averageYearlyMarketPrice * np.power(inflation, 2014 - year))

		# Write to the averages data file.
		numYears = float(endYear - startYear + 1)
		averageCountOver300Gen = averageCountOver300Gen / numYears
		averageCountOver300NoGen = averageCountOver300NoGen / numYears
		averageCallValue = averageCallValue / numYears
		averageRevenue = averageRevenue / numYears
		averageMarketPrice = averageMarketPrice / numYears

		# Write averages to data file.
		averageString = locationName +", "+state+", "+ str(np.round(averageMarketPrice, decimals = 2))+ ", "+ str(np.round(averageRevenue, decimals = 2))
		averageString = averageString +", "+ str(averageCallValue)+", "+str(averageCountOver300Gen)+", "+str(averageCountOver300NoGen)+"\n"
		averagesFile.write(averageString)
		print "Averages written to file."
		for stateAverage in stateAverages:
			if state == stateAverage[0]:
				stateAverage[1] = stateAverage[1] + averageMarketPrice
				stateAverage[2] = stateAverage[2] + averageRevenue
				stateAverage[3] = stateAverage[3] + averageCallValue
				stateAverage[4] = stateAverage[4] + averageCountOver300Gen
				stateAverage[5] = stateAverage[5] + averageCountOver300NoGen
				stateAverage[6] = stateAverage[6] + 1

	for stateAverage in stateAverages:
		state = stateAverage[0]
		count = float(stateAverage[6])

		averageMarketPrice = float(stateAverage[1]) / count
		averageRevenue = float(stateAverage[2]) / count
		averageCallValue = float(stateAverage[3]) / count
		averageCountOver300Gen = float(stateAverage[4]) / count
		averageCountOver300NoGen = float(stateAverage[5]) / count
		
		averageString = state+", "+ str(np.round(averageMarketPrice, decimals = 2))+ ", "+ str(np.round(averageRevenue, decimals = 2))
		averageString = averageString +", "+ str(averageCallValue)+", "+str(averageCountOver300Gen)+", "+str(averageCountOver300NoGen)+"\n"
		stateAveragesFile.write(averageString)
	
	print "Finished"
	averagesFile.close()
	yearlyFile.close()





