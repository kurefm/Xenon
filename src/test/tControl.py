# -*- coding: utf-8 -*-

import thread
import threading
import time

LOCK = threading.Lock()


def release_lock():
    while 1:
        global LOCK
        print help(LOCK)
        try:
            LOCK.release()
        except thread.error:
            pass
        time.sleep(0.2)


def control(timestamp, timer):
    global LOCK
    LOCK.acquire()
    print '[{0}] start time: {1}, print time: {2}.'.format(timer, timestamp, time.time())


if __name__ == '__main__':
    thread.start_new_thread(release_lock, ())
    for i in range(1, 101):
        thread.start_new_thread(control, (time.time(), i))

    raw_input()


