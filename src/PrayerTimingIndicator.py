#!/usr/bin/python3
import os, signal, json, time, requests, socket
import pgi
pgi.install_as_gi()
pgi.require_version('AppIndicator3', '0.1')
pgi.require_version('Gtk', '3.0')

from datetime import datetime
from urllib.request import Request, urlopen, URLError
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
class PrayerTimingIndicator: 
    def __init__(self):
        self.PRAYER_TIMINGS_API = 'http://api.aladhan.com/timings/{0}?latitude={1}&longitude={2}&method2'
        self.PRAYER_TIMINGS_API_HOST = 'http://api.aladhan.com/'
        self.GOOGLE_API = 'https://maps.googleapis.com/maps/api/geocode/json'
        self.location = 'Milton, ON'
        self.prayers = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
        self.APPINDICATOR_ID = 'myappindicator'

        self.internet = True
        self.raw_timings = []
        self.process_timings = []

        self.status = appindicator.IndicatorStatus.ACTIVE
        self.type = appindicator.IndicatorCategory.SYSTEM_SERVICES
        self.iconPath = os.path.abspath('../assets/icon.svg')

        self.indicator = appindicator.Indicator.new(self.APPINDICATOR_ID, self.iconPath, self.type)

    def initialIndicator(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.indicator.set_status(self.status)
        self.loadDatatoMenu('activate')

    def loadDatatoMenu(self,source):
        self.indicator.set_menu(self.createMenu())

    def runIndicator(self):
        gtk.main()

    def processPrayerTimings(self):
        prayersTimings = self.raw_timings
        timings = {}
        for timingName in prayersTimings:
            if timingName in self.prayers:
                timeToDisplay = datetime.strptime(prayersTimings[timingName], "%H:%M")
                timings[timingName] = timeToDisplay.strftime("%I:%M %p")
        self.process_timings = timings

    def addUtilityMenuOptions(self, menu):
        item_about = gtk.MenuItem('About')
        menu.append(item_about)    

        item_setting = gtk.MenuItem('Setting')
        menu.append(item_setting)    
        
        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', self.quit)
        menu.append(item_quit)    

    def reconnectionButton(self, menu):
        item_reconnect = gtk.MenuItem('re-connect...')
        item_reconnect.connect('activate', self.loadDatatoMenu)
        menu.append(item_reconnect)    

    def connection(self, menu):
        if self.internet:
            item_internet = gtk.MenuItem('Connection: Yes')
        else :
            item_internet = gtk.MenuItem('Connection: No')
        menu.append(item_internet)
        menu.append(gtk.SeparatorMenuItem())

    def createMenu(self):
        menu = gtk.Menu()
        self.fetchPrayersTimings()
        self.connection(menu)

        if self.internet:
            self.processPrayerTimings()
            self.prayerTimings(menu)
        else:
            self.reconnectionButton(menu)

        menu.append(gtk.SeparatorMenuItem())
        self.addUtilityMenuOptions(menu)
        menu.show_all()
        return menu

    def prayerTimings(self, menu):
        timings = self.process_timings
        prayers = self.prayers
        for prayer in prayers:
            time = timings[prayer]
            layout = "{0}  {1}".format(prayer,time)
            item = gtk.MenuItem(layout)
            item.set_hexpand(True)
            item.set_halign(gtk.Align.END)
            menu.append(item)
                    
    def quit(self,source):
        gtk.main_quit()

    def getUnixTimeStamp(self):
        return str(int(time.time()))

    def formattedAPI(self):
        lat, lng = self.getLongtitudeLatitude()
        timeStamp = self.getUnixTimeStamp()
        base = self.PRAYER_TIMINGS_API
        base = base.format(timeStamp, lat, lng)
        return base
        
    def fetchPrayersTimings(self):
        try:
            request = Request(self.formattedAPI())
            response = urlopen(request)
            self.raw_timings = json.loads(response.read().decode("utf-8"))["data"]["timings"]
            self.internet = True
        except:
            self.internet = False

    def getLongtitudeLatitude(self):
        params = {'sensor': 'false', 'address': self.location}
        r = requests.get(self.GOOGLE_API, params=params)
        results = r.json()['results']
        location = results[0]['geometry']['location']
        return location['lat'], location['lng']
