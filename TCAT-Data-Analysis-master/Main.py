#This file is responsible for establishing a connection to the SQL database  and the contorl flow of
#the program.
#This file can be run using the command line by navigating to the folder it is in, currently this is
#Adam\Documents then issuing the command

#	python main.py 2018 08 01 2018 08 02 [[-d,--debug,] -sd,-jsd]

#The 6 integer arguements passed are necessary, the format must be yyyy mm dd yyyy mm dd
#they specify the date range to be processed and begin on the first date and process every day up
#until but not including the last date. This means that the above command does not look at 2017-11-15.

import sys
from lib.TCAT_Segment_Library.Parse import parseActual, display, parseScheduled
from lib.TCAT_Segment_Library.Classes import Day, Block, Trip, Segment, Stop, Deviants
from lib.TCAT_Segment_Library.Deviations import report, checkSequence
from lib.TCAT_Segment_Library import Debug, Utility
from Compare import compareDay, compareBlocks, compareTrips
from Onboard import adjustOnboards, fix_boards_alights, count_raw_onboards

readConnection = Utility.getReadConnection('tcat_python', 'MdPlQz1GxpP6vUkL3FW7')

writeConnection = Utility.getWriteConnection('tcat_python', 'MdPlQz1GxpP6vUkL3FW7')

def post_process(actualDay, f, scheduledDay=None):
	if scheduledDay:
		return f(actualDay, scheduledDay=scheduledDay)
	else:
		f(actualDay)
def post_processes(actualDay, fs, scheduledDay=None):
	for f in fs:
		post_process(actualDay, f, scheduledDay)

#This is the function that takes the arguements passed into the file, creates two date objects for
#them and then uses the daterange function to iterrate through every day between them and call the
#createDays funtion.
#It then compares the actualDay object and the scheduledDay object using compareDay(),
#Adds onboard and adjusted Onboard information to the updated actualDay using adjustedOnbboards(),
#Writes the information from the actualDay to the Segments table using writeToSegments(),
#Looks for deviations in the trip using checkSequece(), and generates a breif report of the
#deviations using report(). After processing all days it closes the connection to the table.
def main():
	#7 because technically first argument is name of file.
	if len(sys.argv)<7:
		print('Please enter 6 arguments! (year month date year month date)')
	y1 = int(sys.argv[1])
	m1 = int(sys.argv[2])
	d1 = int(sys.argv[3])

	y2 = int(sys.argv[4])
	m2 = int(sys.argv[5])
	d2 = int(sys.argv[6])
	if len(sys.argv)>6:
		specific_block = False
		block=-1
		for s in sys.argv[6:]:
			if specific_block and s.isdigit():
				block = s
				specific_block = False
			if s=='-d' or s=='--debug':
				Debug.dFlag=True
			if s=='-dd' or s=='--develoepr-debug':
				Debug.sdFlag=True
				Debug.dFlag=True
			if s=='-jdd' or s=='--just-developer-debug':
				Debug.sdFlag=True
			if s=='-b' or s=='--block':
				specific_block = True
	if Debug.dFlag:
		print('Debug mode is [ON] OFF')
	else:
		print('Debug mode is ON [OFF]')
	if Debug.sdFlag:
		print('Developer debug mode activated!')
	start_date = Utility.getDate(y1, m1, d1)
	end_date = Utility.getDate(y2, m2, d2)
	Debug.debug('Connecting to the database...')
	Debug.debug('Connected!')
	Debug.debug('Starting comparison of these days.', start_date=start_date, end_date=end_date)
	#Process dates
	for single_date in Utility.daterange(start_date, end_date):
		day= single_date.strftime('%Y-%m-%d')
		if specific_block:
			Days=Utility.createDays(day, readConnection, block=block)
		else:
			Days=Utility.createDays(day, readConnection)
		actualDay = Days[0]
		scheduledDay = Days[1]
		# Debug.dev_debug('Here are the days:', actualDay=Days[0], pause=True)
		compareDay(actualDay,scheduledDay)
		# Raw onboard count
		Debug.debug('Post Processing initiated.')
		post_processes(actualDay, (fix_boards_alights, count_raw_onboards, adjustOnboards))
		# countRawOnboards(actualDay)
		# adjustOnboards(actualDay)
		Debug.debug('Writing to segments table.')
		Utility.writeToSegments(actualDay, writeConnection)
		Debug.debug('Writing to deviations table.')
		Utility.writeToDeviations(actualDay, writeConnection)
		Debug.check(actualDay, scheduledDay)
		# Debug.debug('Checking sequence')
		# checkSequence(actualDay)
		Debug.review(actualDay, scheduledDay)
		report(actualDay)
	readConnection.close()
	Debug.debug('Done!')

if __name__=='__main__':
	main()
