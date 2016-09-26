#Luke Marshall, Fri 30 August 2013
#takes in lat and long as command arguments, prints the radiation at that point.
import sys
import numpy as np

def getRadiationAtLatLong(path, latitude, longitude):

	#open the file and get the header info such as coords, cell size, numrows and cols.
	
	bottomLeftLatLong = getBottomLeftLatLong(path)
	cellSize = getCellSize(path)
	colsRows = getColsRows(path)
	minLatitude = np.float(bottomLeftLatLong[0] - np.multiply(cellSize, np.float(colsRows[1])))
	maxLongitude = np.float(bottomLeftLatLong[1] + np.multiply(cellSize, np.float(colsRows[0])))
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




def dataFileInfoTester():
	path = "testFile.txt"
	
	#test cell size reader.
	print "Testing Getting Cell Size"
	compare(np.float(0.05), getCellSize(path))
	#test latitude, longitude reading.
	print "Testing Getting Longitude"
	compare(np.float(112.025), getBottomLeftLatLong(path)[1]) #longitude
	print "Testing Getting Latitude"
	compare(np.float(-43.975), getBottomLeftLatLong(path)[0]) #latitude
	#test cols, rows
	print "Testing getting number of columns"
	compare(np.float(839), getColsRows(path)[0]) #cols
	print "Testing getting number of rows"
	compare(np.float(679), getColsRows(path)[1]) #rows

	

def radiationAtLatLongTester():
	# -314 at bottom coords (112.025, -43.975)
	# -159 at next half degree of longitude going east (eg minus one half degree longitude) (111.975, -43.975)
	path = "testfile.txt"
	print "Testing getting radiation at bottom left corner"
	compare(np.float(-314), getRadiationAtLatLong(path, np.float(-43.975),np.float(112.025)))
	

def compare(control, result):
	control = np.round(control)
	result = np.round(result)
	if(control != result):
		print "xxxxxxxxxxxx     No Match! Control = "+str(control) + "    Result = "+str(result)+"    xxxxxxxxxxx"
	else:
		print "MATCH! :)     Control = "+str(control) + "    Result = "+str(result)


if(len(sys.argv) == 2):
	if(sys.argv[1] == "test"):
		print "=====RUNNING TESTS====="
		dataFileInfoTester()
		radiationAtLatLongTester()
	else:
		print "Wrong number of arguments, exiting. Usage: python radiationAtLatLong.py <filename> <lat> <long>  or python radiationAtLatLong.py test for testing"
elif(len(sys.argv) == 4 ):
	path = np.float(sys.argv[1])
	latitude = np.float(sys.argv[2])
	longitude = np.float(sys.argv[3])
	print "===================================="
	print "Finding radiation at coordinates ("+str(latitude)+","+str(longitude)+")"
	print "In File "+path
	print "===================================="
	
	dataFile = open(path, 'r')
	radiation = getRadiationAtLatLong(dataFile, latitude, longitude)
	dataFile.close()
	print "Done."
else:
	print "Wrong number of arguments, exiting. Usage: python radiationAtLatLong.py <filename> <lat> <long>  or python radiationAtLatLong.py test for testing"
