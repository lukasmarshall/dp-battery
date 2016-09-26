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
		
		averagesPath = "/Users/lukemarshall/Documents/Workspace/Thesis/simulationResults/market/shapedCapRevenue/"+str(strikePrice)+".csv"
		
		averagesFile = open(averagesPath, 'w')
		averagesFile.write("Location, Revenue Fixed, Revenue Tracking\n")

		for location in locations.getLocations():
			lat= location[0]
			lon = location[1]
			state= location[2]
			locationName = location[3]


			if state == "nsw":
				capFactor = 0.280152271502
				capFactorTracking = 0.337531327017
			if state == "vic":
				capFactor = 0.259125863986
				capFactorTracking = 0.319551495158
			if state == "qld":
				capFactor = 0.28828551756
				capFactorTracking = 0.342014584626
			if state == "sa":
				capFactor = 0.317160237904
				capFactorTracking = 0.391816336203

			
			dayCounter = 0
			lastDays = 0
			counter = 0
			
			contractStartHour = 7
			contractEndHour = 16

			
			countAboveStrike = 0
			countFixedDemandMet = 0
			countTrackingDemandMet = 0

			countContractTimePeriods = averagePayoutFixed = averagePayoutTracking = 0
			spotRevenueFixed = spotRevenueTracking = 0
			totalFixedMWh = totalTrackingMWh = 0

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

					date = datetime.datetime(year=int(data[i][0]), month = int(data[i][1]), day = int(data[i][2]), hour=int(data[i][3]), minute=int(data[i][4]), tzinfo=SydneyTimezone())
					if dni > 0:
						trackingCos = data[i][10]
						cos = data[i][9]
						ghi_factor = data[i][8]
						ghi = np.multiply(ghi_factor, dni)
						fixedOutputMWh = plant.getPlantOutput(dni=dni, ghi=ghi, timePeriodHrs=0.5, cosine=cos)
						trackingOutputMWh = plant.getPlantOutput(dni=dni, ghi=ghi, timePeriodHrs=0.5, cosine=trackingCos)
					else:
						fixedOutputMWh = 0
						trackingOutputMWh = 0
					price = int(price)
					
					totalFixedMWh = totalFixedMWh + fixedOutputMWh
					totalTrackingMWh = totalTrackingMWh + trackingOutputMWh




					if price < 0:
						price = 0

					hour = date.hour + (float(date.minute)/60.0)
					timePeriodHrs = 0.5
					mwNameplate = 1
					if hour >= contractStartHour and hour <= contractEndHour: 
						spotRevenueFixed = spotRevenueFixed + fixedOutputMWh * min(price, strikePrice)
						spotRevenueTracking = spotRevenueTracking + trackingOutputMWh * min(price, strikePrice)

						countContractTimePeriods = countContractTimePeriods + 1
						if price > strikePrice:
							averagePayoutFixed = averagePayoutFixed + (capFactor * (price - strikePrice) * timePeriodHrs)
							averagePayoutTracking = averagePayoutTracking + (capFactorTracking * (price - strikePrice) * timePeriodHrs)
							countAboveStrike = countAboveStrike + 1
							if fixedOutputMWh > (capFactor * timePeriodHrs * mwNameplate):
								countFixedDemandMet = countFixedDemandMet + 1
							if trackingOutputMWh > (capFactorTracking * timePeriodHrs * mwNameplate):
								countTrackingDemandMet = countTrackingDemandMet + 1
					else:
						spotRevenueFixed = spotRevenueFixed + fixedOutputMWh * min(price, 300)
						spotRevenueTracking = spotRevenueTracking +  trackingOutputMWh * min(price, 300)

			averagePayoutFixed = float(averagePayoutFixed) / float(countAboveStrike)
			averagePayoutTracking = float(averagePayoutTracking) / float(countAboveStrike)

			probabilityFixedMet = float(countFixedDemandMet) / float(countAboveStrike)
			probabilityTrackingMet = float(countTrackingDemandMet) / float(countAboveStrike)

			probabilityAboveStrike = float(countAboveStrike) / float(countContractTimePeriods)

			trackingPrice = (averagePayoutTracking * probabilityAboveStrike / probabilityTrackingMet) * countContractTimePeriods
			fixedPrice = (averagePayoutFixed * probabilityAboveStrike / probabilityFixedMet) * countContractTimePeriods

			totalRevenueTracking = trackingPrice + spotRevenueTracking
			totalRevenueFixed = fixedPrice + spotRevenueFixed

			revenueTrackingPerMWh = float(totalRevenueTracking) / float(totalTrackingMWh)
			revenueFixedPerMWh = float(totalRevenueFixed) / float(totalFixedMWh)

			averageString = state+", "+str(revenueFixedPerMWh)+","+str(revenueTrackingPerMWh)+"\n"
			averagesFile.write(averageString)

			print "Averages written to file."
	
	print "Finished"
	averagesFile.close()
	# yearlyFile.close()







