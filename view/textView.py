

#pretty

class View():

	def __init__(self, controller, **kwargs):
		self.controller = controller
		


	def build(self):
		print "Initialising"

	def updateProgressBar(self, progress):
		print "Progress: "+progress+"%"

	def displayErrorMessage(self,message="default"):	
		print "================================"
		print "=============ERROR=============="
		print message
		print "================================"

	def getDatabasePath(self):
		# return "/Volumes/SOLAR/data.hdf5"
		return "./test.hdf5"

	def getFolderPath(self):
		return "./testFiles"

	def displayImage(image):
		image.show()

	def _dismissPopup(self):
		try:
			self._popup.dismiss()
		except AttributeError:
			print "No popup to close!"

	def getSelectedStartDate(self):
		if self.startPicker:
			return self.startPicker.getSelectedDatetime()
		else:
			return self.controller.getSolarStartDatetime()

	def getSelectedEndDate(self):
		if self.endPicker:
			return self.endPicker.getSelectedDatetime()
		else:
			return self.controller.getSolarEndDatetime()

	def getSelectedLatitude(self):
		return self.mapPin.getLatLong()[0]

	def getSelectedLongitude(self):
		return self.mapPin.getLatLong()[1]


  		












