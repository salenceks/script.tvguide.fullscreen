import sys
import xbmc,xbmcaddon,xbmcvfs
import sqlite3
from subprocess import Popen
import datetime,time
channel = sys.argv[1]
start = sys.argv[2]

ADDON = xbmcaddon.Addon(id='script.tvguide.fullscreen')

def adapt_datetime(ts):
    # http://docs.python.org/2/library/sqlite3.html#registering-an-adapter-callable
    return time.mktime(ts.timetuple())

def convert_datetime(ts):
    try:
        return datetime.datetime.fromtimestamp(float(ts))
    except ValueError:
        return None

sqlite3.register_adapter(datetime.datetime, adapt_datetime)
sqlite3.register_converter('timestamp', convert_datetime)
path = xbmc.translatePath('special://profile/addon_data/script.tvguide.fullscreen/source.db')
try:
    conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
except Exception as detail:
    xbmc.log("EXCEPTION: (script.tvguide.fullscreen)  %s" % detail, xbmc.LOGERROR)

c = conn.cursor()
startDate = datetime.datetime.fromtimestamp(float(start))
c.execute('SELECT DISTINCT * FROM programs WHERE channel=? AND start_date = ?', [channel,startDate])
for row in c:
    title = row["title"]
    endDate = row["end_date"]
    duration = endDate - startDate
    before = int(ADDON.getSetting('autoplaywiths.before'))
    after = int(ADDON.getSetting('autoplaywiths.after'))
    extra = (before + after) * 60
    #TODO start from now
    #seconds = duration.seconds + extra
    #if seconds > (3600*4):
    seconds = 3600*4
    break

# Find the channel's stream url
c.execute('SELECT stream_url FROM custom_stream_url WHERE channel=?', [channel])
row = c.fetchone()
url = ""
if row:
    url = row[0]
if not url:
    quit()

# Find the actual url used to play the stream
core = "dummy"
xbmc.executebuiltin('PlayWith(%s)' % core)
player = xbmc.Player()
player.play(url)
count = 30
url = ""
while count:
    count = count - 1
    time.sleep(1)
    if player.isPlaying():
        url = player.getPlayingFile()
        break
player.stop()

# Play with your own preferred player and paths
if url:
    name = "%s = %s = %s" % (start,channel,title)
    name = name.encode("cp1252")
    filename = xbmc.translatePath("special://temp/%s.ts" % name)
    #filename = "/storage/recordings/%s.ts" % name
    ffmpeg = r"c:\utils\ffmpeg.exe"
    ffmpeg = r"/usr/bin/ffmpeg"
    cmd = [ffmpeg, "-y", "-i", url, "-c", "copy", "-t", str(seconds), filename]
    p = Popen(cmd,shell=True)
    #p = Popen(cmd,shell=False)
