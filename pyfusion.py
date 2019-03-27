# primarily definitions to parse FUSION commands and arguments into a string that can then
#   be called os.system or similar means.
# also a few miscellaneous path (peculiar to storage of LiDAR data at R5 Remote Sensing
#   Lab), print and timing definitions.
#
# Kirk Evans, GIS Analyst, TetraTech EC @ USDA Forest Service R5/Remote Sensing Lab
#   3237 Peacekeeper Way, Suite 201
#   McClellan, CA 95652
#   kdevans@fs.fed.us
#
# for FUSION information and downloads:
#   http://forsys.cfr.washington.edu/fusion/fusionlatest.html


import sys, os, traceback
from time import time

#----------------------------------------------------------------------------------------
# def mkpath() moved to LiDARLib.py:
#----------------------------------------------------------------------------------------

# other functions
def print2(string, txt, boolQuiet = True):
    t = open(txt, 'a')
    t.write(string.strip() + '\n')
    t.close()
    if not boolQuiet:
        print(string)

def elapsed_time(t):
    """ funcion to return a string of format 'hh:mm:ss', representing time elapsed between
        establishing variable t (generally: t = time.time()) and funcion call.

        Result rounded to nearest second"""
    seconds = int(round(time() - t))
    h,rsecs = divmod(seconds,3600)
    m,s = divmod(rsecs,60)
    return str(h).zfill(2) + ":" + str(m).zfill(2) + ":" + str(s).zfill(2)
    #return zfill(h, 2) + ":" + zfill(m, 2) + ":" + zfill(s, 2)

def MakeTreeFC(strPathCSV, strPathOutFC , strPathProjFC):
    """ Function MakeTreeFC """

    import arcpy
    sys.path.append("M:/kirk/share/code/modules")
    import RSL_util10 as ut
    
    isFileGDB, strFC, strFCPath, strTPath = ut.splitPath(strPathOutFC)
    
    ut.message("creating " + strFC + " in " + strFCPath)
    arcpy.CreateFeatureclass_management(strFCPath, strFC, "POINT")
    ut.message("adding fields")
    arcpy.AddField_management(strPathOutFC, "height", "FLOAT")
    arcpy.AddField_management(strPathOutFC, "ID", "LONG")
    arcpy.AddField_management(strPathOutFC, "source", "Text", "100")

    lstPathCSV = strPathCSV.split(",")
    inttrees = 0
    ut.message("Adding records to " + strPathOutFC)
    intrees = arcpy.InsertCursor(strPathOutFC)
    for csv in lstPathCSV:
        trees = open(csv).readlines()
        intc = len(trees) -1 
        inttrees += intc
        ut.message("appending " + str(intc) + " record(s) from " + csv)
        for tree in trees[1:]:
            lstSplitline = tree.split(",")
            intree = intrees.newRow()
            pnt = arcpy.Point()
            
            intree.ID = int(lstSplitline[0])
            intree.height = lstSplitline[4]
            intree.source = csv
            pnt.X, pnt.Y = lstSplitline[1], lstSplitline[2]

            # Set the geometry of the new feature to the array of points
            intree.shape = pnt
            # Insert the feature
            intrees.insertRow(intree)

    print("\n" + str(inttrees) + " tree(s) total.")
        


# ----------------------------------------------------------------------------------------
# FUSION wrapper functions

# FUSION installation path
strPathInstal = "C:\\Fusion"

def CanopyModel(strPathLAS, strPathDTM, fltCellSize, strUTMZone, strPathBEFile = None, strAdlSwitches = None):
    """Function CanopyModel
        args:
            strPathLAS =    input LAS file
            strPathDTM =    output canopy surface/height dtm
            fltCellSize =   cell size in map units
            strUTMZone = utm zone
            strPathBEFile = optional bare earth dtm
            strAdlSwitches= optional additional switches

        Command Syntax: CanopyModel [switches] surfacefile cellsize xyunits zunits coordsys zone horizdatum vertdatum datafile1 datafile2
    """
    strPathBE = ""
    if strPathBEFile:
        strPathBE = '/ground:' + strPathBEFile
    strSwitches = strPathBE
    if strAdlSwitches:
        strSwitches = strSwitches + ' ' + strAdlSwitches
    strParams = str(fltCellSize) + ' M M 1 ' + str(strUTMZone) + ' 2 2'
    lstCMD = [strPathInstal + os.sep + "CanopyModel",
              strSwitches,
              strPathDTM,
              strParams,
              strPathLAS]
    strCMD = ' '.join(lstCMD)
    return strCMD


