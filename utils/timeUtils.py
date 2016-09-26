

def checkDatesSame(date1, date2):
	difference = date1 - date2
	if difference.days == 0 and difference.seconds < 60:
		return True
	else:
		return False
