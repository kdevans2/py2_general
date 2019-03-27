# LiDARLib primarily definitions and classes to parse liDAR library paths
# (peculiar to storage of LiDAR data at R5 Remote Sensing Lab)
#
# Kirk Evans, GIS Analyst, TetraTech EC @ USDA Forest Service R5/Remote Sensing Lab
#   3237 Peacekeeper Way, Suite 201
#   McClellan, CA 95652
#   kdevans@fs.fed.us

import sys, os, string
from time import time

# OK data types
lstFileTypeOK = ['las', 'laz']
strDefaultDrive = 'N'
strSequoiaDrive = 'B'
# LiDAR library base format
strBaseDir = r':\LiDAR'
strBaseDirALT = r':\p_data\temp_LiDAR'
strMasterIndexGDB = strDefaultDrive + r':\lidar\a_indices\LiDAR_indeces.gdb'
# project dictionary
dicLocationLookup = {'Atlantic2015':      ('NonFS', 'alb_r6'),
                     'Bagley2013':        ('SHF', 'u10'),
                     'BMEF2009':          ('LNF', 'u10'),
                     'BMEF2015':          ('LNF', 'u10'),
                     'BeanHill2012':      ('PNF', 'u10'),
                     'Blacksmith2012':    ('ENF', 'u10'),
                     'Blodgett2013':      ('ENF', 'u10'),
                     'BluffCreek2013':    ('SRF', 'u10'),
                     'Bull2012':          ('SNF', 'u11'),
                     'Burney2015':        ('LNF', 'u10'),
                     'CubComplex2009':    ('LNF', 'u10'),
                     'DeadmanCreek2013':  ('INF', 'u11'),
                     'Dinkey2010':        ('SNF', 'u11'),
                     'Dinkey2012':        ('SNF', 'u11'),
                     'EastBranchEastWeaver2012': ('SHF', 'u10'),
                     'EastForksScott2015':('KNF', 'u10'),
                     'ENF_Meadows2015':   ('ENF', 'u10'),
                     'FredsFire2015':     ('ENF', 'u10'),
                     'GopherHill2012':    ('PNF', 'u10'),
                     'GriderWalker2015':  ('KNF', 'u10'),
                     'HagerBasin2013':    ('MDF', 'u10'),
                     'HappyCampNorth2015':('KNF', 'u10'),
                     'HarrisMLV2013':     ('MDF', 'u10'),
                     'HorseCreek2016':    ('KNF', 'u10'),
                     'Humbug2013':        ('KNF', 'u10'),
                     'Illilouette2011':   ('NonFS\\Yosemite', 'u11'),
                     'IndianaSummit2014': ('INF', 'u11'),
                     'IshiKlamath2014':   ('SRF', 'u10'),
                     'KernPlateau2011':   ('INF', 'u11'),
                     'King2015':          ('ENF', 'u10'),
                     'LakeTahoe2010':     ('TMU', 'u10'),
                     'LonePine2015':      ('INF', 'u11'), # bad
                     'LonePine2015_b':    ('INF', 'u11'), # bad
                     'LowerElk2015':      ('KNF', 'u10'),
                     'LowerKlamath2014':  ('SRF', 'u10'),
                     'LowerKlamath2015':  ('SRF', 'u10'),
                     'MarbleValley2012':  ('KNF', 'u10'),
                     'MeadowValley2009':  ('PNF', 'u10'),
                     'MichiganBluff2013': ('TNF', 'u10'),
                     'MillFlatCreek2012': ('SQF', 'u11'),
                     'Moonlight2013':     ('PNF', 'u10'),
                     'MooresFlat2013':    ('TNF', 'u10'),
                     'MountBidwell2013':  ('MDF', 'u10'),
                     'MudCreek2015':      ('SHF', 'u10'),
                     'Mule2012':          ('MNF', 'u10'),
                     'Mule2013':          ('MNF', 'u10'),
                     'OakCreek2012':      ('INF', 'u11'),
                     'Panther-MarbleValleyAnnex2014':('KNF', 'u10'),
                     'Pendola2015':       ('PNF', 'u10'),
                     'PowerFire2015':     ('ENF', 'u10'),
                     'Providence2012':    ('SNF', 'u11'),
                     'Providence2013':    ('SNF', 'u11_84'),
                     'RimFire2013':       ('STF', 'u10'),
                     'Road462013':        ('MDF', 'u10'),
                     'SNAMP2009':         ('TNF', 'u10'),
                     'SNAMP2012':         ('TNF', 'u10'),
                     'SNAMP_SugarPine2012':('SNF', 'u11'),
                     'Sagehen2005':       ('TNF', 'u10'),
                     'Salmon2014':        ('KNF', 'SP_CA'),
                     'SanGabrielMtns2009':('ANF', 'u10'),
                     'SEKI_North2015':    ('NonFS', 'u11'),
                     'SEKI_South2015':    ('NonFS', 'u11'),
                     'SimsFire2012':      ('SRF', 'u10'),
                     'SJER2013':          ('SNF', 'u11_84'),
                     'SlidesGlade2013':   ('MNF', 'u10'),
                     'Smithsonian2013':   ('NonFS\\Yosemite', 'u10'),
                     'SnagHill2012':      ('SHF', 'u10'),
                     'Soaproot2013':      ('SNF', 'u11'),
                     'Sonoma2013':        ('NonFS', 'SP_CA2'),
                     'SouthCreek2012':    ('SQF', 'u11'),
                     'SquawCreek2013':    ('SHF', 'u10'),
                     'SquawCreek2015':    ('SHF', 'u10'),
                     'SSPM2016':          ('NonFS','u11_84'),
                     'STEF2015':          ('STF', 'u10'),
                     'Storrie2009':       ('LNF', 'u10'),
                     'Storrie2013':       ('LNF', 'u10'),
                     'Storrie2015':       ('LNF', 'u10'),
                     'SugarCreek2015':    ('KNF', 'u10'),
                     'SummitSprings2013': ('MNF', 'u10'),
                     'TeaKettle2013':     ('SNF', 'u11_84'),
                     'ThomasFire':        ('NonFS', 'u11'),
                     'TNF1314':           ('TNF', 'u10'),
                     'TNF2013':           ('TNF', 'u10'),
                     'TNF2014':           ('TNF', 'u10'),
                     'Taliaferro2012':    ('MNF', 'u10'),
                     'Taliaferro2013':    ('MNF', 'u10'),
                     'TroutAnnex2013':    ('SHF', 'u10'),
                     'TroutCreek2012':    ('SHF', 'u10'),
                     'VanVleck2015':      ('ENF', 'u10'),
                     'WillowCreek2012':   ('SNF', 'u11')}

