# Takes a latitude, longitude as arguments, spits out timeseries data from individual files in the given folder.
# By Luke Marshall
# 3 September 2013



import os
import re
import numpy as np
import datetime

# Implementation of the abstract tzinfo class, to represent the UTC timezone with no DST adjustments. 
# We need to pass the datetime object one of these so that they are active and thus know their position relative to other times.
# If you dont pass a datetime a tzinfo, it's naive and thus can't be properly sorted relative to other times.

class timezone(datetime.tzinfo):
	def __init__(self):
		print "woo!"

	def dst(self, dt):
		return datetime.timedelta(0)

	def utcoffset(self, dt):
		return 0

	def tzname(self, dt):
		return "UTC"


def getRadiationAtLatLong(path, latitude, longitude):
	suitableLatLong = True

	#open the file and get the header info such as coords, cell size, numrows and cols.
	
	bottomLeftLatLong = getBottomLeftLatLong(path)
	cellSize = getCellSize(path)
	colsRows = getColsRows(path)
	minLatitude = np.float(bottomLeftLatLong[0] - np.multiply(cellSize, np.float(colsRows[0])))
	maxLongitude = np.float(bottomLeftLatLong[1] + np.multiply(cellSize, np.float(colsRows[1])))
	maxLatitude = bottomLeftLatLong[0]
	minLongitude = bottomLeftLatLong[1]
	topRightLatitude = bottomLeftLatLong[0] + np.multiply(cellSize,(colsRows[1]- 1))
	topRightLongitude = bottomLeftLatLong[1]

	print "Minimum lat, long = ("+str(minLatitude)+","+str(minLongitude)+")"
	print "Top right lat, long = ("+str(topRightLatitude)+","+str(topRightLongitude)+")"
	print "Requested lat, long = ("+str(latitude)+","+str(longitude)+")"
	# Verify that lat and long are reasonable so we don't explode the file.
	if(latitude >= minLatitude and latitude <= maxLatitude and longitude >= minLongitude and longitude <= maxLongitude):
		xcoord = int(np.round(np.divide(np.float(topRightLongitude - longitude), cellSize)))
		ycoord = int(np.round(np.divide(np.float(topRightLatitude - latitude), cellSize)))
		data = np.loadtxt(path, dtype='float',skiprows=6, usecols=None, unpack=False)
		print "Table Coordinates: "+str(ycoord)+","+str(xcoord)
		print "Size of Table: "+str(data.shape[0])+","+str(data.shape[1])
		radiation = data[ycoord, xcoord]

	else:
		print "Latitude and longitude are invalid for this file."
		radiation = -1

	return radiation

def getBottomLeftLatLong(path):
	dataFile = open(path,'r')
	for i, line in enumerate(dataFile):
		#longitude
		if(i == 2):
			# print "Found long"
			longitude = np.float(line.split()[1])
		elif(i == 3):
			# print "Found lat"
			latitude = np.float(line.split()[1])
			break
	
	dataFile.close()
	if(latitude is None or longitude is None):
		print "Error getting lat, long, latitude of longitude is None."
	else:
		return (latitude, longitude)

def getCellSize(path):
	# print "Getting Cell size"
	dataFile = open(path,'r')
	for i, line in enumerate(dataFile):
		# print line
		if(i == 4): 
			# print "Found cellsize"
			cellSize = np.float(line.split()[1])
			break
	
	dataFile.close()

	if(cellSize is None):
		print "Error getting cell size, cell size is None."
	else:
		return cellSize

def getColsRows(path):
	dataFile = open(path,'r')
	for i, line in enumerate(dataFile):
		if i == 0:
			numCols = np.float(line.split()[1])
		if i == 1:
			numRows = np.float(line.split()[1])

	dataFile.close()
	if(numCols is None or numRows is None):
		print "Error getting numCols, numRows, numCols or numRows is None."
	else:
		return (numCols, numRows)


# list the files in the directory
# print os.listdir("./")

#For every file in the directory
for fileName in os.listdir("./")
	# split apart a filename
	# fileName = "solar_dni_20120108_20UT.txt"
	# testRegex = '(?<=abc)def'
	# testString = 'abcdef'

	#Define the pattern the solar data files names follow.
	regex = '([a-z_]+)([0-9]{4})([0-9]{2})([0-9]{2})_([0-9]{2})UT.txt'
	#Check if the file name conforms to this pattern
	m = re.search(regex, fileName)

	#If the filename conforms to the pattern, add the date and the DNI.
	if(m is not None):

		dataType = m.group(1)
		year = int(m.group(2))
		#DUDE be CAREFUl these (month/day) are the right way round, no way to check right now!!!
		month = int(m.group(3))
		day = int(m.group(4))
		hour = int(m.group(5))

		print "type: "+str(dataType)
		print "year: "+str(year)
		print "month: "+str(month)
		print "day: "+str(day)
		print "hour: "+str(hour)

		tz = timezone()
		date = datetime.datetime(year=year, month=month, day=day, hour=hour, tzinfo = tz)

	else:
		print "file not matching correct pattern."









