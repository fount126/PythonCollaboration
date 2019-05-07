#NOTE: Only available in python 3.4 and above!
#Inputs: actualDay- the day object representing the day to report
#Returns: the function is void, it  adds information about a day to a file
#This function is used to create a file called report which gives a high level overview of the the
#information and deviations for each day it is called upon. It works by creating a text file called
#report if one does not exist already, and each time the function is called it adds information about
#how many blocks,trips, and stops were missed, as well as the block number, trip number, and route for
#each trip missed.
from ..TCAT_Segment_Library.Debug import debug
def report(actualDay):
	debug('Reporting...')
	cDay=actualDay.date
	CDAY=str(cDay)
	#f= open('CDAY'+'.txt','w+')
	f= open('report.txt','a+')
	f.write('---------------------------------------------------------------------------------------\n')
	f.write('This is the deviation report for '+CDAY +'\n' )
	f.write('\n')
	#for b in actualDay.deviations.blocksMissed:
	# f.write('There were %d blocks missed\n' %(len(actualDay.deviations.blocksMissed)))
	#for t in actualDay.deviations.tripsMissed:
	# f.write('There were %d trips missed\n' %(len( actualDay.deviations.tripsMissed)))
	# for t in actualDay.deviations.tripsMissed:
		# f.write('Block  %d missed trip %d on route %d \n' %(t.blockNumber,t.trip.tripNumber, t.trip.route))
	# f.write('There were %d scheduled stops missed\n' %(len( actualDay.deviations.scheduledStopsMissed)))
	# f.write('There were %d nonscheduled stops made\n' %(len( actualDay.deviations.nonscheduledStopsMade)))
	# f.write(getSegmentDeviations(actualDay))
	f.write('---------------------------------------------------------------------------------------\n')
	#for b in actualDay.blocks:
	#	f.write('This is block %d\r\n ' % (b.blockNumber))
	#	for t in b.trips:
	#		f.write('This is trip %d \n ' % (t.tripNumber))
	#		for s in t.segments:
		#		f.write('(%d , %d);' % (s.segmentID[0].stopID, s.segmentID[1].stopID))

	#for t in actualDay.deviations.tripsMissed:
	#	f.write('Trip Missed %d \n' %(t))
	f.close()
	debug('Reporting done.')
#Helper function to get deviations stored in segments and return them as a string
def getSegmentDeviations(day):
	segDevs = ''
	for block in day.blocks:
		for trip in block.trips:
			for segment in trip.segments:
				if segment.deviation != [] and segment.deviation != None:
					for dev in segment.deviation:
						segDevs+='There was a %s on trip %d on route %d in block %d\n'%(dev, trip.tripNumber, trip.route, block.blockNumber)
	return segDevs

#Inputs: currentActualDay- the day object representing the day to check
#Returns: the function is void, it checks if the segment sequence numbers are in order
#This function iterate through every block in a day, every trip in each block and looks at the segments
#list checking to see if the sequence starts at one and progresses by increments of one. Right now
#it simply prints information to the command line if the sequence is not aligned, but my goal was to
#use this to help determine if a trip has deviations.
def checkSequence(currentActualDay):
	return
	for b in currentActualDay.blocks:
		for t in b.trips:
			ind=0
			while ind < len(t.segments):
				if ind==0 and t.segments[ind].segmentSeq != 1:
					print(str(b.blockNumber)+':'+str(t.tripNumber)+' case 1')
					ind=ind+1
				else:
					if ind>0 and t.segments[ind].segmentSeq != (t.segments[ind-1].segmentSeq + 1) :
						print(str(b.blockNumber)+' : '+str(t.tripNumber)+'case 2')
					ind=ind+1
