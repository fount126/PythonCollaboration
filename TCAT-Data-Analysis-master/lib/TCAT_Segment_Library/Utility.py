from ..TCAT_Segment_Library import Debug
from ..TCAT_Segment_Library.Parse import parseActual, display, parseScheduled
from ..TCAT_Segment_Library.Classes import Day, Block, Trip, Segment, Stop, Deviants
from datetime import timedelta, date, datetime  #for date conversion
import pyodbc
#Inputs: start_date- a date object representing the the first date in a range, end_date- a date object
#	   representing the final date in a the range.
#This is a helper function used to itterate through days given a start date object and an ending
#date object. It is used to create a sort of mirror to the range() function in python, but for
#date objects.
def getDate(y, m, d):
	return date(y,m,d)
def daterange(start_date, end_date):
	for n in range(int ((end_date - start_date).days)):
		yield start_date + timedelta(n)

def getReadConnection(user, password, server = 'AVAILDEV', database = 'Utilities'):
	return pyodbc.connect(r'DRIVER={ODBC Driver 11 for SQL Server};'		#The server driver, as list of these can be found on the pyodbc library readme on github
		r'SERVER=%s;'							   #need server name here
		r'DATABASE=%s;'							#need database name here
		r'UID=%s;'
		r'PWD=%s'% (server, database, user, password))

def getWriteConnection(user, password, server = 'AVAILDEV', database = 'Segments'):
	return pyodbc.connect(r'DRIVER={ODBC Driver 11 for SQL Server};'		#The server driver, as list of these can be found on the pyodbc library readme on github
		r'SERVER=%s;'							   #need server name here
		r'DATABASE=%s;'							#need database name here
		r'UID=%s;'
		r'PWD=%s'% (server, database, user, password))
def sanitize(a, stopID=False):
	if a==None:
		return None
	else:
		return str(a)

#Inputs: the day object you want to write to the table
#Returns: the function is void, it returns nothing
#This function iterates through the all the blocks in a day, the trips in each block, and the
#segments in each trip, writing the information to the Segments database.
def writeToSegments(actualDay, connection):
	Debug.debug('Writing to segments.')
	wCursor = connection.cursor()
	for b in actualDay.blocks:
		for t in b.trips:
			for s in t.segments:
				day=actualDay.date
				bus=s.bus
				blockNumber=b.blockNumber
				route=t.route
				tripNumber=t.tripNumber
				direction=t.direction
				iStopNumber=s.segmentID[0].stopID
				iStopName=s.segmentID[0].stopName
				iStopType=s.segmentID[0].messageTypeID
				iStopSeen=s.segmentID[0].seen
				tStopNumber=s.segmentID[1].stopID
				tStopName=s.segmentID[1].stopName
				tStopType=s.segmentID[1].messageTypeID
				tStopSeen=s.segmentID[1].seen
				boards=s.segmentID[0].boards
				alights=s.segmentID[1].alights
				onboard=s.onboard
				adjOnboard=s.adjustedOnboard
				iStopTime=s.segmentID[0].stopTime
				tStopTime=s.segmentID[1].stopTime
				segDistance=s.distance
				pattern=t.pattern
				segseq=s.segmentSeq
				tripseq=t.tripSeq
				try:
					passenger_per_feet=s.feet_per_passenger
				except Exception:
					passenger_per_feet=None
				try:
					wCursor.execute(' INSERT INTO dbo.Segments (ServiceDate, Bus, Block, Route, Trip, Pattern, Direction, iStopID, iStopName, iStopMessageID, iStopSeen, tStopID, tStopName, tStopMessageID, tStopSeen, Boards, Alights, Onboard, AdjustedOnboard, SegmentSequence, StartTime, EndTime, SegmentFeet, trip_sequence, Feet_times_passengers)'
						' VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)', day, bus, blockNumber,route, tripNumber,pattern,direction, iStopNumber,iStopName,iStopType, iStopSeen, tStopNumber,tStopName,tStopType, tStopSeen, boards, alights, onboard, adjOnboard, segseq, iStopTime, tStopTime, segDistance, tripseq, passenger_per_feet)
				except Exception as e:
					Debug.debug('Was unable to write the following record to dbo.Segments', record=
						'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'%(day, bus, blockNumber,route, tripNumber,pattern,direction, iStopNumber,iStopName,iStopType, iStopSeen, tStopNumber,tStopName,tStopType, tStopSeen, boards, alights, -1, -1, segseq, iStopTime, tStopTime, segDistance), exception=e)
	connection.commit()
	Debug.debug('Done writing.')
