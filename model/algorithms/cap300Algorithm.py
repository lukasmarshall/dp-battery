from model.algorithms.algorithm import Algorithm
import numpy as np

class Cap300Algorithm(Algorithm):
	def __init__(self, strikePrice, fractionContracted, numStates, batteryType="PB-A", capped = False, shaved = False, capValuePerMWh = 11.3):
		self.strikePrice = 300
		self.fractionContracted = fractionContracted
		self.capValuePerMWh = capValuePerMWh
		
		# super(Algorithm, self).__init__(numStates, batteryType)
		Algorithm.__init__(self,numStates, batteryType, capped, shaved)

	def valueFunction(self, outputMWh, priceDollarsPerMWh, dateAndTime):
		payout = 0
		timePeriodHrs = 0.5
		if priceDollarsPerMWh > self.strikePrice:
			payout = -1 * 300  * self.fractionContracted * timePeriodHrs
		
		revenueFromCapSale = self.capValuePerMWh * self.fractionContracted * timePeriodHrs
		marketRevenue = np.multiply(outputMWh, priceDollarsPerMWh)
		value = marketRevenue + payout + revenueFromCapSale
		return value