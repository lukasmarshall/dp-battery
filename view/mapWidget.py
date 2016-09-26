from kivy.uix.widget import Widget
import imageGenerator

class MapWidget(Widget):

	def __init__(self, controller, **kwargs):
		super(MapWidget, self).__init__(**kwargs)
		
		mapImg = FloatLayout()
		heatmap = imageGenerator.generateHeatmap(data)
		
		pin = MapPin( parent=mapImg,view = self,allow_stretch = False, source='resources/images/pin.png', size=(20,34))
		
		self..add_widget(pin)

		self.add_widget(self.progressBar)
		self.add_widget(mapImg)





class MapPin(Image):
	
	def __init__(self,parent, view, **kwargs):
		# self.source='resources/images/map.png'
		# self.pos = parent.center
		super(MapPin, self).__init__(**kwargs)
		

		self.view = view

	def on_touch_move(self, touch):

		# self.view.changeXY(touch.pos[0], touch.pos[1])
		#if the touch intersected the bounding box of the widget and its parent (the map):
		if self.collide_point(touch.px, touch.py) and self.parent.collide_point(touch.x,touch.y):
			#move the widget to the touch point
			self.y = touch.y
			self.x = touch.x - self.width/2

			xPercent = 100 * ((self.x + (self.width/2)) / self.parent.width)
			yPercent = 100 * (self.y / self.parent.height)
			latLong = self.percentToLatLong(xPercent, yPercent)
			self.view.changeXY(latLong[0], latLong[1])
			self.view.updateGraphXY(latLong[0], latLong[1])

		return super(MapPin, self).on_touch_move(touch)

	def on_touch_up(self, touch):
		if self.parent.collide_point(touch.x, touch.y):
			self.y = touch.y
			self.x = touch.x - self.width / 2
			xPercent = 100 * ((self.x + (self.width/2)) / self.parent.width)
			yPercent = 100 * (self.y / self.parent.height)
			latLong = self.percentToLatLong(xPercent, yPercent)
			self.view.changeXY(latLong[0], latLong[1])
			self.view.updateGraphXY(latLong[0], latLong[1])
			# print type(self.view.startPicker.selected_datetime)



	def percentToLatLong(self, xPercent, yPercent):
		CELL_SIZE = 0.05
		NUM_X_CELLS = 839.0
		NUM_Y_CELLS = 679.0

		xPercent = min(xPercent, 100)
		xPercent = max(xPercent, 0)

		yPercent = min(yPercent, 100)
		yPercent = max(yPercent, 0)
		
		BOTTOM_LAT = - 43.975
		TOP_LAT = BOTTOM_LAT + (NUM_Y_CELLS * CELL_SIZE)

		LEFT_LONG = 112.025
		RIGHT_LONG = LEFT_LONG + (NUM_X_CELLS * CELL_SIZE)

		lon = (xPercent / 100) * (RIGHT_LONG - LEFT_LONG) + LEFT_LONG
		lat = (yPercent / 100) * (TOP_LAT - BOTTOM_LAT) + BOTTOM_LAT
		
		return (lat, lon)



