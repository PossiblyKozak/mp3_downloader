#!/usr/bin/env python
# A python to download a song or a list of songs.
# create by Aman Roy
# Creation Date : 18-Feb-2016
# Python version used : - Python 3.4.3+
# All licence belongs to authour.

# import all the libraries used
import re, urllib, os, sys, threading, time, urllib.request, urllib.parse, glob, youtube_dl, spotilib, win32gui, mutagen
from mutagen.easyid3 import EasyID3

class _Const(object):                       # Creation of a constant class, so that mass changes in the code can be done. These can now be changed from the settings in the client
    RETRIES = 5                 # Total number of retries the program undergoes before giving up 
    DIRECTORY = "Songs"         # The subdirectory name in which all the downloaded mp3's will reside.
    WAIT = 4                    # Seconds of delay between the initialization of seperate threads.
    LOG = "SongLog.txt"         # The name of the Log file in whichh all songs will have their url's saved.
    MP3 = 1                     # Determining the website to use when downloadin the song. Sometimes one will be down.
    ERROR = "Errors.txt"        # Saves the Song Name and the attempted download URL in this file
    SONGLISTDIR = "SongLists"   # The directory in which the program will look for .txt files constining song names
    SUBDIR = ""                 # The subdirectory where the songs are currently being saved within the DIRECTORY folder
                 
class update100Thread (threading.Thread):   # So that the updating of the top100's is done in the background
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        updateTop100()

#Renaming a couple of things for ease of use (And capitalized constants)
CONST = _Const 
getSize = os.path.getsize
user_input = input
urlopen = urllib.request.urlopen
encode = urllib.parse.urlencode
retrieve = urllib.request.urlretrieve
cleanup = urllib.request.urlcleanup()

global finishedDownload      # Number of songs which are currently finished downloading 
finishedDownload = 0
global numberOfSongsGlobal      # The number of songs in the list of songs to be downloaded
numberOfSongsGlobal = 0
global previouslyDownloaded     # An array of names of sings which have already been downloaded
previouslyDownloaded = []
global downloadErrors           # Any errors which occur in the download process are added to this array
downloadErrors = []
global totalFileDownloadSize    # total filesize (in Mb) downloaded in this batch of files
totalFileDownloadSize = 0

class bcolors:                  #Creation of a color class for the text in the console
    RED = '\x1b[0;31;40m'
    GREEN = '\x1b[0;32;40m'
    YELLOW = '\x1b[0;33;40m'
    BLUE = '\x1b[0;34;40m'
    PINK = '\x1b[0;35;40m'
    AQUA = '\x1b[0;36;40m'
    WHITE = '\x1b[0;37;40m'

def changeSettings():
    staySettings = True # Flag for staying on the settings screen which is only turned off if the letter x is entered 
    while staySettings:
        screen_clear()
        print("Settings:")
        print(" [0] Number of Retries : %s" % CONST.RETRIES)
        print(" [1] Default Download Directory : %s" % CONST.DIRECTORY)
        print(" [2] Seconds of delay between downloads : %s" % CONST.WAIT)
        print(" [3] Previous song log file : %s" % CONST.LOG)
        print(" [4] Error file name : %s" % CONST.ERROR)
        print(" [5] Folder for the text files : %s" % CONST.SONGLISTDIR)
        print(" [x] Exit to main menu")
        setIndex = input("Enter number of setting you want to change\n>>> ")
        if setIndex == 'x' or setIndex == 'X':  
            staySettings = False
            setSettings()
        elif str.isdigit(setIndex) and int(setIndex) < 6:   # if the str.isdigit wasn't there, the program would crash if a non-integer and not 'x' was entered
            newValue = input("Enter the new value\n>>> ")
            if int(setIndex) == 0:
                CONST.RETRIES = int(newValue)
            elif int(setIndex) == 1:
                os.rename(CONST.DIRECTORY, newValue)
                CONST.DIRECTORY = newValue
            elif int(setIndex) == 2:
                CONST.WAIT = int(newValue)
            elif int(setIndex) == 3:
                os.rename(CONST.LOG, isTextFile(newValue))
                CONST.LOG = isTextFile(newValue)
            elif int(setIndex) == 4:
                os.rename(CONST.ERROR, isTextFile(newValue))
                CONST.ERROR = isTextFile(newValue)
            elif int(setIndex) == 5:
                os.rename(CONST.SONGLISTDIR, newValue)
                CONST.SONGLISTDIR = newValue        
    
def isTextFile(inValue):                    # When setting the settings, some of the values have to be .txt files, this makes sure that file type is associated
    if ".txt" not in inValue:
        inValue = inValue + ".txt"   
    return inValue
    
