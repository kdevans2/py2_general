import os
#import arcpy
#from osgeo import gdal
#from osgeo.gdalconst import GDT_Float32

strGdalPath = r'C:\Python27\ArcGISx6410.3\Lib\site-packages\osgeo'
dicShortNameFormats = {'.dat': 'ENVI',
                       '.asc': 'AAIGrid',
                       '.bmp': 'BMP'}

def GetASCIIrasterSize(strPathASC, strMethod):
    """ function to get ascii raster size by various methods """
    
    lstMethodOK = ['GDAL', 'ARC', 'manual']
    
    if strMethod == 'GDAL':
        inDs = gdal.Open(strPathASC)
        intWidth = int(inDs.RasterXSize)
        intHeight = int(inDs.RasterYSize)
    elif strMethod == 'ARC':
        ext = arcpy.Describe(strPathASC).extent
        intWidth = int(ext.width)
        intHeight = int(ext.height)
    elif strMethod == 'manual':
        with open(strPathASC) as data:
            str1 = data.readline()
            str2 = data.readline()
        intWidth = int(str1.strip().split(' ')[1])
        intHeight = int(str2.strip().split(' ')[1])
    else:
        raise Exception, 'bad method value in GetASCrasterSize. Must be in ' + str(lstMethodOK)
    
    return intWidth, intHeight

def gdal_translateCMD(strPathIn, strPathOut, strAdlSwitches = None):
    """ Function gdal_translateCMD returns a string run at cmd line
        args:
            strPathIn =    input raster
            strPathOut =    output raster
            strAdlSwitches = optional additional switches

        see http://www.gdal.org/gdal_translate.html for switches
    """

    if not strAdlSwitches:
        strAdlSwitches = ""

    # outputFormat
    strEXT = strPathOut[-4:]
    if strEXT not in dicShortNameFormats.keys():
        raise KeyError, 'gdal_translateCMD KeyError: "' + strProj + '" not in shortname lookup'
    strShortName = dicShortNameFormats[strEXT]
    strOF = '-of ' + strShortName
    
    strbaseCMD = strGdalPath + os.sep + "gdal_translate"
    lstCMD = [strbaseCMD,
              strAdlSwitches,
              strOF,
              strPathIn,
              strPathOut]
    strCMD = " ".join(lstCMD)
    return strCMD


def gdal_translateCMD_crop(strPathIn, strPathOut, intCropSize, strMethod = None):
    """ Function gdal_translateCMD_crop returns a string run at cmd line
        args:
            strPathIn =    input raster
            strPathOut =    output ratser
            intCropSize = crop amount, units of pixel
    """
    if strMethod == None:
        strMethod = 'GDAL'

    # get array size
    intWidth, intHeight = GetASCIIrasterSize(strPathIn, strMethod)
    
    intCropWidthX = intWidth - 2 * intCropSize
    intCropWidthY = intHeight - 2 * intCropSize

    lstWin = [str(intCropSize), str(intCropSize), str(intCropWidthX), str(intCropWidthY)]
    strCropSwitch = '-srcwin ' + ' '.join(lstWin)
    # strCropSwitch = '-projwin ' + ' '.join(lstWin)
    strCMD = gdal_translateCMD(strPathIn, strPathOut, strCropSwitch)

    return strCMD

def gdalCopy(strRastIn, strRastOut):
    """function to copy a raster to other format"""
    
    # outputFormat
    strEXT = strRastOut[-4:]
    if strEXT not in dicShortNameFormats.keys():
        raise KeyError, 'gdal_translateCMD KeyError: "' + strEXT + '" not in shortname lookup'
    strShortName = dicShortNameFormats[strEXT]
    
    # get input
    dataset = gdal.Open(strRastIn)
    # copy
    driver = gdal.GetDriverByName(strShortName)
    dst_ds = driver.CreateCopy(strRastOut, dataset, 0 )
    
    # set null to close
    dst_ds = None
    dataset = None

