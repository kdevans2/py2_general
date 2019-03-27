import sys
from time import time, ctime
from string import zfill

def elapsed_time(t):
    """ funcion to return a string of format 'hh:mm:ss', representing time elapsed between
        establishing variable t (generally: t = time.time()) and funcion call.

        Result rounded to nearest second"""
    seconds = int(round(time() - t))
    h,rsecs = divmod(seconds,3600)
    m,s = divmod(rsecs,60)
    return zfill(h, 2) + ":" + zfill(m, 2) + ":" + zfill(s, 2)

class progressor:
    def __init__(self, intTotalCount, intBreaks = 10, BoolLineFeed = False):
        self.count = 0
        self.total = intTotalCount
        self.breaks = intBreaks
        self.increment = int(float(intTotalCount) / intBreaks)
        self.Feed = BoolLineFeed
        if self.Feed:
            self.feedVal = '\n'
        else:
            self.feedVal = ' '

    

    def call(self):
        self.count += 1
        if not self.count % self.increment:
            strPrint = str(int(round(100 * float(self.count) / self.total))) +  self.feedVal
            sys.stdout.write(strPrint)
