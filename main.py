import controller
from utils import timezone
import datetime


tz = timezone.Timezone()
date = datetime.datetime(year=2011, month=1, day=2, hour=20, tzinfo = tz)
# path = "/Volumes/SOLAR/SOLAR_DATA/time_series_hourly_dni/1996/test.hdf5"
datasetPath = "./test.hdf5"
folderPath = "./testFiles"


cont = controller.Controller(textDatabase = True)
# cont.displayImage(date)
print "done"