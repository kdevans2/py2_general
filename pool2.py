import traceback, sys, os, time, multiprocessing, pickle, subprocess
import general as gen

# ----------------------------------------
# worker and wrapper functions
def worker(qInput, qOutput):
    ''' worker function placed into queue. '''
    for TS in iter(qInput.get, 'STOP'):
        R = fWrap(TS)
        qOutput.put(R)

def fWrap(TaskSet):
    ''' Wrapper for passed functions. Organizes results, timing and exceptions into MP_ResultSet objects.'''
    try:
        iResultSet = MP_ResultSet(TaskSet.comment)
        t0 = time.time()
        for task in TaskSet.tasks:
            
            iResult = MP_Result(task.comment, task.args)
            t1 = time.time()
            
            # call function
            args = task.args
            f = task.func
            r = f(*args)
            iResult.result = r
            iResult.time = time.time() - t1
            iResultSet.addResult(iResult)

    except Exception:
        exc_type, exc_value, exc_traceback = sys.exc_info()
        strTrace = ''.join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        print(strTrace)
        iResult.error = strTrace
        iResultSet.addResult(iResult)
        iResultSet.hasError = True
        
    finally:
        # record timing and return resultset object.
        iResultSet.time = time.time() - t0
        return iResultSet

def Range2(i, j):
    ''' dummy test function '''
    time.sleep(j)
    return range(i)

def test_args(a, b= '2'):
    ''' dummy  *args test function '''
    time.sleep(a/2)
    return str(a) + str(b)

def submit(cmd, output = None):
    ''' Submit a command string to the command prompt.
        optional output will be checked for existance if given and returned if true.
    '''
    # if output exists, skip cmd and return output 
    if output and os.path.exists(output):
        print('Output already present.')
        return output
        
    r = os.system(cmd)
    if output:
        if not os.path.exists(output):
            raise Exception('Output not created: ' + output)
        return output
    else:
        if r:
            raise Exception('Nonzero exit status.')
        return 'submit'

def POpen(cmd, output = None):
    ''' function to submit a command via subprocess.Popen.
        optional output will be checked for existance if given and returned if true.
        --- NOT tested.
    '''
    # if output exists, skip cmd and return output 
    if output and os.path.exists(output):
        return output
        
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    (out, err) = proc.communicate()
    if output:
        if not os.path.exists(output):
            raise Exception('Output not created: ' + output + '\nmessage:\n' + out)
        return output
    else:
        return 'POpen'

# ----------------------------------------
# task classes
    
class MP_Task:
    ''' class to hold multiprocessing worker tasks. to be placed into MP_taskset. '''
    def __init__(self, func, args, comment = None):
        self.func = func
        self.args = args
        self.comment = comment

    def __str__(self):
        strPrint = 'MP_Task: ' + self.func.__name__ 
        return strPrint

class MP_TaskSet:
    ''' class to bundle MP_Task instances. '''
    def __init__(self, comment = None):
        self.tasks = []
        self.count = 0
        self.comment = comment

    def addTask(self, task):
        self.tasks.append(task)
        self.count += 1

    def __str__(self):
        strPrint = 'MP_TaskSet: [' + ', '.join([t.func.__name__ for t in self.tasks]) + ']'
        return strPrint
    

# ----------------------------------------
# result classes
class MP_Result:
    ''' class to hold Multiprocessing worker results. Used by fWrap. '''
    def __init__(self, strComment, args):
        self.ID = strComment # a comment or ID
        self.args = args
        self.result = None
        self.time = 0
        self.error = None
        
    def __str__(self):
        strT = gen.time_string(self.time)
        strPrint = self.ID + ", " + strT
        if self.error:
            strPrint += ', EXCEPTION: \n' + self.error
        return strPrint