def CanopyHeight(strPathLAS, strPathDTM, fltCellSize, strPathBEFile, strUTMZone, strAdlSwitches = None, strParamBoss = None):
    """Function CanopyModel
        args:
            strPathLAS =    input LAS file
            strPathDTM =    output canopy surface/height dtm
            fltCellSize =   cell size in map units
            strPathBEFile = bare earth dtm
            strUTMZone = utm zone
            strAdlSwitches= optional additional switches

        Command Syntax: CanopyModel [switches] surfacefile cellsize xyunits zunits coordsys zone horizdatum vertdatum datafile1 datafile2
    """
    strSwitches = '/ground:' + strPathBEFile
    if strAdlSwitches:
        strSwitches = strSwitches + ' ' + strAdlSwitches
    if strParamBoss:
        strParams = strParamBoss
    else:
        strParams = str(fltCellSize) + ' M M 1 ' + str(strUTMZone) + ' 2 2'
    lstCMD = [strPathInstal + os.sep + 'CanopyModel',
              strSwitches,
              strPathDTM,
              strParams,
              strPathLAS]
    strCMD = ' '.join(lstCMD)
    return strCMD



def DTM2ASCII(strPathDTM, strPathASC, strSwitches = None):
    """Function DTM2ASCII
        args:
            strPathDTM =    input DTM
            strPathASC =    output ASC raster
            strSwitches : optional switches, mainly for /raster
        Command Syntax: DTM2ASCII [switches] inputfile [outputfile]
    """
    if not strSwitches:
        strSwitches = ""
    strbaseCMD = strPathInstal + os.sep + "DTM2ASCII"
    lstCMD = [strbaseCMD,
              strSwitches,
              strPathDTM,
              strPathASC]
    strCMD = ' '.join(lstCMD)
    return strCMD


def ASCII2DTM(strPathASC, strPathDTM, strUTMZone, strparams = None):
    """Function ASCII2DTM
        args:
            strPathASC = input ASC raster
            strPathDTM = output DTM
            strUTMZone = utm zone
            strparams = optional paraeters to override standard params (uncommon)
        Command Syntax: ASCII2DTM [switches] surfacefile xyunits zunits coordsys zone horizdatum vertdatum gridfile
    """
    if not strparams:
        strparams = 'm m 1 ' + str(strUTMZone) + ' 2 2'
    lstCMD = [strPathInstal + os.sep + "ASCII2DTM",
              strPathDTM,
              strparams,
              strPathASC]
    strCMD = ' '.join(lstCMD)
    return strCMD


def CanopyMaxima(strPathDTM ,strPathTreesTxt, fltThreshVal = "5.0", strWSEVal = "2.357,0.1219,0.0009,0", strPathBEFile = ""):
    """Function CanopyMaxima
        args:
            strPathDTM =        input canopy surface DTM to search
            strPathTreesTxt =   output text tree list, csv format
            fltThreshVal =      OPTIONAL, minimum height tree to consider in map units, default = 5 
            strWSEVal =         OPTIONAL, coefficients describing shape of exclusion zone
            strPathBEFile =     OPTIONAL be dtm
            
    Command Syntax: CanopyMaxima [switches] inputfile outputfile
        SWITCHES:
            threshold:#
                Limit analysis to areas above a height of # units (default: 10.0).
            wse: A, B, C, D [, E, F]
                Constant and coefficients for the variable window size equation used to compute the window size given the canopy surface height window:
                width = A + B*ht + C*ht^2 + D*ht^3 + C*ht^4 + D*ht^5
                Defaults values are for metric units: A = 2.51503, B = 0, C = 0.00901, D = 0.
                Use A = 8.251, B = 0, C = 0.00274, D = 0 when using imperial units.

    see function parse_MaximaCoeff in LiDARLib.py for parsing of wse coefficient for other purposes.
    """
    strPathBE = ""
    if strPathBEFile:
        strPathBE = "/ground:" + strPathBEFile
    strWSE = "/wse:" + strWSEVal
    strThresh = "/threshold:" + str(float(fltThreshVal))
    strSwitches = strPathBE + " " + strWSE + " " + strThresh
    lstCMD = [strPathInstal + os.sep + "CanopyMaxima",
              strSwitches,
              strPathDTM,
              strPathTreesTxt]  
    strCMD = ' '.join(lstCMD)
    return strCMD

