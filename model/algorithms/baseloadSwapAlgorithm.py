from model.algorithms.algorithm import Algorithm
import numpy as np

class BaseloadSwapAlgorithm(Algorithm):
	def __init__(self, strikePrice, fractionContracted, numStates, batteryType="PB-A", capped = False,shaved = False):
		self.strikePrice = strikePrice
		self.fractionContracted = fractionContracted
		

		print "Baseload Swap Algorithm"
		print "Strike Price = "+str(self.strikePrice)
		print "Fraction Contracted = "+str(fractionContracted)
		
		# super(Algorithm, self).__init__(numStates, batteryType)
		Algorithm.__init__(self, numStates, batteryType, capped, shaved)

	def valueFunction(self, outputMWh, priceDollarsPerMWh, dateAndTime):
		timePeriodHrs = 0.5
		if float(priceDollarsPerMWh) > float(self.strikePrice):
			payout = -1 * (priceDollarsPerMWh - self.strikePrice)  * self.fractionContracted * timePeriodHrs
		else:
			payout =  (self.strikePrice - priceDollarsPerMWh)  * self.fractionContracted * timePeriodHrs

		marketRevenue = np.multiply(outputMWh, priceDollarsPerMWh)
		value = marketRevenue + payout

		return value