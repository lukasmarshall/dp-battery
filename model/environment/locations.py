import numpy as np

def getLocations():
	locations = np.loadtxt("model/environment/locations.txt",dtype='string', delimiter = ",",skiprows=0, usecols=None, unpack=False)
	modifiedLocations = []
	for i in np.arange(locations.shape[0]):
		
		lat = float(str(locations[i][0]).strip(' "\'\t\r\n'))
		lon = float(str(locations[i][1]).strip(' "\'\t\r\n'))
		state = str(locations[i][2]).strip()
		state = state.strip(' "\'\t\r\n')
		name = str(locations[i][3]).strip()
		name = name.strip(' "\'\t\r\n')
		lcoe = np.float(locations[i][4])
		capValue = float(str(locations[i][5]).strip(' "\'\t\r\n'))

		print "lat:"+str(lat)
		print "lon:"+str(lon)

		loc = [lat, lon, state, name, lcoe, capValue]

		modifiedLocations.append(loc)
	return modifiedLocations

def getLocation(placeName):
	locations = getLocations()
	for i in range(len(locations)):
		if locations[i][3] == placeName:
			return locations[i]

