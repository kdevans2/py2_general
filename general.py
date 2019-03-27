# -------------------------------------------------------
# RSL_Util10.py
# Kirk Evans 03/18 TetraTech EC
#
# Commonly used ArcGIS related utility funcions
# This version for script tools using the arc10 geoprocessor object
# -------------------------------------------------------
from math import *
import arcpy, os, time, glob, csv

# -------------------------------------------------------
# general and print related
def elapsed_time(t):
    """ funcion to return a string of format 'hh:mm:ss', representing time elapsed between
        establishing variable t (generally: t = time.time()) and funcion call.

        Result rounded to nearest second by time_string. """
    return time_string(time.time() - t)

def time_string(t):
    """ funcion to return a string of format 'hh:mm:ss', representing time t in seconds 
        Result rounded to nearest second. """
    seconds = int(round(t))
    h,rsecs = divmod(seconds,3600)
    m,s = divmod(rsecs,60)
    return str(h).zfill(2) + ":" + str(m).zfill(2) + ":" + str(s).zfill(2)


def print2(string, txt, boolQuiet = None):
    ''' print function plus log to txt.
        optionally supress print. '''
    if boolQuiet is None:
        boolQuiet = True
        
    with open(txt, 'a') as t:
        t.write(string.strip() + '\n')
        
    if not boolQuiet:
        print(string)

def testgit(arg):
    """ """
    arg2 = arg
    pass

def testgit2(arg):
    """ """
    arg2 = arg
    pass

# -------------------------------------------------------
# path related
def formatPath(input_string):
    """ function to correct backslash issues in paths
        usage: strPath = ut.formatPath(strPath)
    """
    
    lstReplace = [["\a","/a"],
                  ["\b","/b"],
                  ["\f","/f"],
                  ["\n","/n"],
                  ["\r","/r"],
                  ["\t","/t"],
                  ["\v","/v"],
                  ["\\","/"]]

    # replce each type of escape
    for old, new in lstReplace:
        input_string = input_string.replace(old, new)

    return input_string


# -------------------------------------------------------
# geometry
def point_sep(xy1, xy2):
    """ Return the distance between two x,y pairs.
        Inputs are either two strings consisting of a pair of space separated values
            (as returned from the shape.centroid property) or two lists, each of an x,y pair
        A float is returned.
    """
    try:
        if type(xy1) == type(xy2) == type([]):
            x1, y1 = xy1[0], xy1[1]
            x2, y2 = xy2[0], xy2[1]
        elif type(xy1) == type(xy2) == type(""):
            x1, y1 = xy1.split(" ")
            x2, y2 = xy2.split(" ")
            x1 = float(x1)
            y1 = float(y1)
            x2 = float(x2)
            y1 = float(y1)
        else:
            raise Exception("Non matching input types: " + str(xy1) + " and " + str(xy2))
        
        dist = sqrt(pow((x2-x1),2) + pow((y2-y1), 2))
        
        return dist
    
    except:
        raise

def point_sep2(x1, y1, x2, y2):
    """ Return the distance between two x,y pairs.
        A float is returned.
    """
    try:
        dist = sqrt(pow((x2-x1),2) + pow((y2-y1), 2))
        return dist
    except:
        raise

# -------------------------------------------------------
# Delete related    
def DeleteIntermediatesGlob(lstDel):
    print("\t\tDeleting intermediates...")
    for f in lstDel:
        try:
            for d in glob.glob(os.path.splitext(f)[0] + '.*'):
                os.remove(d)
        except:
            print(f + ' delete failed, skipping.')


def DeleteIntermediatesLstDir(lstDel):
    print('\tDeleting...' )
    t0 = time.time()
    strPath = os.path.dirname(lstDel[0])
    lstDel2 = [os.path.splitext(os.path.basename(F))[0] for F in lstDel]
    for f in os.listdir(strPath):
        if splitext2(f)[0] in lstDel2:
            try:
                os.remove(strPath + os.sep + f)
            except WindowsError:
                pass
            except:
                raise

