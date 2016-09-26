import sys
import os
sys.path.insert(0, '/Library/Python/2.7/site-packages')
sys.path.insert(0, '/usr/local/lib') 
sys.path.insert(0, os.path.expanduser('~/lib'))
sys.path.insert(0, '/Library/Python/2.7/site-packages')
sys.path.insert(0, os.path.expanduser('/Library/Python/2.7/site-packages'))

# from controller import Controller
from datetime import datetime
from utils.timezone import Timezone
from utils.timezone import SydneyTimezone
from utils import timeUtils
from scripts import timeseries
from scripts import merchantModel
from scripts import cap300
from scripts import shapedCap
from scripts import baseloadFuture
from scripts import baseloadPeakFuture
from scripts import algorithmRunner
from scripts import determineStorageLevels
from scripts import lcoe
from scripts import baseloadSwapAlgorithmRunner
from scripts import peakloadSwapAlgorithmRunner
from scripts import cap300AlgorithmRunner
from scripts import merchantModelCapped
from scripts import priceAndSolarDailyTrends
from scripts import capacityFactor
from scripts import priceFrequency
from scripts import timeDistributionHighPrices
from scripts import cumulativeShapedPriceFrequency
from scripts import cumulativeShapedPriceFrequencyHighDemand
from scripts import minimumShapedCapValue
from scripts import maximumShapedCapValue
from scripts import capacityFactorShaped
from scripts import probabilityOfShapedDispatch
from scripts import shapedCapPricer
from scripts import shapedCapRevenue
from scripts import batteryTester
import model.environment.cosine as cosine
from model.environment import locations
from controller import Controller
import numpy as np
import cProfile
from scripts import solarMarketFactor
from scripts import solarMarketFactorCapped



# c = Controller(gui = False)
# lcoe.printTimeseries(tracking=False)
# lcoe.printTimeseries(tracking=True)
# merchantModel.printTimeseries(tracking = False)
# merchantModel.printTimeseries(tracking = True)
# merchantModelCapped.printTimeseries(tracking = False)
# merchantModelCapped.printTimeseries(tracking = True)

# capacityFactor.printTimeseries(tracking = True)
# capacityFactor.printTimeseries(tracking = False)
# solarMarketFactor.printTimeseries(tracking = True)
# solarMarketFactor.printTimeseries(tracking = False)
# solarMarketFactorCapped.printTimeseries(tracking = True)
# solarMarketFactorCapped.printTimeseries(tracking = False)
# priceFrequency.printTimeseries()
# priceAndSolarDailyTrends.printTimeseries()
# timeDistributionHighPrices.printTimeseries()
# cumulativeShapedPriceFrequency.printTimeseries()
# cumulativeShapedPriceFrequencyHighDemand.printTimeseries()
# maximumShapedCapValue.printTimeseries()
# minimumShapedCapValue.printTimeseries()
# capacityFactorShaped.printTimeseries(tracking = True)
# capacityFactorShaped.printTimeseries(tracking = False)

# probabilityOfShapedDispatch.printTimeseries()
# shapedCapPricer.printTimeseries()
# shapedCapRevenue.printTimeseries()



# shapedCap.printTimeseries(tracking=False, fractionContracted = 0.25)
# shapedCap.printTimeseries(tracking=True, fractionContracted = 0.25)
# baseloadFuture.printTimeseries(tracking = True, fractionContracted = 0.25)
# baseloadFuture.printTimeseries(tracking = False, fractionContracted = 0.25)

