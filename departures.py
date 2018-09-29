from datetime import date, datetime
import partridge as ptg
import json
import hashlib

path = 'gtfsfp20182018-09-19.zip'

print("Loading GTFS")
service_ids_by_date = ptg.read_service_ids_by_date(path)

tree = {}
dates = {"LUN": date(2018, 10, 1), "VEN": date(2018, 10, 5), "SAM": date(2018, 10, 6), "DIM": date(2018, 10, 7)}
for (day, currentDate) in dates.items():
	print("Loading " + day)
	service_ids = service_ids_by_date[currentDate]

	feed = ptg.get_filtered_feed(path, {
		'trips.txt': {
			'service_id': service_ids
	    },
		'agency.txt': {
			'agency_id': '881'
		}
	})

	trips = {}
	stop_times = feed.stop_times.values
	for time in stop_times:
		if time[0] not in trips:
			trips[time[0]] = {"passList": []}
		hours = int(time[2] // 3600)
		if hours >= 24:
			hours -= 24
		minutes = int((time[2] % 3600) // 60)
		seconds = int(time[2] % 60)
		trips[time[0]]["passList"].append((time[3], datetime.combine(currentDate, datetime.min.time()).replace(hour=hours, minute=minutes, second=seconds).isoformat(), time[4]))

	for (tripId, trip) in trips.items():
		trip["passList"] = sorted(trip["passList"], key=lambda departure: departure[2])
		trip["destination"] = trip["passList"][-1][0]
		trip["lineCode"] = tripId.split("-")[1]

	stops = {}
	for (tripId, trip) in trips.items():
		for stop in trip["passList"]:
			if stop[0] not in stops:
				stops[stop[0]] = []
			stops[stop[0]].append({"direction": trip["destination"], "line": trip["lineCode"], "timestamp": stop[1], "tripId": tripId})
	for (key, stop) in stops.items():
		tree[day + key + ".json"] = json.dumps({"departures": stop}, ensure_ascii=False)

print("Saving...")

file = open("departures.json", "w")
file.write(json.dumps(tree, sort_keys=True, indent=4, ensure_ascii=False))
file.close()

file = open("departures.json.md5", "w")
file.write(hashlib.md5(json.dumps(tree, sort_keys=True, indent=4, ensure_ascii=False).encode('utf-8')).hexdigest())
file.close()