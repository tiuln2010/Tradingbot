import time
import threading
import multiprocessing

class Repeat():
    def __init__(self, fuc, t):
        self.t = t
        self.fuc = fuc
        self.thread = threading.Timer(self.t, self.handling)
        
    def handling(self):
        self.fuc()
        self.thread = threading.Timer(self.t, self.handling)
        self.thread.start()

    def start(self):
        self.thread.start()

    def cancel(self):
        self.thread.cancel()

class Multi():
    def __init__(self, funcs):
        self.funcs = funcs

    def run_process(self):
        counter = 0
        processes = {}
        for func in self.funcs:
           processes['process_'+str(counter)] = multiprocessing.Process(target=func)
           processes['process_'+str(counter)].start()
           counter += 1
        print("{} processes are started".format(counter))
        return processes

    def wait_end(self, processes):
        for process in processes.values():
            process.join()
        print("processes are ended")
        return True


        



