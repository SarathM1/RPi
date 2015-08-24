import time
import threading, Queue
import random

class WorkerThread(threading.Thread):
    
    def __init__(self, dir_q):
        super(WorkerThread, self).__init__()
        self.dir_q = dir_q
        self.stoprequest = threading.Event()

    def run(self):
        
        while not self.stoprequest.isSet():
        
            try:
                cntr = int(self.dir_q.get(True,0.5))

            except Queue.Empty as e:
                continue
        
            while cntr>0:
                print cntr,
                cntr-=1
            print '\n'
    def join(self, timeout=None):
        self.stoprequest.set()
        super(WorkerThread, self).join(timeout)

    

def main():
    dir_q = Queue.Queue()
    
    thread = WorkerThread(dir_q=dir_q)

    
    thread.start()

    while True:
        try:
            dir_q.put(random.randint(1,5))
            time.sleep(1)
        except KeyboardInterrupt, e:        # On ctr + c
            thread.join()       # Ask threads to die and wait for them to do it
            break


if __name__ == '__main__':
    main()