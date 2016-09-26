import numpy as np
import random

class BatteryStorage():
	def __init__(self, storageLevels, effectiveCapacityMWh, batteryType, gridInput = False, maxOutputPowerMW = 1, timePeriodHours = 0.5):
		print "***Initialising Battery Storage ***"
		

		specs = getBatterySpecs(batteryType)
		self.maxOutputPowerMW = maxOutputPowerMW
		self.timePeriodHours = timePeriodHours
		self.batteryType = specs[0]
		self.selfDischargePerDay = specs[1]
		self.cycleEfficiency = specs[2]
		self.maxCycles = specs[3]
		self.maxDod = specs[4]
		self.costPerKWh = specs[5]
		print "======Self Discharge Per Day = "+str(self.selfDischargePerDay)

		print "Initialising Storage: Levels = "+str(storageLevels)+"   Capacity MWh = "+str(effectiveCapacityMWh)+"   Battery Type = "+self.batteryType

		# Incorporate degradation
		
		timePeriodsPerDay = float(48)
		self.lossPerTimePeriod = np.divide(self.selfDischargePerDay, timePeriodsPerDay)
		oneStorageLevelFraction = 1.0 /  float(storageLevels)
		
		# We find the degradation interval and make sure we can cast it to an integer (float infinity will fail)
		VERY_BIG_NUMBER = 1e6
		self.degradationInterval = int(round(min(oneStorageLevelFraction / self.lossPerTimePeriod, VERY_BIG_NUMBER)))
		self.counter = 0
	

		# Incorporate Costs
		capitalCost = np.divide(effectiveCapacityMWh, float(self.maxDod)) * self.costPerKWh * 1000
		costPerCycle = np.divide(capitalCost, float(self.maxCycles))
		self.costPerStorageLevelChange = np.divide(costPerCycle, float(2 * (storageLevels + 1) ) )

		# Incorporate cycle efficiencies
		# We will simply split the cycle efficiencies evenly between charging and discharging. 
		self.inOutEfficiency = np.sqrt(self.cycleEfficiency)

		self.storageLevels = storageLevels
		self.capacityMWh = np.float(effectiveCapacityMWh)
		
		# Use the energy power ratio to determine what the maximum discharge might be. 
		self.maxDischargeMWh = float(maxOutputPowerMW) * float(timePeriodHours)

		# self.maxDischargeMWh = (np.divide(float(effectiveCapacityMWh), float(self.maxDod)) / self.energyPowerRatio) * np.divide(float(24), float(timePeriodsPerDay))
		# self.maxDischargeMWh = min(self.maxDischargeMWh, self.capacityMWh)

		self.oneLevelMWh = np.divide(np.float(self.capacityMWh) , np.float(self.storageLevels))
		self.maxDischargeLevels = max(int(np.divide(np.float(self.maxDischargeMWh), np.float(self.oneLevelMWh))),1)
		if self.maxDischargeLevels < 1:
			print "ERROR: Maximum Discharge Levels < 1"
			print "Increase Storage Discretisation"


		self.maxChargeLevels = storageLevels
		if self.maxDischargeLevels < 1:
			print "ERROR: Maximum Charge Levels < 1"
			print "Increase Storage Discretisation"

		self.gridInput = gridInput

		print "maxDischargeLevels = "+str(self.maxDischargeLevels)
		print "maxChargeLevels = "+str(self.maxChargeLevels)
		print "Cost Per Storage Level Change: "+str(self.costPerStorageLevelChange)

	def getEnergyOut(self, currentLevel, nextLevel):

		if currentLevel > nextLevel:
			return self.oneLevelMWh * (currentLevel - nextLevel) * self.inOutEfficiency
		else:
			return self.oneLevelMWh * (currentLevel - nextLevel) / self.inOutEfficiency


	def getCostOfMovement(self, currentLevel, nextLevel):

		return float(abs(currentLevel - nextLevel)) * self.costPerStorageLevelChange


	def getNumStorageLevels(self):
		return self.storageLevels

	def getCapacityMWh(self):
		return self.capacityMWh

	def getDestinationStorageLevels(self, inputMWh, storageLevel, timeInterval):
		availableChargeMWh = np.multiply(inputMWh, self.inOutEfficiency)
		availableChargeLevels = int(availableChargeMWh / self.oneLevelMWh)
		self.counter = self.counter + 1
		
		# Degrade the storage if needed. 
		# Recall that each time period we call this function as many times as we have storage levels.
		if self.counter  > self.degradationInterval * self.storageLevels:
			storageLevel = max(storageLevel - 1, 0)
		if self.counter > self.degradationInterval * self.storageLevels + self.storageLevels:
			self.counter = 0

		# Trim the start and end levels for efficiency.
		maxDischargeLevels = float((self.maxOutputPowerMW * self.timePeriodHours) + inputMWh) / float(self.oneLevelMWh)
		maxDischargeLevels = min(maxDischargeLevels, self.maxDischargeLevels)

		startLevel = max(0,storageLevel - maxDischargeLevels - 1) #Just trust me you need the -1 here.
		endLevel = min(storageLevel + self.maxChargeLevels, self.storageLevels)
		
		if not self.gridInput: #If we cant get energy from the grid we can trim the end level even further by how much energy is available.
			maxCharge = int(availableChargeMWh / self.oneLevelMWh)
			endLevel = min(storageLevel + maxCharge, endLevel)

		storageLevels = []
		for destinationLevel in np.arange(startLevel, endLevel + 1):
			#CHARGING
			if destinationLevel >= storageLevel: 
				chargeLevels = destinationLevel - storageLevel
				if self.gridInput and chargeLevels > availableChargeLevels: #If the grid input is on and the charge is greater than able to be provided by the sun.
					outputMWh = -1 * (chargeLevels * self.oneLevelMWh- availableChargeMWh)
				else: #Otherwise subtract the energy required from the total input MWh
					outputMWh = inputMWh - ( (chargeLevels * self.oneLevelMWh) / self.inOutEfficiency)
				costOfMovement = self.costPerStorageLevelChange * chargeLevels 
			#DISCHARGING
			else: 
				dischargeLevels = storageLevel - destinationLevel
				costOfMovement = self.costPerStorageLevelChange * dischargeLevels 

				outputMWh =min(inputMWh + self.inOutEfficiency * dischargeLevels * self.oneLevelMWh, self.maxOutputPowerMW * self.timePeriodHours)

			# if destinationLevel > self.storageLevels:

			# 	print str(destinationLevel)+" YOU JUST BROKE SCIENCE BRO! Storage Level: "+str(storageLevel)+" Start: "+str(startLevel)+" End: "+str(endLevel)
			storageLevels.append((destinationLevel, outputMWh, costOfMovement))

		return storageLevels

