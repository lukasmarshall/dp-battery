#Created by Luke Marshall, January 2014.
#utilities for handling specific file formats of solar data files.
#Do not use for anything else
#Do not write apps with these utilities they are SLOW and for testing purposes only.
# These utilities do not use HDF5 - for application writing, use HDF5 only!!!!!!!!

import re

def getValueAtIndex(filePath, yIndex, xIndex):
	
	f= open(filePath,'r',8096)
	NUM_LINES_AT_TOP = 6

	#locate the desired line.
	counter = -1 * NUM_LINES_AT_TOP
	for line in f:
		if counter == yIndex:
			break
		counter += 1

	#split the line and get the desired value.
	value = line.split()[xIndex]
	
	return value

def isFileNameValid(fileName):
	#Define the pattern the solar data files names follow.
	regex = '([a-z_]+)([0-9]{4})([0-9]{2})([0-9]{2})_([0-9]{2})UT.txt'
	#Check if the file name conforms to this pattern
	m = re.search(regex, fileName)

	#If the filename conforms to the pattern, add the date and the DNI.
	if(m is None):
		return False
	else:
		return True

