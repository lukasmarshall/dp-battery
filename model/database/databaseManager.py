import sys
import numpy as np
import os
import datetime
import re
import scripts.originalDataFiles.solarDataTextUtils as solarDataTextUtils
# import controller
import utils.timezone as timezone
import model.environment.cosine as cosine
import sys



class DatabaseManager():
	def __init__(self, controller,path):
		self.SOLAR_DATASET_NAME= "dniDataSet"
		self.MAX_SOLAR_X_DIMENSION= 839
		self.MAX_SOLAR_Y_DIMENSION= 679
		self.BOT_LEFT_LAT = -43.975
		self.BOT_LEFT_LON =112.025
		self.CELL_SIZE = 0.05
		self.controller = controller
		self.EMPTY_DATA_NUMBER = -999
		self.controller = controller
		self.database = None
		self.path = path
		

	def getSolarDataset(self,path=""):
		if self.database is None:
			self.openDatabase(self.path)
		return self.database[self.SOLAR_DATASET_NAME]
		
	
	def openDatabase(self,path):
		#returns a read-only dataset.
		import h5py
		f = h5py.File(path,'r')
		# print "Opened - keys: "+str(f.keys())
		if f is None:
			self.controller.errorMessage("Error: file not found.")
		self.database = f
		return f

	def getTimeseriesCosData(self, lat, lon, startDate, endDate):
		print "getting cos data"
		folderPath = "cosData"
		fileList = os.listdir(folderPath)
		
		tz = timezone.SydneyTimezone()
		startDate = startDate.astimezone(tz)
		endDate = endDate.astimezone(tz)
		cosFileName = str(int(round(lat)))+"-"+str(int(round(lon)))+".csv"
		cosData = None
		timeseries = None

