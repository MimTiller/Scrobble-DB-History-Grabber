import os
import requests,  dataset, base64
from time import sleep
from datetime import datetime


db = dataset.connect('sqlite:///songlist.db')
artistfile = open(r"UniqueArtists.txt","a", encoding='utf-8')
songtable = db['crazyguitarman']

artistlist = songtable.distinct('artist')
count = 0
for x in artistlist:
	print (x['artist'])
	artistfile.write(str(x['artist']) + "\n")
	count = count + 1



print (count, " Unique Artists!")
artistfile.close	