def getBatterySpecsList():
	specs = np.loadtxt("model/plant/batterySpecs_new.txt" ,dtype='string', delimiter = ",",skiprows=1, usecols=None, unpack=False)
	modifiedSpecs = []
	# , Cost 2012 USD p kWh , Cost 2014 AUD p kWh 
	for i in np.arange(specs.shape[0]):
		batteryType = str(specs[i][0]).strip(' "\'\t\r\n')
		epRatio = float(1)
		selfDischargePerDay = float(str(specs[i][1]).strip(' "\'\t\r\n'))/100.0
		cycleEfficiency = float(str(specs[i][2]).strip(' "\'\t\r\n'))/100.0
		maxCycles = float(str(specs[i][3]).strip(' "\'\t\r\n'))
		maxDOD = float(str(specs[i][4]).strip(' "\'\t\r\n'))/100.0
		costPerKWh = float(str(specs[i][5]).strip(' "\'\t\r\n'))
		spec = [batteryType,  selfDischargePerDay, cycleEfficiency, maxCycles, maxDOD, costPerKWh]
		modifiedSpecs.append(spec)
	return modifiedSpecs

def getBatterySpecs(batteryType):
	specs = getBatterySpecsList()
	for i in range(len(specs)):
		if specs[i][0] == batteryType:
			return specs[i]
	print "Error: Battery Not Found!"