def mkpath(strProj, strDrive = None):
    """ Return project path. """
    if strProj not in dicLocationLookup.keys():
        raise KeyError('mkpath KeyError: "' + strProj + '" not in project lookup')
    strForest, strProjection = dicLocationLookup[strProj]
        
    if strDrive:
        strBaseDir2 = strDrive + strBaseDir
    else:
        strBaseDir2 = strDefaultDrive + strBaseDir
             
    strProjPath = strBaseDir2 + os.sep + strForest + os.sep + strProj
    return (strProjPath, strProjection)

class TileObj:
    """ Class TileObj containing LiDAR file properties. """
    def __init__(self, strPathLAS, strDataTileStyle = 'UTM'):
        strPathLAS = strPathLAS.strip()
        self.DTileStyle = strDataTileStyle

        self.path = strPathLAS
        self.location, self.base = os.path.split(strPathLAS)
        self.ID, strExt = os.path.splitext(self.base)
        
        strExt = strExt[1:].lower()
        
        if strExt not in lstFileTypeOK:
            raise Exception("Invalid LiDAR data type, must be in: " + str(lstFileTypeOK))
        self.FType = strExt
        
        while self.ID[0] in string.ascii_letters:
            self.ID = self.ID[1:]

        strLeft, strBottom = self.ID.split('_')
        self.left   = int(strLeft)
        self.bottom = int(strBottom)
        self.right  = self.left + 1000
        self.top    = self.bottom + 1000

        self.XMin = self.left
        self.XMax = self.right
        self.YMin = self.bottom
        self.YMax = self.top
            
        if self.DTileStyle == 'UTM':
            c, r = self.ID.split('_')
            self.QID = c[:-4] + '_' + r[:-4]
        elif self.DTileStyle == 'USGS':
            self.QID = self.ID[:7]

