from kivy.app import App

from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.textinput import TextInput
from kivy.clock import Clock
from kivy.uix.image import Image
from kivy.uix.progressbar import ProgressBar
from kivy.uix.checkbox import CheckBox

import re

import view.plotGenerator as plotGenerator
import view.imageGenerator as imageGenerator
import datetime 
from view.flexidatetimepicker import FlexiDatetimePicker
from view.dialog import SaveDialog
from view.mapPin import MapPin


#pretty

class View(App):
	WINDOW_WIDTH = 800
	WINDOW_HEIGHT = 600
	def __init__(self, controller, **kwargs):
		self.controller = controller
		
		super(View, self).__init__(**kwargs)

	def build(self):
		self.startPicker = None
		self.endPicker = None
		self.cosine = False
		print "Building Main Window"
		layout = BoxLayout(orientation='vertical')
		topBarLayout = BoxLayout(orientation='horizontal')
		#we have a separate graph container that we can clear and then reload the graph image into as it updates.
		#otherwise caches cause some issues and the graph doesnt update properly.
		self.graphContainer = BoxLayout()

		mapWidget = self._generateMap()
		topBarLayout.add_widget(mapWidget)

		self.graph = plotGenerator.linePlot(self.controller.getSimpleTimeseriesData(-36,145, self.controller.getSolarStartDatetime(), self.controller.getSolarStartDatetime()), cumulative=False)
		self.graphContainer.add_widget(self.graph)
		topBarLayout.add_widget(self.graphContainer)

		layout.add_widget(topBarLayout)

		self.label = Label(text="Use the pin above to select a latitude and longitude.")
		self.progressBar= ProgressBar(max=1)

		bottomLeftBox = BoxLayout(orientation='vertical')
		bottomLeftBox.add_widget(self.label)
		# bottomLeftBox.add_widget(self.progressBar)
		bottomLeftBox.add_widget(self._generateExportButton())
		bottomLeftBox.add_widget(self._generateHeatmapButton())
		bottomLeftBox.add_widget(self._generateRunSimulationButton())


		self.bottomBarLayout = BoxLayout()
		self.bottomBarLayout.add_widget(bottomLeftBox)
		

		self.bottomBarLayout.add_widget(self._generateDatetimePicker())
		
		layout.add_widget(self.bottomBarLayout)

		return layout

	def updateProgressBar(self, progress):
		if self.progressBar is not None:
			self.progressBar.value = progress
		if self.heatmapPopupDescription is not None:
			self.heatmapPopupDescription.text = "Generating Heatmap ("+str(round(progress * 1000)/10.0) + " %)"

	def _generateDatetimePicker(self):
		layout = BoxLayout(orientation='vertical')
		startDatetime = self.controller.getSolarStartDatetime()
		endDatetime = startDatetime + datetime.timedelta(days=7)

		#create new datetime objects because we need timezone-naive versions for the datetimepicker class. 
		startDatetime = datetime.datetime(year=startDatetime.year, month=startDatetime.month, day=startDatetime.day, hour=startDatetime.hour, minute=startDatetime.minute, tzinfo=None)
		endDatetime = datetime.datetime(year=endDatetime.year, month = endDatetime.month, day = endDatetime.day, hour = endDatetime.hour, minute=endDatetime.minute, tzinfo = None)

		# print str(startDatetime)
		# print str(endDatetime)

		self.startPicker = FlexiDatetimePicker(density=3, initialDatetime= startDatetime)
		self.endPicker = FlexiDatetimePicker(density = 3, initialDatetime = endDatetime)
		# print str(self.startPicker.selected_datetime)
		# print str(self.endPicker.selected_datetime)

		startLabel = Label(text="Choose Start Date")
		endLabel = Label(text="Choose End Date")

		layout.add_widget(startLabel)
		layout.add_widget(self.startPicker)
		layout.add_widget(endLabel)
		layout.add_widget(self.endPicker)
		return layout

	def displayErrorMessage(self,message="default"):	
		print "Building Popup"
		button = Button(text="Close")
		label = Label(text=message)
		layout= BoxLayout(orientation='vertical')
		layout.add_widget(label)
		layout.add_widget(button)

		popup = Popup(title="Error",content=layout,size_hint=(None, None), size=(400, 400))
		button.bind(on_press=lambda widget:popup.dismiss())
		popup.open()
		print "Popup Opened."

	def _on_checkbox_active(self,checkbox, value):
	    if value:
	        self.cosine = True
	    else:
	        self.cosine = False

	def _displayHeatmapGenerationPopup(self, press):
		print "Building Heatmap Generation Box"
		self.heatmapPopupDescription = Label(text = "Generating Heatmaps can take a long time. \nAre you sure you want to do this?")
		self.heatmapButton = Button(text="Generate")
		self.heatmapButton.bind(on_press=self._generateHeatmap)
		checkbox = CheckBox()
		checkbox.bind(active=self._on_checkbox_active)
		cancelButton = Button(text="Cancel")
		layout = BoxLayout(orientation='vertical')
		layout.add_widget(self.heatmapPopupDescription)
		layout.add_widget(self.heatmapButton)
		layout.add_widget(checkbox)
		layout.add_widget(cancelButton)
		layout.add_widget(self.progressBar)
		popup = Popup(title="Heatmap", content = layout, size_hint=(None, None), size = (400,400))
		cancelButton.bind(on_press = lambda widget:self._cancelHeatmapGeneration(popup))
		popup.open()
		self.heatmapPopup = popup
		print "Heatmap Generation Box Generated"

	def _generateHeatmap(self, touch):
		startDate = self.startPicker.getSelectedDatetime()
		endDate = self.endPicker.getSelectedDatetime()
		self.controller.beginGeneratingHeatmapData(startDate, endDate, cosine = self.cosine)
		if self.heatmapButton is not None and self.heatmapPopup is not None and self.heatmapPopupDescription is not None:
			self.heatmapPopup.content.remove_widget(self.heatmapButton)
			self.heatmapButton = None
			self.heatmapPopupDescription.text = "Generating Heatmap..."


	

	
	def _cancelHeatmapGeneration(self, popup):
		popup.dismiss()
		popup.clear_widgets()
		self.progressBar.parent = None
		self.progressBar.value = 0
		self.heatmapPopup = None
		self.heatmapButton = None
		self.heatmapPopupDescription = None
		self.controller.cancelHeatmapGeneration()

	def _generateMap(self):
		
		layout = RelativeLayout()
		self.mapImg=Image(source='resources/images/map.png',allow_stretch = True, keep_ratio = False)	
		self.mapPin = MapPin( parent=self.mapImg,view = self,allow_stretch = False, source='resources/images/pin.png', size=(20,34))
		self.mapImg.add_widget(self.mapPin)

		layout.add_widget(self.mapImg)

		print "Scheduling."
		Clock.schedule_interval(self._updateMapImg, 2)

		return layout

	def _imageLoaded(self, proxyImage):
		if proxyImage.image.texture:
			self.mapImg.texture = proxyImage.image.texture

	def _updateMapImg(self, timeInterval):
		data = self.controller.getAverageHeatmapData()

		if data is not None and not self.controller.heatmapIsCancelled():
			image = imageGenerator.generateHeatmap(data, self.controller)
			print "Image generated!"
			if self.heatmapPopup is not None:
				print "Popup closing!"
				self.heatmapPopup.clear_widgets()
				self.heatmapPopup.dismiss
				self.heatmapPopup = None
				self.progressBar.parent = None
				self.progressBar.value = 0
			self.mapImg.texture = image.texture
			
		# else:
		# 	print "Still waiting on data. "+str(timeInterval)		

	def _generateExportButton(self):
		exportButton = Button(text='Export as CSV')
		exportButton.bind(on_press = self._getSavePath)
		return exportButton

	def _generateRunSimulationButton(self):
		simButton = Button(text="Run Simulation")
		simButton.bind(on_press=self._chooseSimulation)
		return simButton
	
	def _chooseSimulation(self, press):
		info = Label(text="Please select a simulation from the following options.")
		solarMarketButton = Button(text="Solar w/ Market Prices")
		solarPPAButton = Button(text="Solar w/ PPA")
		solarPPAButton.bind(on_press=self._solarPPASimOptions)
		solarPortfolioButton = Button(text="Solar with Contract Portfolio")
		batteryMarketButton = Button(text="Batteries with Market Trading Only")
		batteryPortfolioButton = Button(text="Batteries with Contract Portfolio")


		layout = BoxLayout(orientation="vertical")
		layout.add_widget(info)
		layout.add_widget(solarMarketButton)
		layout.add_widget(solarPPAButton)
		layout.add_widget(solarPortfolioButton)
		layout.add_widget(batteryMarketButton)
		layout.add_widget(batteryPortfolioButton)


		self.simulationPopup = Popup(title="Run Simulation", content=layout, size_hint=(0.9, 0.9))
		self.simulationPopup.open()

	def _solarPPASimOptions(self, press):
		if self.simulationPopup is not None:
			self.simulationPopup.title = "Solar Plant with PPA Simulation"
			contents = self.simulationPopup.content
			contents.clear_widgets()

			location = Label(text="Location = Lat: "+str(round(self.getSelectedLatitude() * 1000)/1000.0)+"  Lon: "+str(round(self.getSelectedLongitude() * 1000)/1000.0))
			contents.add_widget(location)

			startDate = Label(text="Start Date: "+str(self.startPicker.getSelectedDatetime()))
			contents.add_widget(startDate)

			endDate = Label(text="End Date: "+str(self.endPicker.getSelectedDatetime()))
			contents.add_widget(endDate)

			sizeMWLabel=Label(text="Enter Plant Nameplate Capacity (MW):")
			contents.add_widget(sizeMWLabel)
			
			self.sizeMWInput = TextInput(text='1', multiline=False)
			contents.add_widget(self.sizeMWInput)

			runSimButton = Button(text="Run Simulation")
			runSimButton.bind(on_press=self._runSolarPPASim)
			contents.add_widget(runSimButton)

	def _runSolarPPASim(self, press):
		if self.sizeMWInput is not None:
			namePlateMW = float(self.sizeMWInput.text)
			startDate = self.startPicker.getSelectedDatetime()
			endDate = self.endPicker.getSelectedDatetime()
			lat = self.getSelectedLatitude()
			lon = self.getSelectedLongitude()
			state = "nsw"
			data = self.controller.runSolarPPASimulation(state, startDate, endDate, lat, lon, namePlateMW)
			self._displaySolarSimulationResults(data)

	def _displaySolarSimulationResults(self, data):
		self.simulationPopup.title = "Results"
		graph = plotGenerator.linePlot(data, cumulative=False)
		self.simulationPopup.content.clear_widgets()
		self.simulationPopup.content.add_widget(graph)



	def _generateHeatmapButton(self):
		heatmapButton = Button(text="Generate Heatmap")
		heatmapButton.bind(on_press=self._displayHeatmapGenerationPopup)
		return heatmapButton



	def getDatabasePath(self):
		# return "/Volumes/SOLAR/data.hdf5"
		return "./test.hdf5"

	def getFolderPath(self):
		return "./testFiles"

	def displayImage(image):
		image.show()

	def changeXY(self,x,y):
		labelText = "Current Location - Lat : "+str(round(1000*x)/1000.0) + "  Long:" + str(round(1000*y)/1000.0)
		self.label.text = labelText

	def updateGraphXY(self, lat, lon):
		print "updating graph"
		# Cache.remove('kv.image')
		# Cache.remove('kv.texture')
		startDate = self.startPicker.getSelectedDatetime()
		endDate = self.endPicker.getSelectedDatetime()

		self.graph = plotGenerator.linePlot(self.controller.getSimpleTimeseriesData(lat,lon, startDate, endDate), cumulative=False)
		self.graphContainer.clear_widgets()

		self.graphContainer.add_widget(self.graph)

		# self.graph.reload()


	def _getSavePath(self, touch):

		saveDialog = SaveDialog(save=self._save, cancel=self._dismissPopup)
		self._popup = Popup(title="Save file", content=saveDialog, size_hint=(0.9, 0.9))
		self._popup.open()


	def _dismissPopup(self):
		try:
			self._popup.dismiss()
		except AttributeError:
			print "No popup to close!"

	def _save(self, path, fileName):
		pattern = ".*\/.*"
		# regex = re.compile(pattern)
		if re.match(pattern, fileName): #If we find the filename is a directory, do nothing.
			path = fileName
		else: #otherwise join path and filename.
			path = path + "/"+ fileName
		self.controller.exportTimeseries(path)
		try:
			self._popup.dismiss()
		except AttributeError:
			print "No popup to close"

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


  		












