#!/usr/bin/python3

import os
import signal
import json
import gi
import time
import requests
from datetime import datetime

from urllib.request import Request, urlopen, URLError
gi.require_version('AppIndicator3', '0.1')
gi.require_version('Gtk', '3.0')
gi.require_version('Notify', '0.7')
from gi.repository import Gtk as gtk
from gi.repository import AppIndicator3 as appindicator
from gi.repository import Notify as notify

prayers = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]

APPINDICATOR_ID = 'myappindicator'

def main():
    indicator = appindicator.Indicator.new(APPINDICATOR_ID, os.path.abspath('sample_icon.svg'), appindicator.IndicatorCategory.SYSTEM_SERVICES)
    indicator.set_status(appindicator.IndicatorStatus.ACTIVE)
    indicator.set_menu(prayerTimings())
    gtk.main()

def prayerTimings():
    menu = gtk.Menu()
    timings = fetch_prayersTimings()
    for prayer in prayers:
        time = timings[prayer]
        layout = "{0} {1}"
        layout = layout.format(prayer,time)
        item1 = gtk.MenuItem(layout)
        menu.append(item1)
    menu.show_all()
    return menu

def get_longtitudeLatitude():
    url = 'https://maps.googleapis.com/maps/api/geocode/json'
    params = {'sensor': 'false', 'address': 'Milton, ON'}
    r = requests.get(url, params=params)
    results = r.json()['results']
    location = results[0]['geometry']['location']
    return location['lat'], location['lng']

def fetch_prayersTimings():
    lat, lng = get_longtitudeLatitude()
    timeStamp = str(int(time.time()))
    base = 'http://api.aladhan.com/timings/{0}?latitude={1}&longitude={2}&method2'
    base = base.format(timeStamp, lat, lng)

    request = Request(base)
    response = urlopen(request)
    prayersTimings = json.loads(response.read().decode("utf-8"))["data"]["timings"]

    timings = {}
    for timingName in prayersTimings:
        if timingName in prayers:
            timeToDisplay = datetime.strptime(prayersTimings[timingName], "%H:%M")
            timings[timingName] = timeToDisplay.strftime("%I:%M %p")
    return timings

if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal.SIG_DFL)
    main()