def writeToDeviations(actualDay, connection):
	Debug.debug('Writing to deviations.')
	wCursor = connection.cursor()
	for d in actualDay.deviations:
		# Debug.dev_debug('Here are the deviations...', deviation=d)
		deviant = sanitize(d.deviant.value)
		blockNumber = sanitize(d.block)
		tripNumber = sanitize(d.trip)
		iStop = sanitize(d.iStop)
		tStop = sanitize(d.tStop)
		segment = sanitize(d.segment)
		bus = sanitize(d.bus)
		description = sanitize(d.description)
		service_date = sanitize(d.service_date)
		try:
			wCursor.execute(' INSERT INTO dbo.deviation (deviation_number, block, trip, iStop, tStop, segment, bus, description, service_date)'
				' VALUES(?,?,?,?,?,?,?,?,?)', deviant, blockNumber, tripNumber, iStop, tStop, segment, bus, description, service_date)
		except Exception as e:
			Debug.debug('Was unable to write the following record to dbo.deviation', record=
				'VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)'%(deviant, blockNumber, tripNumber, iStop, tStop, segment, bus, description, service_date), exception=e)
			return
	connection.commit()
	Debug.debug('Done writing.')

selectActualInformation = ( ' SELECT  Message_Type_Id, service_date, block, route, trip, dir, vmh_time, bus, Onboard, boards, alights, Stop_Id,Internet_Name '
							' FROM dbo.vActual_History'
							' WHERE service_date =? '
							' AND Message_Type_Id!=152'
							'ORDER BY vmh_time asc')

selectScheduledInformation = ( ' SELECT service_day,trip_seq, stop_seq, route, trip, direction, block,Pattern_Record_Id, trip_start, trip_end, iStop_Id, tStop_Id,iStop_descr,tStop_descr, segment_feet'
							' FROM dbo.vHistorical_Stop_Schedule '
							' WHERE service_day = ?'
							' ORDER BY trip_seq, stop_seq asc')

selectActualInformationByBlock = ( ' SELECT  Message_Type_Id, service_date, block, route, trip, dir, vmh_time, bus, Onboard, boards, alights, Stop_Id,Internet_Name '
							' FROM dbo.vActual_History'
							' WHERE service_date =? '
							' AND Message_Type_Id!=152 AND block=?'
							'ORDER BY vmh_time asc')

selectScheduledInformationByBlock = ( ' SELECT service_day,trip_seq, stop_seq, route, trip, direction, block,Pattern_Record_Id, trip_start, trip_end, iStop_Id, tStop_Id,iStop_descr,tStop_descr, segment_feet'
							' FROM dbo.vHistorical_Stop_Schedule '
							' WHERE service_day = ? AND block=?'
							' ORDER BY trip_seq, stop_seq asc')

#Inputs: requires a string input called date, which is that service date that will be processed
#Returns: a 2-d array containing the actualDay object and the scheduledDay object
#This function issues two queries to the databases to pull information about the actual and the scheduled trips.
#It pulls all the information from a series of columns  and stores it in a two dimensional array,
#which is stored in the cursor object.
#cursor.execute(selectActualInformation, date)  issues the query passed in the string selectActualInformation
#using the date string passed in through the createDays(date) arguement date. Then I create a day Object.
#results = cursor.fetchone() grabs one row from the 2-d array containing the information I pulled from
#the database, and calls parseActual() to process this row. The fetchone() function removes one row
#from the array so each time it is called the array grows shorter. The while loop runs as long as
#there is information in array that has not been parsed yet. Inside the while loop I look at a row of
#information and call one of the parse() functions on the information from that row. The parse() function
#returns an updated version of the day with the information from that row, and then another row of
#data from the array is place in results by results = cursor.fetchone().
#The createDays() function does this first for the actualDay, then for the scheduled day
def createDays(date, readConnection, block=-1):
	Debug.debug('Creating day.', day=date)
	rCursor = readConnection.cursor()

	Debug.debug('Selecting ActualInformation from database.')
	#This is where the actualDay information is parsed into a Day object
	if block==-1:
		rCursor.execute(selectActualInformation, date)
	else:
		rCursor.execute(selectActualInformation, date, block)
	currentActualDay=Day(date)
	results = rCursor.fetchone()
	Debug.debug('Processing results')
	while results:
		currentActualDay=parseActual(currentActualDay, results)
		results = rCursor.fetchone()
	Debug.debug('Finished processing.')
	#This is where the actualStops information is parsed into a Day object. Includes only stops.
	# cursor.execute(selectActualInformationStopsOnly, date)
	# currentActualStops=Day(date)
	# results = cursor.fetchone()
	# while results:
	#	 currentActualStops=parseActual(currentActualStops, results)
	#	 results = cursor.fetchone()
	Debug.debug('Selecting ScheduledInformation from database.')
	#This is where the scheduledDay information is parsed into a Day object
	if block==-1:
		rCursor.execute(selectScheduledInformation,date)
	else:
		rCursor.execute(selectScheduledInformation,date, block)
	currentScheduledDay=Day(date)
	results = rCursor.fetchone()
	Debug.debug('Processing results.')
	while results:
		currentScheduledDay=parseScheduled(currentScheduledDay, results)
		results = rCursor.fetchone()

	Debug.debug('Finished processing.')
	# days=[currentActualDay, currentActualStops, currentScheduledDay]
	days=[currentActualDay, currentScheduledDay]
	return days

def flatten_segments(block):
	consolidated_trips = []
	for t in block.trips:
		consolidated_trips.extend(t.segments)
	return consolidated_trips
