from enum import Enum
from ..TCAT_Segment_Library.Debug import debug
#TODO: Implement binary read from integer error-code to Deviants list
class Deviants(Enum):
	NONE = 0
	MISSED=1
	IMPLIED = 2
	INFERRED = 4
	NONSCHEDULED=8
	MISALIGNED=16
	POTENTIAL_LOOP=32
	LOOP=64
	POSSIBLE_SCHEDULE_DEFINITION_ERROR=128
	SCHEDULE_DEFINITION_ERROR=256
	BUS_SWITCH=512
	INITIAL_NO_TERMINAL=1024 #Shouldn't be able to occur
class Deviation:
	def __init__(self, deviant, description, block=None, trip=None, iStop=None, tStop=None, segment=None, bus=None, service_date=None):
		self.deviant=Deviants(deviant)
		self.block=block
		if len(str(trip))>10:
			debug("Deviation trip: "+trip+" had a deviation record >10 characters!")
		self.trip=trip
		self.iStop=iStop
		self.tStop=tStop
		if len(str(segment))>10:
			debug("Deviation segment: "+segment+" had a deviation record >10 characters!")
		self.segment=segment
		self.bus=bus
		if len(str(description))>20:
			debug("Deviation description: "+description+" had a deviation record >20 characters!")
		self.description=description
		self.service_date=service_date
class CountMap:
	def __init__(self):
		self.dict = dict()
	def __ensure__(self):
		for key in self.dict.keys():
			if self.dict[key][1] <1:
				self.dict.pop(key)
	def put(self, key, value):
		if key in self.dict.keys():
			self.dict[key] = (value, (self.dict[key][1]+1))
		else:
			self.dict[key] = (value, 1)
	def get(self, key):
		return self.dict[key][0]
	def count(self, key):
		if key in self.dict.keys():
			return self.dict[key][1]
		else:
			return 0
	def contains(self, key):
		if key in self.dict.keys():
			return True
		else:
			return False

	def remove(self, key):
		if key in self.dict.keys():
			self.dict[key] = (self.dict[key][0], self.dict[key][1]-1)
			self.__ensure__()
	def removeAll(self, key):
		if key in self.dict.keys():
			self.dict.pop(key)
			self.__ensure__()

#Definition of stop. Stores raw stop data as attributes.
class Stop:
	def __init__(self, stopID, stopName, messageTypeID, stopTime, onboard, boards, alights, seen):
		self.stopID=stopID
		self.stopName=stopName
		self.messageTypeID=messageTypeID
		self.stopTime=stopTime
		self.onboard=0
		self.avl_onboard=onboard
		self.boards=boards
		self.alights=alights
		self.seen=seen
		#Holds 197 reports
		self.buffer=[]
		self.is_consolidated = False
		# self.deviations= [Deviants.NONE]


	def transferData(self, stop):
		self.stopID = stop.stopID
		self.stopName = stop.stopName
		self.messageTypeID = stop.messageTypeID
		self.stopTime=stop.stopTime
		self.onboard += stop.onboard
		self.avl_onboard = stop.avl_onboard
		self.boards += stop.boards
		self.alights += stop.alights
		self.seen = stop.seen
		self.buffer = stop.buffer
	#Transfers onboards, boards, and alights from the passed in seg
	def transferOBA(self, stop):
		self.onboard += stop.onboard
		self.boards += stop.boards
		self.alights += stop.alights
	# def addDeviation(self, d, type=Deviants):
	# 	if type!=type(Deviants):
	# 		self.deviations.append(Deviants(d))
	# 	else:
	# 		self.deviations.append(d)
	def __str__(self):
		return '%s:%s,' % (str(self.stopID),str(self.messageTypeID))
	def pp_boards_alights(self):
		return '%s:%s{boards:%s,alights:%s}' % (str(self.stopID),str(self.messageTypeID), str(self.boards), str(self.alights))