def GridMetrics(strPathLAS, strPathBEDTM , fltbottomcanopy, intCellSize, strPathOutRoot, strSwitches):
    """ Function GridMetrics
        args:

    Command Syntax: GridMetrics [switches] groundfile heightbreak cellsize outputfile datafile1
        SWITCHES:
    """
    lstCMD = [strPathInstal + os.sep + 'GridMetrics',
              strSwitches,
              strPathBEDTM,
              str(fltbottomcanopy),
              str(intCellSize),
              strPathOutRoot,
              strPathLAS]
    strCMD = ' '.join(lstCMD)
    return strCMD
    
def CSV2GRID(strPathInCSV, strPathOutASC, intCol):
    """ Function CSV2GRID
        args:

    Command Syntax: CSV2GRID [switches] inputfile column outputfile
    """
    lstCMD = [strPathInstal + os.sep + "CSV2GRID",
              strPathInCSV,
              str(intCol),
              strPathOutASC]
    strCMD = ' '.join(lstCMD)
    return strCMD
    
def IntensityImage(strPathInLAS, strPathOutImg, fltcellsize, strSwitches = None):
    """ Function IntensityImage
        args:

    Command IntensityImage [switches] CellSize ImageFile DataFile1 DataFile2
    """

    if not strSwitches:
        strSwitches = ""
    lstCMD = [strPathInstal + os.sep + "IntensityImage",
              strSwitches,
              str(fltcellsize),
              strPathOutImg,
              strPathInLAS]
    strCMD = ' '.join(lstCMD)
    return strCMD

def Cover(strPathInLAS, strPathBEDTM, strPathOutDTM, fltHeightBreak, fltCellSize, strUTMZone, strSwitches = None):
    """ Function Cover
        args

        Syntax Cover [switches] groundfile coverfile heightbreak cellsize xyunits zunits coordsys zone horizdatum vertdatum datafile1 datafile2...
    """
    if not strSwitches:
        strSwitches = ""
    strParams = str(fltCellSize) + ' M M 1 ' + str(strUTMZone) + ' 2 2'
    lstCMD = [strPathInstal + os.sep + "Cover",
              strSwitches,
              strPathBEDTM,
              strPathOutDTM,
              str(fltHeightBreak),
              strParams,
              strPathInLAS]
    strCMD = ' '.join(lstCMD)
    return strCMD
    
def Catalog(strPathInLAS, strPathBaseName, strSwitches = None):
    """ Function Catalog
        args

        Syntax Catalog [switches] datafile [catalogfile]
    """
    #"/firstdensity:900,6,8 /rawcounts /outlier"
    if not strSwitches:
        strSwitches = ""
    lstCMD = [strPathInstal + os.sep + "Catalog",
              strSwitches,
              strPathInLAS,
              strPathBaseName]
    strCMD = ' '.join(lstCMD)
    return strCMD

def ClipData(strPathInLAS, strPathOutLAS, lstExt, strSwitches = None):
    """ Function Catalog
        args
            lstExt: python list of form [MinX, MinY, MaxX, MaxY]
        Syntax ClipData [switches] InputSpecifier SampleFile [MinX, MinY, MaxX, MaxY]
    """
    if not strSwitches:
        strSwitches = ''
    lstCMD = [strPathInstal + os.sep + "ClipData",
              strSwitches,
              strPathInLAS,
              strPathOutLAS,
              ' '.join(lstExt)]
    strCMD = ' '.join(lstCMD)
    return strCMD

