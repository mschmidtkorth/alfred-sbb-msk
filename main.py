# encoding: utf-8

from __future__ import unicode_literals
import sys
import datetime
from workflow import Workflow, ICON_CLOCK, ICON_WARNING, web


def main(wf):
	log.debug('Test 2')
	
	if len(wf.args):
		query = wf.args[0]
	else:
		query = None
	stations = query.replace(', ', ',').split(' ')
	if len(stations) == 2:
		fromStation = wf.decode(stations[0].encode('utf-8'))
		toStation = wf.decode(stations[1].encode('utf-8'))
		
		try:
			url = 'http://transport.opendata.ch/v1/connections?from=' + fromStation + '&to=' + toStation + '&limit=16'
			r = web.get(url)
			log.debug('Response: ' + str(r.json()))
			r.raise_for_status()
		except:
			log.debug('Error on HTTP request')
			wf.add_item(title = 'Unable to receive timetables.', subtitle = 'Please try again later.', valid = False, icon = ICON_WARNING)
			wf.send_feedback()
			exit()
		
		result = r.json()
		connections = result['connections']
		
		for connection in connections:
			strVehicles = ' \U0001F686' + ', '.join(connection['products'])
			strTransfers = ' \U0001F500 ' + str(connection['transfers']) if str(connection['transfers']) + ' transfer' != '' else ''
			departureTime = datetime.datetime.strptime(str(connection['from']['departure'])[:-8], "%Y-%m-%dT%H:%M")
			arrivalTime = datetime.datetime.strptime(str(connection['to']['arrival'][:-8]), "%Y-%m-%dT%H:%M")
			arrivalUnix = connection['to']['arrivalTimestamp']
			timedelta = arrivalTime - departureTime
			if str(departureTime)[:11] == str(arrivalTime)[:11]:
				arrivalTime = str(arrivalTime)
				arrivalTime = arrivalTime[11:]
			wf.add_item(title = '[' + str(timedelta) + '] ' + str(departureTime) + ' to ' + str(arrivalTime), subtitle = connection['from']['station']['name'] + ' to ' + connection['to']['station']['name'] + strVehicles + strTransfers, uid = str(arrivalUnix), valid = False, modifier_subtitles = {"alt": strVehicles}, icon = ICON_CLOCK)
		wf.send_feedback()


if __name__ == "__main__":
	wf = Workflow()
	log = wf.logger
	sys.exit(wf.run(main))