# 		try to find the file in the file list.
		for f in fileList:
			if f == cosFileName:
				cosData = np.loadtxt(folderPath +"/"+f ,dtype='float', delimiter = ",",skiprows=0, usecols=None, unpack=False)
		
		if cosData is None:
			print "Please insert solar data hard drive"
			sys.exit()
			# newPath = folderPath+"/"+cosFileName
			# print "generating cosine at "+newPath
			# cosine.generateCosine(lat, lon, path=folderPath+"/"+cosFileName)
			# print "finished generation."
			# cosData = np.loadtxt(newPath ,dtype='float', delimiter = ",",skiprows=0, usecols=None, unpack=False)
		
		date = startDate
		# print "assembling cosine data series."

		timeseries = None
		for i in np.arange(cosData.shape[0]):
			date = datetime.datetime(year = int(cosData[i][0]), month = int(cosData[i][1]), day = int(cosData[i][2]), hour = int(cosData[i][3]), tzinfo = timezone.SydneyTimezone())
			if date >= startDate and date <= endDate:
				timePeriod = cosData[i]
				if timeseries is None:
					timeseries = timePeriod
				else:
					timeseries = np.vstack((timeseries, timePeriod))

		print "cosine data series assembled."
		return timeseries




	def isLeapYear(self, year):
		isLeapYear = None
		if year % 4 != 0:
			 isLeapYear = False
		elif year %100 != 0:
			 isLeapYear = True
		elif year %400 == 0:
			 isLeapYear = True
		else:
			isLeapYear = False
		return isLeapYear




	def getTimeseriesNemDNICos(self, state, lat, lon, startDate, endDate):
		folder = "overallData"
		fileName = str(state)+str(int(round(lat)))+str(int(round(lat)))
		fileName = fileName+str(startDate.year)+str(startDate.month)+str(startDate.day)+str(startDate.hour)+str(startDate.minute)
		fileName = fileName + str(endDate.year)+str(endDate.month)+str(endDate.day)+str(endDate.hour)+str(endDate.minute)+".csv"
		print str(lat)
		print str(lon)
		print folder+"/"+fileName


		timeseries = None
		fileList = os.listdir(folder)
		for f in fileList:
			if f == fileName:
				print "Existing dataset found. Reading from file."
				timeseries = np.loadtxt(folder +"/"+f ,dtype='float', delimiter = ",",skiprows=0, usecols=None, unpack=False)
		
		if timeseries is None:
			print folder+"/"+fileName
			print "Compiling new  dataset"
			print "Getting Nem Data"
			nemData = self.getTimeseriesNemData(state , startDate, endDate)
			print "Getting Cos Data"
			cosData = self.getTimeseriesCosData(lat, lon, startDate, endDate)
			print "Getting DNI Data"
			solarData = self.getHalfHourTimeseriesData(lat, lon, startDate, endDate)
			print "Assembling Data Series"
			timeseries = None
			for i in np.arange(nemData.shape[0]):
				date = datetime.datetime(year=int(nemData[i][0]), month = int(nemData[i][1]), day = int(nemData[i][2]), hour = int(nemData[i][3]), minute=int(nemData[i][4]), tzinfo=timezone.SydneyTimezone())
				cosDate = datetime.datetime(year = int(cosData[i][0]), month = int(cosData[i][1]), day = int(cosData[i][2]), hour = int(cosData[i][3]), minute = int(cosData[i][4]), tzinfo = timezone.SydneyTimezone())
				solarDate = datetime.datetime(year = int(solarData[i][0]), month = int(solarData[i][1]),day = int(solarData[i][2]), hour = int(solarData[i][3]), minute = int(solarData[i][4]), tzinfo = timezone.SydneyTimezone() )

				if date == cosDate and date == solarDate:
					dni = solarData[i][5]
					timePeriod = np.zeros(shape=(11))
					timePeriod[0] = nemData[i][0] #Year
					timePeriod[1] = nemData[i][1] #Month
					timePeriod[2] = nemData[i][2] #Day
					timePeriod[3] = nemData[i][3] #Hour
					timePeriod[4] = nemData[i][4] #Minute
					timePeriod[5] = nemData[i][5] #Demand
					timePeriod[6] = np.float(nemData[i][6]) #Spot Price
					timePeriod[7] = np.float(dni) #DNI
					timePeriod[8] = cosData[i][5] # Horizontal Cosine
					timePeriod[9] = cosData[i][6] # Fixed Cosine
					timePeriod[10] = cosData[i][7] #Tracking Cosine
					if timeseries is None:
						timeseries = timePeriod
					else:
						timeseries = np.vstack((timeseries, timePeriod))

				else:
					print "Horrific date error. "
					print date
					print cosDate
					print solarDate

			np.savetxt(folder+"/"+fileName, timeseries, delimiter=', ', newline='\n')
		
		return timeseries



	def getTimeseriesNemData(self, state, startDate, endDate):
		# AEMO data is in AEST - GMT + 10
		tz = timezone.SydneyTimezone()
		startDate = startDate.astimezone(tz)
		endDate = endDate.astimezone(tz)

		folderPath = "./nemData"
		
		data = np.loadtxt(folderPath+"/"+state+".csv", delimiter=',',dtype='string',skiprows=1, usecols=None, unpack=False)
		timeseries = None
		for i in np.arange(data.shape[0]):
			date = datetime.datetime(year=int(data[i][0]), month = int(data[i][1]), day = int(data[i][2]), hour = int(data[i][3]), minute=int(data[i][4]), tzinfo=timezone.SydneyTimezone())
			if date >= startDate and date <= endDate:
				timePeriod = np.zeros(shape=(7))
				timePeriod[0] = int(data[i][0])
				timePeriod[1] = int(data[i][1])
				timePeriod[2] = int(data[i][2])
				timePeriod[3] = int(data[i][3])
				timePeriod[4] = int(data[i][4])
				timePeriod[5] = np.float(data[i][5])
				timePeriod[6] = np.float(data[i][6])
				if timeseries is None:
					timeseries = timePeriod
				else:
					timeseries = np.vstack((timeseries, timePeriod))

		return timeseries


		
	def getDNI(self, lat, lon, date):
		tz = timezone.Timezone()
		date = date.astimezone(tz)
		xy = self.latLongToXY(lat, lon)
		dset = self.getSolarDataset()
		
		if date.minute < 2 or date.minute > 58:
			timeIndex = getIndexOfDate(date, dset)
			dni = dset[xy[1],xy[0],timeIndex]
		else:
			date1 = datetime.datetime(year = date.year, month = date.month, day = date.day, hour = date.hour, minute = 0, tzinfo = tz)
			timeDiff = datetime.timedelta(hours=1)
			date2 = date1 + timeDiff
			dni1 = self.getDNI(lat, lon, date1)
			dni2 = self.getDNI(lat, lon, date2)
			dni1Weight = np.divide(date.minute, 60)
			dni2Weight = 1 - dni1Weight
			dni = np.divide( ( np.multiply(dni1Weight, dni1) + np.multiply(dni2Weight, dni2) ),2)
		return max(0, dni)


	def _WattsToPSH(self,watts):
		return float(watts/1000.0)



	def getDateOfIndex(self, index, dset):
		tz = timezone.Timezone()
		startDate = datetime.datetime(year = dset.attrs['startYear'], month = dset.attrs['startMonth'], day = dset.attrs['startDay'], hour= dset.attrs['startHour'], minute = dset.attrs['startMinute'], tzinfo = tz)
		minIntervals = dset.attrs['minsBetweenDataPoints']
		minsDifference = np.multiply(np.float(minIntervals), np.float(index))
		timeDifference = datetime.timedelta(minutes=minsDifference)
		indexDate = startDate + timeDifference
		return indexDate


	def getDNIMap(self,date):
		#initialise numpy array.
		array = np.empty([self.MAX_SOLAR_Y_DIMENSION,self.MAX_SOLAR_X_DIMENSION])

		if self.database is None:
			self.openDatabase(self.path)
		#get the correct date index in the dataset.
		index = getIndexOfDate(date, self.database[self.SOLAR_DATASET_NAME])
		#retrieve the solar dataset.
		dset=self.database[self.SOLAR_DATASET_NAME]
		
		#copy line by line into numpy array.
		for y in range(dset.shape[0]):
			array[y] = dset[y,...,index]
		return array

	def getTimeseriesData(self,lat, lon, startDate, endDate):

		try:
			dset = self.database[self.SOLAR_DATASET_NAME]

			coords = self.latLongToXY(lat,lon)
			# print "lat: "+str(lat) + "     lon:"+str(lon)
			x = coords[0]
			y = coords[1]


			startIndex = getIndexOfDate(startDate, dset)
			endIndex = getIndexOfDate(endDate, dset)

			if(startIndex < 0):
				self.controller.errorMessage("Start date is too early for dataset.")
				startIndex = 0
			if(endIndex < startIndex):
				self.controller.errorMessage("End date is before start date.")
				endIndex = min(startIndex + 1, dset.shape[0])
			if(endIndex < 0):
				self.controller.errorMessage("End date is too early for dataset.")
				endIndex = startIndex + 1
			if(startIndex > dset.shape[2]):
				self.controller.errorMessage("Start date is too late for dataset.")
				endIndex = max(0, endIndex - 1)
			stz = timezone.SydneyTimezone()
			# print "lat: "+str(lat) + "    lon:" + str(lon)
			# print "x:"+str(x) + "    y: "+str(y)
			if(x >= 0 and  x < self.MAX_SOLAR_X_DIMENSION) and (y >= 0 and y < self.MAX_SOLAR_Y_DIMENSION):

				data = np.zeros(shape=((endIndex - startIndex), 6))
				for timeIndex in np.arange(startIndex-2, endIndex):
					# print timeIndex
					date = self.getDateOfIndex(timeIndex, dset=dset)
					sydDate = date.astimezone(stz)
					data[timeIndex - startIndex][0] = sydDate.year
					data[timeIndex - startIndex][1] = sydDate.month
					data[timeIndex - startIndex][2] = sydDate.day
					data[timeIndex - startIndex][3] = sydDate.hour
					data[timeIndex - startIndex][4] = sydDate.minute
					data[timeIndex - startIndex][5] = dset[y,x,timeIndex]
			else:
				self.controller.errorMessage("X and Y Coords out of range! x="+str(x)+"  y="+str(y))
				data = [1,2,3,4,5,6,7][1,2,3,4,5,6,7][1,2,3,4,5,6,7][1,2,3,4,5,6,7][1,2,3,4,5,6,7][1,2,3,4,5,6,7]

			return data
		except IndexError:
			self.controller.errorMessage("Database Index Error")

	def getHalfHourTimeseriesData(self,lat, lon, startDate, endDate):

		try:
			if self.database is None:
				self.openDatabase(self.path)
			dset = self.database[self.SOLAR_DATASET_NAME]

			coords = self.latLongToXY(lat,lon)
			# print "lat: "+str(lat) + "     lon:"+str(lon)
			x = coords[0]
			y = coords[1]

			startIndex = getIndexOfDate(startDate, dset)
			endIndex = getIndexOfDate(endDate, dset)


			if(startIndex < 0):
				self.controller.errorMessage("Start date is too early for dataset.")
				startIndex = 0
			if(endIndex < startIndex):
				self.controller.errorMessage("End date is before start date.")
				endIndex = min(startIndex + 1, dset.shape[0])
			if(endIndex < 0):
				self.controller.errorMessage("End date is too early for dataset.")
				endIndex = startIndex + 1
			if(startIndex > dset.shape[2]):
				self.controller.errorMessage("Start date is too late for dataset.")
				endIndex = max(0, endIndex - 1)
			stz = timezone.SydneyTimezone()
			# print "lat: "+str(lat) + "    lon:" + str(lon)
			# print "x:"+str(x) + "    y: "+str(y)
			if(x >= 0 and  x < self.MAX_SOLAR_X_DIMENSION) and (y >= 0 and y < self.MAX_SOLAR_Y_DIMENSION):

				index = startIndex
				timeDiff = datetime.timedelta(minutes = 30)
				date = self.getDateOfIndex(startIndex, dset)
				date = date.astimezone(stz)
				timeseries = None
				while date <= endDate:
					if date.minute == 30:
						dni = (dset[y,x,index] + dset[y,x,index+1]) / 2.0
					else:
						dni = dset[y,x,index]
					sydDate = date.astimezone(stz)
					timePeriod = np.zeros(shape=(6))
					timePeriod[0] = sydDate.year
					timePeriod[1] = sydDate.month
					timePeriod[2] = sydDate.day
					timePeriod[3] = sydDate.hour
					timePeriod[4] = sydDate.minute
					timePeriod[5] = dni
					if timeseries is None:
						timeseries = timePeriod
					else:
						timeseries = np.vstack((timeseries, timePeriod))

					date = date + timeDiff
					if date.minute == 0:
						index = index + 1

			return timeseries
		except IndexError:
			self.controller.errorMessage("Database Index Error")


	def latLongToXY(self,lat,lon):
		x = int(np.round((lon - self.BOT_LEFT_LON) / self.CELL_SIZE))
		y = self.MAX_SOLAR_Y_DIMENSION - int(np.round((lat - self.BOT_LEFT_LAT) / self.CELL_SIZE))
		x = min(x, self.MAX_SOLAR_X_DIMENSION - 1)
		y = min(y, self.MAX_SOLAR_Y_DIMENSION - 1)
		return (x,y)

	def xyToLatLong(self,x,y):
		lat = self.BOT_LEFT_LAT + np.multiply((self.MAX_SOLAR_X_DIMENSION - x),self.CELL_SIZE)
		lon = self.BOT_LEFT_LON + np.multiply(y, self.CELL_SIZE)
		return (lat, lon)
	def getSolarStartDatetime(self):
		if self.database is None:
			self.openDatabase(self.path)
		dset = self.database[self.SOLAR_DATASET_NAME]
		return self.getDateOfIndex(0,dset)
		# return self.getSolarEndDatetime()
	def getSolarEndDatetime(self):
		if self.database is None:
			self.openDatabase(self.path)
		dset = self.database[self.SOLAR_DATASET_NAME]
		return self.getDateOfIndex(dset.shape[2], dset)

	def generateAverageHeatmapData(self, startDate, endDate, queue):
		print "Generating Cumulative Array."

		firstLoopFraction = 0.9
		secondLoopFraction = 0.1
		if self.database is None:
			self.openDatabase(self.path)
		dset = self.database[self.SOLAR_DATASET_NAME]
		cumulativeArray = np.zeros(shape=[self.MAX_SOLAR_Y_DIMENSION, self.MAX_SOLAR_X_DIMENSION])
		countArray = np.zeros(shape=[self.MAX_SOLAR_Y_DIMENSION, self.MAX_SOLAR_X_DIMENSION])
		
		startIndex = getIndexOfDate(startDate, dset)
		endIndex = getIndexOfDate(endDate, dset)

		#set up mapping functions for the data.
		negFilter = np.vectorize(self.negativeFilter) #get rid of negatives.
		countConverter = np.vectorize(self.isPositive) #count a value only if greater than zero

		#Add the values to the cumulative array by iterating through all time periods.
		#Here we need to keep track of how many times every pixel has a value added, as data drops in and out.
		for i in np.arange(startIndex, endIndex):

			#Stuff for controlling how the gui interacts with the algorithm.
			if self.controller.heatmapIsCancelled():
				break
			percent = np.multiply(np.divide(np.float(i), endIndex - startIndex),firstLoopFraction)
			self.controller.updateSolarHeatmapProgress((percent))
			
			#iterate through all the rows in a given time period 'i'
			for y in np.arange(dset.shape[0]):
				#add the row's values to the cumulative array.
				# print str(dset[y,...,i])
				cumulativeArray[y] = np.add(cumulativeArray[y], negFilter(dset[y,...,i]))
				# print str(cumulativeArray[y])
				#add whether each position in the row has had a value added. (for averaging.)
				countArray[y] = np.add(countArray[y], countConverter(dset[y,...,i]))
				if self.controller.heatmapIsCancelled():
					break
		
		# lastPercent = firstLoopFraction

		#Perform Averaging on each datapoint ie. pixel.
		for y in np.arange(cumulativeArray.shape[0]):
			if self.controller.heatmapIsCancelled():
				break
			percent = np.multiply(np.divide(np.float(y), cumulativeArray.shape[0]) , secondLoopFraction)
			self.controller.updateSolarHeatmapProgress((percent) + firstLoopFraction)

			for x in np.arange(cumulativeArray.shape[1]):
				if(countArray[y][x] >0):
					cumulativeArray[y][x] = np.divide(cumulativeArray[y][x], countArray[y][x])
				else:
					cumulativeArray[y][x] = self.EMPTY_DATA_NUMBER
				if self.controller.heatmapIsCancelled():
					break

		# DANGER FOR TESTING ONLY OVERRIDE EVERYTHING YOU DO AND FILL THE CUMULATIVE ARRAY WITH JUNK
		# cumulativeArray.fill(999)


		print "Cumulative Array Generated."
		queue.put(cumulativeArray)


	def generateAverageCosineHeatmapData(self, startDate, endDate, queue):
		print "Generating Cumulative Array."

		firstLoopFraction = 0.9
		secondLoopFraction = 0.1
		if self.database is None:
			self.openDatabase(self.path)
		dset = self.database[self.SOLAR_DATASET_NAME]
		cumulativeArray = np.zeros(shape=[self.MAX_SOLAR_Y_DIMENSION, self.MAX_SOLAR_X_DIMENSION])
		countArray = np.zeros(shape=[self.MAX_SOLAR_Y_DIMENSION, self.MAX_SOLAR_X_DIMENSION])
		
		startIndex = getIndexOfDate(startDate, dset)
		endIndex = getIndexOfDate(endDate, dset)

		#set up mapping functions for the data.
		negFilter = np.vectorize(self.negativeFilter) #get rid of negatives.
		countConverter = np.vectorize(self.isPositive) #count a value only if greater than zero

		#Add the values to the cumulative array by iterating through all time periods.
		#Here we need to keep track of how many times every pixel has a value added, as data drops in and out.
		for i in np.arange(startIndex, endIndex):

			#Stuff for controlling how the gui interacts with the algorithm.
			if self.controller.heatmapIsCancelled():
				break
			percent = np.multiply(np.divide(np.float(i), endIndex - startIndex),firstLoopFraction)
			self.controller.updateSolarHeatmapProgress((percent))
			
			#iterate through all the rows in a given time period 'i'
			for y in np.arange(dset.shape[0]):
				#add the row's values to the cumulative array.
				# print str(dset[y,...,i])
				#perform cosine adjustment calculations
				cosineAdjusted = negFilter(dset[y,...,i])
				for x in np.arange(cosineAdjusted.shape[0]):
					latlon = self.xyToLatLong(x,y)
					date = self.getDateOfIndex(i, dset)
					cos = cosine.getCosine(angle=latlon[0], date = date, lat = latlon[0], lon=latlon[1], tracking=False)
					cosineAdjusted[x] = np.multiply(cosineAdjusted[x], cos)
				cumulativeArray[y] = np.add(cumulativeArray[y], cosineAdjusted)
				# print str(cumulativeArray[y])
				#add whether each position in the row has had a value added. (for averaging.)
				countArray[y] = np.add(countArray[y], countConverter(dset[y,...,i]))
				if self.controller.heatmapIsCancelled():
					break
		
		# lastPercent = firstLoopFraction

		#Perform Averaging on each datapoint ie. pixel.
		for y in np.arange(cumulativeArray.shape[0]):
			if self.controller.heatmapIsCancelled():
				break
			percent = np.multiply(np.divide(np.float(y), cumulativeArray.shape[0]) , secondLoopFraction)
			self.controller.updateSolarHeatmapProgress((percent) + firstLoopFraction)

			for x in np.arange(cumulativeArray.shape[1]):
				if(countArray[y][x] >0):
					cumulativeArray[y][x] = np.divide(cumulativeArray[y][x], countArray[y][x])
				else:
					cumulativeArray[y][x] = self.EMPTY_DATA_NUMBER
				if self.controller.heatmapIsCancelled():
					break

		# DANGER FOR TESTING ONLY OVERRIDE EVERYTHING YOU DO AND FILL THE CUMULATIVE ARRAY WITH JUNK
		# cumulativeArray.fill(999)
		print "Cumulative Array Generated."
		queue.put(cumulativeArray)

	def isPositive(self,x):
		if (x > 0):
			return 1
		else:
			return 0

	def negativeFilter(self, x):
		if x > 0:
			return x
		else:
			return 0


	def getPriceData(self):
		return np.arange(100)

	def getInsolationData(self):
		return np.arange(100)