class Settings():
    def sGet():
        file = open("Settings.txt", "r")
        sett = file.readline()
        setlist = sett.split(',')
        CONST.RETRIES = int(setlist[0].strip())
        CONST.DIRECTORY = setlist[1].strip()
        CONST.WAIT = int(setlist[2].strip())
        CONST.LOG = setlist[3].strip()
        CONST.ERROR = setlist[4].strip()
        CONST.SONGLISTDIR = setlist[5].strip()   
    
    def sSet():
        file = open("Settings.txt", "w")
        file.write("%s, %s, %s, %s, %s, %s" % (str(CONST.RETRIES), CONST.DIRECTORY, str(CONST.WAIT), CONST.LOG, CONST.ERROR, CONST.SONGLISTDIR))

    def sPrint():
        print(CONST.RETRIES)
        print(CONST.DIRECTORY)
        print(CONST.WAIT)
        print(CONST.LOG)
        print(CONST.ERROR)
        print(CONST.SONGLISTDIR)

def updateTop100():                         # Creates the top 100s and puts them in the song list directory
    for x in range(2006,2018): 
        file = open(CONST.SONGLISTDIR + "/%s.txt" % x, "w")    
        webpage = urlopen("http://www.billboard.com/charts/year-end/%s/hot-100-songs" % x).read()         # The Bilboard webiste simply changes the year in the URL in order to switch between years in the top100 lists.    
        songs = str(webpage).split('ye-chart-item__title">')                                              # The furthest it goes back is 2006
        for y in range (1,len(songs)):
            ns = songs[y].split('\\n')                
            file.write("%s - %s\n" % (removeSpecialCaharacters(ns[1]), removeSpecialCaharacters(ns[4])))
        file.close()

def screen_clear():                         # clear the terminal screen
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def removeSpecialCaharacters(inputString):  # Because this HTML parsing is shady at best
    return inputString.strip().replace("&#039;", "'").replace(" &amp; ",";").replace("&quot;",'') 

def generatePlaylist():  
    file = open("Settings.txt", "r")
    sett = file.readline()
    setlist = sett.split(',')
    bDir = os.getcwd() + "\\" + CONST.DIRECTORY
    od = os.getcwd()

    dir = input("Directory:")
    plName = input("Name:")

    print("Generating Playlist....")
    print(bDir + "\\" + dir)
    for (path, subdirs, files) in os.walk(bDir + "\\" + dir):    
        os.chdir(path)
        if glob.glob("*.mp3") != []:
            _m3u = open(bDir + "\\" + dir + "\\" + plName + ".m3u", "w")
            for song in glob.glob("*.mp3"):
                _m3u.write(song + "\n")
            _m3u.close()
    input("Playlist Generated at "+ (bDir + "\\" + dir + "\\" + plName + ".m3u") + "\nPress Enter to Continue")
    os.chdir(od)

    # function to retrieve video title from provided link

def video_title(url):
    try:
        webpage = urlopen(url).read()
        title = removeSpecialCaharacters(str(webpage).split('<title>')[1].split('</title>')[0])
    except:
        title = 'Youtube Song'
    return title

def print_format_table():                   # For colour purposes
    """
    prints table of formatted text format options
    """
    for style in range(8):
        for fg in range(30,38):
            s1 = ''
            for bg in range(40,48):
                format = ';'.join([str(style), str(fg), str(bg)])
                s1 += '\x1b[%sm %s \x1b[0m' % (format, format)
            print (s1)
        print ('\n')

def prompt():
    print (bcolors.WHITE + '''Select A mode  
    [1] Download from direct entry
    [2] Download from a list
    [3] Download all of your previously downloaded Songs
    [4] List all previously downloaded songs
    [5] Show count of all songs currently in the downloaded directory
    [6] Youtube Playlist Downloader 
    [7] Search History
    [8] Generate Playlist
    [s] Change settings
    Press any other key from keyboard to exit''')
    choice = input('>>> ')
    return str(choice)

def youTubePlaylistDownloader():            # Asks for a url for a youtube playlist, parses out the videos from said playlist and adds them to a text file that you name
    url = input("Enter the youtube playlist url: ")
    fileName = input("Enter a file Name: ")
    webpage = urlopen(url).read()

    videos = str(webpage).split('data-video-id="')
    file = open(CONST.SONGLISTDIR + "\%s.txt" % fileName, "w")
    for url in videos[1:len(videos)-1]:   
        rule = url.split('"')
        title = url.split('data-title="')[1].split('"')[0].replace('[Copyright Free]','').replace('&amp;', '&').replace("\xe2\x80\x93", "-").replace("\xc3\xbc","u").replace("&#39;","'").replace("\xe2\x80\x93", "'")
        finalURL = "https://www.youtube.com/watch?v=" + rule[0]
        printed = "%s@%s\n" %(title.strip(),finalURL)
        file.write(printed)
    file.close()
                