def gdalEvenCrop(strRastIn, strRastOut, intCrop):
    """function to subset a raster and save output in ENVI dat format.
    requires ReadAsArray() which doesn't currently work!
    
    strRastIn: input raster, any format
    strRastOut: output raster, ENVI dat only
    intCrop: number of pixels to remove arround edge of image.
    """
    
    # get input
    inDs = gdal.Open(strRastIn)
    inBand = inDs.GetRasterBand(1)
    tupInGT = inDs.GetGeoTransform()
    
    # crop
    intWidthX = inDs.RasterXSize - 2 * intCrop
    intWidthY = inDs.RasterYSize - 2 * intCrop
    arrData = inBand.ReadAsArray(intCrop, intCrop, intWidthX, intWidthY)
    # create output GeoTransform
    fltMinX = tupInGT[0] + tupInGT[1]* intCrop
    fltMaxY = tupInGT[3] + tupInGT[5]* intCrop
    tupOutGT = (fltMinX, tupInGT[1], tupInGT[2], fltMaxY, tupInGT[4], tupInGT[5])

    # create output
    driver = gdal.GetDriverByName('ENVI')
    outDs = driver.Create(strRastOut, intWidthX, intWidthY, 1, GDT_Float32)
    outBand = outDs.GetRasterBand(1)
    # write array
    outBand.WriteArray(arrData, 0, 0)
    # save, set projection and transform
    outBand.FlushCache()
    outBand.SetNoDataValue(-9999)
    outDs.SetGeoTransform(tupOutGT)
    outDs.SetProjection(inDs.GetProjection())

    # set null to close
    inDs = None
    outDs = None

def gdalClip(strRastIn, strRastOut, lstExt):
    """function to subset a raster and save output in ENVI dat format.
    requires ReadAsArray() which doesn't currently work!
    
    strRastIn: input raster, any format
    strRastOut: output raster, ENVI dat only
    lstExt: space separated string, like ESRI: MinX MinY MaxX MaxY
    """
    #-------------------------
    # NOT TESTED!!
    strMinX, strMinY, strMaxX, strMaxY = lstExt.split(' ')
    fltMinX = float(strMinX)
    fltMinY = float(strMinY)
    fltMaxX = float(strMaxX)
    fltMaxY = float(strMaxY)
    
    # get input
    inDs = gdal.Open(strRastIn)
    inBand = inDs.GetRasterBand(1)
    tupInGT = inDs.GetGeoTransform()
    
    fltXPixelSize = abs(tupInGT[1])
    fltYPixelSize = abs(tupInGT[5])
    
    MinXpix = round((fltMinX - tupInGT[0]) / fltXPixelSize)
    MaxYpix = round((tupInGT[3] - fltMaxY) / fltYPixelSize)
    print MinXpix, MaxYpix
    
    intWidthX = round((fltMaxX - fltMinX) / fltXPixelSize)
    intWidthY = round((fltMaxY - fltMinY) / fltYPixelSize)
    print intWidthX, intWidthY
    
    # crop
    arrData = inBand.ReadAsArray(MinXpix, MaxYpix, intWidthX, intWidthY)
    # create output GeoTransform
    fltMinX = tupInGT[0] + tupInGT[1]* intCrop
    fltMaxY = tupInGT[3] + tupInGT[5]* intCrop
    tupOutGT = (fltMinX, tupInGT[1], tupInGT[2], fltMaxY, tupInGT[4], tupInGT[5])

    # create output
    driver = gdal.GetDriverByName('ENVI')
    outDs = driver.Create(strRastOut, intWidthX, intWidthY, 1, GDT_Float32)
    outBand = outDs.GetRasterBand(1)
    # write array
    outBand.WriteArray(arrData, 0, 0)
    # save, set projection and transform
    outBand.FlushCache()
    outBand.SetNoDataValue(-9999)
    outDs.SetGeoTransform(tupOutGT)
    outDs.SetProjection(inDs.GetProjection())

    # set null to close
    inDs = None
    outDs = None
    