#Definition of segment. Stores raw segment data as attributes.
class Segment:
	def __init__(self, iStop, tStop, bus,distance,segseq):
		self.segmentID=(iStop, tStop)
		self.avl_onboard=0
		self.onboard=0
		#the adjusted number of people onboard such that the total number of boards for a trip
		#equals the total number of alights on that trip.
		self.adjustedOnboard=0
		self.distance=distance
		self.bus=bus
		self.segmentSeq=segseq

		# self.deviations=[]

	#Updates segment distance and sequence number
	def updateSegment(self,distance,segSeq):
		self.distance=distance
		self.segmentSeq=segSeq

	def __str__(self):
		return ('[<%s>-<%s>]'% (str(self.segmentID[0]),str(self.segmentID[1])))
	# def addDeviation(self, d, type=Deviants):
	# 	if type!=type(Deviants):
	# 		self.deviations.append(Deviants(d))
	# 	else:
	# 		self.deviations.append(d)
	# #Transfers onboard from the passed in seg
	# def transferOnboard(self, seg):
	# 	self.onboard += seg.onboard
#Definition of trip. Stores raw trip data as attributes.
#currentBus - the most recent bus associated with the trip
#lastStop - the most recent stop object associated with the trip
#segments- a list of segments of the trip, buses- a list of busses used,
#stops- a list of stop objects made on the trip, adjustment- used for apc calculations, boards- total number of boards on the trip
#alights- total number of alights on the entire trip
#missedStops- list of scheduled stop that were missed
#nonscheduledStopsMade- list of stops that could not be found in scheduled day.

