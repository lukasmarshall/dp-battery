import numpy as np
from model.plant.solarPlant import SolarPlant as Plant
from model.plant.batteryStorage import BatteryStorage as Storage
from controller import Controller
from utils.timezone import SydneyTimezone
import datetime
import sys
from multiprocessing import Process, Queue



class Algorithm():

	def __init__(self, numStates, batteryType="Pb-A", capped = False, shaved = False, shavingFactor = 1.2):
		self.capped = capped
		if(capped):
			print "CAPPED!!!!!"
		self.shaved = shaved
		self.batteryType = batteryType
		self.numStates = numStates
		self.DEFAULT_TIME_INTERVAL = 0.5
		self.path = None
		self.startDate = None
		self.endDate = None

		self.minFractionSolarOutputToStore = 0.05
		self.shavingFactor = shavingFactor


		self.YEAR_INDEX = 0
		self.MONTH_INDEX = 1
		self.DAY_INDEX = 2
		self.HOUR_INDEX = 3
		self.MINUTE_INDEX = 4
		self.PRICE_INDEX = 6
		self.DNI_INDEX = 7
		self.GHI_FACTOR_INDEX = 8

		# Could I have gotten these mixed up?
		self.FIXED_COS_INDEX = 9
		self.TRACKING_COS_INDEX = 10


		if self.capped:
			print "CAPPED"
		if self.shaved:
			print "SHAVED!"



	def runAlgorithm(self, startDate, endDate, location, tracking, storageMWh):

		self.startDate = startDate
		self.endDate = endDate

		self.adjustStorageLevels(storageMWh)

		
		# Run the dynamic programming algorithm and get the results, which is effectively a series of store/sell decisions.
		results = self.buildValuesBackwards(startDate, endDate, location, tracking, storageMWh)
		destinations = results[1]
		print "Total MWh Generated: "+str(results[4])

		
		traverseResult = self.traversePath(destinations)
		averageStorageLevel = traverseResult['averageStorageLevel']
		path = traverseResult['path']

		self.path = path
		self.results = results

		self.printResults(results, path)
		
		print "Average Storage Level: "+ str(averageStorageLevel)


		values = results[0]
		revPerMWhSolar = np.divide(np.float(values[0][0]), np.float(results[4]))
		print "++ Rev Per MWh Solar: "+ str(revPerMWhSolar)
		
		if self.shaved:
			rerunRevenue = self.followPathBackThroughDataset(destinations, startDate, endDate, location, storageMWh, tracking)
			revPerMWhSolar = np.divide(np.float(rerunRevenue), np.float(results[4]) ) 
			print "++ Shaved Revenue: "+str(revPerMWhSolar)
		return (revPerMWhSolar, averageStorageLevel)
	
	def traversePath(self, destinations):
		# Follow the path, also calculate average storage level.
		path = np.zeros(shape=(destinations.shape[0]))
		next = 0 #Starting Point
		averageStorageLevel = 0
		print str(destinations.shape)
		for i in np.arange(destinations.shape[0]):
			next = int(round(destinations[i][next]))
			averageStorageLevel = averageStorageLevel + next
			path[i] = next
		averageStorageLevel = np.divide(float(averageStorageLevel), float(destinations.shape[0]))
		averageStorageLevel = np.divide(averageStorageLevel, float(self.numStates))
		return {'path':path, 'averageStorageLevel':averageStorageLevel}
	

	def buildValuesBackwards(self, startDate, endDate, location, tracking, storageMWh):
		#reverse the arrays containing price and solar data.
		print "Building Values Backwards"
		tz = SydneyTimezone()
		lat= location[0]
		lon = location[1]
		state= location[2]
		# locationName = location[3]
		startDate = startDate.astimezone(tz)
		endDate = endDate.astimezone(tz)

		controller = Controller(gui=False)
		data = controller.getTimeseriesNemDNICos(state=state, lat = lat, lon = lon, startDate = startDate, endDate = endDate)
		plant = Plant(namePlateMW = 1)
		storage = Storage(storageLevels = self.numStates, effectiveCapacityMWh = storageMWh, batteryType = self.batteryType)
		plant = Plant(1)

		values=np.zeros(shape=(data.shape[0] + 1, storage.getNumStorageLevels()+1))
		destinations = np.zeros(shape=( data.shape[0] + 1, storage.getNumStorageLevels()+1))
		
		totalArrayOutput = 0

		# if self.shaved:
		# 	data = self.shaveNemData(data)

		if tracking:
			COS_INDEX = self.TRACKING_COS_INDEX
		else:
			COS_INDEX = self.FIXED_COS_INDEX

		#iterate backwards through time.
		for timeIndex in np.arange(0, data.shape[0])[::-1]:
			# Get the timeperiod outputs
			cos = data[timeIndex][COS_INDEX]
			price = data[timeIndex][self.PRICE_INDEX]

			if self.capped:
				price = min(price, 300)

			dni = data[timeIndex][self.DNI_INDEX]
			ghi_factor = data[timeIndex][self.GHI_FACTOR_INDEX]
			ghi = np.multiply(ghi_factor, dni)			
			arrayOutput = plant.getPlantOutput(dni=dni, ghi=ghi, timePeriodHrs=0.5, cosine=cos)
			totalArrayOutput = totalArrayOutput + arrayOutput
			date = datetime.datetime(year=int(data[timeIndex][self.YEAR_INDEX]), month = int(data[timeIndex][self.MONTH_INDEX]), day = int(data[timeIndex][self.DAY_INDEX]), hour=int(data[timeIndex][self.HOUR_INDEX]), minute=int(data[timeIndex][self.MINUTE_INDEX]), tzinfo=SydneyTimezone())
			
			# iterate through the storagelevels
			for storageLevel in np.arange(storage.getNumStorageLevels()+1):
				# Find the optimal destination and its corresponding value
				valueAndDestination = self.getValueAndDestination(storage = storage, price=price, solarOutputMWh=arrayOutput, storageLevel=storageLevel,  nextTimePeriodValues = values[timeIndex + 1], date = date)
				values[ timeIndex, storageLevel] = valueAndDestination[0]
				destinations[timeIndex, storageLevel] = valueAndDestination[1]
		
		prices = np.transpose(data)[self.PRICE_INDEX]
		sun = np.transpose(data)[self.DNI_INDEX]
		
		return (values, destinations,prices, sun, totalArrayOutput)


	def shaveNemData(self, data):
		previousPrice = data[0][self.PRICE_INDEX]
		for timeIndex in np.arange(0, data.shape[0]):
			price = data[timeIndex][self.PRICE_INDEX]
			# If the next price goes up by more than the shaving factor
			if self.capped:
				price = min(price, 300)
			if price > self.shavingFactor * previousPrice:
				price = previousPrice * self.shavingFactor
				data[timeIndex][self.PRICE_INDEX] = price
			elif price < (1 - (self.shavingFactor - 1)) * previousPrice: #or down by more than the shaving factor
				price = previousPrice * (1 - (self.shavingFactor - 1))
				data[timeIndex][self.PRICE_INDEX] = price
			previousPrice = price
		return data

	def getValueAndDestination(self, storage, price, solarOutputMWh, storageLevel,  nextTimePeriodValues, date):
		# returns list of tuples that contain the level and the output MWh lalala
		storageLevels = storage.getDestinationStorageLevels( inputMWh = solarOutputMWh, storageLevel = storageLevel, timeInterval =  self.DEFAULT_TIME_INTERVAL)
		maxValueDestination = storageLevel
		maxValue = -1000000 #arbitrary incredibly low number for initialisation

		for destination in storageLevels:
			#put value function here
			level = destination[0]
			outputMWh = destination[1]
			costOfMovement = destination[2]
			value =  self.valueFunction(outputMWh, price, date)
			value = value - costOfMovement
			value = value + nextTimePeriodValues[level] 
			if value > maxValue:
				maxValue = value
				maxValueDestination = level

		return (maxValue, maxValueDestination)

	def getRerunPRevPerMwhSolar(self):
		return self.rerunRevPerMWhSolar

	def valueFunction(self, outputMWh, priceDollarsPerMWh, dateAndTime):
		return np.multiply(outputMWh, priceDollarsPerMWh)

	def printResults(self,results, path):
		values = results[0]
		valueOfZeroStart = values[0][0]
		destinations = results[1]
		prices = results[2]
		sun = results[3]
		totalArrayMWh = results[4]

		# print "values"
		# for i in np.arange(values.shape[0]):
		# 	for j in np.arange(values.shape[1]):
		# 		sys.stdout.write(str(round(values[i][j]))+" ")
		# 	print ""

		# print "destinations"
		# for i in np.arange(destinations.shape[0]):
		# 	if i < prices.shape[0]:
		# 		sys.stdout.write("$"+str(round(prices[i]))+"/MWh ")
		# 		sys.stdout.write("DNI: "+str(round(sun[i]))+"W  ")
		# 	for j in np.arange(destinations.shape[1]):
		# 		sys.stdout.write(str(round(destinations[i][j]))+" ")
		# 	print ""

		print "Length of path:"+str(path.shape[0])
		print "Length of prices:"+str(prices.shape[0])

		# #Print the path
		# print "Path:"
		# for i in np.arange(prices.shape[0]):
		# 	print "$"+str(prices[i])+"   DNI:"+str(max(sun[i],0))+"W            "+str(path[i])

		revPerMWhSolar = np.divide(np.float(valueOfZeroStart), np.float(results[4]))
		print "Revenue: "+str(round(revPerMWhSolar, 2))+ "/ MWh Solar Energy Generated"

	def followPathBackThroughDataset(self, destinations, startDate, endDate, location, storageMWh, tracking):
		#reverse the arrays containing price and solar data.
		print "Following Path back through dataset."
		tz = SydneyTimezone()
		lat= location[0]
		lon = location[1]
		state= location[2]
		# locationName = location[3]
		startDate = startDate.astimezone(tz)
		endDate = endDate.astimezone(tz)

		controller = Controller(gui=False)
		data = controller.getTimeseriesNemDNICos(state=state, lat = lat, lon = lon, startDate = startDate, endDate = endDate)
		plant = Plant(namePlateMW = 1)
		storage = Storage(storageLevels = self.numStates, effectiveCapacityMWh = storageMWh, batteryType = self.batteryType)
		plant = Plant(1)

		#iterate backwards through time.
		totalRevenue = 0
		currentLevel = 0

		if tracking:
			COS_INDEX = self.TRACKING_COS_INDEX
		else:
			COS_INDEX = self.FIXED_COS_INDEX

		for timeIndex in np.arange(0, data.shape[0]):
			# Get the timeperiod outputs
			cos = COS_INDEX
			price = data[timeIndex][self.PRICE_INDEX]
			if self.capped and price > 300:
				price = 300
			dni = data[timeIndex][self.DNI_INDEX]
			ghi_factor = data[timeIndex][self.GHI_FACTOR_INDEX]
			ghi = np.multiply(ghi_factor, dni)			
			arrayOutput = plant.getPlantOutput(dni=dni, ghi=ghi, timePeriodHrs=0.5, cosine=cos)
			
			date = datetime.datetime(year=int(data[timeIndex][self.YEAR_INDEX]), month = int(data[timeIndex][self.MONTH_INDEX]), day = int(data[timeIndex][self.DAY_INDEX]), hour=int(data[timeIndex][self.HOUR_INDEX]), minute=int(data[timeIndex][self.MINUTE_INDEX]), tzinfo=SydneyTimezone())
			
			nextLevel = destinations[timeIndex][currentLevel]
			storageEnergy = storage.getEnergyOut(currentLevel, nextLevel)
			costOfMovement = storage.getCostOfMovement(currentLevel, nextLevel)
			outputMWh = arrayOutput + storageEnergy
			value = self.valueFunction(outputMWh, price, date) - costOfMovement
			totalRevenue = totalRevenue + value
			currentLevel = nextLevel
		
		return totalRevenue

	def getAverageStrategy(self):
		if self.path is not None:
			startIndex = int((self.startDate.hour * 2) + round(2 * float(self.startDate.minute)/ 60.0))
			averagePath = np.zeros(shape=(48))

			index = startIndex
			counter = 0
			for level in self.path:
				averagePath[index] = averagePath[index] + level
				index = index + 1
				if index >= 48:
					index = 0
					counter = counter + 1
			for i in np.arange(averagePath.shape[0]):
				averagePath[i] = float(averagePath[i]) / float(counter)
				averagePath[i] = float(averagePath[i]) / float(self.numStates)
			return averagePath

	

	def getProbabilityStrategy(self):
			if self.path is not None:
				startIndex = int((self.startDate.hour * 2) + round(2 * float(self.startDate.minute)/ 60.0))
				averagePath = np.zeros(shape=(48))

				index = startIndex
				counter = 0
				for level in self.path:
					if level > 1:
						averagePath[index] = averagePath[index] + 1
					index = index + 1
					if index >= 48:
						index = 0
						counter = counter + 1
				for i in np.arange(averagePath.shape[0]):
					averagePath[i] = float(averagePath[i]) / float(counter)
					# averagePath[i] = float(averagePath[i]) / float(self.numStates)
				return averagePath

	def getFullStrategy(self):
		results = self.results
		path = self.path
		prices = results[2]
		sun = results[3]
		outData = np.zeros(shape=(prices.shape[0], 4))
		halfHour = int((self.startDate.hour * 2) + round(2 * float(self.startDate.minute)/ 60.0))
		for i in np.arange(prices.shape[0]):
			outData[i][0] = round(float(halfHour)/ 2.0, 1)
			outData[i][1] = prices[i]
			outData[i][2] = max(sun[i],0)
			outData[i][3] = path[i]
			halfHour = halfHour + 1
			if halfHour >= 48:
				halfHour = 0
		return outData

	def adjustStorageLevels(self, storageMWh):
		# Calculate the minimum number of storage levels for an accurate result given the fraction of solar output to store in each timeperiod
		minStorageLevels = int(round(storageMWh / (self.minFractionSolarOutputToStore / 2)))
		# Adjust the number of possible battery states if it is less than the required minimum calculated above.
		if self.numStates < minStorageLevels:
			print "Storage levels requested too low. Resetting storage levels to: "+str(minStorageLevels)+" levels"
			self.numStates = minStorageLevels



	# def buildValuesBackwardsThreading(self, startDate, endDate, location, tracking, storageMWh):
	# 		#reverse the arrays containing price and solar data.
	# 		print "Building Values Backwards"
	# 		tz = SydneyTimezone()
	# 		lat= location[0]
	# 		lon = location[1]
	# 		state= location[2]
	# 		# locationName = location[3]
	# 		startDate = startDate.astimezone(tz)
	# 		endDate = endDate.astimezone(tz)

	# 		controller = Controller(gui=False)
	# 		data = controller.getTimeseriesNemDNICos(state=state, lat = lat, lon = lon, startDate = startDate, endDate = endDate)
	# 		plant = Plant(namePlateMW = 1)
	# 		storage = Storage(storageLevels = self.numStates, effectiveCapacityMWh = storageMWh, batteryType = self.batteryType)
	# 		plant = Plant(1)

	# 		values=np.zeros(shape=(data.shape[0] + 1, storage.getNumStorageLevels()+1))
	# 		destinations = np.zeros(shape=( data.shape[0] + 1, storage.getNumStorageLevels()+1))
			
	# 		totalArrayOutput = 0
	# 		#iterate backwards through time.
	# 		for timeIndex in np.arange(0, data.shape[0])[::-1]:
	# 			# Get the timeperiod outputs
	# 			if tracking:
	# 				cos = data[timeIndex][10]
	# 			else:
	# 				cos = data[timeIndex][9]
				

	# 			price = data[timeIndex][6]
	# 			if self.capped:
	# 				price = min(price, 300)
	# 			dni = data[timeIndex][7]
	# 			ghi_factor = data[timeIndex][8]
	# 			ghi = np.multiply(ghi_factor, dni)			
	# 			arrayOutput = plant.getPlantOutput(dni=dni, ghi=ghi, timePeriodHrs=0.5, cosine=cos)
	# 			totalArrayOutput = arrayOutput + totalArrayOutput
	# 			date = datetime.datetime(year=int(data[timeIndex][0]), month = int(data[timeIndex][1]), day = int(data[timeIndex][2]), hour=int(data[timeIndex][3]), minute=int(data[timeIndex][4]), tzinfo=SydneyTimezone())
	# 			# iterate through the storagelevels

	# 			threadQueue = Queue()
	# 			threads = []
	# 			for storageLevel in np.arange(storage.getNumStorageLevels()+1):
	# 				myThread = Process(target = self.getValueAndDestinationThreading, args =(storage, price, arrayOutput, storageLevel,  values[timeIndex + 1],  date, threadQueue) )
	# 				myThread.start()
	# 				threads.append(myThread)
	# 			for t in threads:
	# 				t.join()
	# 			while not threadQueue.empty():
	# 				result = threadQueue.get()
	# 				storageLevel = result[0]
	# 				values[ timeIndex, storageLevel] = result[1]
	# 				destinations[timeIndex, storageLevel] = result[2]
				
	# 		print "Values Built"
	# 		return (values, destinations,data[...,6], data[...,7], totalArrayOutput)


	# def getValueAndDestinationThreading(self, storage, price, solarOutputMWh, storageLevel,  nextTimePeriodValues, date, threadQueue):
	# 	# returns list of tuples that contain the level and the output MWh lalala
	# 	storageLevels = storage.getDestinationStorageLevels( inputMWh = solarOutputMWh, storageLevel = storageLevel, timeInterval =  self.DEFAULT_TIME_INTERVAL)
	# 	maxValueDestination = storageLevel
	# 	maxValue = -1000000

	# 	for destination in storageLevels:
	# 		#put value function here
	# 		level = destination[0]
	# 		outputMWh = destination[1]
	# 		value =  self.valueFunction(outputMWh, price, date)
	# 		value = value + nextTimePeriodValues[level]
	# 		if value > maxValue:
	# 			maxValue = value
	# 			maxValueDestination = level

	# 	threadQueue.put((storageLevel, maxValue, maxValueDestination))





