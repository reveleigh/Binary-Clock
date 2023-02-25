import _thread
import time

# Create a lock object
lock = _thread.allocate_lock()

# Define a function to be executed by Thread 1
def thread1():
    print("Thread 1 started")
    time.sleep(2)
    print("Thread 1 releasing lock")
    lock.release()

# Define a function to be executed by Thread 2
def thread2():
    print("Thread 2 waiting for lock")
    lock.acquire()
    print("Thread 2 acquired lock and running")
    time.sleep(1)
    print("Thread 2 releasing lock")
    lock.release()

# Create Thread 1
_thread.start_new_thread(thread1, ())

# Wait for Thread 1 to release the lock
time.sleep(1)

# Create Thread 2
_thread.start_new_thread(thread2, ())

# Wait for both threads to finish
time.sleep(5)