class Trip:
	def __init__(self, tripNumber, bus, stopID, stopName, stopTime, messageTypeID, onboard, boards, alights, route, direction, pattern, tripSeq):
	  self.tripNumber=tripNumber
	  self.currentBus = bus
	  self.lastStop = Stop(stopID,  stopName, messageTypeID, stopTime, onboard, boards, alights, 1)
	  self.numberOfStops = 1
	  self.tripStartTime = stopTime
	  self.tripEndTime = stopTime
	  self.route=route
	  self.direction=direction
	  self.pattern=pattern
	  self.segments=[]
	  self.buses=[bus]
	  self.stops=[self.lastStop]
	  self.adjustment=0
	  self.boards=0
	  self.alights=0
	  self.adjboards=0
	  self.adjalights=0
	  self.problems=''
	  self.nonscheduledStopsMade=[]
	  # Used for transferring 197s safely
	  self.buffer=[]
	  self.tripSeq = tripSeq
	  # self.deviations=[Deviants.NONE]

	def onboards_are_equal(self):
		for s in self.segments:
			if s.avl_onboard!=s.onboard:
				return False
			if s.segmentID[0].avl_onboard!=s.segmentID[0].onboard or s.segmentID[1].avl_onboard!=s.segmentID[1].onboard:
				return False
		return True
	# Adds a segment to the trip using a stop object and a bus object.
	# Precondition: avl_onboard and onboard are equal in all segments.
	def addSegment(self, stop, bus):

		# if not self.onboards_are_equal():
		# 	debug('Onboards are not equal. Possible problem...', trip=self, stopAdded=stop, bus=bus)
		# if 'dFlag' in globals():
		# 	assert self.onboards_are_equal()
		#If 197, add to buffer
		if stop.messageTypeID == 197:
			self.buffer.append(stop)
			return
		#From here only 150s or 0s
		#If trip buffer is not empty
		if self.buffer:
			#Move trip buffer to stop buffer
			stop.buffer = self.buffer
			self.buffer = []

			# MISUNDERSTOOD: Thought 197s did not have onboard
			# # Compare new stop avl onboard to last stop avl onboard to find 197 boards/alights
			# if(stop.avl_onboard > self.segments[-1].avl_onboard):
			# 	stop.buffer[-1].boards = stop.avl_onboard-self.segments[-1].avl_onboard
			# 	stop.buffer[-1].alights = 0
			# else:
			# 	stop.buffer[-1].boards = 0
			# 	stop.buffer[-1].alights = self.segments[-1].avl_onboard - stop.avl_onboard

		lastStop=self.lastStop
		#Initializes with 0 passengers and -1 seq
		newSegment=Segment(lastStop,stop,bus,0,-1)
		self.segments.append(newSegment)
		self.stops.append(stop)
		self.lastStop=stop
		self.numberOfStops+=1
		self.tripEndTime=stop.stopTime
		#newSegment.onboard=lastStop.onboard

	# def addDeviation(self, d, type=Deviants):
	# 	if type!=type(Deviants):
	# 		self.deviations.append(Deviants(d))
	# 	else:
	# 		self.deviations.append(d)
	def processBuffers(self, fun=None):
		#If function to be run on all buffers, do that
		if fun:
			fun(self.segments)
		#Make sure all buffers are cleared
		for s in self.segments:
			for d in s.segment[1].buffer:
				s.segmentID[0].boards+=d.boards
				s.segmentID[0].alights+=d.alights
				s.segmentID[0].onboards+=d.onboards
			s.segment[1].buffer.clear()
	#UNAUDITED, just grabs onboards from initial stops and sets segment attributes
	# def calculateOnboards(self):
	# 	#WIP
	# 	index = 0
	# 	length = len(self.segments)
	# 	crntBus = self.segments[0].bus
	# 	while index < length:
	# 		s = self.segments[index]
	# 		if crntBus != s.bus:
	# 			dev_debug('Bus switch mid-route!', pause=True, segment=s, bus1=crntBus, bus2=s.bus)
	# 			s.deviation.append(Deviants.BUS_SWITCH)
	# 			busPassengers[crntBus]=0
	# 		crntBus=s.bus
	# 		#Bus has not been encountered yet
	# 		if not crntBus in busPassengers.keys():
	# 			busPassengers[s.bus]=0
	# 		#Deadhead trip
	# 		if self.route==999:
	# 			dev_debug('Deadhead!', pause=True)
	# 			busPassengers[s.bus]=0
	# 			continue
	# 		if s.segmentID[0].messageTypeID != 197: #Should always be the case
	# 			#Calculate boards and alights on trip
	# 			self.boards += s.segmentID[0].boards
	# 			self.alights += s.segmentID[0].alights
	# 			#onboard this segment is the previous amount + boards - alights of this stop
	# 			s.boards = s.segmentID[0].boards
	# 			s.alights = s.segmentID[0].alights
	# 			s.onboard = s.segmentID[0].onboard
	# 			s.onboard += s.segmentID[0].boards-s.segmentID[0].alights
	# 			#Bus passengers for cross-bus on same trip
	# 			bussPassengers[s.bus]+=s.segmentID[0].boards-s.segmentID[0].alights
	# 		else:
	# 			debug('Encountered a 197. Check why onBoard is getting 197s.', pause=197, segment=s)
	# 		index+=1
	# 	#Start with lastSeg being initial stop
	# 	lastSeg = None
	# 	# for s in self.segments:

	#Updates trip using route and pattern.
	def updateTrip(self, route, pattern, tripSeq):
		self.route = route
		self.pattern = pattern
		self.tripSeq = tripSeq
	def removeStop(self, index, conservePassengers=False):
		seg = self.segments.pop(index)
		if index==0:
			return
		else:
			lastSeg = self.segments.pop(index-1)
			newSeg = Segment(lastSeg.segmentID[0], seg.segmentID[1], self.bus, lastSeg.distance+seg.distance, seg.segmentSeq)
			self.segment.insert(index-1, newSeg)

	#Iterates over segments in the given range to find the initial stopID.
	def findStop(self, stop, index1=0, index2=-1, initialStop=True):
		#Fix Preconditions
		#If initial stop, set wStop as initial stop index on segment.
		#Else, set as terminal stop index
		if initialStop:
			wStop = 0
		else:
			wStop = 1
		#if index2 is <0, make it the number of segments in this trip. (so
		#it will loop to the last segment).
		if index2<0:
			index2=len(self.segments)
		#Iterates over segments
		while index1<index2:
			#compares stop (id) to the iterator's second stop id.
			if stop == self.segments[index1].segmentID[wStop].stopID:
				return index1
			else:
				index1+=1
		#Was not found
		return -1



	#idOne- first stop number of segment
	#idTwo- second stop number of segment
	#index- index to start search
	#Returns segment or -1 if none found.
	def findMatch(self, idOne, idTwo,index):
		s=index
		#Iterates over segments
		while s < len(self.segments):
			#compares stop ids of first and second stop on segments
			if self.segments[s].segmentID[0].stopID==idOne and self.segments[s].segmentID[1].stopID==idTwo:
				return s
			else:
			  s=s+1
		return -1

	#Returns all stop numbers in this Trip.
	def getStopNumbers(self):
		x=[]
		if self.stops==None:
			print('oh man, getStopNumbers failed. Is %s initialized?'%(self))
			return x
		else:
			for s in self.stops:
				x.append(s.stopID)
			return x
	#Modification of getStopNumbers to get stop segments on this trip.
	def getStopSegments(self):
		x=[]
		if self.segments==None:
			print('oh man, getStopNumbers failed. Is %s initialized?'%(self))
			return x
		else:
			for s in self.segments:
				x.append(s)
			return x



	def __str__(self):
		stringBuff = 'trip#'+str(self.tripNumber)+'=('
		for seg in self.segments:
			stringBuff+=('%s:%s,'% (str(seg.segmentID[0].stopID),str(seg.segmentID[0].messageTypeID)))
		if len(self.segments)>0:
			stringBuff+=('%s:%s)'% (str(self.segments[-1].segmentID[1].stopID),str(self.segments[-1].segmentID[1].messageTypeID)))
		else:
			stringBuff+=(')')
		return stringBuff



