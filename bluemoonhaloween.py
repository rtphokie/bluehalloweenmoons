import unittest
from skyfield import api, almanac
from pytz import timezone
from datetime import datetime
import numpy as np
import simple_cache
from pprint import pprint

ts = api.load.timescale(builtin=True)
load = api.Loader('/var/data')
# eph = load('de421.bsp')
eph = load('de430t.bsp')
# eph = load('de406.bsp')

@simple_cache.cache_it(filename="blue_moon.cache", ttl=18000)
def blue_moons(startyear, endyear, oct31only=False, zone=timezone('UTC')):
    t, y = find_phases(endyear, startyear, zone)
    prevmonth=0     # the month the last full moon was seen
    bluedeltas=[]   # list of days separating blue moons
    blues = []      # list of blue moons
    prevblue = None # date of previous blue moon
    for yi, ti in zip(y, t):
        if yi==2:
            dt = ti.utc_datetime()
            dt = dt.astimezone(zone)
            if prevmonth == dt.month: # its blue
                if prevblue is not None: # skip calcs on first occurance
                    if not oct31only or (dt.month == 10 and dt.day == 31):
                        delta = dt - prevblue
                        bluedeltas.append(delta.days)
                if not oct31only or (dt.month == 10 and dt.day == 31):
                    blues.append(dt)#.strftime('%c'))
                    prevblue = dt
            prevmonth = dt.month
    bluedeltamean = np.mean(bluedeltas)
    return blues, bluedeltamean

@simple_cache.cache_it(filename="moon_phases.cache", ttl=18000)
def find_phases(endyear, startyear, zone):
    d0 = datetime(startyear, 1, 1)
    d1 = datetime(endyear + 1, 1, 1)
    # localize to eastern timezone
    e0 = zone.localize(d0)
    e1 = zone.localize(d1)
    t, y = almanac.find_discrete(ts.from_datetime(e0), ts.from_datetime(e1), almanac.moon_phases(eph))
    return t, y


def build_md_table(tzlist, oct31only=False, startyear=1900, endyear=2100, dtrowpattern='%Y-%m-%d'):
    results = dict.fromkeys(tzlist, [])
    years = set()
    for tzname in results.keys():
        print(tzname)
        blues, bluedeltamean = blue_moons(startyear, endyear, zone=timezone(f'US/{tzname}'), oct31only=oct31only)
        results[tzname] = blues
        for dt in blues:
            years.add(dt.strftime(dtrowpattern))
    # markdown table of results
    mdtext = f"| year | {' | '.join(results.keys())} |\n"
    mdtext += f"|---|{'---|' * len(results.keys())}\n"
    for year in sorted(years):
        mdtext += f"| {year} | "
        for tzname in results.keys():
            found = False
            for dt in results[tzname]:
                if dt.strftime(dtrowpattern) == year:
                    mdtext += f" {dt.strftime('%I:%M %p')} |"
                    found = True
            if not found:
                mdtext += " |"
        mdtext +="\n"
    return mdtext

class MyTestCase(unittest.TestCase):

    def test_blue_moons(self):
        tzlist = ['Eastern', 'Central', 'Mountain', 'Pacific', 'Alaska', 'Hawaii']
        oct31only=True
        mdtext = build_md_table(tzlist, oct31only=True, startyear=1900, endyear=2099)
        print(mdtext)


    def test_oct_31_blue_moons(self):
        tzlist = ['Eastern', 'Central', 'Mountain', 'Pacific', 'Alaska', 'Hawaii']
        oct31only=True
        mdtext = build_md_table(tzlist, oct31only=False, startyear=1900, endyear=2099)
        print(mdtext)

if __name__ == '__main__':
    unittest.main()
