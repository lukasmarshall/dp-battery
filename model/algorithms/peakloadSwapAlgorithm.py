from model.algorithms.algorithm import Algorithm
import numpy as np

class PeakloadSwapAlgorithm(Algorithm):
	def __init__(self, strikePrice, fractionContracted, numStates, batteryType="PB-A", capped = False, shaved = False):
		self.strikePrice = strikePrice
		self.fractionContracted = fractionContracted

		
		# super(Algorithm, self).__init__(numStates, batteryType)
		Algorithm.__init__(self,numStates, batteryType, capped, shaved)

	def valueFunction(self, outputMWh, priceDollarsPerMWh, dateAndTime):
		payout = 0
		timePeriodHrs = 0.5
		if dateAndTime.hour >= 7 and dateAndTime.hour < 22 and dateAndTime.weekday() < 5:
			if priceDollarsPerMWh > self.strikePrice:
				payout = -1 * (priceDollarsPerMWh - self.strikePrice)  * self.fractionContracted * timePeriodHrs
			else:
				payout =  (self.strikePrice - priceDollarsPerMWh)  * self.fractionContracted * timePeriodHrs
		marketRevenue = (outputMWh * priceDollarsPerMWh)
		value = marketRevenue + payout
		return value