class LibraryPaths:
    """ Class LibraryPaths containing project specific library paths and other naming conventions. """
    def __init__(self, strProj, strDrive = None, strFileType = 'laz', strSub = None, strDataTileStyle = 'UTM', strBETileStyle = 'unique'):
        self.lstDataTileStyleOK = ['UTM', 'USGS']
        self.lstBETileStyleOK = ['unique', 'quad', 'single']
        
        if strFileType not in lstFileTypeOK :
            raise Exception("Invalid LiDAR file type, must be in: " + str(lstFileTypeOK))
        self.FType = strFileType
        
        if strDataTileStyle not in self.lstDataTileStyleOK :
            raise Exception("Invalid data tiling style, must be in: " + str(self.lstDataTileStyleOK))
        self.DTileStyle = strDataTileStyle
        
        if strBETileStyle not in self.lstBETileStyleOK:
            raise Exception("Invalid BE dtm tiling scheme, must be in: " + str(self.lstBETileStyleOK))
        self.strBEStyle = strBETileStyle

        if strSub:
            self.Sub = strSub
        else:
            self.Sub = 'all'
        
        # get path and projection
        strProjPath, strProjection = mkpath(strProj, strDrive)
        # set projection
        self.ProjCode = strProjection
        if self.ProjCode == 'u10':
            self.Projection = "PROJCS['NAD_1983_UTM_Zone_10N',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-123.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"
            self.UTMcode = '10'
        elif self.ProjCode == 'u11':
            self.Projection = "PROJCS['NAD_1983_UTM_Zone_11N',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['False_Easting',500000.0],PARAMETER['False_Northing',0.0],PARAMETER['Central_Meridian',-117.0],PARAMETER['Scale_Factor',0.9996],PARAMETER['Latitude_Of_Origin',0.0],UNIT['Meter',1.0]]"
            self.UTMcode = '11'
        elif self.ProjCode == 'u11_84':
            self.Projection = "PROJCS['WGS_1984_UTM_zone_11N',GEOGCS['GCS_WGS_1984',DATUM['D_WGS_1984',SPHEROID['WGS_1984',6378137.0,298.257223563]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Transverse_Mercator'],PARAMETER['false_easting',500000.0],PARAMETER['false_northing',0.0],PARAMETER['central_meridian',-117.0],PARAMETER['scale_factor',0.9996],PARAMETER['latitude_of_origin',0.0],UNIT['Meter',1.0]]"
            self.UTMcode = '11'
        elif self.ProjCode == 'alb_r6':
            self.Projection = "PROJCS['NAD_1983_USFS_R6_Albers',GEOGCS['GCS_North_American_1983',DATUM['D_North_American_1983',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Albers'],PARAMETER['false_easting',600000.0],PARAMETER['false_northing',0.0],PARAMETER['central_meridian',-120.0],PARAMETER['standard_parallel_1',43.0],PARAMETER['standard_parallel_2',48.0],PARAMETER['latitude_of_origin',34.0],UNIT['Meter',1.0]]"
            self.UTMcode = '0'
        elif self.ProjCode == 'SP_CA2':
            self.Projection = "PROJCS['NAD_1983_HARN_StatePlane_California_II_FIPS_0402_Feet',GEOGCS['GCS_North_American_1983_HARN',DATUM['D_North_American_1983_HARN',SPHEROID['GRS_1980',6378137.0,298.257222101]],PRIMEM['Greenwich',0.0],UNIT['Degree',0.0174532925199433]],PROJECTION['Lambert_Conformal_Conic'],PARAMETER['False_Easting',6561666.666666666],PARAMETER['False_Northing',1640416.666666667],PARAMETER['Central_Meridian',-122.0],PARAMETER['Standard_Parallel_1',38.33333333333334],PARAMETER['Standard_Parallel_2',39.83333333333334],PARAMETER['Latitude_Of_Origin',37.66666666666666],UNIT['Foot_US',0.3048006096012192]]"
            self.UTMcode = '0'
            
        # main path
        self.p = strProjPath + os.sep

        # path subdirectories
        # Raw
        self.pR = self.p + 'Raw' + os.sep
        self.pRdtm = self.pR + 'DTM' + os.sep
        self.pRdtmBE = self.pRdtm + 'BareEarth' + os.sep
        self.pRdtmCA = self.pRdtm + 'Canopy' + os.sep
        self.pRpnts = self.pR + 'Points' + os.sep
        self.pRpntsBE = self.pRpnts + 'BareEarth' + os.sep
        self.pRpntsLAS = self.pRpnts + 'FullCloud' + os.sep
        self.pRpntsTLAS = self.pRpnts + 'tiled_LAS' + os.sep
        self.pRpntsTLAZ = self.pRpnts + 'tiled_LAZ' + os.sep
        self.pRsts = self.pR + 'Stats' + os.sep
        # Final
        self.pF = self.p + 'Final' + os.sep
        self.pFvect = self.pF + 'Vectors' + os.sep
        self.pFvectGDB = self.pF + 'Vectors' + os.sep + 'working.gdb' + os.sep
        self.pFvectTAO = self.pFvect + 'TAOs' + os.sep
        self.pFrast = self.pF + 'Rasters' + os.sep
        self.pFrastBE = self.pFrast + 'BareEarth' + os.sep
        self.pFrastBEw = self.pFrastBE + 'working' + os.sep
        self.pFrastCA = self.pFrast + 'Canopy' + os.sep
        self.pFrastCAw = self.pFrastCA + 'working' + os.sep
        self.pFrastCAd = self.pFrastCA + 'derivatives' + os.sep
        self.pFrastINT = self.pFrast + 'Intensity' + os.sep
        self.pFrastINTw = self.pFrastINT + 'working' + os.sep
        self.pFrastSTS = self.pFrast + 'Stats' + os.sep
        self.pFrastQQ = self.pFrast + 'catalogQAQC' + os.sep
        # Change to local working dirs if present
        strDProjPath = mkpath(strProj, strSequoiaDrive)[0]
        if strProjPath != strDProjPath and os.path.exists(strDProjPath):
            self.pFrastBEw = self.pFrastBEw.replace(strProjPath, strDProjPath)
            self.pFrastCAw = self.pFrastCAw.replace(strProjPath, strDProjPath)
            self.pFrastINTw = self.pFrastINTw.replace(strProjPath, strDProjPath)
        
        # text lists
        self.LasList = self.pRpnts + self.Sub + '_' + self.FType + '.txt'
        self.BEDTMList = self.pRdtm + self.Sub + '_BE_list.txt'
        self.TiledLasList = self.pRpnts + self.Sub + '_' + self.FType + '_tiled.txt'
        
        # feature classes
        if self.Sub == 'all':
            self.IndexFC =        strMasterIndexGDB + os.sep + strProj + '_index'
            self.IndexFC_retile = strMasterIndexGDB + os.sep + strProj + '_retileUTM'
        else:
            self.IndexFC =        self.pFvectGDB + os.sep + strProj + '_index_' + self.Sub
            self.IndexFC_retile = self.pFvectGDB + os.sep + strProj + '_retileUTM' + self.Sub
        self.BoundaryFC = strMasterIndexGDB + os.sep + strProj + '_bnd'

    def GetBEdtm(self, strPathLAS):
        """ Return bare earth dtm for tile based on strBEStyle property. """
        objT = TileObj(strPathLAS, self.DTileStyle)
        if self.strBEStyle == 'unique':
            strPathBEDTM = self.pRdtmBE + 'be_' + objT.ID + '_1.dtm'
        elif self.strBEStyle == 'quad':    
            strPathBEDTM = self.pRdtmBE + 'be_' + objT.QID + '_1.dtm'
        elif self.strBEStyle == 'single': 
            strPathBEDTM = self.pRdtmBE + 'be_' + self.Sub +'_1.dtm'
        return strPathBEDTM

    def GetBEdtmTest(self, strPathLAS):
        """ Return smallest existing bare earth dtm.  """
        objT = TileObj(strPathLAS, self.DTileStyle)

        lstBEDTM = [self.pRdtmBE + 'be_' + objT.ID + '_1.dtm',
                    self.pRdtmBE + 'be_' + objT.QID + '_1.dtm',
                    self.pRdtmBE + 'be_' + self.Sub + '_1.dtm' ,
                    self.pRdtmBE + 'be_all_1.dtm']

        for strPathBEDTM in lstBEDTM:
            if os.path.exists(strPathBEDTM):
                return strPathBEDTM

        raise Exception("No suitable BE DTM found.")
        
    def GetBEdtm_fromID(self, strID):
        strPathBEDTM = self.pRdtmBE + 'be_' + ID + '_1.dtm'
        return strPathBEDTM
        
    