class MP_ResultSet:
    ''' class to hold MP_Results. '''
    def __init__(self, strID):
        self.results = []
        self.count = 0
        self.ID = strID # like old 'strComment'
        self.time = 0
        self.hasError = False

    def addResult(self, result):
        self.results.append(result)
        self.count += 1
        
    def __str__(self):
        strT = gen.time_string(self.time)
        strPrint = str(self.ID) + ", " + strT
        if self.hasError:
            strPrint += ', EXCEPTION recorded.'
        return strPrint

class PoolResults:
    ''' class to hold multiprocessing resultset objects (MP_ResultSets) '''
    def __init__(self, workers):
        self.workers = workers
        self.runtime = 0
        self.ResultSets = []
        self.Count = 0
        self.ErrorCount = 0

    def __len__(self):
        return self.Count

    def __str__(self):
        strText = 'PoolResult object\n\tWorkers: ' + str(self.workers) + \
                  '\n\tTaskSets: ' + str(self.Count) + \
                  '\n\tErrors: ' + str(self.ErrorCount) + \
                  '\n\tTime: ' + gen.time_string(self.runtime)
        return strText
    
    def record(self, resultset):
        self.ResultSets.append(resultset)
        self.Count += 1
        if resultset.hasError:
            self.ErrorCount += 1

    def printErrors(self, listAll = False):
        intDefaultList = 6
        if listAll == True:
            intDo = self.ErrorCount
        else:
            intDo = intDefaultList
        i = 0
        bolContinue = True
        for rs in self.ResultSets:
            for r in rs.results:
                if r.error:
                    print(rs)
                    print('\t' + str(r) + '\n')
                    i += 1
                    if i == intDo:
                        intRemaining = self.ErrorCount - intDo
                        if intRemaining:
                            print('Error descriptions limited to ' + str(intDo) + ' results.\n\t' + str(intRemaining) + ' reamining.')
                            bolContinue = False
            if not bolContinue:
                break
                
    def printResultsSets(self):
        for rs in self.ResultSets:
            print('\t' + rs.ID) 
            for r in rs.results:
                print('\t' + r.ID + ': ' + str(r.result))

    def listOutputs(self, intResultSetIndex = None):
        if not intResultSetIndex is None:
            intIndex = intResultSetIndex
            return [rs.results[intIndex].result for rs in self.ResultSets]
        else:
            return [[r.result for r in rs.results] for rs in self.ResultSets]

    def Pickle(self, strTXT):
        ''' go pickle (your)self '''
        with open(strTXT, 'wb') as f:
            pickle.dump(self, f, pickle.HIGHEST_PROTOCOL)
                
        
def DoPool(lstTasks, intWorkers, txtPickle = None):
    # Create queues and result object
    print('\n\tStart Pool:')
    print('\t\t' + str(len(lstTasks)) + ' task(s).')
    t0 = time.time()
    task_queue = multiprocessing.Queue()
    done_queue = multiprocessing.Queue()
    iPoolResult = PoolResults(intWorkers)

    # Submit tasks
    #print '\t\tFilling queue with tasks'
    for task in lstTasks:
        task_queue.put(task)

    # Start worker processes
    print('\t\t' + str(intWorkers) + ' worker(s).')
    for i in range(intWorkers):
        multiprocessing.Process(target=worker, args=(task_queue, done_queue)).start()
    
    # Get and print results
    print('\t\tUnordered results:')
    for i in range(len(lstTasks)):
        resultSet = done_queue.get()
        print('\t\t\t' + str(resultSet))
        iPoolResult.record(resultSet)

    # Tell child processes to stop
    for i in range(intWorkers):
        task_queue.put('STOP')

    iPoolResult.runtime = time.time() - t0

    if iPoolResult.ErrorCount:
        print('\n\t\tPool done: WITH ERRORS!.\n')
    else:
        print('\n\t\tPool done: ' + gen.time_string(iPoolResult.runtime) + '\n')

    if txtPickle:
        iPoolResult.Pickle(txtPickle)
        
    return iPoolResult
