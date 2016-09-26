import numpy as np

#Data is a 1D array of prices.

def readFromNEMFile(path):
	x = 1


#Runs the put pricer
def putPrice0To100(prices):
	print "exercisePrice, optionPrice"
	for i in np.arange(100):
		optionPrice = putPricer(prices, i)
		print str(i)+", "+str(optionPrice)

#Prices a put option by determining the loss to the seller based on historical data.
def putPricer(plantOutput1MW, prices, exercisePrice):
	loss = 0
	for i in np.arange(prices.shape[i]):
		if prices[i] < exercisePrice and plantOutput[i] > 0:
			loss = loss + (exercisePrice - prices[i])
	return loss

def averagePrice(prices):
	total = 0
	for i in np.arange(prices.shape[0]):
		total = total + prices[i]

	average = np.divide(total, prices.shape[0])
	return average