#Definition of Block. Stores raw block data.
class Block:
	def __init__(self, blockNumber):
		self.blockNumber=blockNumber
		self.trips=[]
		self.numberOfTrips=0
		self.numberOfBuses=0
		# self.deviations=[Deviants.NONE]
	# def addDeviation(self, d, type=Deviants):
	# 	if type!=type(Deviants):
	# 		self.deviations.append(Deviants(d))
	# 	else:
	# 		self.deviations.append(d)
	#adds a trip to the block.
	def addTrip(self, trip):
		self.trips.append(trip)
		self.numberOfTrips+=1
		self.numberOfBuses+=1
	#returns a trip from the block using block number
	def getTrip(self, tripNumber):
		#Iterates over trips
		for t in self.trips:
			#if tripNumbers match, return the trip
			if t.tripNumber==tripNumber:
				return t
		print('Could not find trip')

	#Returns a list of trip numbers.
	def getTripNumbers(self):
		trips = []
		#Iterates over trips
		for t in self.trips:
			trips.append(t.tripNumber)
		return trips

	def __str__(self):
		stringBuff = 'block#'+str(self.blockNumber)+'=\n('
		#Grab up until before last element
		for trip in self.trips[:-1]:
			stringBuff+=(str(trip)+',\n')
		#last element
		stringBuff+=(str(self.trips[-1])+')')
		return stringBuff

#Definition of Day. Stores raw Day data.
class Day:
	def __init__(self, date):
	  	self.date=date
	  	self.numberOfBlocks=0
	  	self.busesUsed=[]
	  	self.blocks=[]
		# Used to store Deviation records
	  	self.deviations=[]
	# def addDeviation(self, d, type=Deviants):
	# 	if type!=type(Deviants):
	# 		self.deviations.append(Deviants(d))
	# 	else:
	# 		self.deviations.append(d)
	#Adds a block to the Day.
	def addBlock(self, block):
		self.blocks.append(block)
		self.numberOfBlocks+=1

	#Returns a block based off the block number.
	def getBlock(self, blockNumber):
		for b in self.blocks:
			if blockNumber==b.blockNumber:
				return b
		print('Could not find Block')

	#Returns a list of all block numbers.
	def getBlockNumbers(self):
		list=[]
		for block in self.blocks:
			list.append(block.blockNumber)
		return list

	#Adds a bus to the block.
	def addBus(self,bus):
		if bus not in self.busesUsed:
			self.busesUsed.append(bus)
	def __str__(self):
		stringBuff = 'date#'+str(self.date)+'=\n('
		#Grab up until before last element
		for block in self.blocks[:-1]:
			stringBuff+=(str(block)+',\n')
		#last element
		if self.blocks:
			stringBuff+=(str(self.blocks[-1]))
		stringBuff+=')'
		return stringBuff
