from ..TCAT_Segment_Library.Classes import Day, Block, Trip, Segment, Stop, Deviation
from ..TCAT_Segment_Library.Debug import debug, dev_debug
 #This function is responsible for creating block, trip, segment and stop objects from the information
 #pulled from the SQL table.
 #Inputs: currentDay- a day that is being updated, results-an array which contains the information from
 #	   one row of the database.
 #Returns: an updated version of the day object using the information from results
 #Lines 8-19 are variables that store the information from the results array.		 #need to update
 #			  cBlockNumber not in currentDay.getBlockNumbers()
 #Checks if the block number from the results is in the day object yet, if it is not then it enters
 #the elif block and creates a block, trip and adds both to the day and returns the updated day.
 #If it has then it moves onto the else block and gets a reference to the block object in the currentBlock variable
 #			   cTripNumber not in currentBlock.getTripNumbers()
 #Checks if the trip number from result is in the currentBlock of the day object yet, if not then it
 # enters the if blok and creates a new trip object, adds it to the block object that
 #TODO: heck for missed stop at end
def parseActual(currentDay,results):
	cMessageTypeID=results[0]
	cBlockNumber=results[2]
	cRoute=results[3]
	cTripNumber=results[4]
	cDir=results[5]
	cVMHTime=results[6]
	cBus=results[7]
	cOnboard=results[8]
	cBoards=results[9]
	cAlights=results[10]
	cStopID=results[11]
	cStopName=results[12]
	if cMessageTypeID != 197 and cStopID == 0:
		debug('Got a stopID 0', pause=True)

	#if the block is not in the list of blocks for our current day we create a new block object and trip object
	if cBlockNumber not in currentDay.getBlockNumbers():
		newBlock=Block(cBlockNumber)
		# the call to create a new trip also creates a new stop object ||||| TC: unlear why there is just one stop object. |||||
		newTrip = Trip (cTripNumber, cBus, cStopID, cStopName, cVMHTime, cMessageTypeID, cOnboard, cBoards, cAlights,cRoute, cDir, 0, 0)
		newBlock.addTrip(newTrip)
		currentDay.addBlock(newBlock)
		currentDay.addBus(cBus)

		return currentDay
	else:
		currentBlock=currentDay.getBlock(cBlockNumber)					#the block number from the list of rows must be in the day objects list of blocks so i get it by using a function that takes a integer block number and returns the block object
		if cTripNumber not in currentBlock.getTripNumbers():				  # if the trip number is not in the list of trips in the block we are ooking at then we make a new trip
			newTrip =Trip (cTripNumber, cBus, cStopID, cStopName, cVMHTime, cMessageTypeID, cOnboard, cBoards, cAlights,cRoute, cDir, 0, 0)
			currentBlock.addTrip(newTrip)
			currentDay.addBus(cBus)

			return currentDay
		else:
			currentTrip = currentBlock.getTrip(cTripNumber)					 #using the trip number from the row we get a reference to the trip object that matches the row we are looking at
			if cBus != currentTrip.currentBus:								  # if the bus from the row does not match the last bus used by the trip we have to add it to the trip,
				currentTrip.buses.append(cBus)
				currentTrip.currentBus=cBus									   #adds the bus from the row to the list of buses used by the trip and makes it the most recently used
				currentDay.busesUsed.append(cBus)							   #A list of buses used can be found in currentDay.busesUsed
				if cStopID == currentTrip.lastStop.stopID:					  #if the stop number matches the last stop seen we disregard it, this needs to be changed to account for alights and boards
					currentTrip.lastStop.boards += cBoards
					currentTrip.lastStop.alights += cAlights
					currentTrip.lastStop.onboard += cBoards-cAlights

					currentTrip.lastStop.seen+=1

					return currentDay
				else:
					currentStop=Stop(cStopID,cStopName, cMessageTypeID,cVMHTime,cOnboard,cBoards,cAlights,1)  #If it gets here then all we have to do is create a new stop object, and then
					currentTrip.addSegment(currentStop,cBus)					#use the add segement function to create a segment from the new stop and lst stop

					return currentDay
			else:
				if cStopID == currentTrip.lastStop.stopID:
					currentTrip.lastStop.boards += cBoards
					currentTrip.lastStop.alights += cAlights
					currentTrip.lastStop.onboard += cBoards-cAlights
					currentTrip.lastStop.seen+=1

					return currentDay
				else:
					currentStop=Stop(cStopID,cStopName, cMessageTypeID,cVMHTime,cOnboard,cBoards,cAlights,1) #same thing as line 42, but for the case of the same bus
					currentTrip.addSegment(currentStop,cBus)

					return currentDay

