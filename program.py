#!/usr/bin/env python
# A python to download a song or a list of songs.
# create by Aman Roy
# Creation Date : 18-Feb-2016
# Python version used : - Python 3.4.3+
# All licence belongs to authour.

# import all the libraries used
import re, urllib, os, sys, threading, time, urllib.request, urllib.parse

class bcolors:
    RED = '\x1b[0;31;40m'
    GREEN = '\x1b[0;32;40m'
    YELLOW = '\x1b[0;33;40m'
    BLUE = '\x1b[0;34;40m'
    PINK = '\x1b[0;35;40m'
    AQUA = '\x1b[0;36;40m'
    WHITE = '\x1b[0;37;40m'

# Creation of a constant class, so that mass changes in the code can be done.
class _Const(object):
    RETRIES = 5                 # Total number of retries the program undergoes before giving up 
    DIRECTORY = "Songs"         # The subdirectory name in which all the downloaded mp3's will reside.
    WAIT = 4                    # Seconds of delay between the initialization of seperate threads.
    LOG = "SongLog.txt"         # The name of the Log file in whichh all songs will have their url's saved.
    MP3 = 0                # Determining the website to use when downloadin the song. Sometimes one will be down.
    ERROR = "Errors.txt"
    SONGLISTDIR = "SongLists" 
    SUBDIR = ""  

def changeSettings():
    staySettings = True
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
        if setIndex == 'x':
            staySettings = False
            setSettings()
        elif str.isdigit(setIndex) and int(setIndex) < 6:
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
    
def isTextFile(inValue):
    if ".txt" not in inValue:
        inValue = inValue + ".txt"   
    return inValue
    
def getSettings():
    file = open("Settings.txt", "r")
    sett = file.readline()
    setlist = sett.split(',')
    CONST.RETRIES = int(setlist[0].strip())
    CONST.DIRECTORY = setlist[1].strip()
    CONST.WAIT = int(setlist[2].strip())
    CONST.LOG = setlist[3].strip()
    CONST.ERROR = setlist[4].strip()
    CONST.SONGLISTDIR = setlist[5].strip()

global finishedDownload 
finishedDownload = 0
global numberOfSongsGlobal
numberOfSongsGlobal = 0
global previouslyDownloaded 
previouslyDownloaded = []
global downloadErrors
downloadErrors = []
global totalFileDownloadSize
totalFileDownloadSize = 0

# 
CONST = _Const
getSize = os.path.getsize
user_input = input
urlopen = urllib.request.urlopen
encode = urllib.parse.urlencode
retrieve = urllib.request.urlretrieve
cleanup = urllib.request.urlcleanup()

def updateTop100():    
    for x in range(2006,2016):
        if os.path.isfile(CONST.SONGLISTDIR +  "\%s.txt" % x) == False:  
            file = open(CONST.SONGLISTDIR+  "\%s.txt" % x, "w")    
            webpage = urlopen("http://www.billboard.com/charts/year-end/%s/hot-100-songs" % x).read()            
            songs = str(webpage).split('<h2 class="chart-row__song">')
            for y in range (1,101):
                s2 = songs[y].split('</h2>')
                songName = removeSpecialCaharacters(s2[0]).split()
                sn = ""
                for songWord in songName:
                    sn = "%s%s " % (sn, songWord.capitalize())
                artist = s2[1].split('"Artist Name">')
                if '</h3>' in artist[0]:
                    artist = removeSpecialCaharacters(artist[0].split('</h3>')[0].split(">")[1].replace('"','')[3:].strip())
                else:
                    artist = removeSpecialCaharacters(artist[1].split("</a>")[0].replace('"','')[3:].strip())
                artist = artist[:len(artist)-2].replace(" Featuring ", ";")
                file.write("%s - %s\n" % (artist, sn.strip()))
            file.close()
        else:
            #print("Top100-%s.txt Already Exists." % x)
            pass
            
    file = open(CONST.SONGLISTDIR +  "\Top100.txt", "w")
    webpage = urlopen("http://www.billboard.com/charts/hot-100").read()
    songs = str(webpage).split('<h2 class="chart-row__song">')
    
    for y in range (1,101):
        s2 = songs[y].split('</h2>')
        songName = removeSpecialCaharacters(s2[0].lower()).split()
        sn = ""
        for songWord in songName:
            sn = "%s%s " % (sn, songWord.capitalize())
        artist = s2[1].split('"Artist Name">')
        if '</h3>' in artist[0]:
            artist = removeSpecialCaharacters(artist[0].split('</h3>')[0].split(">")[1].replace('"','')[3:])
        else:
            artist = removeSpecialCaharacters(artist[1].split("</a>")[0].replace('"','')[3:])
        artist = artist[:len(artist)-2].replace(" Featuring ", ";")
        file.write("%s - %s\n" % (artist, sn.strip()))
    file.close()

