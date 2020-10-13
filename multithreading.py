from threading import Thread,Lock
import time
counter=0
lock = Lock()
def add():
    global counter
    for _ in range(100):
        with lock:
            counter+=1
            print(counter)

t1= Thread(target=add)
t2= Thread(target=add)
t3= Thread(target=add)
t1.start()
t2.start()
t3.start()
