import os
import requests,  dataset, base64
from time import sleep
from datetime import datetime


#connect to database so we can add the songs
db = dataset.connect('sqlite:///songlist.db')
songtable = db['songs']

tagquestion = input('do you want to grab genre tags along with your scrobbler history? (takes about 2x as long) y/n: ')
if tagquestion == 'y':
	gettags = True
else:
	gettags= False



#build the request sent to last.fm
def get_recent_tracks(page):
	# set vars
	base_url = "http://ws.audioscrobbler.com/2.0/"
	#refer to last.fm's API documentation, there are tons of different methods you can use
	method = "user.getrecenttracks"
	user = "crazyguitarman"
	#https://www.last.fm/api/account/create
	key = "e38cc7822bd7476fe4083e36ee69748e"
	#exclude data_format if you want to parse XML instead
	data_format = "json"
	#extended gives the date it was scrobbled, if the user has loved the track, etc. 
	extended = '1'
	limit = '200'
	#check if page number is specified. if not, get the initial data. this is used to find the total # of pages there are, total # of tracks scrobbled, etc.
	if page == None:
		print ("getting # of pages")
		payload = {"method": method,
				   "user": user,
				   "api_key": key,
				   "format": data_format,
					"extended": extended,
					"limit": limit}
	else:
		payload = {"method": method,
				   "user": user,
				   "api_key": key,
				   "format": data_format,
					"extended": extended,
					"limit": limit,
					"page": page}
		print ("getting request for", user)
	#put it all together and use requests to get the json
	r = requests.get(base_url, payload)
	data = r.json()
	print ("http status:", r.status_code)
	return data



def get_tags(artist,track):
	# set vars
	base_url = "http://ws.audioscrobbler.com/2.0/"
	#refer to last.fm's API documentation, there are tons of different methods you can use
	method = "track.getTopTags"
	#https://www.last.fm/api/account/create
	key = "e38cc7822bd7476fe4083e36ee69748e"
	#exclude data_format if you want to parse XML instead
	data_format = "json"
	#extended gives the date it was scrobbled, if the user has loved the track, etc. 
	payload = {"method": method,
			   "artist": artist,
			   "api_key": key,
			   "format": data_format,
				"track": track,
				#autocorrect uses last.fm to find the info you are looking for even if mis-spelled
				"autocorrect": 1}
	tagr = requests.get(base_url, payload)
	tagdata = tagr.json()
	songtags = []
	
	for x in range(0,5):
		try:
			songtags.append(tagdata['toptags']['tag'][x]['name'])
		except:
			pass
	return (songtags)

def get_history():
	data = get_recent_tracks(None)
	pages = data['recenttracks']['@attr']['totalPages']
	songs = data['recenttracks']['@attr']['total']
	print (pages,"pages total", songs,"songs")
	#reason I step it backwards from highest to lowest is because I want the item ID's in the database to match.
	#1st item in database is the oldest song in the scrobble history
	for page in range (int(pages),0,-1):
		data = get_recent_tracks(page)
		print ("printing page {}".format(page))
		items = (data['recenttracks']['track'])
		inlist = int(len(items))
		print(inlist ,"tracks on this page")
		
		#same reason here
		for x  in range(inlist-1, 0,-1):
			#print('checking song', x)
			#pull all the information out that we want from the json data
			tracks = data['recenttracks']['track'][int(x)]
			time= (tracks['date']['uts'])
			timezone_corrected_time= (datetime.fromtimestamp(int(time)).strftime('%Y-%m-%d %H:%M:%S'))
			img = tracks['image'][-1]['#text']
			artistmbid = str(tracks['artist']['mbid'])
			albumbid = str(tracks['album']['mbid'])
			artist = tracks['artist']['name']
			song = tracks['name']
			album = tracks['album']['#text']
			url = tracks['url']

			search = songtable.find_one(time=timezone_corrected_time)
			#find if this song has been added in the past, by looking at its scrobble timestamp
			if search:
				pass
			else:
				if gettags:
					tags = ', '.join(get_tags(artist,song))
				else:
					tags = ''
				songtable.insert(dict(artist=artist, artistmbid=artistmbid, album=album, albumbid=albumbid,img=img, song=song,time=timezone_corrected_time,url=url, tags=tags) )
				print ("NEWSONG: page{0}.song{1}: adding {2} by {3}, scrobbled at {4}".format(page,x,song,artist,timezone_corrected_time))


running = True
while running:
	get_history()
	print('COMPLETED: update at {}'.format(datetime.now()))
# update every 30 minutes 
	sleep(1800)

