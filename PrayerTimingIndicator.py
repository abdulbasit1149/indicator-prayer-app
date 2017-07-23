#!/usr/bin/python3
import os, signal, json, gi, time, requests

gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')

from datetime import datetime
from urllib.request import Request, urlopen, URLError
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator

class PrayerTimingIndicator: 
    def __init__(self):
        self.PRAYER_TIMINGS_API = 'http://api.aladhan.com/timings/{0}?latitude={1}&longitude={2}&method2'
        self.GOOGLE_API = 'https://maps.googleapis.com/maps/api/geocode/json'
        self.location = 'Milton, ON'
        self.prayers = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
        self.APPINDICATOR_ID = 'myappindicator'

        self.status = appindicator.IndicatorStatus.ACTIVE
        self.type = appindicator.IndicatorCategory.SYSTEM_SERVICES
        self.iconPath = os.path.abspath('sample_icon.svg')

        self.indicator = appindicator.Indicator.new(self.APPINDICATOR_ID, self.iconPath, self.type)

    def initialIndicator(self):
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        self.indicator.set_status(self.status)
        self.indicator.set_menu(self.prayerTimings())

    def runIndicator(self):
        gtk.main()

    def prayerTimings(self):
        menu = gtk.Menu()
        timings = self.processPrayerTimings()
        for prayer in self.prayers:
            time = timings[prayer]
            layout = "{0} {1}"
            layout = layout.format(prayer,time)
            item1 = gtk.MenuItem(layout)
            menu.append(item1)

        menu.append(gtk.SeparatorMenuItem())
        item_quit = gtk.MenuItem('Quit')
        item_quit.connect('activate', self.quit)
        menu.append(item_quit)    
        menu.show_all()
        return menu

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
        request = Request(self.formattedAPI())
        response = urlopen(request)
        prayersTimings = json.loads(response.read().decode("utf-8"))["data"]["timings"]
        return prayersTimings

    def processPrayerTimings(self):
        prayersTimings = self.fetchPrayersTimings()
        timings = {}
        for timingName in prayersTimings:
            if timingName in self.prayers:
                timeToDisplay = datetime.strptime(prayersTimings[timingName], "%H:%M")
                timings[timingName] = timeToDisplay.strftime("%I:%M %p")
        return timings

    def getLongtitudeLatitude(self):
        params = {'sensor': 'false', 'address': self.location}
        r = requests.get(self.GOOGLE_API, params=params)
        results = r.json()['results']
        location = results[0]['geometry']['location']
        return location['lat'], location['lng']
