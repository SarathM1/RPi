import os, time
import threading, Queue

class WorkerThread(threading.Thread):
    """ A worker thread that takes directory names from a queue, finds all
        files in them recursively and reports the result.

        Input is done by placing directory names (as strings) into the
        Queue passed in dir_q.

        Output is done by placing tuples into the Queue passed in result_q.
        Each tuple is (thread name, dirname, [list of files]).

        Ask the thread to stop by calling its join() method.
    """
    def __init__(self, dir_q, result_q):
        super(WorkerThread, self).__init__()
        self.dir_q = dir_q
        self.result_q = result_q
        self.stoprequest = threading.Event()

    def run(self):
        # As long as we weren't asked to stop, try to take new tasks from the
        # queue. The tasks are taken with a blocking 'get', so no CPU
        # cycles are wasted while waiting.
        # Also, 'get' is given a timeout, so stoprequest is always checked,
        # even if there's nothing in the queue.
        
        #while not self.stoprequest.isSet():
        try:
            cntr = int(self.dir_q.get(True,0.05))

        except Queue.Empty as e:
            print "dir_q.get: ", str(e) 
        self.result_q.put((1,2,3))

        while cntr>0:
            try:
                #cntr = self.dir_q.get(True,0.05)
                print cntr
                cntr-=1
                """
                dirname = self.dir_q.get(True, 0.05)

                filenames = list(self._files_in_dir(dirname))
                self.result_q.put((self.name, dirname, filenames))
                """

            except Queue.Empty:
                continue

    def join(self, timeout=None):
        self.stoprequest.set()
        super(WorkerThread, self).join(timeout)

    def _files_in_dir(self, dirname):
        """ Given a directory name, yields the names of all files (not dirs)
            contained in this directory and its sub-directories.
        """
        for path, dirs, files in os.walk(dirname):
            for file in files:
                yield os.path.join(path, file)

def main(args):
    # Create a single input and a single output queue for all threads.
    dir_q = Queue.Queue()
    result_q = Queue.Queue()

    # Create the "thread pool"
    #pool = [WorkerThread(dir_q=dir_q, result_q=result_q) for i in range(4)]
    pool = WorkerThread(dir_q=dir_q, result_q=result_q)

    # Start all threads
    #for thread in pool:
    #    thread.start()
    pool.start()

    # Give the workers some work to do
    work_count = 0

    for dir in args:
        work_count+=1
        dir_q.put(dir)
        """
        if os.path.exists(dir):
            work_count += 1
            dir_q.put(dir)
        """
    print 'Assigned %s dirs to workers' % work_count

    # Now get all the results
    while work_count > 0:
        # Blocking 'get' from a Queue.
        result = result_q.get()
        print '%s: %s : %s' % (
            result[0], result[1], result[2])
        work_count -= 1

    # Ask threads to die and wait for them to do it
    #for thread in pool:
        #thread.join()
    pool.join()


if __name__ == '__main__':
    import sys
    main(sys.argv[1:])