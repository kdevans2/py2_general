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
    """ funcion to return a string of format 'hh:mm:ss', representing time
        elapsed between t0 and funcion call, rounded to nearest second"""
    seconds = int(round(time.time() - t))
    h,rsecs = divmod(seconds,3600)
    m,s = divmod(rsecs,60)
    return str(h).zfill(2) + ":" + str(m).zfill(2) + ":" + str(s).zfill(2)

def splitext2(f):
    i = f.index('.')
    return [f[:i], f[i:]]

def message(string):
    print(string)
    arcpy.AddMessage(string)

def warning(string):
    print(string)
    arcpy.AddWarning(string)
    
def error(string):
    print(string)
    arcpy.AddError(string)

def print2(string, txt, boolQuiet = None):
    ''' print function plus log to txt.
        optionally supress print. '''
    if boolQuiet is None:
        boolQuiet = True
        
    with open(txt, 'a') as t:
        t.write(string.strip() + '\n')
        
    if not boolQuiet:
        print(string)
        

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


def splitPath(strPathFC):
    """ function to separate path and FC variables and determine GDB vs. MDB
        usage:
            isFileGDB, strFC, strFCPath, strTPath = ut.splitPath(strPathFC)
        where:
            isFileGDB = 1 or 0 int,
            strFC =  feature class name,
            strFCPath = feature class worskpace,
            strTPath = workspace for tables = strFCPath w/o feature dataset"""

    try:
        if ".gdb" in strPathFC:
            isFileGDB = True
            intind = strPathFC.index(".gdb")
        elif ".mdb" in strPathFC:
            isFileGDB = False
            intind = strPathFC.index(".mdb")
        else:
            return "", "", "", ""
        
        # set path and fc name
        strFC = strPathFC[intind + 5:]
        strTPath = strPathFC[:intind + 4]
        strFCPath = strTPath
        # if fc in in feature dataset, then account for
        intind2 = strFC.find("/")
        if intind2 != -1:
            strFCPath = strFCPath + "/" + strFC[:intind2]
            strFC = strFC[intind2 + 1:]
            
        return isFileGDB, strFC, strFCPath, strTPath
    
    except:
        raise

def splitPath2(strPathFC):
    """ function to separate path and FC variables and determine GDB vs. MDB
        functional for both layer and feature class input types
        usage:
            isFileGDB, strFC, strFCPath, strTPath = RSL_util.splitPath(strPathFC)
        where:
            isFileGDB = 1 or 0 int,
            strFC =  feature class name,
            strFCPath = feature class worskpace,
            strTPath = workspace for tables = strFCPath w/o feature dataset"""

    try:
        desc = arcpy.Describe(strPathFC)
        if desc.DataType == "FeatureLayer":
            strPathFC = formatPath(desc.CatalogPath)
        
        if ".gdb" in strPathFC:
            isFileGDB = True
            intind = strPathFC.index(".gdb")
        elif ".mdb" in strPathFC:
            isFileGDB = False
            intind = strPathFC.index(".mdb")
        else:
            return "", "", "", ""
        
        # set path and fc name
        strFC = strPathFC[intind + 5:]
        strTPath = strPathFC[:intind + 4]
        strFCPath = strTPath
        # if fc in in feature dataset, then account for
        intind2 = strFC.find("/")
        if intind2 != -1:
            strFCPath = strFCPath + "/" + strFC[:intind2]
            strFC = strFC[intind2 + 1:]
            
        return isFileGDB, strFC, strFCPath, strTPath
    
    except:
        raise


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
# Table related
def addfieldtype(strTable,strField):
    ''' Return field type string as used as addfield keyword. '''
    dictFieldType = {"String":"Text",
                     "Integer":"Long",
                     "SmallInteger":"Short",
                     "OID":"OID",
                     "Geometry":"Geometry",
                     "Single":"Float",
                     "Double":"Double",
                     "Date":"Date",
                     "Blob":"Blob"}
    try:
        fld = arcpy.ListFields(strTable, strField)
        if fld:
            strtype = dictFieldType[fld[0].type]
            return strtype
        else:
            raise Exception("field: " + strField + " not found.")
    except:
        raise

    
def Table2CSV(strPathFC, strPathCSV, lstFields = None, bolAddLine = False):
    ''' Export feature class table to CSV text
        Lame work around for failing arcpy.CopyRows function.
        lstFields: optional list of output fields. Default is all fields except the geometry field.
        bolAddLine: option to add additional linefeed. Needed for reading in R. 
    '''
    if lstFields is None:
        lstFields = [f.name for f in arcpy.ListFields(strPathFC) if f.type != 'Geometry']

    with arcpy.da.SearchCursor(strPathFC, lstFields) as rows:
        with open(strPathCSV, 'wb') as csvfile:
            spamwriter = csv.writer(csvfile, delimiter=',')
            spamwriter.writerow(lstFields)
            for row in rows:
                try:
                    spamwriter.writerow(row)
                except:
                    print(row)
                    raise
            if bolAddLine:
                csvfile.write('\n')

                
# -------------------------------------------------------
# Raster related
def Round(rastIn):
    ''' Function to round spatial analyst rasters.
        Curently only for positive values.
    '''
    rastUp = arcpy.sa.RoundUp(rastIn)
    rastDown = arcpy.sa.RoundDown(rastIn)

    rastOut = arcpy.sa.Con( (rastUp - rastIn) <= 0.5, rastUp, rastDown)
    return arcpy.sa.Int(rastOut)


# -------------------------------------------------------
# Delete related
def DeleteIntermediates(lstDel):
    print("\t\tDeleting intermediates...")
    for f in lstDel:
        try:
            arcpy.Delete_management(f)
        except:
            print(f + ' delete failed skipping')

            
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

