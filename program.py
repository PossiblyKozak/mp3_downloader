#!/usr/bin/env python
# A python to download a song or a list of songs.
# create by Aman Roy
# Creation Date : 18-Feb-2016
# Python version used : - Python 3.4.3+
# Please use right spelling to avoid errors
# All licence belongs to authour.

# import all the library used
import re, urllib, os, sys, threading, time

class _Const(object):
    def RETRIES():
        return 5
    def DIRECTORY():
        return "Songs"
    def WAIT():
        return 2
    def LOG():
        return "SongLog.txt"
    def MP3():
        return 0

global finishedDownload
finishedDownload = 0
global previouslyDownloaded
previouslyDownloaded = []

# determine python version
CONST = _Const
getSize = os.path.getsize
user_input = input
import urllib.request
import urllib.parse
urlopen = urllib.request.urlopen
encode = urllib.parse.urlencode
retrieve = urllib.request.urlretrieve
cleanup = urllib.request.urlcleanup()

def updateTop100():
    for x in range(2006,2016):
        if os.path.isfile("Top100-%s.txt" % x) == False:  
            file = open("Top100-%s.txt" % x, "w")    
            webpage = urlopen("http://www.billboard.com/charts/year-end/%s/hot-100-songs" % x).read()            
            songs = str(webpage).split('<h2 class="chart-row__song">')
            for y in range (1,101):
                s2 = songs[y].split('</h2>')
                songName = s2[0].replace("&#039;", "'").lower().replace("&amp;","&").replace("&quot;",'"').split()
                sn = ""
                for songWord in songName:
                    sn = "%s%s " % (sn, songWord.capitalize())
                artist = s2[1].split('"Artist Name">')
                if '</h3>' in artist[0]:
                    artist = artist[0].split('</h3>')[0].split(">")[1].replace('"','')[3:].strip().replace("&#039;", "'").replace(" &amp; ",";").replace("&quot;",'')
                else:
                    artist = artist[1].split("</a>")[0].replace('"','')[3:].strip().replace("&#039;", "'").replace(" &amp; ",";").replace("&quot;",'')
                artist = artist[:len(artist)-2].replace(" Featuring ", ";")
                file.write("%s - %s\n" % (artist, sn.strip()))
            file.close()
        else:
            #print("Top100-%s.txt Already Exists." % x)
            pass
            
    file = open("Top100.txt", "w")    
    webpage = urlopen("http://www.billboard.com/charts/hot-100").read()
    songs = str(webpage).split('<h2 class="chart-row__song">')
    
    for y in range (1,101):
        s2 = songs[y].split('</h2>')
        songName = s2[0].replace("&#039;", "'").lower().replace("&amp;","&").replace("&quot;",'"').split()
        sn = ""
        for songWord in songName:
            sn = "%s%s " % (sn, songWord.capitalize())
        artist = s2[1].split('"Artist Name">')
        if '</h3>' in artist[0]:
            artist = artist[0].split('</h3>')[0].split(">")[1].replace('"','')[3:].strip().replace("&#039;", "'").replace(" &amp; ",";").replace("&quot;",'')
        else:
            artist = artist[1].split("</a>")[0].replace('"','')[3:].strip().replace("&#039;", "'").replace(" &amp; ",";").replace("&quot;",'')
        artist = artist[:len(artist)-2].replace(" Featuring ", ";")
        file.write("%s - %s\n" % (artist, sn.strip()))
    file.close()

# clear the terminal screen
def screen_clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')


# function to retrieve video title from provided link
def video_title(url):
    try:
        webpage = urlopen(url).read()
        title = str(webpage).split('<title>')[1].split('</title>')[0]
    except:
        title = 'Youtube Song'
    
    return title

# the intro to the script
def intro():
    print('''Created by Aman Roy
    FB:- amanroy007
    Email:- royaman8757@gmail.com''')


