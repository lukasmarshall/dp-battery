import numpy as np

def saveTimeseriesDataAsCSV(data, path):
	print "Beginning Write"
	f = open(path, 'w')
	print "opened file"
	f.write("Year, Month, Day, Hour_UTC, Minute, Value\n")
	for y in np.arange(data.shape[0]):
		for x in np.arange(data.shape[1]):
			if int(data[y][x]) == int(-999):
				f.write("NaN")
			else:
				f.write(str(int(data[y][x])))
			f.write(",")
		f.write("\n")
	f.close()