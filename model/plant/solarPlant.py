import numpy as np

class SolarPlant():
	def __init__(self, namePlateMW):
		self.namePlateMW = namePlateMW
		self.deratingFactor = 0.7752

	# def getPlantOutputOld(self, dni, ghi, timePeriodHrs, cosine):
	# 	psh = np.multiply(np.divide(dni , 1000), timePeriodHrs)
	# 	psh = np.multiply(psh, cosine)
	# 	psh = psh + (0.2 * np.multiply(np.divide(ghi , 1000), timePeriodHrs)) # diffuse
	# 	return max(np.multiply(psh, self.namePlateMW),0)

	def getPlantOutput(self, dni, ghi, timePeriodHrs, cosine):
		psh = np.divide(dni , 1000)
		psh = np.multiply(psh, cosine)
		psh = psh + (0.2 * np.divide(ghi, 1000)) # diffuse
		plantOutput = psh* self.namePlateMW * self.deratingFactor
		plantOutput = max(plantOutput, 0)
		plantOutput = min(plantOutput, 1)
		plantOutputMWh = plantOutput * timePeriodHrs
		return plantOutputMWh
