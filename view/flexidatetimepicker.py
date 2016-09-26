from kivy.garden.datetimepicker import DatetimePicker
from calendar import monthrange
from kivy.clock import Clock
from kivy.factory import Factory
from kivy.garden.roulette import TimeFormatCyclicRoulette, Roulette, CyclicRoulette
from kivy.metrics import dp
from utils.timezone import Timezone

from datetime import datetime


Symbol = Factory.Symbol
Dash = Factory.Dash
Colon = Factory.Colon

class FlexiDatetimePicker(DatetimePicker):
	def __init__(self, initialDatetime, **kw):
		self.initialDatetime = initialDatetime
		super(FlexiDatetimePicker, self).__init__(**kw)

	def init_roulettes(self):
		self._calibrate_month_size_trigger = t = \
					Clock.create_trigger(self.calibrate_month_size)
		self._adjust_day_cycle_trigger = \
					Clock.create_trigger(self._adjust_day_cycle, -1)
		kw = {'density': self.density}
		self.second = second = TimeFormatCyclicRoulette(cycle=60, **kw)
		second.select_and_center(self.initialDatetime.second)
		self.minute = minute = TimeFormatCyclicRoulette(cycle=60, **kw)
		minute.select_and_center(self.initialDatetime.minute)
		self.hour = hour = TimeFormatCyclicRoulette(cycle=24, **kw)
		hour.select_and_center(self.initialDatetime.hour)
		self.year = year = Roulette(**kw)
		year.select_and_center(self.initialDatetime.year)
		self.month = month = CyclicRoulette(cycle=12, zero_indexed=False, **kw)
		month.select_and_center(self.initialDatetime.month)

		month_size = monthrange(self.initialDatetime.year, self.initialDatetime.month)[1]
		self.day = day = CyclicRoulette(cycle=month_size, zero_indexed=False,
										on_centered=self._adjust_day_cycle_trigger,
										**kw)
		day.select_and_center(self.initialDatetime.day)

		self.month.bind(selected_value=t)
		self.year.bind(selected_value=t)

		self.set_selected_datetime()
		self._bind_updates()

		children = [
					year, Dash(), month, Dash(), day, Symbol(),
					hour, Colon(), minute, Colon(), second,
					]
		add = self.add_widget
		width = dp(20)
		for c in children:
			add(c)
			width += c.width
		self.width = width

	def getSelectedDatetime(self):
		#use this instead of the selected_datetime attribute because it returns OFFSET--aware datetimes which will work with the database. 
		date = self.selected_datetime
		newDate = datetime(year = date.year, month = date.month, day= date.day, hour = date.hour, minute = date.minute, tzinfo = Timezone())
		return newDate


