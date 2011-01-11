#!/usr/bin/python
import re

regexps = [
	r"(\d+)_[\dabcdef]+_.\.jpe?g$",		# for standard flickr filenames like 1900328588_27ec773ab1_o.jpg
	r"\.?(\d+)\.jpe?g$",			# for title.id.jpg filenames like "Tuareg Libya.1900328588.jpg"
	r"^(\d+)(.jpe?g)?$"			# id(.jpg)
	]

patterns = [re.compile(r) for r in regexps]

def uid(x):
	"""Returns the uid in string x, or False if none found""" 
	for p in patterns:
		test = re.search(p,x)
		if test:
			return int(test.groups()[0])
	return False

def url(uid):
	return "http://www.flickr.com/photo.gne?id=%s" % uid

def get_gnome_background():
	import gconf
	client = gconf.client_get_default()
	return client.get_string ("/desktop/gnome/background/picture_filename")

if __name__ == "__main__":
	import optparse
	description = "Find the FILE(s) on flickr, print URL of its friendly photo page and open it in a web browser."
	usage = "usage: %prog [options] FILE(s)"

	parser = optparse.OptionParser(usage=usage,description=description,version="%prog 0.3")

	parser.add_option("-n","--no-browser",action="store_false",dest="use_browser",default=True,help="Don't open the photos in browser")
	parser.add_option("-q","--quiet",action="store_true",dest="quiet",default=False,help="Don't print list of failures")
	parser.add_option("-g","--gnome",action="store_true",dest="examine_gnome",default=False,help="Examine current gnome background")

	(options, args) = parser.parse_args()

	if options.use_browser:
		import webbrowser

	if options.examine_gnome:
		x = get_gnome_background()
		print x
		args.append(x)

	if not args and not options.examine_gnome:
		parser.print_usage()

	failures = []

	for x in args:
		u = uid(x)
		if u:
			link = url(u)
			print link
			if options.use_browser:
				webbrowser.open_new(link)
		else:
			failures.append(x)

	if failures and not options.quiet:
		print "The following filenames do not contain a flickr id:"
		print failures


