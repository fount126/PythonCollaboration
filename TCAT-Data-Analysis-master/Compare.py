from lib.TCAT_Segment_Library.Classes import Block, Segment, Deviants, Deviation, Stop, CountMap
from lib.TCAT_Segment_Library.Debug import debug, dev_debug

#Compares the actual day versus the scheduled day, and updates the actual day's
#deviation object.
# Precondition: actualDay is an unprocessed Day class representing the raw Avail data.
# scheduledDay is a Day class that defines what a day is supposed to be like.
# Postcondition: actualDay will be manipulated so that it resembles the scheduledDay in the following ways:
# 1. If a trip was run, every stop will be accounted for. If a stop was missed, a proper deviation will be accounted for.
# Any other deviation is accounted for in the table. However, every segment exists in the trip regardless of deviation.
# 2. If a trip or block was not run, its segments will not exist. However, a deviation is thrown for every trip, and for the block
# if appropriate.
def compareDay(actualDay, scheduledDay):
	debug('Comparing day...', scheduledDay=scheduledDay, actualDay=actualDay)
	#Iterates over scheduled blocks in the day
	# dev_debug('\n\n\n\n\n~~~~~~~~~~~~~~~~~~~~~Test 0~~~~~~~~~~~~~~~~~~~~~\n\n\n\n\n\n',blocks=scheduledDay.blocks,size=len(scheduledDay.blocks), pause=True)
	for sBlock in scheduledDay.blocks:
		# dev_debug('Weird, check:',scheduledBlockNumbers=scheduledDay.getBlockNumbers(), actualBlockNumbers=actualDay.getBlockNumbers(), pause=True)
		#If the scheduled block is not in the set of actual blocks
		if sBlock.blockNumber not in actualDay.getBlockNumbers():
			#Adds a deviation for blocks missed
			actualDay.deviations.append(Deviation(Deviants.MISSED, "Missed block.", block=sBlock.blockNumber, service_date=scheduledDay.date))
			#Iterates over scheduled trips missed
			for sTrip in sBlock.trips:
				actualDay.deviations.append(Deviation(Deviants.MISSED, "Missed Trip.", block=sBlock.blockNumber, service_date=scheduledDay.date, trip=sTrip.tripNumber))
				for seg in sTrip.segments:
					actualDay.deviations.append(Deviation(Deviants.MISSED, "Missed segment.", iStop=seg.segmentID[0].stopID, tStop=seg.segmentID[1].stopID, block=sBlock.blockNumber, service_date=scheduledDay.date, trip=sTrip.tripNumber, ))
		else:
			#Compare on a block by block basis
			compareBlocks(actualDay,actualDay.getBlock(sBlock.blockNumber), sBlock)

	debug('Finished comparing day', scheduledDay=scheduledDay, actualDay=actualDay)


#Compares the actual block versus the scheduled block, and updates the actual day's
#deviation object. Assumes same block id
# Precondition: actualDay is an partially processed Day class where all missing blocks have been accounted for.
# actualBlock is an unprocessed actual block that is within actualDay.
# scheduledBlock is the model of how the block is supposed to be run.
# Postcondition: actualDay will be manipulated to account for any missed trips in the indicated block in the following ways:
# If the block is missing a trip, a deviation for the segment and trip will be created.
# else if the trip exists, its segments will be processed such that every segment in actualBlock has a corresponding one in scheduledBlock
def compareBlocks(actualDay,actualBlock,scheduledBlock):
	debug('Comparing blocks...', scheduledBlock=scheduledBlock, actualBlock=actualBlock)
	#Iterates over the scheduled trips in the block
	for sTrip in scheduledBlock.trips:
		#If a scheduled trip isn't in the actual trips
		if sTrip.tripNumber not in actualBlock.getTripNumbers():
			actualDay.deviations.append(Deviation(Deviants.MISSED, "Missed Trip.", block=actualBlock.blockNumber, service_date=actualDay.date, trip=sTrip.tripNumber))
			for seg in sTrip.segments:
				actualDay.deviations.append(Deviation(Deviants.MISSED, "Missed segment.", iStop=seg.segmentID[0].stopID, tStop=seg.segmentID[1].stopID, block=actualBlock.blockNumber, service_date=actualDay.date, trip=sTrip.tripNumber))
		else:
			aTrip= actualBlock.getTrip(sTrip.tripNumber)
			# dev_debug('Extra-test...', sTrip_route=sTrip.route, sTrip_pattern=sTrip.pattern, sTrip_tripSeq=sTrip.tripSeq, pause=True)
			aTrip.updateTrip(sTrip.route, sTrip.pattern, sTrip.tripSeq)
			#Compare on a trip by trip basis
			compareTrips(actualDay,actualBlock, aTrip, sTrip)
	debug('Finished comparing blocks...', scheduledBlock=scheduledBlock, actualBlock=actualBlock)

