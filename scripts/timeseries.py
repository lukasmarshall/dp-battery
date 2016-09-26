from controller import Controller
from utils.timezone import SydneyTimezone
import datetime
import numpy as np
def printTimeseries():
	controller = Controller(gui=False)
	tz = SydneyTimezone()
	startDate = datetime.datetime(year=2011, month=1, day=1, hour=1, tzinfo = tz)
	endDate= datetime.datetime(year=2011, month=2, day=1, hour=1, tzinfo = tz)
	data = controller.getTimeseriesNemDNICos(state="nsw", lat = -33, lon = 150, startDate = startDate, endDate = endDate)
	print "Year, Month, Day, Hour, Minutes, Demand, RRP_$_per_MWh, DNI_W/M2, Horizontal_Cos, Fixed_Cos, Tracking_Cos"
	for i in np.arange(data.shape[0]):
		print str(int(data[i][0]))+", "+str(int(data[i][1]))+", "+str(int(data[i][2]))+", "+str(int(data[i][3]))+", "\
				+str(int(data[i][4]))+", "+str(data[i][5])+", "+str(data[i][6])+", "+str(data[i][7])+", "+str(data[i][8])\
				+", "+str(data[i][9])+", "+str(data[i][10]) 
