import numpy as np

from kivy.properties import ObjectProperty
from kivy.uix.image import Image
from kivy.core.image.img_pygame import ImageLoaderPygame

from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

import StringIO
import matplotlib.cm as cm



def linePlot(data=[1,2,3,4], cumulative = False, xLabel = "Hours From Start Time", yLabel = "Insolation (W/m^2)"):
	if not cumulative:
		plt.clf()
	plt.plot(data)
	plt.ylabel(yLabel)
	plt.xlabel(xLabel)
	plt.ylim((0,1200))
	return pyplotToImage(plt)


def cardioid(start, stop, step):
	"""A rotated cardioid."""
	theta = np.arange(start, stop, step)
	r = 1 - np.sin(theta)
	return theta, r


def polar_plot(theta, r, rmax):
	"""Draw a polat plot.

	:returns: matplotlib.Figure
	"""
	fig = Figure(facecolor='white')
	ax = fig.add_subplot(111, polar=True, frameon=False)
	ax.grid(False)
	ax.set_xticklabels([])
	ax.set_yticklabels([])
	ax.plot(theta, r, color='g', linewidth=2)
	ax.set_rmax(rmax)
	return fig

def generateTestGraph():
	theta, r = cardioid(0, 8.0, 0.01)
	image = figureToPng(polar_plot(theta, r, 2.5))
	memImage = MemoryImage(image)
	return memImage

def figureToPng(figure):
		#converts a matplotlib figure to a png in memory
		data = StringIO.StringIO()
		canvas = FigureCanvasAgg(figure)
		canvas.print_png(data)
		# print type(data)
		return data.getvalue()

def pyplotToImage(plot):
	image = figureToPng(plot.figure(1))
	return MemoryImage(image)




def generateHeatmap(data):

	plt.imshow(data, extent=(0, data.shape[1], data.shape[0], 0),
				interpolation='nearest', cmap=cm.gist_yarg)
	plt.figure.frameon=False
	return pyplotToImage(plt)


class MemoryImage(Image):
	memory_data = ObjectProperty(None)
	def __init__(self, memory_data, **kwargs):
		super(MemoryImage, self).__init__(**kwargs)
		self.memory_data = memory_data

	def on_memory_data(self, *args):
		data = StringIO.StringIO(self.memory_data)
		with self.canvas:
			self.texture = ImageLoaderPygame(data).texture


	
	