# find out what the user wants to do
def prompt():
    # userr prompt to ask mode
    print ('''Select A mode  
    [1] Download from direct entry
    [2] Download from a list    
    [3] Download from the youtube link
    [4] Download from a list of youtube links
    [5] Download all of your previously downloaded Songs
    Press any other key from keyboard to exit''')
    
    choice = input('>>> ')
    return str(choice)

class nameThread (threading.Thread):
    def __init__(self, threadID, name, songName, numSong):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.songName = songName
        self.numSong = numSong
    def run(self):
        single_name_download(self.songName, self.numSong, "", 0)
        
class linkThread (threading.Thread):
    def __init__(self, threadID, youtubeLink, numSongs):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.youtubeLink = youtubeLink
        self.numSongs = numSongs
    def run(self):
        link_download(self.youtubeLink, 0, self.threadID, self.numSongs)        
        
class update100Thread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        updateTop100()
                
# download from a list
def list_download(isHistory):  
    global finishedDownload
    if isHistory:
        fileName = CONST.LOG()        
    else:          
        fileName = input('Please enter the File Name With extension (i.e. ".txt")')  # get the file name to be opened
    a = 0
    numSong = 0
    # find the file and set fhand as handler
    try:
        fhand = open(fileName, 'r')
        print ('File opened successfully')
    except IOError:
        print('File does not exist')
        exit(1)      
    sn = []
    screen_clear()
    if isHistory:
        ph = input("Press h to print your history, or press any other characters to continue:")
        if ph == 'h' or ph == 'H':
            screen_clear()
            printHistory()
        else:
            screen_clear()    
    for songs in fhand:        
        if songs.strip() != "":
            if "www.youtube.com" in songs:
                if '@' not in songs:
                    songs = songs.strip()
                else:
                    songs = songs.split('@')      
            else:
                if '@' not in songs:
                    songs = songs.strip().replace('\n','').replace('/','')
                else:
                    songs = songs.split('@')
            numSong = numSong + 1            
            sn.append(songs)
            
    print("There are %s songs in the file provided" % numSong)
    print("The download should take about %s minute(s) and %s seconds" % (((numSong*10+120)//60), ((numSong*10+120)%60)))
    a = input("Press Enter to Begin Download...")
    a = 0        
    screen_clear()
    print("There are %s songs in the file provided" % numSong)
    print("The download should take about %s minute(s) and %s seconds" % (((numSong*10+120)//60), ((numSong*10+120)%60)))
    print("Beginning download...\n")
    
    for songs in sn:
        if "feat." in songs:
            songs = songs.split('(')[0]    
        delay = True
        ts = True
        if type(songs) != type(sn):
            if os.path.isfile(CONST.DIRECTORY() + "\%s.mp3" % songs.strip()) == False:
                songs = songs.strip()
                if "www.youtube.com" in songs:
                    thread = linkThread(a, songs, numSong)
                else:
                    thread = nameThread(a, songs, songs, numSong)
            else:
                print("The song '%s.mp3' is already downloaded" % songs)
                finishedDownload = finishedDownload + 1
                delay = False
                ts = False
        else:
            if os.path.isfile(CONST.DIRECTORY() + "\%s.mp3" % songs[0].strip()):
                print("The song '%s.mp3' is already downloaded" % songs)
                finishedDownload = finishedDownload + 1
                delay = False
                ts = False
            else:
                thread = linkThread(songs[0].strip(), songs[1].strip(), numSong)
        if ts:                   
            thread.start()
        if delay:
            time.sleep(CONST.WAIT())
        a = a + 1
    fhand.close()


# download directly with a song name
def single_name_download(song, numSongs, downloadLinkOnly, retries):
    global finishedDownload
    global previouslyDownloaded
    if retries < CONST.RETRIES():
        if song == "":
            song = input('Enter the song name: ')  # get the song name from user
        if song in previouslyDownloaded:
            print("Song was previously downloaded, using stored URL")
            downloadLinkOnly = previouslyDownloaded[previouslyDownloaded.index(song)+1]
            if CONST.MP3() == 1:
                if "yt-mp3" not in downloadLinkOnly:
                    downloadLinkOnly = "http://www.yt-mp3.com/watch?v=" + downloadLinkOnly
            elif CONST.MP3() == 0:
                if "youtubeinmp3" not in downloadLinkOnly:
                    downloadLinkOnly = "http://www.youtubeinmp3.com/fetch/?video=" + downloadLinkOnly
        succ = True
        if "feat." in song:
            song = song.split('(')[0]
            # try to get the search result and exit upon error
        if os.path.isfile(CONST.DIRECTORY() + "\%s.mp3" % song) == False or song not in previouslyDownloaded:         
            if downloadLinkOnly == "":
                try:
                    print("Searching for %s..." % song)
                    query_string = encode({"search_query" : song})
                    html_content = urlopen("http://www.youtube.com/results?" + query_string)
                    print(" - Found %s." % song)
                    if version == 3:  # if using python 3.x
                        search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
                    else:  # if using python 2.x
                        search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read())
                except:
                    print(' - Network Error Downloading %s' % song) 
                    succ = False
            if succ == True:
                # generate a download link that can be used to get the audio file using youtube2mp3 API
                x = False                
                if downloadLinkOnly == "":
                    if CONST.MP3() == 0:
                        downloadLinkOnly = 'http://www.youtubeinmp3.com/fetch/?video=' + 'http://www.youtube.com/watch?v=' + search_results[0]
                    elif CONST.MP3() == 1:
                        downloadLinkOnly = "http://www.yt-mp3.com/watch?v=" + 'http://www.youtube.com/watch?v=' + search_results[0]                    
                try:
                    print(' - Downloading %s' % song)
                    # code a progress bar for visuals? this way is more portable than wget
                    retrieve(downloadLinkOnly, filename=CONST.DIRECTORY() + '\%s.mp3' % song)
                    cleanup  # clear the cache created by urlretrieve
                    x = True
                    print("The file '%s.mp3' is %sMB" % (song, round(getSize(CONST.DIRECTORY() + "\%s.mp3" % song)/1048576, 1)), end = "")
                    if getSize (CONST.DIRECTORY() + "\%s.mp3" % song) < 1048576:
                        print("- Downloaded incorrectly")
                        os.remove(CONST.DIRECTORY() + "\%s.mp3" % song)
                        single_name_download(song, numSongs, downloadLinkOnly, retries + 1)
                        x = False
                        time.sleep(CONST.WAIT()*2)
                except:
                    print(' - Error downloading %s' % song)
                    single_name_download(song, numSongs, downloadLinkOnly, retries + 1)
                    x = False
                    time.sleep(CONST.WAIT()*2)
                if x:
                    finishedDownload = finishedDownload + 1
                    print(" - Download Successful")        
                    print("%s / %s Songs downloaded" % (finishedDownload, numSongs))
                    if song not in previouslyDownloaded:            
                        file = open(CONST.LOG(), "a")
                        file.write("\n%s@%s" % (song, downloadLinkOnly))
                        file.close()
        else:
            print("The song '%s.mp3 is already downloaded" % song)            
            finishedDownload = finishedDownload + 1
            print("%s / %s Songs downloaded" % (finishedDownload, numSongs))
    else:
        print ("Max retries reached for %s" % song)
        finishedDownload = finishedDownload + 1


# download directly with a youtube link
def link_download(youtubeLink, retries, song, numSongs):
    global finishedDownload    
    global previouslyDownloaded
    if retries < CONST.RETRIES():
        if youtubeLink == "":
            print('Enter full youtube link (case sensitive)')
            print('e.g. - https://www.youtube.com/watch?v=rYEDA3JcQqw')
            youtubeLink = input('>>> ')
        succ = True
        if song == "":
            print("Searching for song Title..." )
            song = video_title(youtubeLink)
            # try to get the search result and exit upon error
        if os.path.isfile(CONST.DIRECTORY() + "\%s.mp3" % song) == False:         
            # generate a download link that can be used to get the audio file using youtube2mp3 API
            x = False                
            if CONST.MP3() == 0:           
                print("using youtubeinmp3")
                if 'youtubeinmp3' not in youtubeLink:
                    downloadLinkOnly = "http://www.youtubeinmp3.com/fetch/?video=" + youtubeLink
                else:
                    downloadLinkOnly = youtubeLink
            elif CONST.MP3() == 1:
                if 'yt-mp3' not in youtubeLink:
                    downloadLinkOnly = "http://www.yt-mp3.com/watch?v=" + youtubeLink
                else:
                    downloadLinkOnly = youtubeLink
            try:
                print(' - Downloading %s' % song)
                # code a progress bar for visuals? this way is more portable than wget
                retrieve(downloadLinkOnly, filename=CONST.DIRECTORY() + '\%s.mp3' % song)
                cleanup  # clear the cache created by urlretrieve
                x = True
                print("The file '%s.mp3' is %sMB" % (song, round(getSize(CONST.DIRECTORY() + "\%s.mp3" % song)/1048576, 1)), end="")
                if getSize (CONST.DIRECTORY() + "\%s.mp3" % song) < 1048576:
                    print(" - Downloaded incorrectly")
                    os.remove(CONST.DIRECTORY() + "\%s.mp3" % song)
                    link_download(youtubeLink, retries + 1, song, numSongs)
                    x = False
                    time.sleep(CONST.WAIT()*2)
            except:
                print(' - Error downloading %s' % song)
                single_name_download(song, numSongs, downloadLinkOnly, retries + 1)
                x = False
                time.sleep(CONST.WAIT()*2)
            if x:
                finishedDownload = finishedDownload + 1
                print(" - Download Successful")        
                print("%s / %s Songs downloaded" % (finishedDownload, numSongs))
                if song in previouslyDownloaded:
                    file = open(CONST.LOG(), "a")
                    file.write("\n%s@%s" % (song, downloadLinkOnly))
                    file.close()
        else:
            print("The song '%s.mp3 is already downloaded" % song)            
            finishedDownload = finishedDownload + 1
            print("%s / %s Songs downloaded" % (finishedDownload, numSongs))
    else:
        print ("Max retries reached for %s" % song)
        finishedDownload = finishedDownload + 1

# program exit
def exit(code):
    sys.exit(code)

def getHistory():
    global previouslyDownloaded 
    songLog = open(CONST.LOG(), 'r')
    for songLink in songLog:
        if songLink.strip() != "": 
            sl = songLink.split('@')
            previouslyDownloaded.append(sl[0].strip())
            previouslyDownloaded.append(sl[1].strip())
        
def printHistory():
    global previouslyDownloaded
    for titles in previouslyDownloaded:
        if 'www.youtube.com' not in titles:
            print(titles)
    print("")
        

# main guts of the program
def main():    
    finishedDownload = 0
    thread = update100Thread()
    thread.start()    
    if not os.path.exists(CONST.DIRECTORY()):
        os.makedirs(CONST.DIRECTORY())
    if not os.path.exists(CONST.LOG()):
        file = open(CONST.LOG(), "w")
        file.close()
    try:
        screen_clear()
        getHistory()
        choice = prompt()        
        try:
            if choice == '1':
                single_name_download("", 1, "", 0)                
            elif choice == '2':                
                list_download(False)
            elif choice == '3':
                link_download("", 0, "", 1)
            elif choice == '4':
                list_download(False)
            elif choice == '5':                
                list_download(True)
        except NameError:
            exit(1)
    except KeyboardInterrupt:
        exit(1)

if __name__ == '__main__':
    main()  # run the main program
    exit(0)  # exit the program
