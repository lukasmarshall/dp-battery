# import view.limitedKivyView as kivyView
import view.textView as textView
# import view.imageGenerator as imageGenerator
import model.database.databaseManager as databaseManager
import model.database.textDatabaseManager as textDatabaseManager
from utils import fileIO

from threading import Thread
from Queue import Queue

import re


class Controller():
	dbManager = None
	def __init__(self, gui=True, textDatabase=False):

		self.cancelledHeatmap = False
		self.cancelledTimeseries = False
		self.savePath = None
		
		path = "/Volumes/SOLAR/data.hdf5"
		# path = "./test.hdf5"
		if textDatabase:
			self.dbManager = textDatabaseManager.DatabaseManager(self,path)
		else:
			self.dbManager = databaseManager.DatabaseManager(self,path)
		self.queue = Queue()
		self.solarDataThread = None
		# if gui:
		# 	self.view = kivyView.View(self)
		# 	self.view.run()
		# else:
		self.view = textView.View(self)
		

	def getDatabaseManager(self):
		return self.dbManager

	def heatmapIsCancelled(self):
		return self.cancelledHeatmap
		
	def errorMessage(self,message):
		self.view.displayErrorMessage(message)

	def createSolarDataset(self):
		folderPath = self.view.getFolderPath()
		databasePath = self.view.getDatabasePath()
		self.dbManager.createSolarDataset(folderPath, databasePath)

	def displayImage(self,date):
		data = self.dbManager.getDNIMap(date)
		image = imageGenerator.generateHeatmap(data)
		self.view.displayImage(image)
		
	def getTimeseriesNemDNI(self, state, lat, lon, startDate, endDate):
		return self.dbManager.getTimeseriesNemDNI(state, lat, lon, startDate, endDate)
	
	def getSolarDataFolder(self):
		return self.view.getFolderPath()

	def getTimeseriesData(self,lat,lon, startDate, endDate):
		if self.dbManager is not None:
			return self.dbManager.getTimeseriesData(lat,lon, startDate, endDate)
		else:
			return [1,2,3,4]

	def getSimpleTimeseriesData(self, lat, lon, startDate, endDate):
		data = self.getTimeseriesData(lat, lon, startDate, endDate)
		return data[...,5]

	def getSolarStartDatetime(self):
		return self.dbManager.getSolarStartDatetime()
		

	def getSolarEndDatetime(self):
		return self.dbManager.getSolarEndDatetime()

	def getAverageHeatmapData(self):
		data = None
		if self.solarDataThread is not None:
			while not self.queue.empty():
				data = self.queue.get()
			if not self.solarDataThread.isAlive():
				self.solarDataThread = None
		return data

	def checkDatesValid(self, startDate, endDate):
		return self.dbManager.checkDatesValid(startDate, endDate)

	def beginGeneratingHeatmapData(self, startDate, endDate, cosine=False):
		print "Beginning Heatmap Generation."
		self.cancelledHeatmap = False
		if cosine:
			self.solarDataThread = Thread(target=self.dbManager.generateAverageCosineHeatmapData, args=(startDate, endDate, self.queue))
		else:
			self.solarDataThread = Thread(target=self.dbManager.generateAverageHeatmapData, args=(startDate, endDate, self.queue))
		self.solarDataThread.start()
		print "Thread Begun!"


	def cancelHeatmapGeneration(self):
		if self.solarDataThread is not None:
			while not self.queue.empty():
				data = self.queue.get()
			if not self.solarDataThread.isAlive():
				self.solarDataThread = None
			else:
				self.cancelledHeatmap = True



	def exportTimeseries(self, savePath, dni = True):
		startDate = self.view.getSelectedStartDate()
		endDate = self.view.getSelectedEndDate()
		lat = self.view.getSelectedLatitude()
		lon = self.view.getSelectedLongitude()

		pattern = ".*\.csv"
		regex = re.compile(pattern)

		if not re.match(pattern, savePath):
			self.savePath = savePath + ".csv"
		else:
			self.savePath = savePath

		self.cancelledTimeseries = False
		self.solarDataThread = Thread(target=self.dbManager.getTimeseriesData, args=(lat, lon, startDate, endDate,self.queue, dni))
		
		self.solarDataThread.start()
		print "Thread Begun!"



	def saveTimeseriesIfDataGenerated(self):
		data = None
		if self.solarDataThread is not None:
			while not self.queue.empty():
				data = self.queue.get()
			if not self.solarDataThread.isAlive():
				self.solarDataThread = None
		if data is not None:
			try:
				print "Attempting csv write"
				fileIO.saveTimeseriesDataAsCSV(data, self.savePath)
			except:
				self.view.displayErrorMessage(message="Error: Invalid Save path:\n"+self.savePath)
		if data is not None:
			return True
		else:
			return False

		
	def getTimeseriesNemDNICos(self, state, lat, lon, startDate, endDate):
		return self.dbManager.getTimeseriesNemDNICos(state, lat, lon, startDate, endDate)

	def getTimeseriesCosData(self, lat, lon, startDate, endDate):
		return self.dbManager.getTimeseriesCosData( lat, lon, startDate, endDate)

	def updateSolarHeatmapProgress(self,percent):
		print "Percent Completed: " + str(percent * 100)+"%"
		self.view.updateProgressBar(percent)
	
	def reportWriteFinished(self):
		self.view.reportWriteFinished()


	def runSolarPPASimulation(self, state, startDate, endDate, lat, lon, namePlateMW):
		print "Simulating "+str(namePlateMW)+" MW Plant"
		return self.dbManager.getGenerationProfile( state, lat, lon, startDate,endDate, namePlateMW)

	