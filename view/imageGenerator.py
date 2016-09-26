#Luke Marshall, Wed 28 August 2013

import Image

import numpy as np

from kivy.properties import ObjectProperty
from kivy.uix.image import Image as KivyImage
from kivy.core.image.img_pygame import ImageLoaderPygame

import StringIO



#Takes in a solar data file as a commandline argument, writes it to a heatmapped image.

def getColor(percent, rgbTable):
	colors = rgbTable
	if(np.isnan(percent)):
		color = (int(255),int(255),int(255))
	else:
		percent = min(percent, 100)
		color =  (int(colors[int(percent)][0]),int(colors[int(percent)][1]),int(colors[int(percent)][2]))
		
	# print color
	return color


def colorPixel(value,x,y,im, rgbTable):
	if value != -999:
		position = (int(x),int(y))
		percent = value / 10
		color = getColor(percent, rgbTable)
		im.putpixel(position,color)



def generateHeatmap(data, controller):
	if data is not None:
		rgbTable = np.loadtxt("heatmap",dtype='float', delimiter=",")

		numrows =  data.shape[0]
		numcols =  data.shape[1]

		im = Image.new("RGB",(numcols,numrows),"white")

		print "Progress:"

		for y in np.arange(numrows):
			percent = np.multiply(np.divide(np.float(y), np.float(numrows)),0.25)
			controller.updateSolarHeatmapProgress(percent + 0.75)
			for x in np.arange(numcols):
				colorPixel(data[y][x], x , y, im,rgbTable)

		output = StringIO.StringIO()
		im.show()
		im.save(output, format='PNG')
		contents = output.getvalue()
		output.close()
		memImage = MemoryImage(memory_data=contents, allow_stretch = True, keep_ratio = False)
		# im.show()
		return memImage
	else:
		print "Data is None noooo!@"
		return Image(source='resources/images/mapError.png',allow_stretch = True, keep_ratio = False)	

class MemoryImage(KivyImage):
	memory_data = ObjectProperty(None)
	def __init__(self, memory_data, **kwargs):
		super(MemoryImage, self).__init__(**kwargs)
		self.memory_data = memory_data

	def on_memory_data(self, *args):
		data = StringIO.StringIO(self.memory_data)
		with self.canvas:
			self.texture = ImageLoaderPygame(data).texture


