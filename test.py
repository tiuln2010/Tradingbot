import traceback
import threading
import time

def save_err(method):
    def wrapper(*args, **kwargs):
        try:
            result = method(*args, **kwargs)
            return result
        except :
            te = time.time()
            a = traceback.format_exc()
            print(te)
            print(a)
    return wrapper

@save_err
def helper(b, c, a = 'a'):
    help_wow(1)
    print(a,b,c)

def help_wow(x):
    print('wow'+x)

def printer():
    i = 3
    while i > 0 :
        print('zzzzz')
        time.sleep(2)
        i -= 1

#@save_err
def starter():
    h = threading.Thread(target = helper, args = (1,2))
    p = threading.Thread(target = printer)
    h.start()
    p.start()

starter()