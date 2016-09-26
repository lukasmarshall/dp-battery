from model.plant.batteryStorage import BatteryStorage as Storage
from model.plant.solarPlant import SolarPlant as Plant
import numpy as np

def runTest():
	plant = Plant(namePlateMW = 4)
	storage = Storage(storageLevels = 120, effectiveCapacityMWh = 1, batteryType = "Li-Ion")

	error = False
	for storageLevel in np.arange(100):
		solarOutputMWh = 0.4
		storageLevels = storage.getDestinationStorageLevels( inputMWh = solarOutputMWh, storageLevel = storageLevel, timeInterval =  0.5)
		
		for destination in storageLevels:
			#put value function here
			level = destination[0]

			if level == storageLevel:
				found = True
				outputMWh = destination[1]
				costOfMovement = destination[2]
				if outputMWh != solarOutputMWh:
					print "Error: In not same as out!"
					print "battery output: "+str(outputMWh)
					print "solar output: "+str(solarOutputMWh)
					error = True

	if error:
		print "!!!!!! ++++++ TEST FAILED ++++++ !!!!!!"
	else:
		print "<<<<<< TEST PASSED! :D >>>>>>"

		
		