# Assumes no loops
def getMiddleBits(sTrip, iStop, tStop):
	dev_debug('Get middle bits run!', sTrip=sTrip, iStop=iStop.stopID, tStop=tStop.stopID)
	index = 0
	segments = sTrip.segments
	ret = []
	while segments[index].segmentID[0].stopID!=iStop.stopID:
		index+=1
		if index+1 == len(segments):
			return ret
	while segments[index].segmentID[0].stopID!=tStop.stopID:
		ret.append(segments[index])
		index+=1
		if index+1 == len(segments):
			return ret
	if ret:
		ret[0].segmentID[0].transferData(iStop)
		ret[-1].segmentID[1].transferData(tStop)
	return ret

#Compares the actual day versus the scheduled day, and updates the actual day's
#deviation object.
#Precondition: actualDay is a partially processed Day class, if there are missing blocks or trips, they have been accounted for already.
# actualBlock is a block class that exists in actualDay that has any missing trips already accounted for.
# aTrip: a Trip class that exists within actualBlock.
# sTrip: a Trip class that models how aTrip was supposed to run. Includes the corresponding distance and sequence values for the segments.
# Postcondition: actualDay's aTrip will now resemble sTrip with regard to sequence, and have a 1-1 correspondence for each segment.
# The segments in aTrip will also have the data for segment distance and sequence, as well as onboard count.
# TODO: Add onboard count
def compareTrips(actualDay,actualBlock, aTrip, sTrip):
	# debug('Comparing trips...', sTrip=sTrip.tripNumber, aTrip=aTrip.tripNumber, tripSeq = sTrip.tripSeq, pause=True)
	aIndex=0
	sIndex=0
	#loops over "actual" index and "scheduled" indexes.
	#TODO: check what is left in both stacks

	# Better version
	# segments = CountMap()
	# for seg in aTrip.segments:
	# 	segments.put(seg.segmentID[0].stopID, seg)
	# schedule = CountMap()
	# rebuilt=[]
	# for seg in sTrip.segments:
	# 	schedule.put(seg.segmentID[0].stopID, seg)
	# 	if segments.count(seg.segmentID[0])>1:
	# 		dev_debug('New: Loop')
	# 		actualDay.deviations.append(Deviation(Deviants.LOOP, "Loop.", iStop=aSegment.segmentID[0].stopID, tStop=aSegment.segmentID[1].stopID, block=actualBlock.blockNumber, service_date=actualDay.date, trip=sTrip.tripNumber, bus=aSegment.bus))
	#
	# 	if segments.contains(seg.segmentID[0]):
	# 		modelIStop = seg.segmentID[0]
	# 		actualIStop = segments.get(modelIStop.stopID).segmentID[0]
	# 		iStop = Stop(modelIStop.stopID, modelIStop.stopName, actualIStop.messageTypeID, actualIStop.stopTime, actualIStop.onboard, actualIStop.boards, actualIStop.alights, actualIStop.seen)
	# 		modelTStop = seg.segmentID[1]
	# 		actualTStop = segments.get(modelTStop.stopID).segmentID[1]
	# 		tStop = Stop(modelTStop.stopID, modelTStop.stopName, actualTStop.messageTypeID, actualTStop.stopTime, actualTStop.onboard, actualTStop.boards, actualTStop.alights, actualTStop.seen)
	# 		rebuilt.append(Segment(Stop(iStop, tStop, bus, distance, segseq))
	# 	else:
	# 		modelIStop = seg.segmentID[0]
	# 		actualIStop =
	# 		# Find 197s stop
	#
	# 		#
	# 		modelTStop = seg.segmentID[1]
	#  END better version
	while aIndex < len(aTrip.segments) and sIndex < len(sTrip.segments):
		debug('Current indexes...', aIndex=aIndex, sIndex=sIndex, sTrip=sTrip.tripNumber, aTrip=aTrip.tripNumber)
		aSegment = aTrip.segments[aIndex]
		sSegment = sTrip.segments[sIndex]
		# From last segment, add 197 boards and alights to terminal.
		while aSegment.segmentID[0].buffer:
			stop=aSegment.segmentID[0].buffer.pop()
			aSegment.segmentID[0].boards+=stop.boards
			aSegment.segmentID[0].alights+=stop.alights
			aSegment.segmentID[0].avl_onboard=stop.avl_onboard
			aSegment.segmentID[0].is_consolidated=True
			del stop

		# if aSegment.segmentID[0].stopID == 0:
		# 	dev_debug('\n\n\n\n\n\n\nStopID 0\n\n\n\n\n\n\n', pause=True, aTrip=aTrip.tripNumber)
		checkCases(aSegment,sSegment)
		#If both segments match stops, simply update aSegment.
		if aSegment.segmentID[0].stopID == sSegment.segmentID[0].stopID and aSegment.segmentID[1].stopID == sSegment.segmentID[1].stopID:
			aSegment.updateSegment(sSegment.distance, sSegment.segmentSeq)
			# If there happens to be a buffer, add stop values.
			while aSegment.segmentID[1].buffer:
				stop = aSegment.segmentID[1].buffer.pop()
				debug('Boards and lights being added!', originalBoards=aSegment.segmentID[0].boards, originalAlights=aSegment.segmentID[0].alights, boardsAdded=stop.boards, alightsAdded=stop.alights)
				aSegment.segmentID[0].boards +=stop.boards
				aSegment.segmentID[0].alights +=stop.alights
				aSegment.segmentID[0].avl_onboard=stop.avl_onboard
				aSegment.segmentID[0].is_consolidated=True
				del stop
			aIndex +=1
			sIndex +=1
			continue
		#elseif the initial stops of both segments match...
		elif aSegment.segmentID[0].stopID == sSegment.segmentID[0].stopID:
			#If the actual terminal stop's id does not match a scheduled stop
			if aSegment.segmentID[1].stopID not in sTrip.getStopNumbers():
				assert aSegment.segmentID[1].messageTypeID!=197, 'There should not be a 197 here.'
				#if the terminal stops of both are not actual stops in this trip...
				if sSegment.segmentID[1].stopID not in aTrip.getStopNumbers():
					#TODO: LATER Stop_Ids [1362, 1363] treat as 197 or flag stops. (But has actual boards and alights)
					#Either a (missed stop AND schedule definition error OR Nonscheduled stop) OR
					actualDay.deviations.append(Deviation(Deviants.MISSED, "Actuals missing.", iStop=aSegment.segmentID[0].stopID, tStop=aSegment.segmentID[1].stopID, block=actualBlock.blockNumber, service_date=actualDay.date, trip=sTrip.tripNumber, bus=aSegment.bus))
					actualDay.deviations.append(Deviation(Deviants.SCHEDULE_DEFINITION_ERROR, "Scheduled missing.", iStop=aSegment.segmentID[0].stopID, tStop=aSegment.segmentID[1].stopID, block=actualBlock.blockNumber, service_date=actualDay.date, trip=sTrip.tripNumber, bus=aSegment.bus))
					sIndex+=1
					aIndex+=1
					# debug('Missed stop!.', deviation=Deviants.MISSED, sStopID=sSegment.segmentID[1].stopID, aStopID=aSegment.segmentID[1].stopID)
					# if aTrip.segments[aIndex+1].segmentID[1].buffer:
					# 	stop = aTrip.segments[aIndex+1].segmentID[1].buffer.pop()
					# 	aTrip.segments.insert(aIndex+1, stop)
					# 	actualDay.deviations.append(Deviation(Deviants.INFERRED, "Found 197.", iStop=stop.stopID, block=actualBlock.blockNumber, service_date=actualDay.date, trip=sTrip.tripNumber, bus=aSegment.bus))
					# 	debug("Inferring a stop:", pause=True, stop=stop)
				#if the second "actual" stop is not in the scheduled trip, add
				#a non-scheduled stop.
				else:
					aTrip.nonscheduledStopsMade.append(aSegment.segmentID[1].stopID) # aSegment.deviation.append(2)
					actualDay.deviations.append(Deviation(Deviants.NONSCHEDULED, "Stop not scheduled.", iStop=aSegment.segmentID[0].stopID, tStop=aSegment.segmentID[1].stopID, block=actualBlock.blockNumber, service_date=actualDay.date, trip=sTrip.tripNumber, bus=aSegment.bus))
					aIndex+=1
			#else, this means the actual terminal stop is part of scheduled trip (actual terminal stop is IN sTrip).
			else:
				#TODO: Look more into this, confusing
				# This is where we decide whether to rebuild or not.
				sIndexOfAStop1= sTrip.findStop(aSegment.segmentID[1].stopID, index1=sIndex, initialStop=False)
				#If the actual terminal stop cannot be found from the current index-forward
				#in the scheduled trip as a scheduled terminal stop...
				if sIndexOfAStop1 == -1:
					sIndexOfAStop0 = sTrip.findStop(aSegment.segmentID[1].stopID, index1=sIndex)
					#if the actual second stop cannot be found from the current index-
					#forward in the scheduled trip as a first stop either,
					if sIndexOfAStop0==-1:
						sIndexOfAStop0 = sTrip.findStop(aSegment.segmentID[1].stopID, index2=sIndex)
						assert sIndexOfAStop0!=-1, 'Actual terminal stop number is in the scheduled trip, but when we checked for the index before and after, it did not exist. Should not be possible.'
						actualDay.deviations.append(Deviation(Deviants.LOOP, "Loop.", iStop=aSegment.segmentID[0].stopID, tStop=aSegment.segmentID[1].stopID, block=actualBlock.blockNumber, service_date=actualDay.date, trip=sTrip.tripNumber, bus=aSegment.bus))
						debug('Loop detected: Deviation of 6.', trip=aTrip.tripNumber, iStop=aSegment.segmentID[0].stopID, time=aSegment.segmentID[0].stopTime, pause=False)
						aIndex+=1
						sIndex+=1
						continue #Skip rest of analysis on this stop

					#found the actual terminal stop as a scheduled initial stop, but not as a scheduled terminal stop
					else:
						assert False, 'This should not be possible either, as under no circumstance should an initial actual stop not exist as a scheduled initial stop, but as a scheduled terminal stop.'
						debug('Warning: The impossible deviation (7) has just occurred!')
						actualDay.deviations.append(Deviation(Deviants.INITIAL_NO_TERMINAL, "Impossible?", iStop=aSegment.segmentID[0].stopID, tStop=aSegment.segmentID[1].stopID, block=actualBlock.blockNumber, service_date=actualDay.date, trip=sTrip.tripNumber, bus=aSegment.bus))
						sIndex = sIndexOfAStop0
						aIndex +=1
						continue
				#Found actual terminal stop as a later scheduled terminal stop. Time to
				#connect the segments by adding more segments.
				else: #If sIndexOfAStop1 != -1
					#TODO:could be 197, could be a done trip
					#If it is a stop report(150)
					i = aSegment.segmentID[0] #Starts as actual (or scheduled, doesnt matter) initial stop
					i_1 = aSegment.segmentID[1] #Actual terminal stop
					if sTrip.tripNumber==1818:
						dev_debug('\n\n\n\n\n\nMoment you\'ve been waiting for\n\n\n\n\n\n',pause=False)
					dev_debug('Inference here: ', sTrip=sTrip, aTrip=aTrip, startingpoint=i, endpoint=i_1)
					# dev_debug('Inference is happening!', pause=False, trip=aTrip.tripNumber, i=i.stopID, i_1=i_1.stopID, aTrip=aTrip, sTrip=sTrip)
					segmentsToAdd = getMiddleBits(sTrip, i, i_1)
					if segmentsToAdd:
						for seg in segmentsToAdd:
							seg.bus = aSegment.bus
							if i_1.buffer: #Check for 197s
								dev_debug('i_1 buffer found...', buffer=str("[%s]" % (", ".join(map(str, (i_1.buffer))))))
								stop = i_1.buffer.pop()
								dev_debug('i_1 buffer boards/alights', boards_alights=stop.pp_boards_alights)
								seg.segmentID[1].avl_onboard=stop.avl_onboard
								seg.segmentID[1].boards+=stop.boards
								seg.segmentID[1].alights+=stop.alights
								seg.segmentID[1].stopTime=stop.stopTime
								dev_debug('Adding Segment...', segment=seg, distance=seg.distance, istopID=i.stopID, tstopID=stop.stopID,istopName=i.stopName, tstopName=stop.stopName)
								seg.segmentID[1].messageTypeID=stop.messageTypeID
								del stop
							else: #No 197s
								dev_debug('No i_1 buffer found...')
								seg.segmentID[1].stopTime=None
						dev_debug('boards/alights', segmentsToAddAlights=str("[%s]" % (", ".join(map(lambda x: x.segmentID[1].pp_boards_alights(), segmentsToAdd)))), aTrip=aTrip, pause=False)
						dev_debug('Checking more info before error...', lengthToAdd=len(segmentsToAdd), segmentsToAdd=str("[%s]" % (", ".join(map(str, (segmentsToAdd))))))
						if aIndex+1>=len(aTrip.segments):
							dev_debug('aIndex+1>=len(aTrip.segments)')
							segmentsToAdd[-1].segmentID = (segmentsToAdd[-1].segmentID[0],aTrip.segments[aIndex].segmentID[1])
						else:
							dev_debug('aIndex+1<len(aTrip.segments)')
							segmentsToAdd[-1].segmentID = (segmentsToAdd[-1].segmentID[0], aTrip.segments[aIndex+1].segmentID[0])
							outConnection = Segment(segmentsToAdd[-1].segmentID[1], aTrip.segments[aIndex+1].segmentID[1], aSegment.bus,aTrip.segments[aIndex+1].distance,aTrip.segments[aIndex+1].segmentSeq)
							segmentsToAdd.append(outConnection)
						segmentsToAdd[-1].segmentID[1].buffer = i_1.buffer
						actualRebuilt = []
						aTrip.segments.remove(aSegment)
					#Rebuild actual segments by grabbing all before the index we are at
						actualRebuilt= aTrip.segments[:aIndex]
					#Then inserting segments we inferred
						actualRebuilt.extend(segmentsToAdd)
					#Then add all the segments after the index we are at
						actualRebuilt.extend(aTrip.segments[aIndex+1:])
						aTrip.segments=actualRebuilt

						if sTrip.tripNumber==1818:
							dev_debug('Info...', actualRebuilt=str("[%s]" % (", ".join(map(str, (actualRebuilt))))), aTrip=aTrip, pause=False)
						# aIndex+=len(segmentsToAdd)
						# sIndex+=len(segmentsToAdd)
					else:
						aIndex+=1
						sIndex+=1
		#first actual stop matches the second scheduled. Misaligned segment. (6)
		elif aSegment.segmentID[0].stopID == sSegment.segmentID[1].stopID:
			#Attempt to fix by incrementing scheduled index.
			prob='We were on block: %s on trip %s at indexes %s, %s looking at actual segment(%s, %s) and scheduled segment (%s, %s) and we had a strange offset where the actual was one segment behind the schedule.'
			aTrip.problems+= (prob % (str(actualBlock.blockNumber), str(aTrip.tripNumber), str(aIndex), str(sIndex), str(aSegment.segmentID[0].stopID), str(aSegment.segmentID[1].stopID), str(sSegment.segmentID[0].stopID), str(sSegment.segmentID[1].stopID)))
			# aSegment.updateSegment()
			aIndex += 1
			actualDay.deviations.append(Deviation(Deviants.MISALIGNED, "iA = tS", service_date=actualDay.date, block=actualBlock.blockNumber, trip=aTrip.tripNumber, iStop=aSegment.segmentID[0].stopID, tStop=aSegment.segmentID[1].stopID, bus=aSegment.bus))
		#first scheduled stop matches the second actual stop. Misaligned segment. (7)
		elif sSegment.segmentID[0].stopID == aSegment.segmentID[1].stopID:
			#Attempt to fix by incrementing actual index
			prob='We were on block: %s on trip %s at indexes %s, %s looking at actual segment(%s, %s) and scheduled segment (%s, %s) and we had a strange offset where the schedule was one segment behind the actual.'
			aTrip.problems+= (prob % (str(actualBlock.blockNumber), str(aTrip.tripNumber), str(aIndex), str(sIndex), str(aSegment.segmentID[0].stopID), str(aSegment.segmentID[1].stopID), str(sSegment.segmentID[0].stopID), str(sSegment.segmentID[1].stopID)))
			sIndex += 1
			actualDay.deviations.append(Deviation(Deviants.MISALIGNED, "iS = tA", service_date=actualDay.date, block=actualBlock.blockNumber, trip=aTrip.tripNumber, iStop=aSegment.segmentID[0].stopID, tStop=aSegment.segmentID[1].stopID, bus=aSegment.bus))
		#Second stop of both actual and scheduled segment match. Missed stop? Missed match?
		elif aSegment.segmentID[1].stopID == sSegment.segmentID[1].stopID:
			#Scheduled stop was not made.
			if sSegment.segmentID[0].stopID not in aTrip.getStopNumbers():
				dev_debug('Stop missed.', iStop=aSegment.segmentID[0], tStop=aSegment.segmentID[1], trip=aTrip.tripNumber, pause=False)
				actualDay.deviations.append(Deviation(Deviants.MISSED, "Missed stop.", iStop=sSegment.segmentID[1].stopID, service_date=actualDay.date, block=actualBlock.blockNumber, trip=aTrip.tripNumber, bus=aSegment.bus))
			#Actual stop was not a scheduled stop TODO: Treat as flag stop
			if aSegment.segmentID[0].stopID not in sTrip.getStopNumbers():
				actualDay.deviations.append(Deviation(Deviants.NONSCHEDULED, "Nonscheduled stop.", iStop=aSegment.segmentID[0].stopID, service_date=actualDay.date, block=actualBlock.blockNumber, trip=aTrip.tripNumber, bus=aSegment.bus))
			sIndex += 1
			aIndex += 1
			prob = 'We were on block %s on trip %s at indexes %s, %s looking at acutal segment (%s, %s) and scheduled segment (%s, %s) and we had a case of miss match, not sure how to deal with this so I just incremented both indexes.'
			aTrip.problems+=(prob % (str(actualBlock.blockNumber), str(aTrip.tripNumber), str(aIndex), str(sIndex), str(aSegment.segmentID[0].stopID), str(aSegment.segmentID[1].stopID), str(sSegment.segmentID[0].stopID), str(sSegment.segmentID[1].stopID)))
		#Prev intern's (Adam's) note: I am not sure in what context the 3 above ElseIf situations occur so right now I am just
		#trying to align the sequences and record information about each instance when it happens,
		#once I look at the deviation report I can make adjustments to the code to better handle each case

		#No stops match in the first and last segment.
		else: #if aSegment.segmentID[0].stopID == sSegment.segmentID[0].stopID and aSegment.segmentID[1].stopID == sSegment.segmentID[1].stopID:
			indexOne = sTrip.findMatch(aSegment.segmentID[0].stopID,  aSegment.segmentID[1].stopID, sIndex)
			indexTwo = aTrip.findMatch(sSegment.segmentID[0].stopID,  sSegment.segmentID[1].stopID, aIndex)
			#No segments matching the actual found in the scheduled trip (indexOne) and the scheduled segment was not found in the actual trip
			if indexOne==-1 and indexTwo==-1:#TODO: Throw away trip
				# dev_debug('Case 6.1')
				#index of actual initial stop in scheduled trip
				sIndexAStop0= sTrip.findStop(aSegment.segmentID[0].stopID, index1=sIndex)
				#index of actual terminal stop in scheduled trip
				sIndexAStop1= sTrip.findStop(aSegment.segmentID[1].stopID, index1=sIndex)
				#index of scheduled initial stop in actual trip
				aIndexSStop0= aTrip.findStop(sSegment.segmentID[0].stopID, index1=aIndex)
				#index of scheduled terminal stop in actual trip
				aIndexSStop1= aTrip.findStop(sSegment.segmentID[1].stopID, index1=aIndex)

				#All of the above were not found
				if sIndexAStop0==-1 and sIndexAStop1==-1 and aIndexSStop0==-1 and aIndexSStop1==-1:
					# dev_debug('Case 6.1.1')
					#Log, move on
					prob = 'We were on block %s on trip %s at indexes %s, %s looking at acutal segment (%s, %s) and scheduled segment (%s, %s) and we had a miss miss case where nothing could be found.'
					aTrip.problems+=(prob % (str(actualBlock.blockNumber), str(aTrip.tripNumber), str(aIndex), str(sIndex), str(aSegment.segmentID[0].stopID), str(aSegment.segmentID[1].stopID), str(sSegment.segmentID[0].stopID), str(sSegment.segmentID[1].stopID)))
					sIndex += 1
					aIndex += 1
				#Some were found
				else:
					#get shortest jump from either current
					shortestJump= getMin(sIndexAStop0-sIndex,sIndexAStop1-sIndex,aIndexSStop0-aIndex,aIndexSStop1-aIndex)
					# dev_debug('Case 6.1.2', sIndexAStop0=sIndexAStop0, sIndexAStop1=sIndexAStop1, aIndexSStop0=aIndexSStop0, aIndexSStop1=aIndexSStop1, shortestJump=shortestJump)
					if shortestJump == 1 :
						# dev_debug('Case 6.1.2.1')
						sIndex = sIndexAStop0
					elif shortestJump == 2:
						# dev_debug('Case 6.1.2.2')
						aIndex += 1
						sIndex = sIndexAStop1
					elif shortestJump == 3:
						# dev_debug('Case 6.1.2.3', aIndex=aIndex, newAIndex=aIndexSStop0)
						aIndex = aIndexSStop0
					elif shortestJump == 4:
						# dev_debug('Case 6.1.2.4')
						sIndex += 1
						aIndex = aIndexSStop1
				if sIndexAStop0 == -1:
					# dev_debug('Case 6.1.3', aIndex=aIndex)
					actualDay.deviations.append(Deviation(Deviants.NONSCHEDULED, "Nonscheduled stop.", iStop=aSegment.segmentID[0].stopID, service_date=actualDay.date, block=actualBlock.blockNumber, trip=aTrip.tripNumber, bus=aSegment.bus))
				if sIndexAStop1 == -1:
					# dev_debug('Case 6.1.4', aIndex=aIndex)
					actualDay.deviations.append(Deviation(Deviants.NONSCHEDULED, "Nonscheduled stop.", iStop=aSegment.segmentID[1].stopID, service_date=actualDay.date, block=actualBlock.blockNumber, trip=aTrip.tripNumber, bus=aSegment.bus))
				if aIndexSStop0 == -1:
					# dev_debug('Case 6.1.5', aIndex=aIndex)
					actualDay.deviations.append(Deviation(Deviants.NONSCHEDULED, "Nonscheduled stop.", iStop=sSegment.segmentID[0].stopID, service_date=actualDay.date, block=actualBlock.blockNumber, trip=aTrip.tripNumber, bus=aSegment.bus))
				if aIndexSStop1 == -1:
					# dev_debug('Case 6.1.6')
					actualDay.deviations.append(Deviation(Deviants.NONSCHEDULED, "Nonscheduled stop.", iStop=sSegment.segmentID[1].stopID, service_date=actualDay.date, block=actualBlock.blockNumber, trip=aTrip.tripNumber, bus=aSegment.bus))
			elif indexOne==-1 and indexTwo!=-1:
				# dev_debug('Case 6.1.7')
				aIndex=indexTwo
			elif indexOne!=-1 and indexTwo==-1:
				# dev_debug('Case 6.1.8')
				sIndex=indexOne
			else:
				# dev_debug('Case 6.1.9')
				if indexOne < indexTwo:
					# dev_debug('Case 6.1.9.1')
					sIndex=indexOne
				else:
					# dev_debug('Case 6.1.9.2')
					aIndex=indexTwo
		if aIndex==-1:
			dev_debug('Bug is here... Should not be able to have aIndex=-1', pause=False)
		while aSegment.segmentID[1].buffer:
			stop = aSegment.segmentID[1].buffer.pop()
			aSegment.segmentID[0].boards +=stop.boards
			aSegment.segmentID[0].alights +=stop.alights
			aSegment.segmentID[0].avl_onboard=stop.avl_onboard
			aSegment.segmentID[0].is_consolidated=True
			del stop