#----------------------------------------------------------------------------------------

# other functions
def print2(string, txt, boolQuiet = None):
    with open(txt, 'a') as t:
        t.write(string.strip() + '\n')
    if not boolQuiet:
        print(string)

def elapsed_time(t):
    """ Return a string of format 'hh:mm:ss', representing time elapsed between
        establishing variable t (generally: t = time.time()) and funcion call.

        Result rounded to nearest second.
    """
    seconds = int(round(time() - t))
    h,rsecs = divmod(seconds,3600)
    m,s = divmod(rsecs,60)
    str(h).zfill(2) + ":" + str(m).zfill(2) + ":" + str(s).zfill(2)

def parse_MaximaCoeff(strCoeff):
    """ Return a widely acceptable (dir and file names, feature classes, etc) name
        based on FUSION CanopyMaxima wse coefficient string.
        Removes commas (from FUSION string format), and periods and minus signs.
        Also works other way: general to FUSION
    """
    if ',' in strCoeff:
        lstCoeff = strCoeff.split(',')
        lstCoeffOut = []
        
        for coeff in lstCoeff:
            coeffOut = coeff.replace('.', 'p')
            if float(coeff) < 0:
                coeffOut = 'n' + coeffOut[1:]
            lstCoeffOut.append(coeffOut)
            
        return '_'.join(lstCoeffOut)
    
    elif '_' in strCoeff:
        lstCoeff = strCoeff.split(',')
        lstCoeffOut = []
        
        for coeff in lstCoeff:
            coeffOut = coeff.replace('p', '.')
            if coeff[0] == n:
                coeffOut = '-' + coeffOut[1:]
            lstCoeffOut.append(coeffOut)
                
        return ','.join(lstCoeffOut)
    
    else:
        raise Exception('strCoeff not recognizable')