# baseloadPeakFuture.printTimeseries(tracking=True, fractionContracted = 0.25)
# baseloadPeakFuture.printTimeseries(tracking=False, fractionContracted = 0.25)
# baseloadPeakFuture.printTimeseries(tracking=True, fractionContracted = 0.2)
# baseloadPeakFuture.printTimeseries(tracking=False, fractionContracted = 0.2)
# baseloadPeakFuture.printTimeseries(tracking=True, fractionContracted = 0.15)
# baseloadPeakFuture.printTimeseries(tracking=False, fractionContracted = 0.15)
# baseloadPeakFuture.printTimeseries(tracking=True, fractionContracted = 0.1)
# baseloadPeakFuture.printTimeseries(tracking=False, fractionContracted = 0.1)
# baseloadPeakFuture.printTimeseries(tracking=True, fractionContracted = 0)
# baseloadPeakFuture.printTimeseries(tracking=False, fractionContracted = 0)

# cap300.printTimeseries(tracking=False, fractionContracted = 0.25)
# cap300.printTimeseries(tracking=True, fractionContracted = 0.25)
# cap300.printTimeseries(tracking=False, fractionContracted = 0.2)
# cap300.printTimeseries(tracking=True, fractionContracted = 0.2)
# cap300.printTimeseries(tracking=False, fractionContracted = 0.15)
# cap300.printTimeseries(tracking=True, fractionContracted = 0.15)
# cap300.printTimeseries(tracking=False, fractionContracted = 0.1)
# cap300.printTimeseries(tracking=True, fractionContracted = 0.1)


# algorithmRunner.printTimeseries(tracking=False, storageMWh = 1)
# algorithmRunner.printTimeseries(tracking=True, storageMWh = 1)

# algorithmRunner.printTimeseries(tracking = False, storageMWh = 4, capped = True)
# algorithmRunner.printTimeseries(tracking=True, storageMWh = 4, capped = True)


# baseloadSwapAlgorithmRunner.printTimeseries(tracking=True, storageMWh = 1, fractionContracted = 0.15)
# baseloadSwapAlgorithmRunner.printTimeseries(tracking=False, storageMWh = 1, fractionContracted = 0.125)
# peakloadSwapAlgorithmRunner.printTimeseries(tracking=True, storageMWh = 1, fractionContracted = 0.15)
# peakloadSwapAlgorithmRunner.printTimeseries(tracking=False, storageMWh = 1, fractionContracted = 0.125)
# cap300AlgorithmRunner.printTimeseries(tracking=True, storageMWh = 1, fractionContracted = 0.15)
# cap300AlgorithmRunner.printTimeseries(tracking=False, storageMWh = 1, fractionContracted = 0.125)


# baseloadSwapAlgorithmRunner.printTimeseries(tracking=True, storageMWh = 2, fractionContracted = 0.15)
# baseloadSwapAlgorithmRunner.printTimeseries(tracking=False, storageMWh = 2, fractionContracted = 0.125)
# peakloadSwapAlgorithmRunner.printTimeseries(tracking=True, storageMWh = 2, fractionContracted = 0.28)
# peakloadSwapAlgorithmRunner.printTimeseries(tracking=False, storageMWh = 2, fractionContracted = 0.2)
# cap300AlgorithmRunner.printTimeseries(tracking=True, storageMWh = 2, fractionContracted = 0.15)
# cap300AlgorithmRunner.printTimeseries(tracking=False, storageMWh = 2, fractionContracted = 0.125)


# baseloadSwapAlgorithmRunner.printTimeseries(tracking=True, storageMWh = 3, fractionContracted = 0.15)
# baseloadSwapAlgorithmRunner.printTimeseries(tracking=False, storageMWh = 3, fractionContracted = 0.125)
# peakloadSwapAlgorithmRunner.printTimeseries(tracking=True, storageMWh = 3, fractionContracted = 0.15)
# peakloadSwapAlgorithmRunner.printTimeseries(tracking=False, storageMWh = 3, fractionContracted = 0.125)
# cap300AlgorithmRunner.printTimeseries(tracking=True, storageMWh = 3, fractionContracted = 0.15)
# cap300AlgorithmRunner.printTimeseries(tracking=False, storageMWh = 3, fractionContracted = 0.125)