def LDA2LAS(strPathIn, strPathOut):
    """ Function LDA2LAS
        args
        LDA2LAS [switches] InputFile OutputFile
    """
    strPathIn = strPathIn.strip()
    lstCMD = [strPathInstal + os.sep + "LDA2LAS",
              strPathIn,
              strPathOut]
    strCMD = ' '.join(lstCMD)
    return strCMD
    
def GridSurfaceStats(strPathInDTM, strPathOutDTM, strSampleFactor, strSwitches = None):
    """ Function GridSurfaceStats
        args
        GridSurfaceStats [switches] inputfile outputfile samplefactor
    """
    if not strSwitches:
        strSwitches = ''
    lstCMD = [strPathInstal + os.sep + "GridSurfaceStats",
              strSwitches,
              strPathInDTM,
              strPathOutDTM,
              str(strSampleFactor)]
    strCMD = ' '.join(lstCMD)
    return strCMD
    
def ASCIIImport(strPathIn, strPathOut, strPathParamFile, strSwitches):
    """ function ASCIIImport
        args:
        ASCIIImport [switches] ParamFile InputFile [OutputFile]
    """
    if not strSwitches:
        strSwitches = ''
    lstCMD = [strPathInstal + os.sep + "ASCIIImport",
              strSwitches,
              strPathParamFile,
              strPathIn,
              strPathOut]
    strCMD = ' '.join(lstCMD)
    return strCMD
    
def FirstLastReturn(strLASIn, strBaseOut, strSwitches = None):
    """ function ASCIIImport
        args:
        FirstLastReturn [switches] OutputFile DataFile
    """
    if not strSwitches:
        strSwitches = ''
    lstCMD = [strPathInstal + os.sep + "FirstLastReturn",
              strSwitches,
              strBaseOut,
              strLASIn]
    strCMD = ' '.join(lstCMD)
    return strCMD

def ShowInPDQ(strPathLAS):
    """ function ShowInPDQ
        args:
        ShowInPDQ InputFile
    """
    lstCMD = [strPathInstal + os.sep + "PDQ",
              strPathLAS]
    strCMD = ' '.join(lstCMD)
    return strCMD

def LDA2LAS(InputFile, OutputFile):
    """ function LDA2LAS
        args:
        LDA2LAS InputFile, OutputFile
    """
    lstCMD = [strPathInstal + os.sep + "LDA2LAS",
              InputFile,
              OutputFile]
    strCMD = ' '.join(lstCMD)
    return strCMD

def GridSurfaceCreate(InputFile, OutputFile, fltCellSize, strUTMZone, strSwitches = None, strParams = None):
    """ function GridSurfaceCreate
        args:
        GridSurfaceCreate InputFile, OutputFile
    """
    if strParams:
        strParams = str(fltCellSize) + ' ' + strParams 
    else:
        strParams = str(fltCellSize) + ' m m 1 ' + str(strUTMZone) + ' 2 2'
    if not strSwitches:
        strSwitches = ''
    lstCMD = [strPathInstal + os.sep + "GridSurfaceCreate",
              strSwitches,
              OutputFile,
              strParams,
              InputFile]
    strCMD = ' '.join(lstCMD)
    return strCMD

def GroundFilter(InputFile, OutputFile, fltCellSize = None, strSwitches = None):
    """ function GridSurfaceCreate
        args:
        GroundFilter InputFile, OutputFile
    """

    if not fltCellSize:
        fltCellSize = 5
    if not strSwitches:
        strSwitches = ''
    lstCMD = [strPathInstal + os.sep + "GroundFilter",
              strSwitches,
              OutputFile,
              str(fltCellSize),
              InputFile]
    strCMD = ' '.join(lstCMD)
    return strCMD

def TreeSeg(InputFile, OutputRoot, fltHtThresh, strSwitches = None):
    """ function TreeSeg
        args:
        TreeSeg InputFile, OutputRoot, fltHtThresh
    """
    if not strSwitches:
        strSwitches = ''
    lstCMD = [strPathInstal + os.sep + "TreeSeg",
              strSwitches,
              InputFile,
              str(fltHtThresh),
              OutputRoot]
    
    strCMD = ' '.join(lstCMD)
    return strCMD
