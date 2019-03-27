from numpy import *
import copy, os, traceback, sys
import RSL_util10 as ut

class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class RasterObjError(Error):
    """ Exception for passing back detailed errors from raster object module
        call:   tb = sys.exc_info()[2]
                raise RasterObjError("blahblah", [tb, str(sys.exc_type), str(sys.exc_value)])
    Attribute:
        message:    explanation of the error
        details:    traceback and sys details
    """    
    def __init__(self, message, details):
        # RasterObjError module errors
        moduletb, etype, evalue = details
        moduletbinfo = traceback.format_tb(moduletb)[0]
        ut.error("\n" + message)
        modulemsg = "RasterObjError Module ERROR Traceback Info:\n  "  + moduletbinfo + "    " + etype + ": " + evalue
        ut.error(modulemsg)
    
class rasterobject:
    """ raster object for lidar work
        raster type to be read in is ascii
    """
    def __init__(self, strPathRast, ingest = True):
        try:
            self.source = strPathRast
            with open(strPathRast) as inImage:
                self.lstheader = []
                for i in range(6):
                    self.lstheader.append(inImage.readline().strip())
                    
                if 0:
                    self.intcols =        int(self.lstheader[0][14:]) # number of cols (x)
                    self.introws =        int(self.lstheader[1][14:]) # number of rows (y)
                    self.fltxll =       float(self.lstheader[2][14:]) # lower left x
                    self.fltyll =       float(self.lstheader[3][14:]) # lower left y
                    self.fltcellesize = float(self.lstheader[4][14:]) # cell size
                    self.fltNODATA =    float(self.lstheader[5][14:]) # NODATA value
                else:
                    self.intcols =        int(self.lstheader[0].split(" ")[1]) # number of cols (x)
                    self.introws =        int(self.lstheader[1].split(" ")[1]) # number of rows (y)
                    self.fltxll =       float(self.lstheader[2].split(" ")[1]) # lower left x
                    self.fltyll =       float(self.lstheader[3].split(" ")[1]) # lower left y
                    self.fltcellesize = float(self.lstheader[4].split(" ")[1]) # cell size
                    self.fltNODATA =    float(self.lstheader[5].split(" ")[1]) # NODATA value

                if ingest:
                    self.data = zeros((self.introws,self.intcols), dtype=float, order='C')
                    for i in range(self.introws):
                        self.data[i] = inImage.readline().strip().split(" ")
        except:
            tb = sys.exc_info()[2]
            raise RasterObjError("error in class 'rasterobject'", [tb, str(sys.exc_type), str(sys.exc_value)])
    
    def GetCoordIndex(self, lstcoord):
        """ convert from coordinate values to index values for cell lookup 
        """
        ix = (lstcoord[0] - self.fltxll) / self.fltcellesize
        iy = (self.fltyll + self.introws * self.fltcellesize - lstcoord[1]) / self.fltcellesize
        return [int(ix), int(iy)]
    
    def GetCellValueByIndex(self, lstind):
        """ retreive value at specified location (column, row i.e x,y) 
        """
        try:
            return self.data[lstind[1],lstind[0]]
        except IndexError:
            return self.fltNODATA
        
    def GetCellValueByCoord(self, lstcoord):
        """ retreive value at specified location given x y coords (x,y) 
        """
        lstind = self.GetCoordIndex(lstcoord)
        return self.GetCellValueByIndex(lstind)

    def AssembleHeader(self):
        """ Assemble header information for use by 'SaveSelf' functions
        """
        strheader = "\n".join(self.lstheader) + "\n"
        return strheader
        
    def SaveSelf(self):
        """ convert from coordinate values to index values for cell lookup 
        """
        if self.source: 
            outfile = open(self.source, "w")
            outfile.write(self.AssembleHeader())
            for i in range(self.data.shape[0]):
                lstline = []
                for j in self.data[i]:
                    lstline.append(str(j))
                outfile.write(" ".join(lstline) + "\n")
            outfile.close()               
            return strPathoutfile
        else:
            raise Exception, "self.source not defined. use SaveSelfAs"

    def SaveSelfAs(self, strPathoutfile):
        outfile = open(strPathoutfile, "w")
        outfile.write(self.AssembleHeader())
        for i in range(self.data.shape[0]):
            lstline = []
            for j in self.data[i]:
                lstline.append(str(j))
            outfile.write(" ".join(lstline) + "\n")
        outfile.close()               
        return strPathoutfile

    def ApplyKernel(self, arrKern, BoolNormalize = False):
        for n in arrKern.shape:
            if n%2 <> 1:
                raise Exception, "irregular kernel shape. shape must be odd"
        r,c = arrKern.shape
        gr, gc = array([r,c])/2
        arrout = self.data.copy()
        for j in range(gr,self.introws - gr):
            for i in range(gc,self.introws - gc):
                if self.data[j,i] == self.fltNODATA:
                    continue
                arrsub = self.data[j-gr:j+gr+1, i-gc:i+gc+1]
                #if self.fltNODATA in arrsub
                arrout[j,i] = sum(arrsub * arrKern)

        if BoolNormalize:
            for j in range(gr,self.introws - gr):
                for i in range(gc,self.introws - gc):
                    if self.data[j,i] == self.fltNODATA:
                        continue
                #if self.fltNODATA in arrsub
                arrout[j,i] = arrout[j,i] / arrKern.sum()

        self.data = arrout
        

def MakeShell(templaterast, value = None):
    outrast = copy.deepcopy(templaterast)
    if value is None:
        value = templaterast.fltNODATA
    outrast.data.fill(value)
    outrast.source = None
    return outrast

def MakeCopy(templaterast):
    outrast = copy.deepcopy(templaterast)
    return outrast

def readARCkernel(strPathKern):
    inFile = open(strPathKern)
    lstdim = inFile.readline().strip().split(" ")
    tupdim = (lstdim[1], lstdim[0])
    a = zeros(tupdim, dtype=float, order='C')
    for i in range(lstdim[1]):
        a.data[i] = inFile.readline().strip().split(" ")
    return a

def rasterfail():
    pass