# baseloadSwapAlgorithmRunner.printTimeseries(tracking=True, storageMWh = 4, fractionContracted = 0.15)
# baseloadSwapAlgorithmRunner.printTimeseries(tracking=False, storageMWh = 4, fractionContracted = 0.125)
# peakloadSwapAlgorithmRunner.printTimeseries(tracking=True, storageMWh = 4, fractionContracted = 0.15)
# peakloadSwapAlgorithmRunner.printTimeseries(tracking=False, storageMWh = 4, fractionContracted = 0.125)
# cap300AlgorithmRunner.printTimeseries(tracking=True, storageMWh = 4, fractionContracted = 0.15)
# cap300AlgorithmRunner.printTimeseries(tracking=False, storageMWh = 4, fractionContracted = 0.125)


# Shaved Simulations.
# algorithmRunner.printTimeseries(tracking = False, storageMWh = 2, shaved = True, capped=True)
# algorithmRunner.printTimeseries(tracking=True, storageMWh = 2, shaved = True, capped=True)
# algorithmRunner.printTimeseries(tracking = False, storageMWh = 3, shaved = True, capped=True)
# algorithmRunner.printTimeseries(tracking=True, storageMWh = 3, shaved = True, capped=True)


# baseloadSwapAlgorithmRunner.printTimeseries(tracking=True, storageMWh = 2, fractionContracted = 0.15, shaved = True)
# baseloadSwapAlgorithmRunner.printTimeseries(tracking=False, storageMWh = 2, fractionContracted = 0.125, shaved = True)
# peakloadSwapAlgorithmRunner.printTimeseries(tracking=True, storageMWh = 2, fractionContracted = 0.28, shaved = True)
# peakloadSwapAlgorithmRunner.printTimeseries(tracking=False, storageMWh = 2, fractionContracted = 0.2, shaved = True)
# cap300AlgorithmRunner.printTimeseries(tracking=True, storageMWh = 2, fractionContracted = 0.15, shaved = True)
# cap300AlgorithmRunner.printTimeseries(tracking=False, storageMWh = 2, fractionContracted = 0.125, shaved = True)


# baseloadSwapAlgorithmRunner.printTimeseries(tracking=True, storageMWh = 3, fractionContracted = 0.15, shaved = True)
# baseloadSwapAlgorithmRunner.printTimeseries(tracking=False, storageMWh = 3, fractionContracted = 0.125, shaved = True)
# peakloadSwapAlgorithmRunner.printTimeseries(tracking=True, storageMWh = 3, fractionContracted = 0.28, shaved = True)
# peakloadSwapAlgorithmRunner.printTimeseries(tracking=False, storageMWh = 3, fractionContracted = 0.2, shaved = True)
# cap300AlgorithmRunner.printTimeseries(tracking=True, storageMWh = 3, fractionContracted = 0.15, shaved = True)
cap300AlgorithmRunner.printTimeseries(tracking=False, storageMWh = 3, fractionContracted = 0.125, shaved = True)

# baseloadSwapAlgorithmRunner.printTimeseries(tracking=True, storageMWh = 4, fractionContracted = 0.15, shaved = True)
# baseloadSwapAlgorithmRunner.printTimeseries(tracking=False, storageMWh = 4, fractionContracted = 0.125, shaved = True)
# peakloadSwapAlgorithmRunner.printTimeseries(tracking=True, storageMWh = 4, fractionContracted = 0.28, shaved = True)
# peakloadSwapAlgorithmRunner.printTimeseries(tracking=False, storageMWh = 4, fractionContracted = 0.2, shaved = True)
# cap300AlgorithmRunner.printTimeseries(tracking=True, storageMWh = 4, fractionContracted = 0.15, shaved = True)
# cap300AlgorithmRunner.printTimeseries(tracking=False, storageMWh = 4, fractionContracted = 0.125, shaved = True)








# batteryTester.runTest()


# cProfile.run('peakloadSwapAlgorithmRunner.printTimeseries(tracking=False, storageMWh = 1, fractionContracted = 0.25)')