# createSolarDataset()

def createSolarDataset(folderPath, datasetPath=None, database=None):
		print "\n\n\n\n\n\n\n\n\n======================"
		print "CREATING SOLAR DATABASE"
		print "Original Data Folder: "+folderPath
		print "HDF5 File: "+datasetPath
		print "======================\n\n\n\n\n\n\n\n\n"
		

		#path for data to be read in
		fileList = os.listdir(folderPath)
		# print fileList

		#create the hdf5 file
		if database is None:
			try:
				import h5py
				database = h5py.File(datasetPath, 'w')
				print "Database Opened. Keys: "+ str(database.keys())
			except IOError:
				print "Could not open database!"

		SOLAR_DATASET_NAME= "dniDataSet"
		MAX_SOLAR_X_DIMENSION= 839
		MAX_SOLAR_Y_DIMENSION= 679

		BOT_LEFT_LAT = -43.975
		BOT_LEFT_LON =112.025
		CELL_SIZE = 0.05
		EMPTY_DATA_NUMBER = -999



		#initialise the dataset in the hdf5 file.
		#if you don't initialise with the right x and y dimensions, we slow down like CRAZY every time we resize. NOT WORTH IT
		
		try:
			dset = database[SOLAR_DATASET_NAME]
			print "\n\n!!!!!!!!!!!!==============ADDING TO OLD DATASET==============!!!!!!!!\n\n"
		except KeyError as e:
			print "\n\nNot found: "+str(e)
			print "==============Dataset not found - CREATING NEW DATASET==============\n\n"
			dset = database.create_dataset(SOLAR_DATASET_NAME,(MAX_SOLAR_Y_DIMENSION,MAX_SOLAR_X_DIMENSION,1),dtype='i',maxshape=(MAX_SOLAR_Y_DIMENSION,MAX_SOLAR_X_DIMENSION,None),chunks=True,fillvalue = EMPTY_DATA_NUMBER)
			dset.attrs['startYear'] = np.int(1995)
			dset.attrs['startMonth'] = np.int(12)
			dset.attrs['startDay'] = np.int(30)
			dset.attrs['startHour'] = np.int(1)
			dset.attrs['startMinute'] = np.int(0)
			dset.attrs['minsBetweenDataPoints'] = np.int(60)

		# iterate through timeseries
		for fileName in fileList:
			if(solarDataTextUtils.isFileNameValid(fileName)):
				print str(fileName)
				# read the dataset into  numpy array
				testData = np.loadtxt(folderPath+"/"+fileName, dtype='float',skiprows=6, usecols=None, unpack=False)
				
				# print fileName
				date = getDateFromFileName(fileName)
				# print date
				dateIndex = getIndexOfDate(date, dset)
				#if the dataset is smaller than the required date index:

				if(dset.shape[2] <= dateIndex):
					#resize the dataset to fit the index.
					dset.resize((MAX_SOLAR_Y_DIMENSION,MAX_SOLAR_X_DIMENSION,dateIndex+1),axis=None)
					# print str(dset.shape)
				if(dset.shape[0] > MAX_SOLAR_Y_DIMENSION or dset.shape[1] > MAX_SOLAR_X_DIMENSION):
					print "Error: Dataset is the wrong shape."
				
				
				# iterate through latitude axis
				for i in np.arange(dset.shape[0]):
					
					# read an entire row into the hdf5 dataset.
					dset[i,...,dateIndex] = testData[i]

					#for testing only, fill it instead with a single number.
					# to use this you also need to oment out the verification loop down the bottom there.
					# fullSun = np.zeros(shape=(MAX_SOLAR_X_DIMENSION))
					# fullSun.fill(999)
					# dset[i,...,dateIndex] = fullSun


				
				
				# Now verify data read in correctly.
				for i in np.arange(dset.shape[0]):
					if not (dset[i,...,dateIndex] == testData[i]).all():
						print "======================================"
						print "DATA NOT READ IN CORRECTLY."
						print "======================================"
						break;



		# self.database.close()
		print "Database Created. Keys: "+str(database.keys())

		
		return database