# Weird function, fix later
#Input: 4 integers,
#Returns: a integer representing which arguement is the minimum
# This is made to return the minimum index, so if any of the 4 arguements are negative, they are set
# to an unreasonably large number so they cannot be returned
def getMin(x0,x1,y0,y1):
	if x0 < 0 :
		x0 = 100000
	if x1 < 0:
		x1 = 100000
	if y0 < 0:
		y0 = 100000
	if y1 < 0:
		y1 = 100000
	minimum = min(x0,x1,y0,y1)
	if minimum == 100000:
		print('something messed up in getMin()')
	if x0 == minimum:
		return 1
	if x1 == minimum:
		return 2
	if y0 == minimum:
		return 3
	if y1 == minimum:
		return 4


#This function was written handle a special case where stop are the same but the numbers don't match
#my goal was to have it handle as many special casses as I could find so the Segments database could
#be more accurate
def checkCases(aSegment,sSegment):
	if (aSegment.segmentID[1].stopID == 1512 and sSegment.segmentID[1].stopID == 1513) or (aSegment.segmentID[1].stopID == 1513 and sSegment.segmentID[1].stopID == 1512):
		aSegment.updateSegment(sSegment.distance, sSegment.segmentSeq)
		aSegment.segmentID[1].stopID = 1513
		return True
	return False
