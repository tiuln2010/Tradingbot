import time
import datetime
import traceback

def timeit(method):
    def timed(*args, **kw):
        
        ts = time.time()
        result = method(*args, **kw)
        te = time.time()

        now = str(datetime.datetime.now())
        msg = ('method : {} (args : {}, {}) {:06.2f} sec').format(method.__name__, args, kw, te-ts)
        f = open('speedlog.txt', 'a')
        f.write('\n'+now+'\n')
        f.write(msg)
        f.close()

        return result
    return timed

def save_err(method):
    def wrapper(*args, **kw):
        try:
            result = method(*args, **kw)
            return result
        except :
            def classification():
                now = str(datetime.datetime.now())
                name = method.__name__
                msg = ('{} method : {} (args : {}, {})').format(now, name, args, kw)
                return msg

            msg = classification()
            trace = str(traceback.format_exc())
            
            f = open('errorlog.txt', 'a')
            f.write('\n'+msg+'\n')
            f.write(trace)
            f.close()
    return wrapper