def assemble_MaximaRoot(strCoeff, fltThresh, fltCellSize, intSmoothSize = 0):
    """ Return an string describing CanopyMaxima settings in folder, file and
        feature class names. """
    strCoeff_P = parse_MaximaCoeff(strCoeff)
    strThresh_P = 't' + str(fltThresh).replace('.', 'p')
    strCellSize_P =  str(fltCellSize).replace('.', 'p')
    strRoot = strCoeff_P + '__' + strThresh_P + '_' + strCellSize_P 
    if intSmoothSize:
        strRoot = strRoot + '_smooth' + str(intSmoothSize)

    return strRoot
        
def parse_MaximaRoot(strRoot):
    """ Return the setting components of CanopyMaxima root string. """
    strCoeff_P, strRest = strRoot.split('__')
    lstRest = strRest.split('_')
    
    strCoeff = parse_MaximaCoeff(strCoeff_P)
    fltThresh = float(lstRest[0].replace('.', 'p'))
    strCellSize = lstRest[1].replace('.', 'p')
    if strCellSize[0] == 'c':
        strCellSize = strCellSize[1:]
        print('WARNING "c" prefix present with cell size in strRoot. Not recommended.')
    fltCellSize = float(strCellSize) 
    
    if len(lstRest) == 2:
        intSmoothSize = 0
    elif len(lstRest) == 3:
        intSmoothSize = int(lstRest[1][6:])
    else:
        raise Exception('strRoot (non coeff portion) not recognizable')

    return strCoeff, fltThresh, fltCellSize, intSmoothSize