#This function is esentially the same as parseActual but works on the scheduled day
#lines 68 to 81 are variables that hold the information taken from one row.
def parseScheduled(currentDay,results):
	sTripSeq=results[1]
	sSegSeq=results[2]
	sRoute=results[3]
	sTrip=results[4]
	sDirection=results[5]
	sBlock=results[6]
	pattern=results[7]
	sTripStart=results[8]
	sTripEnd=results[9]
	sIStopID=results[10]
	sTStopID=results[11]
	sIStopName=results[12]
	sTStopName=results[13]
	sSegmentDistance=results[14]
	# dev_debug('sTrip data...',sTripNumber=sTrip, sRoute=sRoute, sTripSeq=sTripSeq, pause=True)
	if sRoute==999:

		return currentDay
	if sTStopID==None:													  # if the terminal stop number is null we ignore it

		return currentDay
	if sBlock not in currentDay.getBlockNumbers():							  # if the block from the row is not in the list of blocks from the day then we create two stop objects, make a segment from them, and create a new trip and block object
		iStop=Stop(sIStopID, sIStopName, 0,0,0,0,0,0)
		tStop=Stop(sTStopID, sTStopName, 0,0,0,0,0,0)
		newSegment=Segment(iStop, tStop,0, sSegmentDistance,sSegSeq )
		newTrip=Trip( sTrip, 0, 0, 0, 0, 0, 0, 0, 0, sRoute, sDirection, pattern, sTripSeq) #( tripNumber, bus, stopID, stopName, stopTime, messageTypeID, onboard, boards, alights,route,direction,pattern)

		# dev_debug('sTrip data...', sRoute=sRoute, sTripSeq=newTrip.tripSeq, pause=True)
		newTrip.segments.append(newSegment)
		newTrip.numberOfStops+=1

		newTrip.stops.append(iStop)
		newTrip.stops.append(tStop)
		newBlock=Block(sBlock)
		newBlock.addTrip(newTrip)
		currentDay.addBlock(newBlock)

		return currentDay
	else:
		currentBlock=currentDay.getBlock(sBlock)										#since the current block already exsists we get a referece to it
		if sTStopID==None:														  # if the terminal stop number is null we ignore it

			return currentDay
		else:
			if sTrip not in currentBlock.getTripNumbers():					  # if the trip from the row is not an object yet we have to create two stop objects, used them to create a segement and then create a trip
				iStop=Stop(sIStopID, sIStopName, 0,0,0,0,0,0)
				tStop=Stop(sTStopID, sTStopName, 0,0,0,0,0,0)
				newSegment=Segment(iStop, tStop,0, sSegmentDistance,sSegSeq )
				newTrip=Trip( sTrip, 0, 0, 0, 0, 0, 0, 0, 0, sRoute, sDirection, pattern, sTripSeq)
				newTrip.segments.append(newSegment)
				newTrip.numberOfStops+=1

				newTrip.stops.append(iStop)
				newTrip.stops.append(tStop)
				currentBlock.addTrip(newTrip)

				return currentDay
			else:
				currentTrip=currentBlock.getTrip(sTrip)
				if sIStopID == currentTrip.stops[-2].stopID and sTStopID == currentTrip.stops[-1].stopID :

					return currentDay
				else:
					iStop=currentTrip.stops[-1]
					tStop=Stop(sTStopID, sTStopName, 0,0,0,0,0,0)
					newSegment=Segment(iStop, tStop,0, sSegmentDistance, sSegSeq )
					currentTrip.stops.append(tStop)
					currentTrip.segments.append(newSegment)
					currentTrip.numberOfStops+=1

					return currentDay
				  #we get a reference to the trip object and use it to form a new segemnt by using the last stop and the new stop


#Given a day object this function will iterate through all of the blocks in the day, and for each block
#it iterates through all the trips in that block, and for each trip it iterates through the list of
#segments and prints them, This function is primarily for my own testsing, to make sure values were
#actually being written to the ojects
def display(currentDay):
	print(currentDay.date)
	for b in currentDay.blocks:
		print('block ' + str(b.blockNumber))
		for t in b.trips:
			print('trip ' + str(t.tripNumber))
			for s in t.segments:
				print('Segment : ' +  '(' + str(s.segmentID[0].stopID) +' , ' +str(s.segmentID[1].stopID) +')', end= '; ')
				print('seg distance'+str(s.distance))