def list_download(isHistory, sn):           # Download from a list
    global finishedDownload
    global numberOfSongsGlobal
    numberOfSongsGlobal = 1 # so that the main menu doesn't override the screen before the directory can be chosen
    a = 0
    numSong = 0
    if (len(sn) == 0):
        fileUnOpened = True
        while fileUnOpened:
            if isHistory:
                fileName = CONST.LOG()  # if the download list is already defined, then dont bother asking for a file name.        
            else:          
                fileName = input('Please enter the name of the file in the "%s" folder: ' % CONST.SONGLISTDIR)  # get the file name to be opened
            try:
                fhand = open(CONST.SONGLISTDIR + ("\%s" % fileName) + ".txt", 'r')
                print ('File opened successfully')
                fileUnOpened = False
            except IOError:
                print('File does not exist\n')
                # loops until you enter a valid file                
        screen_clear()

        if isHistory:
            ph = input("Press h to print your history, or press any other characters to continue:")     #Make the history visible so you can know what you're getting into
            if ph == 'h' or ph == 'H':
                screen_clear()
                printHistory("")
            else:
                screen_clear()   
        
        for songs in fhand:        
            if songs.strip() != "":
                if "www.youtube.com" in songs: # This happens in the history as well as when getting list of youtube links. 
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
            
    numSong = len(sn)
    numberOfSongsGlobal = numSong
    print(bcolors.YELLOW + "There are %s songs in the file provided" % numSong)
    print("The download should take about %s minute(s) and %s seconds" % (((numSong*10+120)//60), ((numSong*10+120)%60)))
    if input(bcolors.WHITE + "Would you like to create a subfolder for this group of songs? (y/n)\n>>> ") == "y":
        subFolder = input("Enter the name of the folder\n>>>") 
        if not os.path.exists(CONST.DIRECTORY + "\%s" % subFolder):
            os.makedirs("%s\%s" % (CONST.DIRECTORY, subFolder))
        CONST.SUBDIR = '\\%s' % subFolder
    else:
        CONST.SUBDIR = ""
    input("Press Enter to Begin Download...")
    a = 0
    #screen_clear()
    try:
        for songs in sn:
            if '@https://' in songs:
                pass
            if "feat." in songs:
                songs = songs.split('(')[0]    
            delay = True
            ts = True
            if type(songs) != type(sn):            
                if os.path.isfile(CONST.DIRECTORY + CONST.SUBDIR + "\%s.mp3" % songs.strip()) == False:
                    songs = songs.strip()
                    downloadMP3(songs)
                    #thread = nameThread(a, songs, songs, numSong)
                else:
                    finishedDownload = finishedDownload + 1        
                    delay = False
                    ts = False
            else:
                if os.path.isfile(CONST.DIRECTORY + CONST.SUBDIR + "\%s.mp3" % songs[0].strip()):
                    finishedDownload = finishedDownload + 1  
                    delay = False
                    ts = False
                else:
                    pass
            a = a + 1
        
    except NameError as e:
        print(e)

def downloadMP3(sName, subFolder = ""):
    query_string = urllib.parse.urlencode({"search_query" : sName + " Audio"})
    html_content = urllib.request.urlopen("http://www.youtube.com/results?" + query_string)
    search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
    url = 'http://www.youtube.com/watch?v=' + search_results[0]
    options = {
        'format': 'bestaudio/best',
        'extractaudio' : True,  # only keep the audio
        'audioformat' : "mp3",  # convert to mp3 
        'outtmpl': CONST.DIRECTORY + CONST.SUBDIR + '/%(title)s.mp3',    # name the file the Title of the video
        'noplaylist' : True,    # only download single song, not playlist
        }
    with youtube_dl.YoutubeDL(options) as ydl:
        info_dict = ydl.extract_info(url, download=False)
        if (not os.path.exists(CONST.DIRECTORY + CONST.SUBDIR + "\\" + removeAudio(info_dict.get("title")) + ".mp3")):
            ydl.download([url])  
            os.rename(CONST.DIRECTORY + CONST.SUBDIR + "\\" + info_dict.get("title") + ".mp3", CONST.DIRECTORY + CONST.SUBDIR + "\\" + removeAudio(info_dict.get("title")) + ".mp3")

def removeAudio(name):
    return name.lower().replace("audio", "").replace("(video)", "").replace("official", "").replace("official video", "").replace("with lyrics", "").replace("audio + lyrics", "").replace("lyric", "").replace("lyrics", "").replace("official music video", "").replace("hq audio", "").replace("audio hq", "").replace("hd", "").replace("hq", "").replace("[]", "").replace("()", "").strip().title()

def single_name_download(song, numSongs, downloadLinkOnly, retries, isYoutubeDownload):     # download directly with a song name
    if song == "":
        print(bcolors.WHITE + 'Enter the song name or full youtube link: ')  # get the song name from user
        song = input('>>> ')
    if "www.youtube.com" in song: 
        song = video_title(song)  
    if "feat." in song:
        song = song.split('(')[0]
    downloadMP3(song) 

def exit(code):                             # program exit
    sys.exit(code)

def getHistory():
    global previouslyDownloaded 
    previouslyDownloaded = []
    songLog = open(os.getcwd() + "\\" + CONST.LOG, 'r')
    for songLink in songLog:
        if songLink.strip() != "": 
            sl = songLink.split('@')
            previouslyDownloaded.append(sl[0].strip())
            previouslyDownloaded.append(sl[1].strip())
        
def printHistory(search):
    global previouslyDownloaded
    downloadSearch = []
    x = 0
    color = 30
    for titles in previouslyDownloaded:
        if 'www.youtube.com' not in titles:
            if search.lower() in titles.lower():
                color = color + 1
                x = x + len(titles) + 5
                if x > 180:
                    print()
                    x = 0
                if color > 37:
                    color = 31
                if color == 34:
                    color = 35
                print(titles, end='|\x1b[0;%s;40m' % color)
                downloadSearch.append(titles)

def getwindow(Title="SpotifyMainWindow"):
	window_id = win32gui.FindWindow(Title, None)
	return window_id

def song_info():
	try:
		song_info = win32gui.GetWindowText(getwindow())
	except:
		pass
	return song_info

def getSong():
	try:
		temp = song_info()
		artist, song = temp.split("-",1)
		song = song.strip()
		return song
	except:
		return "There is nothing playing at this moment"

def main():                                 # main guts of the program
    global finishedDownload
    global numberOfSongsGlobal
    global downloadErrors    
    global totalFileDownloadSize
    Continue = True
    finishedDownload = 0
    if not os.path.exists("Settings.txt"):
        Settings.sSet()
    else:
        Settings.sGet()
    if not os.path.exists(CONST.DIRECTORY):
        os.makedirs(CONST.DIRECTORY)
    if not os.path.exists(CONST.SONGLISTDIR):
        os.makedirs(CONST.SONGLISTDIR)
    if not os.path.exists(CONST.LOG):
        file = open(CONST.LOG, "w")
        file.close()
    if not os.path.exists(CONST.SONGLISTDIR + "2006.txt"):
        thread = update100Thread()
        thread.start()       
    while Continue:
        if finishedDownload == numberOfSongsGlobal + 1 or numberOfSongsGlobal == 0:
            try:
                CONST.SUBDIR = ""
                downloadErrors = []
                finishedDownload = 0
                numberOfSongsGlobal = 0
                totalFileDownloadSize = 0
                screen_clear()
                getHistory()
                choice = prompt()        
                try:
                    if choice == '1':
                        single_name_download("", 1, "", 0, False)                
                    elif choice == '2':                
                        list_download(False, [])
                    elif choice == 'c':         
                        single_name_download(song_info(), 1, "", 0, False)
                    elif choice == '3':
                        list_download(True, [])
                    elif choice == '4':                
                        printHistory("")
                        input()
                    elif choice == '5':
                        alls = os.listdir(CONST.DIRECTORY)
                        totalSize = 0
                        totalCount = 0
                        for sng in alls:
                            if os.path.isdir(os.path.join(CONST.DIRECTORY, sng)):
                                suballs = os.listdir(os.path.join(CONST.DIRECTORY, sng))
                                for subsng in suballs:
                                    totalSize = totalSize + getSize(os.path.join(CONST.DIRECTORY, sng) + "\%s" % subsng)/1048576
                                    totalCount = totalCount + 1
                            else:
                                totalSize = totalSize + getSize(CONST.DIRECTORY + "\%s" % sng)/1048576
                                totalCount = totalCount + 1
                        print("There are %s songs totalling to %s Mb of .mp3 files." % (totalCount, "{0:.2f}".format(totalSize)))
                        input()
                    elif choice == '6':
                        youTubePlaylistDownloader()
                    elif choice == '7':
                        search = input("Enter search term\n>>> ")
                        printHistory(search)
                        input()
                    elif choice == 's':
                        changeSettings()
                    elif choice == "8":
                        generatePlaylist()
                    else:
                        Continue = False
                        screen_clear()
                        exit(1)
                except NameError:
                    print("NameError")
                    Continue = False
                    exit(1)
            except KeyboardInterrupt:
                Continue = False
                exit(1)
            time.sleep(0.5)

if __name__ == '__main__':
    main()  # run the main program
    exit(0)  # exit the program