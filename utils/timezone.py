import datetime

class Timezone(datetime.tzinfo):
		def __init__(self):
			x = 1

		def dst(self, dt):
			return datetime.timedelta(0)

		def utcoffset(self, dt):
			return datetime.timedelta(0)

		def tzname(self, dt):
			return "UTC"

class SydneyTimezone(datetime.tzinfo):
		def __init__(self):
			x = 1

		def dst(self, dt):
			return datetime.timedelta(0)

		def utcoffset(self, dt):
			return datetime.timedelta(hours=10)

		def tzname(self, dt):
			return "UTC"