import threading

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
