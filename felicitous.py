#!/usr/bin/python
from __future__ import division
import math, random, sys, os, datetime, xml.dom.minidom, urllib, optparse
# non standard modules, both avaliable in easy_install
import ephem		# http://rhodesmill.org/pyephem/
import flickrapi	# http://stuvel.eu/projects/flickrapi

description = """Set an interesting desktop background from flickr based on time of day and current weather for your location."""

default_yahoo_location_parameter = "UKXX0028"	# Cambridge, UK
downloads = os.path.expanduser("~/twilight")	# directory in which save backgrounds

min_width = 1280	# reject photos narrower than this
min_ratio = 4/3		# reject photos thinner than this

parser = optparse.OptionParser(description=description,version="%prog 0.1")

parser.add_option("-l","--location",action="store",type="string",dest="yahoo_location_parameter",default=default_yahoo_location_parameter,help="Yahoo weather location parameter")
parser.add_option("-w","--weather",action="store",type="string",dest="weather",default=None,help="force weather")
parser.add_option("-t","--time-of-day",action="store",type="string",dest="time_of_day",default=None,help="force time of day")
parser.add_option("-n","--nilpotent",action="store_false",default=True,dest="active",help="don't download anything, just print URLs")

(options, args) = parser.parse_args()

def set_gnome_background(x):
	import gconf
	client = gconf.client_get_default()
	client.set_string ("/desktop/gnome/background/picture_filename",x)		# doesn't work in crontab :(
	#client.set_string ("/desktop/gnome/background/picture_options","scaled")

tags = []

yahoo_weather_url = "http://weather.yahooapis.com/forecastrss?p=%s&u=c" % options.yahoo_location_parameter

dom = xml.dom.minidom.parse(urllib.urlopen(yahoo_weather_url))

weather_title = dom.getElementsByTagName("title")[2].firstChild.data
weather_description = dom.getElementsByTagName("yweather:condition")[0].getAttribute("text").lower()
weather_latitude = str(dom.getElementsByTagName("geo:lat")[0].firstChild.data)
weather_longitude =  str(dom.getElementsByTagName("geo:long")[0].firstChild.data)

if not options.weather:
	print "%s: %s" % (weather_title, weather_description)

	# http://developer.yahoo.com/weather/#codes
	possible_weathers = ["tornado", "hurricane", "snow", "hail", "storm", "fog", "dust", "haze", "sunny", "rain", "windy", "cloudy"]
	# with priority, rarest first

	for x in possible_weathers:
		if x in weather_description and "partly" not in weather_description:
			options.weather = x
			break
	else:
		print "weather '%s' does not correspond to any familiar weather tags below" % weather_description
		print possible_weathers

if options.weather:
	print "using '%s' for weather tag" % options.weather
	tags.append(options.weather)

observer = ephem.Observer()
observer.lat = weather_latitude
observer.long= weather_longitude
observer.elevation = 0		# unlikely to be negative, not significant

observer.date = ephem.now()
# all times in ephem are UTC

# calculate time of day
times_of_day = [ "night", "dawn", "sunrise", "morning", "evening", "sunset", "dusk"]

# twilight? day?
# twilight does not distinguish between dawn and dusk, day is indescriptive

def calculate_time_of_day(observer):
	print
	print "latitude, longitude, elevation: %s, %s, %s" % (observer.lat, observer.long, observer.elevation)
	print "time: %s UTC" % observer.date

	sun = ephem.Sun()
	sun.compute(observer)

	print "the sun is at altitude %s " % sun.alt

	if sun.alt >= 0:
		# the sun is above the horizon, ie. day

		sunrise =  observer.previous_rising(sun).datetime()
		sunset = observer.next_setting(sun).datetime()

		noon = sunrise + (sunset - sunrise) // 2

		sun.compute(observer)	# important!

		if observer.date.datetime() < noon:
			# the sun is rising in the sky
			if sun.alt < math.pi / 15:
				return "sunrise"			
			elif sun.alt < math.pi / 4:
				return "morning"

		else:
			# the sun is setting in the sky
			if sun.alt < math.pi / 15:
				return "sunset"	
			elif sun.alt < math.pi / 6:
				return "evening"

		return "day"

	elif sun.alt < 0:
		# the sun is beneath the horizon, ie. night
		
		sunrise =  observer.next_rising(sun).datetime()
		sunset = observer.previous_setting(sun).datetime()

		midnight = sunset + (sunrise - sunset) // 2

		sun.compute(observer)	# important!

		if sun.alt > - math.pi/15:
			# 12 degrees for dawn / dusk
			if observer.date.datetime() < midnight:
				# we are between sunset and midnight
				return "dusk"
			else:
				# we are between midnight and sunrise
				return "dawn"

		return "night"

if not options.time_of_day:
	options.time_of_day = calculate_time_of_day(observer)

print "the time of day is: %s" % options.time_of_day

if options.time_of_day != "day":
	tags.append(options.time_of_day)

# check for full moon

def calculate_interesting_moon(observer):
	moon = ephem.Moon()
	moon.compute(observer)

	if moon.alt > 0 and moon.phase / 100 > (1 - 1/14):
		print "Tonight is a full moon (howl)"
		return "full moon"

moon_tag = calculate_interesting_moon(observer)
if moon_tag:
	tags.append(moon_tag)

#print "The tags we have collected are: %s" % ", ".join(tags)

tags_argument = ",".join([x.replace(" ","") for x in tags])

key = "54771e884f7535711008bb8b523f5c5d"
secret = "12cb2f6d39e0a1d7"

flickr =  flickrapi.FlickrAPI(key,secret=secret,format="rest")

response = flickr.photos_search(tags=tags_argument,tag_mode="all",sort="interestingness-desc",content_type=1,media="photos",extras="o_dims",per_page="500")
dom = xml.dom.minidom.parseString(response)

assert dom.getElementsByTagName("rsp")[0].getAttribute("stat") == "ok" , "flickr request failed :("

choices = []
for n,photo in enumerate(dom.getElementsByTagName("photo")):
	height= photo.getAttribute("o_height")
	width = photo.getAttribute("o_width")
	if height and width:
		# photo has original for download :)
		height = int(height)
		width = int(width)

		if width >= min_width and width/height >= min_ratio:
			choices.append(photo)

if not choices:
	print "no photos of satisfactory size :("
	sys.exit()

for x in choices:
	# we favour more interesting photos expontentially, but introduce randomness
	if random.random() < 1/8:
		choice = x
		break
else:
	choice = choices[0]

photo_id = choice.getAttribute("id")
response = flickr.photos_getSizes(photo_id=photo_id)
dom = xml.dom.minidom.parseString(response)
orig_url = dom.getElementsByTagName("size")[-1].getAttribute("source")

response = flickr.photos_getInfo(photo_id=photo_id)
dom = xml.dom.minidom.parseString(response)
title = dom.getElementsByTagName("title")[0].firstChild.data
user = dom.getElementsByTagName("owner")[0].getAttribute("username")
url = dom.getElementsByTagName("url")[0].firstChild.data

print
print "'%s' by '%s'" % (title,user)
print url

dest = os.path.join(downloads,os.path.basename(orig_url))

if options.active:
	print
	if not os.path.exists(dest):
		print "Downloading %s to %s" % (orig_url, dest)
		urllib.urlretrieve(orig_url,dest)

	set_gnome_background(dest)

	print "Voila!"

