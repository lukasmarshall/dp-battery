import databaseManager
import os



# folderPath = "/Volumes/SOLAR/SOLAR_DATA/time_series_hourly_dni"
# datasetPath = "/Volumes/SOLAR/data.hdf5"
folderPath = "./testFiles"
datasetPath = "./test.hdf5"


yearFolders = os.listdir(folderPath)
dset = None
for yearPath in yearFolders:
	print "Yearpath: "+yearPath
	if yearPath != ".DS_Store":
		dset = databaseManager.createSolarDataset(folderPath+"/"+yearPath, datasetPath = datasetPath, database = dset)
print "============= DONE =============="
