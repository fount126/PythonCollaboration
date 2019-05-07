from lib.TCAT_Segment_Library import Debug, Utility
from lib.TCAT_Segment_Library.Classes import Deviation, Deviants

def fix_boards_alights(currentActualDay):
	Debug.debug('Fixing boards and alights.')
	# Correct onboard
	for b in currentActualDay.blocks:
		for t in b.trips:
			for seg in t.segments:
				if seg.segmentID[1].messageTypeID==197 or seg.segmentID[1].is_consolidated:
					difference = seg.segmentID[1].avl_onboard - seg.segmentID[0].avl_onboard
					if difference!=0:
						Debug.dev_debug('Non-zero difference', difference = difference, trip=t.tripNumber, iStop = seg.segmentID[0].stopID, tStop = seg.segmentID[1].stopID, iStop_avl_onboard = seg.segmentID[0].avl_onboard, tStop_avl_onboard = seg.segmentID[1].avl_onboard)
					if difference > 0:
						seg.segmentID[1].boards = difference
						seg.segmentID[1].alights = 0
					else:
						seg.segmentID[1].boards = 0
						seg.segmentID[1].alights = -difference
	Debug.debug('Finished fixing boards and alights!')

	# if stop.boards!=0 or stop.alights!=0:
	# 	debug('Boards or alights are not zero.', stop_boards=stop.boards, stop_alights=stop.alights, stop_onboard=stop.onboard)



def count_raw_onboards(currentActualDay):
	Debug.debug('Counting raw onboards.')
	# Correct onboard
	for b in currentActualDay.blocks:
		onboard=0
		if b.trips and b.trips[0].segments:
			bus = b.trips[0].segments[0].bus
		else:
			Debug.debug('No bus found.', block=b.blockNumber, pause=True)
			bus=-1
		for t in b.trips:
			# Reset on deadhead, if alights, count those by negative
			if t.route == 999:
				if t.segments:
					onboard = -t.segments[0].segmentID[1].alights
			else:
				for seg in t.segments:
					if seg.bus != bus:
						currentActualDay.deviations.append(Deviation(Deviants.BUS_SWITCH, 'Bus-switch mid-block', block=b.blockNumber, trip=t.tripNumber, iStop=seg.segmentID[0].stopID, tStop=seg.segmentID[1].stopID, segment=None, bus=seg.bus, service_date=currentActualDay.date))
					onboard = onboard+seg.segmentID[0].boards-seg.segmentID[0].alights
					seg.onboard=onboard
					seg.feet_per_passenger=onboard*seg.distance
			# count last stop
				if t.segments:
					stop = t.segments[-1].segmentID[1]
					onboard = onboard+stop.boards-stop.alights
	Debug.debug('Finished counting raw onboards!')



def ensure_onboards(onboard):
	return 0 if onboard<0 else onboard
#Inputs: currentActualDay - the day object represeting the current day
#Returns: This function is void, it does not return anything. It just updates the objects in a day
#This function is meant to iterate over a day twice. The first time it does so it adds onboard information
#to each segment based on the previous segments onboards plus the boards at the first stop of the
#segment and minus the alights of the  first stop of the segment. While doing this it does a calculation
# of the total number of boards and alights on each trip. It then iterates through all the trips in
#the day again and if total boards were greater than the number of total alights it proportionally
# reduces the number of boards at each stop and calculates the adjusted onboard number such that
#total boards equals total alights for each trip.
#If the total number of alights is greater than the total number of boards then it reduces the number
#of alights at each stop on the trip proportially so that total boards is equal to the total alights.
def adjustOnboards(currentActualDay):
	Debug.debug('Adjusting onboards')
	# Correct onboard
	for b in currentActualDay.blocks:
		onboard=0

		for t in b.trips:
			# Reset on deadhead, if alights, count those by negative
			if t.route == 999:
				if t.segments:
					onboard = -t.segments[0].segmentID[1].alights

			else:
				for seg in t.segments:
					onboard = onboard+seg.segmentID[0].boards-seg.segmentID[0].alights
					onboard=ensure_onboards(onboard)
					seg.adjustedOnboard=onboard
					seg.feet_per_passenger=onboard*seg.distance
				# count last stop
				if t.segments:
					stop = t.segments[-1].segmentID[1]
					onboard = onboard+stop.boards-stop.alights
