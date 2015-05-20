# -*- encoding: utf-8 -*-

import threading

semaphore = threading.Semaphore(5)

semaphore.acquire()


semaphore.release()
semaphore.release()
semaphore.release()
semaphore.release()
semaphore.release()
print semaphore._Semaphore__value



