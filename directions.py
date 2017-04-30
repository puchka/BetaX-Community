#!/usr/bin/python

'''
Generate polyline from waypoints and render a map
'''

import base64
import googlemaps
from datetime import datetime
import sys

input_file = open(sys.argv[1], 'r')
output_file = open(sys.argv[1].split('.')[0] + '.html', 'w')
res_file = open(sys.argv[1].split('.')[0] + '_res.txt', 'w')

way_points = []

while 1:
    line = input_file.readline()
    if line == '':
        break
    coords = line.split(',')
    way_points.append((float(coords[0]), float(coords[1])))

origin = way_points[0]

destination = way_points[-1]

del way_points[0]
del way_points[-1]

def decode_polyline(polyline_str):
    '''Pass a Google Maps encoded polyline string; returns list of lat/lon pairs'''
    index, lat, lng = 0, 0, 0
    coordinates = []
    changes = {'latitude': 0, 'longitude': 0}

    # Coordinates have variable length when encoded, so just keep
    # track of whether we've hit the end of the string. In each
    # while loop iteration, a single coordinate is decoded.
    while index < len(polyline_str):
        # Gather lat/lon changes, store them in a dictionary to apply them later
        for unit in ['latitude', 'longitude']: 
            shift, result = 0, 0

            while True:
                byte = ord(polyline_str[index]) - 63
                index+=1
                result |= (byte & 0x1f) << shift
                shift += 5
                if not byte >= 0x20:
                    break

            if (result & 1):
                changes[unit] = ~(result >> 1)
            else:
                changes[unit] = (result >> 1)

        lat += changes['latitude']
        lng += changes['longitude']

        coordinates.append((lat / 100000.0, lng / 100000.0))

    return coordinates

gmaps = googlemaps.Client(key='YOUR_API_KEY')

now = datetime.now()

if len(sys.argv) == 3:
	if sys.argv[2] == '-w':
		mode = "walking"
	elif sys.argv[2] == '-b':
		mode = "bicycling"
	elif sys.argv[2] == '-t':
		mode = "transit"
	else:
		mode = "driving"
else:
	mode = 'driving'

directions_result = gmaps.directions(origin,
                                     destination,
                                     waypoints=way_points,
                                     mode=mode,
                                     departure_time=now,
                                     alternatives=False)

result = directions_result[0]['overview_polyline']['points']

a = decode_polyline(result)

output_file.write("""<!DOCTYPE html>
<html>
  <head>
    <meta name=\"viewport\" content=\"initial-scale=1.0, user-scalable=no\">
    <meta charset=\"utf-8\">
    <title>Simple Polylines</title>
    <style>
      html, body {
        height: 100%;
        margin: 0;
        padding: 0;
      }
      #map {
        height: 100%;
      }
    </style>
  </head>
  <body>
    <div id=\"map\"></div>
    <script>

      // This example creates a 2-pixel-wide red polyline showing the path of William
      // Kingsford Smith's first trans-Pacific flight between Oakland, CA, and
      // Brisbane, Australia.

      function initMap() {
        var map = new google.maps.Map(document.getElementById('map'), {
          zoom: 13,
          center: {lat: -18.9, lng: 47.5},
          mapTypeId: google.maps.MapTypeId.TERRAIN
        });

        var flightPlanCoordinates = [""")

i = 0
while i < len(a):
    output_file.write('{lat: ' + str(a[i][0]) + ', lng: ' + str(a[i][1]) + '}')
    res_file.write(str(a[i][0]) + ', ' + str(a[i][1]) + '\n')
    if i == len(a) - 1:
        output_file.write('\n')
    else:
        output_file.write(',\n')
    i = i + 1

output_file.write("""];
        var flightPath = new google.maps.Polyline({
          path: flightPlanCoordinates,
          geodesic: true,
          strokeColor: '#FF0000',
          strokeOpacity: 1.0,
          strokeWeight: 2
        });

        flightPath.setMap(map);
      }
    </script>
    <script async defer
    src=\"https://maps.googleapis.com/maps/api/js?key=YOUR_API_KEY&callback=initMap\">
    </script>
  </body>
</html>""")

input_file.close()
output_file.close()
res_file.close()