# clear the terminal screen
def screen_clear():
    if os.name == 'nt':
        os.system('cls')
    else:
        os.system('clear')

def removeSpecialCaharacters(inputString):
    return inputString.strip().replace("&#039;", "'").replace(" &amp; ",";").replace("&quot;",'')

# function to retrieve video title from provided link
def video_title(url):
    try:
        webpage = urlopen(url).read()
        title = removeSpecialCaharacters(str(webpage).split('<title>')[1].split('</title>')[0])
    except:
        title = 'Youtube Song'
    return title

def print_format_table():
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

# find out what the user wants to do
def prompt():
    # user prompt to ask mode
    print (bcolors.WHITE + '''Select A mode  
    [1] Download from direct entry
    [2] Download from a list
    [3] Download all of your previously downloaded Songs
    [4] List all previously downloaded songs
    [5] Show count of all songs currently in the downloaded directory
    [6] Youtube Playlist Downloader 
    [s] Change settings
    Press any other key from keyboard to exit''')
    #print_format_table()
    choice = input('>>> ')
    return str(choice)

def youTubePlaylistDownloader():
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
    

class nameThread (threading.Thread):
    def __init__(self, threadID, name, songName, numSong):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.songName = songName
        self.numSong = numSong
    def run(self):
        try:
            single_name_download(self.songName, self.numSong, "", 0, False)
        except KeyboardInterrupt:
            os.remove(CONST.DIRECTORY + "\%s.mp3" % self.songName)
            exit(0)
                 
        
