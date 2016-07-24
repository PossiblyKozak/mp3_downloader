#!/usr/bin/env python
# A python to download a song or a list of songs.
# create by Aman Roy
# Creation Date : 18-Feb-2016
# Python version used : - Python 3.4.3+ (ported for python2)
# Please use right spelling to avoid errors
# All licence belongs to authour.

# import all the library used
import re
import urllib
import os
import sys
import threading
import time

class _Const(object):
    def RETRIES():
        return 5
    def DIRECTORY():
        return "Songs"
    def WAIT():
        return 2
    def LOG():
        return "SongLog.txt"

global finishedDownload
finishedDownload = 0
global previouslyDownloaded
previouslyDownloaded = []

# determine python version
CONST = _Const
getSize = os.path.getsize
version = sys.version_info[0]
# set user_input for correct version of python
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
    
    choice = user_input('>>> ')
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
                
# download from a list
def list_download(isHistory):  
    global finishedDownload
    if isHistory:
        fileName = CONST.LOG()        
    else:          
        fileName = user_input('Please enter the File Name With extension (i.e. ".txt")')  # get the file name to be opened
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
        delay = True
        if type(songs) != type(sn):
            if os.path.isfile(CONST.DIRECTORY() + "\%s.mp3" % songs) == False:
                if "www.youtube.com" in songs:
                    thread = linkThread(a, songs, numSong)
                else:
                    thread = nameThread(a, songs, songs, numSong)
            else:
                delay = False
        else:
            if os.path.isfile(CONST.DIRECTORY() + "\%s.mp3" % songs[0].strip()):
                delay = False
            thread = linkThread(songs[0].strip(), songs[1].strip(), numSong)
                   
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
            song = user_input('Enter the song name: ')  # get the song name from user
        if song in previouslyDownloaded:
            downloadLinkOnly = previouslyDownloaded[previouslyDownloaded.index(song)+1]
            if "youtubeinmp3" not in downloadLinkOnly:
                downloadLinkOnly = 'http://www.youtubeinmp3.com/fetch/?video=' + downloadLinkOnly
        succ = True
            # try to get the search result and exit upon error
        if os.path.isfile(CONST.DIRECTORY() + "\%s.mp3" % song) == False:         
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
                    downloadLinkOnly = 'http://www.youtubeinmp3.com/fetch/?video=' + 'http://www.youtube.com/watch?v=' + search_results[0]
                    #downloadLinkOnly = "http://serve01.mp3skull.onl/get?id=" + search_results[0]
                try:
                    print(' - Downloading %s' % song)
                    # code a progress bar for visuals? this way is more portable than wget
                    retrieve(downloadLinkOnly, filename=CONST.DIRECTORY() + '\%s.mp3' % song)
                    cleanup  # clear the cache created by urlretrieve
                    x = True
                    print("The file '%s.mp3' is %sMB" % (song, round(getSize(CONST.DIRECTORY() + "\%s.mp3" % song)/1048576, 1)))
                    if getSize (CONST.DIRECTORY() + "\%s.mp3" % song) < 1048576:
                        print("%s downloaded incorrectly" % song)
                        os.remove(CONST.DIRECTORY() + "\%s.mp3" % song)
                        single_name_download(song, numSongs, downloadLinkOnly, retries + 1)
                        x = False
                        time.sleep(CONST.WAIT()*2)
                except:
                    print(' - Error downloading %s' % song)
                    os.remove(CONST.DIRECTORY() + "\%s.mp3" % song)
                if x:
                    finishedDownload = finishedDownload + 1
                    print("   - %s Download Successful" % song)        
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
            youtubeLink = user_input('>>> ')
        succ = True
        if song == "":
            print("Searching for song Title..." )
            song = video_title(youtubeLink)
            # try to get the search result and exit upon error
        if os.path.isfile(CONST.DIRECTORY() + "\%s.mp3" % song) == False:         
            # generate a download link that can be used to get the audio file using youtube2mp3 API
            x = False                
            if 'http://www.youtubeinmp3.com/fetch/?video=' not in youtubeLink:
                downloadLinkOnly = 'http://www.youtubeinmp3.com/fetch/?video=' + youtubeLink
            else:
                downloadLinkOnly = youtubeLink
            try:
                print(' - Downloading %s' % song)
                # code a progress bar for visuals? this way is more portable than wget
                retrieve(downloadLinkOnly, filename=CONST.DIRECTORY() + '\%s.mp3' % song)
                cleanup  # clear the cache created by urlretrieve
                x = True
                print("The file '%s.mp3' is %sMB" % (song, round(getSize(CONST.DIRECTORY() + "\%s.mp3" % song)/1048576, 1)))
                if getSize (CONST.DIRECTORY() + "\%s.mp3" % song) < 1048576:
                    print("%s downloaded incorrectly" % song)
                    os.remove(CONST.DIRECTORY() + "\%s.mp3" % song)
                    link_download(youtubeLink, retries + 1, song, numSongs)
                    x = False
                    time.sleep(CONST.WAIT()*2)
            except:
                print(' - Error downloading %s' % song)
                os.remove("%s.mp3" % song)
            if x:
                finishedDownload = finishedDownload + 1
                print("   - %s Download Successful" % song)        
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
