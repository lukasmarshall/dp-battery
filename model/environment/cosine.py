import subprocess
from datetime import datetime
from utils.timezone import Timezone
import numpy as np

def getCosine(angle, date, lat,lon, tracking=False):
	utcoffset =  np.divide(date.utcoffset().total_seconds(), (60 * 60))

	lat = -1 * lat
	if tracking:
		tracking = "tracking"
	else:
		tracking = "fixed"
	cosine =  subprocess.check_output(["java", "-jar", "cosine.jar", str(tracking), str(angle), str(lat), str(lon), str(date.year), str(date.month), str(date.day), str(date.hour), str(date.minute), str(utcoffset)])
	return np.double(cosine.splitlines()[0])

def generateCosine(lat,lon, path):
	lat = -1 * lat
	subprocess.check_output(["java", "-jar", "cosine_timeseries.jar",  str(lat), str(lat), str(lon), path])


