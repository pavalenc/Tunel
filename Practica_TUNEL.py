# -*- coding: utf-8 -*-
"""
Created on Thu Mar 24 10:20:13 2022

@author: Elena
"""

import time
import random
from multiprocessing import Lock, Condition, Process
from multiprocessing import Value
from multiprocessing import current_process


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
        self.sentido = Value('i', 0) # 0: ir al norte, 1: ir al sur
        self.no_coches_N = Condition(self.mutex)
        self.no_coches_S = Condition(self.mutex)
    
    def no_hay_coches_N(self):
        return self.ncoche_N.value == 0 and (self.sentido.value == 1 or self.ncoche_esperando_N.value == 0)
    
    def no_hay_coches_S(self):
        return self.ncoche_S.value == 0 and (self.sentido.value == 0 or self.ncoche_esperando_S.value == 0)
    
    def quiero_ir_N(self):
        self.mutex.acquire()
        self.ncoche_esperando_N.value += 1 #para indicar que hay un coche más que quiere ir al norte
        self.no_coches_S.wait_for(self.no_hay_coches_S) #espera a que se cumpla las condiciones de la función no_hay_coches_N para poder entrar
        self.ncoche_esperando_N.value -= 1 #deja de esperar porque procede a entrar
        self.ncoche_N.value += 1 #y entra
        self.mutex.release()
   
    
    def pasar_N(self): #está dentro del tunel y sale por el norte
        self.mutex.acquire()
        self.ncoche_N.value -= 1 #sale
        self.sentido.value = 1 #para cuando sale el primero, ya damos el turno a los que quieren ir al sur
        if self.ncoche_N.value == 0:
            self.no_coches_N.notify_all() #así, cuando todos los que estaban dentro han salido, se da un aviso para que ya puedan entrar los del sur
        self.mutex.release()
    
    def quiero_ir_S(self):
        self.mutex.acquire()
        self.ncoche_esperando_S.value += 1
        self.no_coches_N.wait_for(self.no_hay_coches_N) #espero a que hayan salido todos los del norte
        self.ncoche_esperando_S.value -= 1 
        self.ncoche_S.value += 1
        self.mutex.release()
        
    def pasar_S(self): #está dentro del tunel y sale por el sur
        self.mutex.acquire()
        self.ncoche_S.value -= 1
        self.sentido.value == 0
        if self.ncoche_S.value == 0:
            self.no_coches_S.notify_all()
        self.mutex.release()
    
def delay(n=3):
    time.sleep(random.random()*n)
    
def coche_N(cid, monitor):
    delay()
    print(f"El coche {cid} quiere pasar el tunel hacia el norte")
    monitor.quiero_ir_N()
    print(f"El coche {cid} está pasando al norte")
    delay()
    print(f"El coche {cid} sale del túnel por el norte")
    monitor.pasar_N()

def coche_S(cid, monitor):
    delay()
    print(f"El coche {cid} quiere pasar el tunel hacia el sur")
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
    