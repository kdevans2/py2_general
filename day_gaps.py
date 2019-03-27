# -------------------------------------------------------
# day_gaps.py
# Kirk Evans 03/18 TetraTech EC
#
# Functions to support creation of missing moisture rasters used by ees3
#
# Known limitations: arc 10.x.
# -------------------------------------------------------
import os, sys, glob
import datetime as dt


def d2str(DT):
    ''' Return a string of format YYYYMMDD for datetime or date object dt. '''
    return str(DT.year) + str(DT.month).zfill(2) + str(DT.day).zfill(2)


def str2d(s):
    ''' Return a date object given string s of format YYYYMMDD.
            Also works if s is an int
        Returns None if date conversion fails.
        Carefull, this function may mask unanticipated exceptions,
            check for None result
    '''
    try:
        s = str(s)
        D = dt.date(int(s[:4]), int(s[4:6]), int(s[6:]))
    except Exception:
        return None
    return D


def str2d_2(s):
    ''' Return a date object given string s of format 'm/d/yyyy h:m:s'.
        Truncates time.
    '''
    strD = s.split(' ')[0]
    strM, strD, strY = strD.split('/')
    D = dt.date(int(strY), int(strM), int(strD))

    return D


def _ListSpanDates(dtStart, dtEnd):
    ''' Return a list of date objects for all dates objects from dtStart to dtEnd.

        dtStart: starting date object
        dtEnd: ending date object, inclusive
        Note: currently only working for dtEnd not earlier than dtStart.
    '''
    lstAll = []
    DT = dtStart
    while DT <= dtEnd:
        lstAll.append(DT)
        DT += dt.timedelta(1)
    
    return lstAll


def GetPresentDates(strDir = None, intYear = None, strWild = None, bolTest = False):
    ''' Return a list of date objects for all moisture rasters in strDir.

        strDir: directory to be searched
        intYear: optional limit results to those in intYear
        strWild: optional wildcard to specify naming convention of raster
            default is ees3 standard: YYYYMMDD.dat. Wildcard must use
            ???????? for YYYYMMDD match. No other date formats supported.
        bolTest: optional boolean to test if unanticipated filename matches
            were found by glob, namely where the YYYYMMDD string match was not
            a valid date.
    '''
    if strDir is None:
        strDir = os.getcwd()
        
    if strWild is None:
        strWild = '????????_cal.tif' 
    strWild2 = strDir + os.sep + strWild
    print(strWild2)

    # get matching files names
    lstFiles = [os.path.basename(f) for f in glob.glob(strWild2) if os.path.isfile(f)]

    # strip to date substring
    intStart = strWild.index('????????')
    lstPresentStr = [f[intStart: intStart + 8] for f in lstFiles]
    
    # convert to date format, excluding invalid date strings found by glob
    lstPresentDt = [str2d(strD) for strD in lstPresentStr if str2d(strD)]

    # optionally test if bad string matches were found
    if bolTest:
        if len(lstPresentDt) != len(lstPresentStr):
            lstBad = [strD for strD in lstPresentStr if not str2d(strD)]
            raise Exception('Invalid filenames found: ' + str(lstBad))
        
    if intYear:
        return sorted([D for D in lstPresentDt if D.year == intYear])
    else:
        return sorted(lstPresentDt)


def ListMissing(lstD_Present, lstD_Need = None):
    ''' Return a list of date objects not present in lstDates.

        lstD_Present: list of present dates in date format
        lstD_Need: optional list of needed dates in date format. If
            not provided then lstD_Need will be all dates from ealiest in lstD_Present
            to latest in lstD_Present.
    '''
    if lstD_Need is None:
        lstD_PresentS = sorted(lstD_Present)
        lstD_Need = _ListSpanDates(lstD_PresentS[0], lstD_PresentS[-1])
                          
    lstMissing = [D for D in lstD_Need if D not in lstD_Present]

    return lstMissing


def GroupMissingDates(lstMis):
    ''' Return a list of lists where each sublist is a list of
        consecutive dates not present in lstDates.
    '''
    lstGroups = []
    lstMis = sorted(lstMis)

    lstGroup = [lstMis[0]]
    for i, d in enumerate(lstMis[1:]):
        dPrev = lstMis[i]
        if (d-dPrev).days == 1:
            lstGroup.append(d)
        else:
            lstGroups.append(lstGroup)
            lstGroup = [d]

    lstGroups.append(lstGroup)
    return lstGroups


def BookEndDates(lstD):
    ''' Return date pair of date preceeding that in lstD and that after.
        lstD: list of date objects, meant to be an element of result of GroupMissingDates.
    '''
    lstD2 = sorted(lstD)
    
    return lstD2[0] - dt.timedelta(1), lstD2[-1] + dt.timedelta(1)

    
def ListMissingGroups(strDir, lstD_Need = None, intYear = None, strWild = None, bolTest = False):
    ''' Wrapper to combine GetPresentDates, ListMissing and GroupMissingDates calls.
        Warning, lstD_Need and intYear args can conflict. Not tested, use with care!
    '''
    
    lstD_Present = GetPresentDates(strDir, intYear, strWild, bolTest)
    lstMis = ListMissing(lstD_Present)
    lstG = GroupMissingDates(lstMis)

    return lstG
