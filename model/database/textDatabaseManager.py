import numpy as np
import datetime
import re
import os
# import scripts.originalDataFiles.solarDataTextUtils as solarDataTextUtils
import controller
import utils.timezone as timezone
from utils.timezone import Timezone



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
		self.path = path
		self.preRootPath = "/Volumes/SOLAR"
		# self.preRootPath = ""
		

	def getTimeseriesNemData(self, state, startDate, endDate):
		folderPath = "./nemData"
		data = np.loadtxt(folderPath+"/"+state+".csv", delimiter=',',dtype='string',skiprows=1, usecols=None, unpack=False)
		timeseries = None
		for i in np.arange(data.shape[0]):
			date = datetime.datetime(year=int(data[i][0]), month = int(data[i][1]), day = int(data[i][2]), hour = int(data[i][3]), minute=int(data[i][4]), tzinfo=timezone.SydneyTimezone())
			if date >= startDate:
				if timeseries is None:
					print date
					timeseries = np.zeros(shape=(1))
					timeseries.fill(float(data[i][6]))
					print 
				else:
					np.append(timeseries, [float(data[i][6])])
					print timeseries.shape[0]
				print timeseries.shape[0]
			if date >= endDate:
				break;
		print timeseries
		return timeseries

	def checkDatesValid(self, startDate, endDate):
		tz = Timezone()
		minDate = datetime.datetime(year=1996, month=1, day = 1, hour = 1, tzinfo = tz)
		maxDate = datetime.datetime(year=2012, month = 6, day = 30, hour = 11, tzinfo = tz)
		if startDate >= minDate and startDate <= maxDate and startDate < endDate:
			return True
		else:
			return False

	def getTimeseriesData(self,lat, lon, startDate, endDate, queue, dni=True):
		print "getting timeseries data from text files"
		if dni:
			print "Getting DNI Data"
			rootPath = self.preRootPath+"/"+"SOLAR_DATA/time_series_hourly_dni"
		else:
			print "Getting GHI Data"
			rootPath = self.preRootPath+"/"+"SOLAR_DATA/time_series_hourly_ghi"

		startYear = startDate.year
		endYear = endDate.year
		data = None
		totalDifference = endDate - startDate
		totalHours = (totalDifference.days * 24) + (totalDifference.seconds/(60.0* 60.0))
		self.controller.updateSolarHeatmapProgress(0)
		# "Year, Month, Day, Hour, Minute, Value
		for year in np.arange(startYear, endYear+1):
			folderPath = rootPath+"/"+str(year)
			files = os.listdir(folderPath)
			for f in files:
				fileDate = self.getDateFromFileName(f)
				if fileDate is not None:
					if fileDate >= startDate and fileDate <= endDate:
						print f
						radiation = self.getRadiationAtLatLong(folderPath+"/"+f, lat, lon)
						datapoint = np.array([[fileDate.year, fileDate.month, fileDate.day, fileDate.hour, fileDate.minute, radiation]], dtype='i')
						remainingDifference = endDate - fileDate
						percent = 1 - np.divide(np.float((remainingDifference.days * 24) + (remainingDifference.seconds/(60.0 * 60.0))),totalHours)
						self.controller.updateSolarHeatmapProgress(percent)
						if data is None:
							data = datapoint
						else:
							data = np.concatenate((data, datapoint))
		queue.put(data)
		
	def getRadiationAtLatLong(self, path, latitude, longitude):
		#open the file and get the header info such as coords, cell size, numrows and cols.
		xy = self.latLongToXY(latitude, longitude)
		xcoord = xy[0]
		ycoord = xy[1]
		data = np.loadtxt(path, dtype='float',skiprows=6, usecols=None, unpack=False)
		# print "Table Coordinates: "+str(ycoord)+","+str(xcoord)
		# print "Size of Table: "+str(data.shape[0])+","+str(data.shape[1])
		radiation = data[ycoord, xcoord]
		return np.float(radiation)

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
		tz = timezone.Timezone()
		return datetime.datetime(year=1996, month=1, day=1, hour=1, tzinfo = tz)

	def getSolarEndDatetime(self):
		tz = timezone.Timezone()
		return datetime.datetime(year=1997, month=1, day=1, hour=1, tzinfo = tz)


	def generateAverageHeatmapData(self, startDate, endDate, queue):
		print "Generating Cumulative Array."
		return np.zeros(shape=(self.MAX_SOLAR_Y_DIMENSION, self.MAX_SOLAR_X_DIMENSION))


	def generateAverageCosineHeatmapData(self, startDate, endDate, queue):
		print "Generating Cumulative Array."
		return np.zeros(shape=(self.MAX_SOLAR_Y_DIMENSION, self.MAX_SOLAR_X_DIMENSION))

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



	def getDateFromFileName(self,fileName):
		#Define the pattern the solar data files names follow.
		regex = '([a-z_]+)([0-9]{4})([0-9]{2})([0-9]{2})_([0-9]{2})UT.txt'
		#Check if the file name conforms to this pattern
		m = re.search(regex, fileName)
		date = None
		#If the filename conforms to the pattern, add the date and the DNI.
		if(m is not None):

			# dataType = m.group(1)
			year = int(m.group(2))
			month = int(m.group(3))
			day = int(m.group(4))
			hour = int(m.group(5))


			tz = timezone.Timezone()
			date = datetime.datetime(year=year, month=month, day=day, hour=hour, tzinfo = tz)
		return date
		





