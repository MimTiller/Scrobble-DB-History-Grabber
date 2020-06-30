
import dataset
import sys, time
sys.path.insert(1,'C:/taskscheduler/utilities')
from emailer import email
from htmltable import tablemaker


db = dataset.connect('sqlite:///C:/PythonProjects/Personal/Scrobble DB History Grabber/songlist.db')
username = "crazyguitarman"
table = db[username]
counts = db['plays-{}'.format(username)]
results = table.distinct('song','artist')

uniquecount = 0 
for result in results:
	uniquecount += 1
	artist = result["artist"]
	song = result["song"]
	songid = artist + " - " + song
	search_plays = table.count(artist = artist, song = song)
	if search_plays == 1: 
		pass
	else:
		data = dict(count = search_plays, songid=songid)
		print ("adding to counts, {} plays: {}".format(search_plays,songid))
		counts.upsert(data, ["songid"])
		print (uniquecount)


