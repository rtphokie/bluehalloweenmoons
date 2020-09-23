import unittest
from skyfield import api, almanac
from pytz import timezone
from datetime import datetime
import numpy as np

eastern = timezone('US/Eastern')
pacific = timezone('US/Pacific')

ts = api.load.timescale(builtin=True)
load = api.Loader('/var/data')
eph = load('de430t.bsp')
# eph = load('de406.bsp')


def blue_moons(startyear, endyear, oct31only=False):
    d0 = datetime(startyear, 1, 1)
    d1 = datetime(endyear+1, 1, 1)
    # localize to eastern timezone
    e0 = eastern.localize(d0)
    e1 = eastern.localize(d1)
    t, y = almanac.find_discrete(ts.from_datetime(e0), ts.from_datetime(e1), almanac.moon_phases(eph))
    prevmonth=0     # the month the last full moon was seen
    bluedeltas=[]   # list of days separating blue moons
    blues = []      # list of blue moons
    prevblue = None # date of previous blue moon
    for yi, ti in zip(y, t):
        if yi==2:
            dt = ti.utc_datetime()
            dt = dt.astimezone(eastern)
            if prevmonth == dt.month: # its blue
                if prevblue is not None: # skip calcs on first occurance
                    if not oct31only or (dt.month == 10 and dt.day == 31):
                        delta = dt - prevblue
                        bluedeltas.append(delta.days)
                if not oct31only or (dt.month == 10 and dt.day == 31):
                    blues.append(dt.strftime('%c'))
                    prevblue = dt
            prevmonth = dt.month
    bluedeltamean = np.mean(bluedeltas)
    return blues, bluedeltamean


class MyTestCase(unittest.TestCase):

    def test_blue_moons(self):
        blues, bluedeltamean = blue_moons(1900,2099)
        print("\n1. ".join(blues))
        print(f"\nmean days between blue moons: {bluedeltamean}")

    def test_oct_31_blue_moons(self):
        blues, bluedeltamean = blue_moons(1900,2099, oct31only=True)
        print("\n1. ".join(blues))
        print(f"\nmean days between Oct 31 blue moons: {bluedeltamean}")

if __name__ == '__main__':
    unittest.main()
