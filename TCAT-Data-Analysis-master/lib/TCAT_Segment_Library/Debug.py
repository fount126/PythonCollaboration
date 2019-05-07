if not 'dFlag' in globals():
	dFlag = False
if not 'sdFlag' in globals():
	sdFlag = False
if not 'checkFlag' in globals():
	checkFlag = False
__location = 'log.txt'
__firstMsg = True
def debug(msg, pause=False, **kwargs):
	if (not 'dFlag' in globals()) or (not dFlag):
		return
	print('[DEBUG]: %s.' % (msg))
	for x in kwargs:
		print('    [%s]=[%s]'%(x,kwargs[x]))
	if pause:
		input()
	write_debug(msg, kwargs)
def dev_debug(msg, pause=False, **kwargs):
	if (not 'sdFlag' in globals()) or (not sdFlag):
		return
	print('[SUPER DEBUG]: %s.' % (msg))
	for x in kwargs:
		print('    [%s]=[%s]'%(x,kwargs[x]))
	if pause:
		input()
	write_debug(msg, kwargs)

def write_debug(msg, kwargs, loc=None):
	global __location
	global __firstMsg
	if loc==None:
		loc=__location
	f = open(loc, 'a')
	if __firstMsg:
		f.write('\n_____________________________________________________________________________________________________\n')
		__firstMsg=False
	f.write(str(msg)+'\n')
	for x in kwargs:
		f.write(('    [%s]=[%s]'%(x,kwargs[x]))+'\n')
	f.close()
def review(actualDay, scheduledDay):
	if (not 'dFlag' in globals()) or (not dFlag):
		return
	userin = input('Type the trip number of the trip you would like to review, or type "quit".\nYou could stop at any point by inputting "QUIT".')
	def getTrip(actualDay, tripNumber):
		for b in actualDay.blocks:
			for t in actualDay.trips:
				if t.tripNumber==tripNumber:
					return t
		return None
	while userin != 'quit':
		if userin.trim().isdigit():
			tripNumber = int(userin)
			t = getTrip(actualDay, tripNumber)
			if t:
				print(str("[%s]" % (", ".join(map(lambda x: x.segmentID[1].pp_boards_alights(), t.segments)))))
			else:
				print("Trip not found.")

		userin = input('Type a tripNumber or "quit"')


def check(actualDay, scheduledDay):
	debug('Starting post-process analysis')

	debug('Finished post-process analysis')