def getDateFromFileName(fileName):
	#Define the pattern the solar data files names follow.
	regex = '([a-z_]+)([0-9]{4})([0-9]{2})([0-9]{2})_([0-9]{2})UT.txt'
	#Check if the file name conforms to this pattern
	m = re.search(regex, fileName)

	#If the filename conforms to the pattern, add the date and the DNI.
	if(m is not None):

		dataType = m.group(1)
		year = int(m.group(2))
		month = int(m.group(3))
		day = int(m.group(4))
		hour = int(m.group(5))


		tz = timezone.Timezone()
		date = datetime.datetime(year=year, month=month, day=day, hour=hour, tzinfo = tz)

	else:
		controller.errorMessage("file not matching correct pattern.")

	return date

def getIndexOfDate(date, dset):
	#gets the index of a given date in the dataset.
	#can return negative indexes if the given date is before the start of the dataset.

	#get the start date object of the dataset
	tz = timezone.Timezone()
	date = date.astimezone(tz)
	
	startDate = datetime.datetime(year = dset.attrs['startYear'], month = dset.attrs['startMonth'], day = dset.attrs['startDay'], hour= dset.attrs['startHour'], minute = dset.attrs['startMinute'], tzinfo = tz)
	minIntervals = dset.attrs['minsBetweenDataPoints']
	#a timedelta object is the result of the subtraction of two dates
	timeDifference = date - startDate
	minsInDay = np.multiply(24,60)
	secondsInMinute = np.float(60)
	timeDifferenceMinutes = np.multiply(timeDifference.days, minsInDay) + np.divide(timeDifference.seconds, secondsInMinute)

	index = np.divide(timeDifferenceMinutes, minIntervals)
	index = np.int(np.round(index))

	return index







