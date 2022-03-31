#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Mar 18 10:33:21 2021

@author: mat
"""
"""
Solution to the one-way tunnel
"""
from multiprocessing import Process
from multiprocessing import Condition, Lock
from multiprocessing import Value
from multiprocessing import current_process
import time, random

NORTH = 0
SOUTH = 1
NCARS = 10

class Monitor():
    
    def __init__(self):
        self.mutex = Lock()
        self.ncoche_N = Value('i', 0) #cohes que van al norte
        self.ncoche_S = Value('i', 0) #coches que van al sur
        self.ncoche_esperando_N = Value('i', 0) #coches que quieren ir al norte
        self.ncoche_esperando_S = Value('i', 0) #coches que quieren ir al sur
        self.no_coches_N = Condition(self.mutex)
        self.no_coches_S = Condition(self.mutex)
    
    def  no_hay_coches_N(self):
        return self.ncoche_N.value == 0 and self.ncoche_esperando_N.value == 0
    
    def  no_hay_coches_S(self):
        return self.ncoche_S.value == 0 and self.ncoche_esperando_S.value == 0
    
    def quiero_ir_N(self):
        self.mutex.acquire()
        self.ncoche_esperando_N.value += 1
        self.no_coches_S.wait_for(self.no_hay_coches_S)
        self.ncoche_esperando_N.value -= 1
        self.ncoche_N.value += 1
        self.mutex.release()
    
    def pasar_N(self):
        self.mutex.acquire()
        self.ncoche_N.value -= 1
        if self.ncoche_N.value == 0:
            self.no_coches_N.notify_all()
        self.mutex.release()
    
    def quiero_ir_S(self):
        self.mutex.acquire()
        self.ncoche_esperando_S.value += 1
        self.no_coches_N.wait_for(self.no_hay_coches_N)
        self.ncoche_esperando_S.value -= 1
        self.ncoche_S.value += 1
        self.mutex.release()
        
    def pasar_S(self):
        self.mutex.acquire()
        self.ncoche_S.value -= 1
        if self.ncoche_S.value == 0:
            self.no_coches_S.notify_all()
        self.mutex.release()
    
def delay(n=3):
    time.sleep(random.random()*n)
    
def coche_N(cid, monitor):
    delay()
    print(f"El coche {cid} quiere pasar al norte")
    monitor.quiero_ir_N()
    print(f"El coche {cid} está pasando al norte")
    delay()
    print(f"El coche {cid} sale del túnel por el norte")
    monitor.pasar_N()

def coche_S(cid, monitor):
    delay()
    print(f"El coche {cid} quiere pasar al sur")
    monitor.quiero_ir_S()
    print(f"El coche {cid} está pasando al sur")
    delay()
    print(f"El coche {cid} sale del túnel por el sur")
    monitor.pasar_S()

def main():
    monitor = Monitor()
    coches = []
    cid = 0
    for _ in range(NCARS):
        direction = NORTH if random.randint(0,1)==1  else SOUTH
        cid += 1
        if direction == NORTH:
            p = Process(target=coche_N, args=(cid, monitor))
        else:
            p = Process(target=coche_S, args=(cid, monitor)) 
        p.start()
        coches.append(p)
        
    for p in coches:
        p.join()

if __name__ == '__main__':
    main()
