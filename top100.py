# import all the library used
import re
import urllib
import os
import sys
import threading
import time

version = sys.version_info[0]
if version == 2:  # python 2.x
    user_input = raw_input
    import urllib2
    urlopen = urllib2.urlopen  # open a url
    encode = urllib.urlencode  # encode a search line
    retrieve = urllib.urlretrieve  # retrieve url info
    cleanup = urllib.urlcleanup()  # cleanup url cache
else:  # python 3.x
    user_input = input
    import urllib.request
    import urllib.parse
    urlopen = urllib.request.urlopen
    encode = urllib.parse.urlencode
    retrieve = urllib.request.urlretrieve
    cleanup = urllib.request.urlcleanup()
    


for x in range(2006,2016):
    if os.path.isfile("Top100-%s.txt" % x) == False:  
        file = open("Top100-%s.txt" % x, "w")    
        webpage = urlopen("http://www.billboard.com/charts/year-end/%s/hot-100-songs" % x).read()
        print('\n Top 100 for %s\n' % x)
        songs = str(webpage).split('<h2 class="chart-row__song">')
        for y in range (1,101):
            s2 = songs[y].split('</h2>')
            songName = s2[0].replace("&#039;", "'").lower().replace("&amp;","&").replace("&quot;",'"').split()
            sn = ""
            for songWord in songName:
                sn = "%s%s " % (sn, songWord.capitalize())
            print(sn.strip(), end=" - ")
            artist = s2[1].split('"Artist Name">')
            if '</h3>' in artist[0]:
                artist = artist[0].split('</h3>')[0].split(">")[1].replace('"','')[3:].strip().replace("&#039;", "'").replace("&amp;","&").replace("&quot;",'"')
            else:
                artist = artist[1].split("</a>")[0].replace('"','')[3:].strip().replace("&#039;", "'").replace("&amp;","&").replace("&quot;",'"')
            print(artist[:len(artist)-2])
            file.write("%s - %s\n" % (sn.strip(), artist[:len(artist)-2]))
        file.close()
    else:
        print("Top100-%s.txt Already Exists." % x)
   
if os.path.isfile("Top100-%s.txt" % x) == False:      
    file = open("Top100.txt", "w")    
    webpage = urlopen("http://www.billboard.com/charts/hot-100").read()
    print('\n Top 100 Right Now\n')
    songs = str(webpage).split('<h2 class="chart-row__song">')
    for y in range (1,101):
        s2 = songs[y].split('</h2>')
        songName = s2[0].replace("&#039;", "'").lower().replace("&amp;","&").replace("&quot;",'"').split()
        sn = ""
        for songWord in songName:
            sn = "%s%s " % (sn, songWord.capitalize())
        print(sn.strip(), end=" - ")
        artist = s2[1].split('"Artist Name">')
        if '</h3>' in artist[0]:
            artist = artist[0].split('</h3>')[0].split(">")[1].replace('"','')[3:].strip().replace("&#039;", "'").replace("&amp;","&").replace("&quot;",'"')
        else:
            artist = artist[1].split("</a>")[0].replace('"','')[3:].strip().replace("&#039;", "'").replace("&amp;","&").replace("&quot;",'"')
        print(artist[:len(artist)-2])
        file.write("%s - %s\n" % (sn.strip(), artist[:len(artist)-2]))
    file.close()
else:
    print("Top100.txt Already Exists.")
