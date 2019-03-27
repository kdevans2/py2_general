import os, numpy, arcpy, time
from multiprocessing import Process, Queue, current_process, freeze_support

def elapsed_time(t):
    """ Return a string of format 'hh:mm:ss', representing time elapsed between
        t (generally: t = time.time()) and funcion call.

        Result rounded to nearest second"""
    seconds = int(round(time.time() - t))
    h,rsecs = divmod(seconds,3600)
    m,s = divmod(rsecs,60)
    return str(h).zfill(2) + ":" + str(m).zfill(2) + ":" + str(s).zfill(2)

# Function run by worker processes
def worker(input, output):
    for func, args in iter(input.get, 'STOP'):
        result = calculate(func, args)
        output.put(result)
        
# Function used to calculate result
def calculate(func, args):
    result = func(args)
    return result

# OS system calls
def submit(arg):
    os.system(cmd)
    return 'Done, submit'

def submitmulti(lstargs):
    lstcmds, strComment = lstargs
    t0 = time.time()
    for cmd in lstcmds:
        os.system(cmd)
    t = elapsed_time(t0)
    return strComment + ", " + t

def GM_rasterize(lstargs):
    strPathCSV, intIndex, strPathOut, intCellSizeMult, strComment = lstargs
    t0 = time.time()
    strPathHead = strPathCSV[:-4] + '_ascii_header.txt'
    
    with open(strPathHead) as txt:
        lstVals = [float(x.strip().split(' ')[1]) for x in txt.readlines()]
    intCols, intRows, fltMinX, fltMinY, fltCS, fltNoData = lstVals

    l = []
    with open(strPathCSV) as txt:
        for line in txt.readlines()[1:]:
            l.append(float(line.split(',')[intIndex - 1]))

    # make values into array, reshape    
    a = numpy.reshape(numpy.array(l), (intRows,intCols))
    a = a[intCellSizeMult:-intCellSizeMult, intCellSizeMult:-intCellSizeMult]
    fltMinX = fltMinX - fltCS/2 + intCellSizeMult * fltCS
    fltMinY = fltMinY - fltCS/2 + intCellSizeMult * fltCS
    rasOut = arcpy.NumPyArrayToRaster(a, arcpy.Point(fltMinX, fltMinY), fltCS, fltCS, fltNoData)
    arcpy.CopyRaster_management(rasOut, strPathOut)
    del rasOut
    t = elapsed_time(t0)
    return strComment + ", " + t

def SaveBand(lstargs):
    t0 = time.time()
    strPathIn, strPathOut, strComment = lstargs
    arcpy.CopyRaster_management(strPathIn, strPathOut)
    t = elapsed_time(t0)
    return strComment + ", " + t

def ClipRaster(lstargs):
    t0 = time.time()
    strPathIn, strPathOut, strBND, strComment = lstargs
    strPathInter = strPathOut[:-4] + '_temp.img'
    arcpy.env.pyramid = 'NONE'
    #arcpy.ASCIIToRaster_conversion(in_ascii_file=strPathIn, out_raster=strPathInter, data_type="FLOAT")
    arcpy.Clip_management(strPathIn, strBND, strPathOut)
    #arcpy.Delete_management(strPathInter)
    t = elapsed_time(t0)
    return strComment + ", " + t

def CropRaster(lstargs):
    t0 = time.time()
    strPathIn, strPathOut, intCells, strComment = lstargs
    MinX = str((int(strX) -        intBuf + fltCellSize*intCellSizeMult ))
    MinY = str((int(strY) -        intBuf + fltCellSize*intCellSizeMult ))
    MaxX = str((int(strX) + 1000 + intBuf - fltCellSize*intCellSizeMult ))
    MaxY = str((int(strY) + 1000 + intBuf - fltCellSize*intCellSizeMult ))
    strBND = ' '.join([MinX,MaxY,MaxX,MinY])
    arcpy.Clip_management(strPathIn, strBND, strPathOut)
    t = elapsed_time(t0)
    return strComment + ", " + t
    
##def test1(lstargs):
##    intCount, strComment = lstargs
##    for i in range(intCount):
##        j = (i+1)/1.0
##        if not j % 10000000:
##            print j
##    return strComment

def DoPool(lstTasks, intWorkers):
    # Create queues
    print('\n\t\t' + str(len(lstTasks)) + ' task(s) found.')
    #print '\t\tMaking empty queues'
    task_queue = Queue()
    done_queue = Queue()

    # Submit tasks
    #print '\t\tFilling queue with tasks'
    for task in lstTasks:
        task_queue.put(task)

    # Start worker processes
    print('\t\tStarting ' + str(intWorkers) + " workers")
    for i in range(intWorkers):
        Process(target=worker, args=(task_queue, done_queue)).start()

    # Get and print results
    print('\t\tUnordered results:')
    for i in range(len(lstTasks)):
        print('\t\t\t' + done_queue.get())

    # Tell child processes to stop
    print('\t\tStop workers')
    for i in range(intWorkers):
        task_queue.put('STOP')

    print('\t\tPool Done\n')