class update100Thread (threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
    def run(self):
        updateTop100()
                
# download from a list
def list_download(isHistory):  
    global finishedDownload
    global numberOfSongsGlobal
    numberOfSongsGlobal = 1
    a = 0
    numSong = 0
    fileUnOpened = True
    while fileUnOpened:
        if isHistory:
            fileName = CONST.LOG()        
        else:          
            fileName = input('Please enter the name of the file in the "%s" folder: ' % CONST.SONGLISTDIR)  # get the file name to be opened
        # find the file and set fhand as handler
        try:
            fhand = open(CONST.SONGLISTDIR + ("\%s" % fileName) + ".txt", 'r')
            print ('File opened successfully')
            fileUnOpened = False;
        except IOError:
            print('File does not exist\n')
            
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
            
    numberOfSongsGlobal = numSong
    print(bcolors.YELLOW + "There are %s songs in the file provided" % numSong)
    print("The download should take about %s minute(s) and %s seconds" % (((numSong*10+120)//60), ((numSong*10+120)%60)))
    if input(bcolors.WHITE + "Would you like to create a subfolder for this group of songs? (y/n)\n>>> ") == "y":
        subFolder = input("Enter the name of the folder\n>>>") 
        if not os.path.exists(CONST.DIRECTORY + "\%s" % subFolder):
            os.makedirs("%s\%s" % (CONST.DIRECTORY, subFolder))
        CONST.SUBDIR = '\\%s' % subFolder
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
                    thread = nameThread(a, songs, songs, numSong)
                else:
                    finishedDownload = finishedDownload + 1
                    printProgress(finishedDownload, numSong, "", bcolors.YELLOW + "The song '%s.mp3' is already downloaded" % songs)             
                    delay = False
                    ts = False
            else:
                if os.path.isfile(CONST.DIRECTORY + CONST.SUBDIR + "\%s.mp3" % songs[0].strip()):
                    finishedDownload = finishedDownload + 1
                    printProgress(finishedDownload, numSong, "", bcolors.YELLOW + "The song '%s.mp3' is already downloaded" % songs)     
                    delay = False
                    ts = False
                else:
                    thread = nameThread(a, songs[0].strip(), songs[1].strip(), numSong)
            if ts:                   
                thread.start()
            if delay:
                time.sleep(CONST.WAIT)
            a = a + 1
        fhand.close()
    except NameError as e:
        print(e)

# download directly with a song name
def single_name_download(song, numSongs, downloadLinkOnly, retries, isYoutubeDownload):
    global finishedDownload
    global previouslyDownloaded
    global downloadErrors        
    global totalFileDownloadSize
    if retries < CONST.RETRIES:
        if song == "":
            print(bcolors.WHITE + 'Enter the song name or full youtube link: ')  # get the song name from user
            song = input('>>> ')
        if song in previouslyDownloaded:
            print(bcolors.PINK + "Song was previously downloaded, using stored URL")
            downloadLinkOnly = previouslyDownloaded[previouslyDownloaded.index(song)+1]
            if CONST.MP3 == 1:
                if "yt-mp3" not in downloadLinkOnly:
                    downloadLinkOnly = "http://www.yt-mp3.com/watch?v=" + downloadLinkOnly
            elif CONST.MP3 == 0:
                if "youtubeinmp3" not in downloadLinkOnly:
                    downloadLinkOnly = "http://www.youtubeinmp3.com/fetch/?video=" + downloadLinkOnly
        if "www.youtube.com" in song:                   
            if CONST.MP3 == 0:
                downloadLinkOnly = 'http://www.youtubeinmp3.com/fetch/?video=' + song
            elif CONST.MP3 == 1:
                downloadLinkOnly = "http://www.yt-mp3.com/watch?v=" + song                  
            song = video_title(song)            
        succ = True
        if "feat." in song:
            song = song.split('(')[0]
            # try to get the search result and exit upon error
        if os.path.isfile(CONST.DIRECTORY + CONST.SUBDIR + "\%s.mp3" % song) == False or song not in previouslyDownloaded:         
            if downloadLinkOnly == "":
                try:
                    printProgress(finishedDownload, numSongs, "", bcolors.YELLOW + "Searching for %s..." % song)
                    query_string = encode({"search_query" : song})
                    html_content = urlopen("http://www.youtube.com/results?" + query_string)
                    printProgress(finishedDownload, numSongs, "", bcolors.YELLOW + "Found %s." % song)
                    search_results = re.findall(r'href=\"\/watch\?v=(.{11})', html_content.read().decode())
                except:
                    printProgress(finishedDownload, numSongs, "", bcolors.RED + 'Network Error Downloading %s' % song) 
                    succ = False
            if succ == True:
                # generate a download link that can be used to get the audio file using youtube2mp3 API
                x = False                
                if downloadLinkOnly == "":
                    if CONST.MP3 == 0:
                        downloadLinkOnly = 'http://www.youtubeinmp3.com/fetch/?video=' + 'http://www.youtube.com/watch?v=' + search_results[0]
                    elif CONST.MP3 == 1:
                        downloadLinkOnly = "http://www.yt-mp3.com/watch?v=" + 'http://www.youtube.com/watch?v=' + search_results[0]                    
                try:
                    printProgress(finishedDownload, numSongs, "", bcolors.YELLOW + "Downloading %s (Retry %s of %s)" % (song,retries, CONST.RETRIES))
                    # code a progress bar for visuals? this way is more portable than wget
                    retrieve(downloadLinkOnly, filename=CONST.DIRECTORY + CONST.SUBDIR + '\%s.mp3' % song)
                    cleanup  # clear the cache created by urlretrieve
                    x = True
                    printProgress(finishedDownload, numSongs, "", bcolors.YELLOW + "The file '%s.mp3' is %sMB" % (song, round(getSize(CONST.DIRECTORY + CONST.SUBDIR + "\%s.mp3" % song)/1048576, 1)))
                    fileSize = getSize(CONST.DIRECTORY + CONST.SUBDIR + "\%s.mp3" % song) 
                    if fileSize < 1048576:                        
                        os.remove(CONST.DIRECTORY + CONST.SUBDIR + "\%s.mp3" % song)
                        single_name_download(song, numSongs, downloadLinkOnly, retries + 1, False)
                        x = False
                        time.sleep(CONST.WAIT*2)
                    else : 
                        totalFileDownloadSize = totalFileDownloadSize + fileSize 
                except:
                    printProgress(finishedDownload, numSongs, "", bcolors.RED + 'Error downloading %s' % song)
                    single_name_download(song, numSongs, downloadLinkOnly, retries + 1, False)
                    x = False
                    time.sleep(CONST.WAIT*2)
                if x:
                    finishedDownload = finishedDownload + 1
                    printProgress(finishedDownload, numSongs, "", bcolors.GREEN + "Download Successful")                         
                    #print("%s / %s Songs downloaded" % (finishedDownload, numSongs))
                    if song not in previouslyDownloaded:            
                        file = open(CONST.LOG, "a")
                        file.write("\n%s@%s" % (song, downloadLinkOnly))
                        file.close()
        else:
            printProgress(finishedDownload, numSongs, "", bcolors.YELLOW + "The song '%s.mp3 is already downloaded" % song)            
            finishedDownload = finishedDownload + 1
            printProgress(finishedDownload, numSongs)
            #print("%s / %s Songs downloaded" % (finishedDownload, numSongs))
    else:        
        finishedDownload = finishedDownload + 1
        downloadErrors.append(song)
        printProgress(finishedDownload, numSongs, "", bcolors.RED + "Max retries reached for %s" % song)
        if not os.path.exists(CONST.ERROR):
            file = open(CONST.ERROR, "w")
            file.close()
        file = open(CONST.ERROR, "a")
        file.write("\n%s@%s" % (song, downloadLinkOnly))
        file.close()

def printProgress (iteration, total, prefix = '', suffix = '', decimals = 1, barLength = 75):
    global finishedDownload
    global downloadErrors    
    global numberOfSongsGlobal
    global totalFileDownloadSize
    """
    Call in a loop to create terminal progress bar
    @params:
        iteration   - Required  : current iteration (Int)
        total       - Required  : total iterations (Int)
        prefix      - Optional  : prefix string (Str)
        suffix      - Optional  : suffix string (Str)
        decimals    - Optional  : positive number of decimals in percent complete (Int)
        barLength   - Optional  : character length of bar (Int)
    """
    formatStr       = "{0:." + str(decimals) + "f}"
    percents        = formatStr.format(100 * (iteration / float(total)))
    filledLength    = int(round(barLength * iteration / float(total)))
    bar             = bcolors.BLUE + '█' * filledLength + bcolors.WHITE + '-' * (barLength - filledLength)
    screen_clear()
    print(bcolors.WHITE + '\r%s |%s| %s%s \n%s' % (prefix, bar, percents, '%', suffix), end = ""),    
    print()
    if iteration == total:
        print(bcolors.WHITE + "Total of %sMb Downloaded" % "{0:.2f}".format(totalFileDownloadSize/1048576))
        if len(downloadErrors) != 0:
            print("Errors:" + bcolors.RED)
        for errors in downloadErrors:
            print(errors)    
        if len(downloadErrors) != 0:        
            print(bcolors.RED + "\nThere were %s errors in the download process" % len(downloadErrors))
            print("Try downloading them individually, or with a different name format")
            input(bcolors.WHITE + "Press Enter To Continue")
            numberOfSongsGlobal = 0
            screen_clear()
        else :
            print(bcolors.GREEN + "There were no errors! :)")
            input()
                


# program exit
def exit(code):
    sys.exit(code)

def getHistory():
    global previouslyDownloaded 
    previouslyDownloaded = []
    songLog = open(CONST.LOG, 'r')
    for songLink in songLog:
        if songLink.strip() != "": 
            sl = songLink.split('@')
            previouslyDownloaded.append(sl[0].strip())
            previouslyDownloaded.append(sl[1].strip())
        
def printHistory():
    global previouslyDownloaded
    x = 0
    color = 30
    for titles in previouslyDownloaded:
        if 'www.youtube.com' not in titles:
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
                        
    print()       

def setSettings():
    file = open("Settings.txt", "w")
    file.write("%s, %s, %s, %s, %s, %s" % (str(CONST.RETRIES), CONST.DIRECTORY, str(CONST.WAIT), CONST.LOG, CONST.ERROR, CONST.SONGLISTDIR))

# main guts of the program
def main():         
    global finishedDownload
    global numberOfSongsGlobal
    global downloadErrors    
    global totalFileDownloadSize
    Continue = True
    finishedDownload = 0
    if not os.path.exists(CONST.DIRECTORY):
        os.makedirs(CONST.DIRECTORY)
    if not os.path.exists(CONST.SONGLISTDIR):
        os.makedirs(CONST.SONGLISTDIR)
    if not os.path.exists(CONST.LOG):
        file = open(CONST.LOG, "w")
        file.close()
    if not os.path.exists("Settings.txt"):
        setSettings()
    else:
        getSettings()
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
                        list_download(False)
                    elif choice == '3':
                        list_download(True)
                    elif choice == '4':                
                        printHistory()
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
                    elif choice == 's':
                        changeSettings()
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
